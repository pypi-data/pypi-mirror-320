import abc
import dataclasses
import logging
import numbers
from concurrent.futures import ThreadPoolExecutor, as_completed
from inspect import signature
from typing import Any, Iterable, List, Optional

import pandas as pd
from mlflow import MlflowException
from mlflow.deployments import set_deployments_target
from mlflow.metrics import MetricValue
from mlflow.models import EvaluationMetric

from databricks.rag_eval import constants, context, env_vars, schemas, session
from databricks.rag_eval.clients.managedrag import managed_rag_client
from databricks.rag_eval.config import assessment_config, evaluation_config
from databricks.rag_eval.evaluation import entities
from databricks.rag_eval.mlflow import mlflow_utils
from databricks.rag_eval.utils import error_utils, rate_limit, rating_utils

_logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class Assessment(abc.ABC):
    """
    Assessment represents a method to assess the quality of a RAG system.
    """

    config: assessment_config.AssessmentConfig

    @abc.abstractmethod
    def run(self, eval_item: entities.EvalItem) -> List[entities.AssessmentResult]:
        """
        Run the assessment on a single eval item and produce a list of assessment results.
        A single eval item can produce multiple assessment results since multiple assessments can be batch computed
        together for a single EvalItem.

        If the eval item does not have required fields for the assessment, return an empty list.

        :param eval_item: The eval item to assess.
        :return: A list of assessment results.
        """
        pass


@dataclasses.dataclass(frozen=True)
class BuiltInAssessment(Assessment):
    """
    Builtin assessment using the LLM judge service to compute the assessments
    """

    config: assessment_config.BuiltinAssessmentConfig
    """Configuration for the assessment."""
    rate_limiter: rate_limit.RateLimiter
    """Rate limiter to apply to the LLM endpoint caller."""
    managed_rag_client: managed_rag_client.ManagedRagClient
    """LLM judge client to use for the assessment."""
    input_requirement_expression: Optional[
        assessment_config.AssessmentInputRequirementExpression
    ] = None

    def run(self, eval_item: entities.EvalItem) -> List[entities.AssessmentResult]:
        # Fail fast if evaluation item does not meet input requirements
        if self.input_requirement_expression is not None:
            input_requirements_error = _get_unsatisfied_input_requirements(
                eval_item, self.input_requirement_expression
            )
            if input_requirements_error is not None:
                return [
                    _construct_input_requirements_error(
                        self.config, input_requirements_error, eval_item
                    )
                ]

        with self.rate_limiter:
            return self.managed_rag_client.get_assessment(eval_item, self.config)


