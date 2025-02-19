from typing import List, Optional

from mlflow.exceptions import MlflowException
from mlflow.metrics.base import EvaluationExample
from mlflow.metrics.genai.genai_metric import make_genai_metric
from mlflow.metrics.genai.utils import _get_latest_metric_version
from mlflow.models import EvaluationMetric
from mlflow.protos.databricks_pb2 import INTERNAL_ERROR, INVALID_PARAMETER_VALUE
from mlflow.utils.annotations import experimental
from mlflow.utils.class_utils import _get_class_from_string


@experimental
def answer_similarity(
    model: Optional[str] = None,
    metric_version: Optional[str] = None,
    examples: Optional[List[EvaluationExample]] = None,
    judge_request_timeout=60,
) -> EvaluationMetric:
    """
    This function will create a genai metric used to evaluate the answer similarity of an LLM
    using the model provided. Answer similarity will be assessed by the semantic similarity of the
    output to the ``ground_truth``, which should be specified in the ``targets`` column.

    The ``targets`` eval_arg must be provided as part of the input dataset or output
    predictions. This can be mapped to a column of a different name using ``col_mapping``
    in the ``evaluator_config`` parameter, or using the ``targets`` parameter in mlflow.evaluate().

    An MlflowException will be raised if the specified version for this metric does not exist.

    :param model: (Optional) The model that will be used to evaluate this metric. Defaults to
        gpt-4. Your use of a third party LLM service (e.g., OpenAI) for evaluation may
        be subject to and governed by the LLM service's terms of use.
    :param metric_version: (Optional) The version of the answer similarity metric to use.
        Defaults to the latest version.
    :param examples: (Optional) Provide a list of examples to help the judge model evaluate the
        answer similarity. It is highly recommended to add examples to be used as a reference to
        evaluate the new results.
    :param judge_request_timeout: (Optional) The timeout in seconds for the judge API request.
        Defaults to 60 seconds.
    :return: A metric object
    """
    if metric_version is None:
        metric_version = _get_latest_metric_version()
    class_name = f"mlflow.metrics.genai.prompts.{metric_version}.AnswerSimilarityMetric"
    try:
        answer_similarity_class_module = _get_class_from_string(class_name)
    except ModuleNotFoundError:
        raise MlflowException(
            f"Failed to find answer similarity metric for version {metric_version}."
            f" Please check the version",
            error_code=INVALID_PARAMETER_VALUE,
        ) from None
    except Exception as e:
        raise MlflowException(
            f"Failed to construct answer similarity metric {metric_version}. Error: {e!r}",
            error_code=INTERNAL_ERROR,
        ) from None

    if examples is None:
        examples = answer_similarity_class_module.default_examples
    if model is None:
        model = answer_similarity_class_module.default_model

    return make_genai_metric(
        name="answer_similarity",
        definition=answer_similarity_class_module.definition,
        grading_prompt=answer_similarity_class_module.grading_prompt,
        examples=examples,
        version=metric_version,
        model=model,
        grading_context_columns=answer_similarity_class_module.grading_context_columns,
        parameters=answer_similarity_class_module.parameters,
        aggregations=["mean", "variance", "p90"],
        greater_is_better=True,
        judge_request_timeout=judge_request_timeout,
    )