@dataclasses.dataclass(frozen=True)
class EvaluationMetricAssessment(Assessment):
    """
    Custom assessment using the MLflow EvaluationMetric provided by the user.
    """

    config: assessment_config.EvaluationMetricAssessmentConfig
    """Configuration for the assessment."""
    rate_limiter: rate_limit.RateLimiter
    """Rate limiter to apply to the eval_fn calls."""
    managed_rag_client: managed_rag_client.ManagedRagClient
    """LLM judge client to use to emit usage data."""

    @property
    def name(self):
        return self.config.assessment_name

    @property
    def assessment_type(self):
        return self.config.assessment_type

    def run(self, eval_item: entities.EvalItem) -> List[entities.AssessmentResult]:
        # Note: this lets us call the Databricks endpoints.
        set_deployments_target(mlflow_utils.resolve_deployments_target())
        match self.assessment_type:
            case assessment_config.AssessmentType.RETRIEVAL:
                return [self._run_per_chunk_assessment(eval_item)]
            case assessment_config.AssessmentType.RETRIEVAL_LIST:
                return [self._run_per_request_assessment(eval_item)]
            case assessment_config.AssessmentType.ANSWER:
                return [self._run_per_request_assessment(eval_item)]
            case _:
                raise error_utils.ValidationError(
                    f"Assessment type '{self.assessment_type}' is not supported."
                    f"Supported types are: {assessment_config.AssessmentType.ANSWER}, {assessment_config.AssessmentType.RETRIEVAL_LIST}, and {assessment_config.AssessmentType.RETRIEVAL}."
                )

    def _run_per_request_assessment(
        self, eval_item: entities.EvalItem
    ) -> entities.PerRequestAssessmentResult:
        """
        Run a per-request assessment on the eval item and produce a per-request assessment result.
        """
        eval_metric = self._load_metric()
        rating: entities.Rating = self._compute_rating(
            eval_metric, eval_item, chunk=None
        )

        return entities.PerRequestAssessmentResult(
            assessment_name=self.name,
            assessment_type=self.assessment_type,
            assessment_source=entities.AssessmentSource.custom(),
            rating=rating,
        )

    def _run_per_chunk_assessment(
        self, eval_item: entities.EvalItem
    ) -> entities.PerChunkAssessmentResult:
        """
        Run a per-chunk assessment on the eval item and produce a per-chunk assessment result.

        The per-chunk assessment is a positional assessment, where each position in the retrieval context
        is rated separately.
        """
        if eval_item.retrieval_context is None:
            return entities.PerChunkAssessmentResult(
                assessment_name=self.name,
                assessment_source=entities.AssessmentSource.custom(),
                positional_rating={
                    0: entities.Rating.error(
                        error_message="Missing required field(s): retrieved_context",
                        error_code=rating_utils.MISSING_INPUTS_ERROR_CODE,
                    )
                },
            )
        positional_ratings = {}
        eval_metric = self._load_metric()
        for pos, chunk in enumerate(eval_item.retrieval_context):
            # Skip the chunk if it is empty
            if chunk is None or not chunk.content:
                positional_ratings[pos] = entities.Rating.value(
                    rationale=constants.CHUNK_CONTENT_IS_EMPTY_RATIONALE,
                )
                continue

            rating: entities.Rating = self._compute_rating(
                eval_metric, eval_item, chunk
            )

            positional_ratings[pos] = rating

        return entities.PerChunkAssessmentResult(
            assessment_name=self.name,
            assessment_source=entities.AssessmentSource.custom(),
            positional_rating=positional_ratings,
        )

    def _load_metric(self) -> EvaluationMetric:
        """
        Loads the Mlflow EvaluationMetric object.
        """
        return self.config.evaluation_metric

    def _compute_rating(
        self,
        eval_metric: EvaluationMetric,
        eval_item: entities.EvalItem,
        chunk: Optional[entities.Chunk],
    ) -> entities.Rating:
        """
        Compute a Rating for an assessment given the EvalItem, input chunk and position.
        If chunk and position are both defined, treat this as a retrieval assessment.
        """
        try:
            eval_fn_kwargs = _extract_mlflow_eval_fn_kwargs(
                eval_metric, eval_item, chunk
            )
            with self.rate_limiter:
                # noinspection PyCallingNonCallable
                metric_value = eval_metric(**eval_fn_kwargs)
        except MlflowException as e:
            # Can happen if the eval item doesn't contain the required fields
            # for the custom metric. We can't determine this beforehand as the
            # prompt is baked into the eval_fn and can't be extracted.
            # In this case, return an error Rating
            return entities.Rating.error(str(e))

        return _mlflow_eval_value_to_rating(metric_value, self.config.binary_conversion)


def _get_assessments_for_configs(
    assessment_configs: Iterable[assessment_config.AssessmentConfig],
) -> List[Assessment]:
    """
    Construct a list of assessments for an EvaluationConfig.
    """
    builtin_rate_limiter = _build_rate_limiter_for_assessment()
    custom_rate_limiter = _build_rate_limiter_for_assessment()
    managed_rag_client = context.get_context().build_managed_rag_client()

    results = []
    for assessment_conf in assessment_configs:
        if isinstance(assessment_conf, assessment_config.BuiltinAssessmentConfig):
            assessment_name = assessment_conf.assessment_name
            try:
                input_requirement_expression = (
                    managed_rag_client.get_assessment_metric_definitions(
                        [assessment_name]
                    ).get(assessment_name, None)
                )
            except Exception as e:
                # Log the error and continue with the assessment
                _logger.debug(
                    f"Error in collecting input requirements for {assessment_name}: {e}"
                )
                input_requirement_expression = None

            results.append(
                BuiltInAssessment(
                    config=assessment_conf,
                    rate_limiter=builtin_rate_limiter,
                    managed_rag_client=managed_rag_client,
                    input_requirement_expression=input_requirement_expression,
                )
            )
        elif isinstance(
            assessment_conf, assessment_config.EvaluationMetricAssessmentConfig
        ):
            results.append(
                EvaluationMetricAssessment(
                    config=assessment_conf,
                    rate_limiter=custom_rate_limiter,
                    managed_rag_client=managed_rag_client,
                )
            )
    return results