@experimental
def answer_correctness(
    model: Optional[str] = None,
    metric_version: Optional[str] = None,
    examples: Optional[List[EvaluationExample]] = None,
    judge_request_timeout=60,
) -> EvaluationMetric:
    """
    This function will create a genai metric used to evaluate the answer correctness of an LLM
    using the model provided. Answer correctness will be assessed by the accuracy of the provided
    output based on the ``ground_truth``, which should be specified in the ``targets`` column.

    The ``targets`` eval_arg must be provided as part of the input dataset or output
    predictions. This can be mapped to a column of a different name using ``col_mapping``
    in the ``evaluator_config`` parameter, or using the ``targets`` parameter in mlflow.evaluate().

    An MlflowException will be raised if the specified version for this metric does not exist.

    :param model: (Optional) The model that will be used to evaluate this metric. Defaults to
        gpt-4. Your use of a third party LLM service (e.g., OpenAI) for evaluation may
        be subject to and governed by the LLM service's terms of use.
    :param metric_version: (Optional) The version of the answer correctness metric to use.
        Defaults to the latest version.
    :param examples: (Optional) Provide a list of examples to help the judge model evaluate the
        answer correctness. It is highly recommended to add examples to be used as a reference to
        evaluate the new results.
    :param judge_request_timeout: (Optional) The timeout in seconds for the judge API request.
        Defaults to 60 seconds.
    :return: A metric object
    """
    if metric_version is None:
        metric_version = _get_latest_metric_version()
    class_name = f"mlflow.metrics.genai.prompts.{metric_version}.AnswerCorrectnessMetric"
    try:
        answer_correctness_class_module = _get_class_from_string(class_name)
    except ModuleNotFoundError:
        raise MlflowException(
            f"Failed to find answer correctness metric for version {metric_version}."
            f"Please check the version",
            error_code=INVALID_PARAMETER_VALUE,
        ) from None
    except Exception as e:
        raise MlflowException(
            f"Failed to construct answer correctness metric {metric_version}. Error: {e!r}",
            error_code=INTERNAL_ERROR,
        ) from None

    if examples is None:
        examples = answer_correctness_class_module.default_examples
    if model is None:
        model = answer_correctness_class_module.default_model

    return make_genai_metric(
        name="answer_correctness",
        definition=answer_correctness_class_module.definition,
        grading_prompt=answer_correctness_class_module.grading_prompt,
        examples=examples,
        version=metric_version,
        model=model,
        grading_context_columns=answer_correctness_class_module.grading_context_columns,
        parameters=answer_correctness_class_module.parameters,
        aggregations=["mean", "variance", "p90"],
        greater_is_better=True,
        judge_request_timeout=judge_request_timeout,
    )


@experimental
def faithfulness(
    model: Optional[str] = None,
    metric_version: Optional[str] = _get_latest_metric_version(),
    examples: Optional[List[EvaluationExample]] = None,
    judge_request_timeout=60,
) -> EvaluationMetric:
    """
    This function will create a genai metric used to evaluate the faithfullness of an LLM using the
    model provided. Faithfulness will be assessed based on how factually consistent the output
    is to the ``context``.

    The ``context`` eval_arg must be provided as part of the input dataset or output
    predictions. This can be mapped to a column of a different name using ``col_mapping``
    in the ``evaluator_config`` parameter.

    An MlflowException will be raised if the specified version for this metric does not exist.

    :param model: (Optional) The model that will be used to evaluate this metric. Defaults to
        gpt-4. Your use of a third party LLM service (e.g., OpenAI) for evaluation may
        be subject to and governed by the LLM service's terms of use.
    :param metric_version: (Optional) The version of the faithfulness metric to use.
        Defaults to the latest version.
    :param examples: (Optional) Provide a list of examples to help the judge model evaluate the
        faithfulness. It is highly recommended to add examples to be used as a reference to evaluate
        the new results.
    :param judge_request_timeout: (Optional) The timeout in seconds for the judge API request.
        Defaults to 60 seconds.
    :return: A metric object
    """
    class_name = f"mlflow.metrics.genai.prompts.{metric_version}.FaithfulnessMetric"
    try:
        faithfulness_class_module = _get_class_from_string(class_name)
    except ModuleNotFoundError:
        raise MlflowException(
            f"Failed to find faithfulness metric for version {metric_version}."
            f" Please check the version",
            error_code=INVALID_PARAMETER_VALUE,
        ) from None
    except Exception as e:
        raise MlflowException(
            f"Failed to construct faithfulness metric {metric_version}. Error: {e!r}",
            error_code=INTERNAL_ERROR,
        ) from None

    if examples is None:
        examples = faithfulness_class_module.default_examples
    if model is None:
        model = faithfulness_class_module.default_model

    return make_genai_metric(
        name="faithfulness",
        definition=faithfulness_class_module.definition,
        grading_prompt=faithfulness_class_module.grading_prompt,
        examples=examples,
        version=metric_version,
        model=model,
        grading_context_columns=faithfulness_class_module.grading_context_columns,
        parameters=faithfulness_class_module.parameters,
        aggregations=["mean", "variance", "p90"],
        greater_is_better=True,
        judge_request_timeout=judge_request_timeout,
    )