def _build_rate_limiter_for_assessment() -> rate_limit.RateLimiter:
    """Build a rate limiter for the assessment."""
    # Return a no-op rate limiter if the rate limiter for assessment is not enabled
    if not env_vars.RAG_EVAL_ENABLE_RATE_LIMIT_FOR_ASSESSMENT.get():
        return rate_limit.RateLimiter.no_op()

    # For now, rate limiter config is from environment variables
    rate_limit_config = rate_limit.RateLimitConfig(
        quota=env_vars.RAG_EVAL_RATE_LIMIT_QUOTA.get(),
        time_window_in_seconds=env_vars.RAG_EVAL_RATE_LIMIT_TIME_WINDOW_IN_SECONDS.get(),
    )
    return rate_limit.RateLimiter.build(
        quota=rate_limit_config.quota,
        time_window_in_seconds=rate_limit_config.time_window_in_seconds,
    )


def _get_assessments_to_run(
    config: evaluation_config.EvaluationConfig, eval_item: entities.EvalItem
) -> List[Assessment]:
    """
    Get the minimum required list of assessments for a given evaluation item.
    :param config: The evaluation config
    :param eval_item: Evaluation item
    :return: Minimum list of assessments to run
    """
    assessments_to_run: List[Assessment] = _get_assessments_for_configs(
        tuple(config.assessment_configs)
    )
    # If the assessments are provided by the user, do not filter them
    if not config.is_default_config:
        return assessments_to_run

    enabled_metrics = set(assessment_config.builtin_assessment_names())
    if (
        eval_item.ground_truth_answer is not None
        or eval_item.expected_facts is not None
    ):
        enabled_metrics -= (
            evaluation_config.unnecessary_metrics_with_expected_response_or_expected_facts()
        )
    elif eval_item.grading_notes is not None:
        enabled_metrics -= evaluation_config.unnecessary_metrics_with_grading_notes()
    else:
        enabled_metrics -= (
            evaluation_config.metrics_requiring_ground_truth_or_expected_facts_or_grading_notes()
        )

    # If no guidelines column and no global guidelines, disable guideline adherence
    if eval_item.guidelines is None and config.global_guidelines is None:
        enabled_metrics -= {assessment_config.GUIDELINE_ADHERENCE.assessment_name}

    # If no retrieval context, disable retrieval metrics
    if eval_item.retrieval_context is None:
        enabled_metrics -= {
            config.assessment_name
            for config in assessment_config._builtin_assessment_configs()
            if config.require_retrieval_context
            or config.require_retrieval_context_array
        }

    minimum_assessments_to_run = [
        assessment
        for assessment in assessments_to_run
        if (
            isinstance(assessment, BuiltInAssessment)
            and assessment.config.assessment_name in enabled_metrics
        )
        or isinstance(assessment, EvaluationMetricAssessment)
    ]
    return minimum_assessments_to_run


def generate_llm_assessments(
    *,
    eval_item: entities.EvalItem,
    config: evaluation_config.EvaluationConfig,
) -> List[entities.AssessmentResult]:
    """
    Performs the LLM judged assessment on a EvalItems and generates a list of assessment results
    using the given LLM judge model and assessments.

    The method only uses the compatible assessments for the given eval dataset.
    An assessment is incompatible if it requires extra information which is missing in the eval item.
    For example, an assessment is not compatible if it requires retrieval context
    but the eval dataset does not have retrieval context.

    :param eval_item: The eval item to evaluate on.
    :param config: The config for the evaluation.
    """
    assessments = _get_assessments_to_run(config, eval_item)
    if not assessments:
        return []

    assessment_results: List[entities.AssessmentResult] = []
    # Use a thread pool to run assessments in parallel
    # Use the number of assessments as the number of workers
    with ThreadPoolExecutor(max_workers=len(assessments)) as executor:
        futures = [
            executor.submit(
                _run_assessment,
                eval_item=eval_item,
                assessment=assessment,
                current_session=session.current_session(),
            )
            for assessment in assessments
        ]

        # Run the global guidelines assessment if the guideline adherence judge is running and
        # global guidelines are defined in the config
        guideline_adherence_assessment = next(
            (
                assessment
                for assessment in assessments
                if isinstance(assessment, BuiltInAssessment)
                and assessment.config == assessment_config.GUIDELINE_ADHERENCE
            ),
            None,
        )
        if (
            config.global_guidelines is not None
            and guideline_adherence_assessment is not None
        ):
            global_guidelines_eval_item = eval_item.as_dict()
            global_guidelines_eval_item["guidelines"] = config.global_guidelines
            futures.append(
                executor.submit(
                    _run_assessment,
                    eval_item=entities.EvalItem.from_dict(global_guidelines_eval_item),
                    assessment=BuiltInAssessment(
                        config=assessment_config.GLOBAL_GUIDELINE_ADHERENCE,
                        rate_limiter=_build_rate_limiter_for_assessment(),
                        managed_rag_client=context.get_context().build_managed_rag_client(),
                        input_requirement_expression=guideline_adherence_assessment.input_requirement_expression,
                    ),
                    current_session=session.current_session(),
                )
            )

        try:
            for future in as_completed(futures):
                result = future.result()
                assessment_results.extend(result)
        except KeyboardInterrupt:
            for future in futures:
                future.cancel()
            print("Assessment generation interrupted.")
            raise

    return assessment_results


def _run_assessment(
    eval_item: entities.EvalItem,
    assessment: Assessment,
    current_session: Optional[session.Session] = None,
) -> List[entities.AssessmentResult]:
    """
    Run the assessment on a single eval item and produce a list of assessment results.
    """
    session.set_session(current_session)
    return assessment.run(eval_item)


def _extract_mlflow_eval_fn_kwargs(
    eval_metric: EvaluationMetric,
    eval_item: entities.EvalItem,
    chunk: Optional[entities.Chunk],
) -> Any:
    """
    Given an eval_item, create the dictionary of kwargs to provide to the eval_fn for a custom
    metric.
    To support metrics from `make_genai_metric`, we also include args like `inputs, `predictions`, `context`, and `targets`.
    Excludes None values or args not required by the eval_metric.
    """
    base_kwargs = {
        schemas.REQUEST_COL: eval_item.question,
        constants.MLFLOW_EVAL_FN_INPUTS: eval_item.question,
        schemas.RESPONSE_COL: eval_item.answer,
        constants.MLFLOW_EVAL_FN_PREDICTIONS: eval_item.answer,
        schemas.RETRIEVED_CONTEXT_COL: (
            eval_item.concatenated_retrieval_context if chunk is None else chunk.content
        ),
        constants.MLFLOW_EVAL_FN_CONTEXT: (
            eval_item.concatenated_retrieval_context if chunk is None else chunk.content
        ),
        schemas.EXPECTED_RESPONSE_COL: eval_item.ground_truth_answer,
        constants.MLFLOW_EVAL_FN_TARGETS: eval_item.ground_truth_answer,
    }
    # noinspection PyTypeChecker
    required_args = set(signature(eval_metric).parameters.keys())
    return {
        key: pd.Series([value])
        for key, value in base_kwargs.items()
        if value is not None and key in required_args
    }


def _mlflow_eval_value_to_rating(
    mlflow_metric_value: Optional[MetricValue],
    binary_conversion: Optional[assessment_config.BinaryConversion],
) -> entities.Rating:
    """
    Convert the MLflow metric value to a Rating object.
    Assumes that the MLflow metric value only contains results for a single row.
    """
    # Return error rating if the scores or justifications are empty
    if (
        mlflow_metric_value is None
        or mlflow_metric_value.scores is None
        or len(mlflow_metric_value.scores) == 0
        or mlflow_metric_value.justifications is None
        or len(mlflow_metric_value.justifications) == 0
    ):
        return entities.Rating.error(
            f"Fail to get the assessment result: {mlflow_metric_value}"
        )

    # Assume that the scores and justifications are for a single row
    assert (
        len(mlflow_metric_value.scores) == 1
    ), f"Expected a single score, but got {len(mlflow_metric_value.scores)} scores."
    score = mlflow_metric_value.scores[0]
    justification = mlflow_metric_value.justifications[0]

    if score is None:
        # If the score is None, it means there is as an error.
        # In this case, the error message is the justification.
        return entities.Rating.error(justification)

    if not isinstance(score, numbers.Real):
        # If the score is not a real number, we treat it as an error.
        return entities.Rating.error(
            f"Could not extract numerical score from '{score}': {justification}"
        )
    else:
        bool_value = binary_conversion.convert(score) if binary_conversion else None
        categorical_value = (
            entities.CategoricalRating.YES
            if bool_value
            else (entities.CategoricalRating.NO if bool_value is not None else None)
        )
        return entities.Rating.value(
            categorical_value=categorical_value,
            double_value=float(score),
            rationale=justification,
        )


def _get_unsatisfied_input_requirements(
    eval_item: entities.EvalItem,
    input_requirement_expression: assessment_config.AssessmentInputRequirementExpression,
) -> Optional[entities.Rating]:
    """
    Check if the evaluation item satisfies the input requirements specified in the input requirement expression.
    :param eval_item: Evaluation item
    :param input_requirement_expression: Input requirement expression
    :return: None if the input requirements are satisfied, otherwise an error rating
    """
    eval_dict = eval_item.as_dict()
    missing_required_fields = [
        column
        for column in assessment_config.AssessmentInputRequirementExpression.get_user_facing_requirement_names(
            input_requirement_expression.required
        )
        if eval_dict.get(column, None) is None
    ]
    at_least_one_of_requirements = assessment_config.AssessmentInputRequirementExpression.get_user_facing_requirement_names(
        input_requirement_expression.at_least_one_of
    )
    at_least_one_of_fields = [
        column
        for column in at_least_one_of_requirements
        if eval_dict.get(column, None) is not None
    ]
    missing_at_least_one_of_fields = (
        [" or ".join(at_least_one_of_requirements)]
        if len(at_least_one_of_requirements) and not len(at_least_one_of_fields)
        else []
    )

    if len(missing_required_fields) or len(missing_at_least_one_of_fields):
        missing_fields = ", ".join(
            missing_required_fields + missing_at_least_one_of_fields
        )
        return entities.Rating.error(
            error_message=f"Missing required field(s): {missing_fields}",
            error_code=rating_utils.MISSING_INPUTS_ERROR_CODE,
        )

    conflicting_at_most_one_of_fields = [
        column
        for column in assessment_config.AssessmentInputRequirementExpression.get_user_facing_requirement_names(
            input_requirement_expression.at_most_one_of
        )
        if eval_dict.get(column, None) is not None
    ]
    if len(conflicting_at_most_one_of_fields) > 1:
        conflicting_fields = " or ".join(conflicting_at_most_one_of_fields)
        return entities.Rating.error(
            error_message=f"Conflicting field(s): more than one of [{conflicting_fields}] cannot be defined",
            error_code=rating_utils.CONFLICTING_INPUTS_ERROR_CODE,
        )

    return None


def _construct_input_requirements_error(
    config: assessment_config.AssessmentConfig,
    input_requirements_error: entities.Rating,
    eval_item: entities.EvalItem,
) -> entities.AssessmentResult:
    """
    Returns the assessment results for the unsatisfied input requirements for the given eval item.
    :param config: Assessment config
    :param input_requirements_error: Input requirements error
    :param eval_item: Evaluation item
    :return: Assessment result for the unsatisfied input requirements
    """
    assessment_name = config.assessment_name
    input_requirements_error.error_message += f" for metric: {assessment_name}"
    if config.assessment_type == assessment_config.AssessmentType.RETRIEVAL:
        num_chunks = (
            len(eval_item.retrieval_context)
            if eval_item.retrieval_context is not None
            else 0
        )
        return entities.PerChunkAssessmentResult(
            assessment_name=assessment_name,
            assessment_source=entities.AssessmentSource.builtin(),
            positional_rating={
                idx: input_requirements_error for idx in range(num_chunks)
            },
        )
    else:
        return entities.PerRequestAssessmentResult(
            assessment_name=assessment_name,
            assessment_type=config.assessment_type,
            assessment_source=entities.AssessmentSource.builtin(),
            rating=input_requirements_error,
        )
