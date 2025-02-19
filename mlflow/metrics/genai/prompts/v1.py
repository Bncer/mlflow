from dataclasses import dataclass, field
from typing import Any, Dict, List

from mlflow.metrics.base import (
    EvaluationExample,
)
from mlflow.metrics.genai.prompt_template import (
    PromptTemplate,
)

# TODO: Update the default_mode and default_parameters to the correct values post experimentation
default_model = "openai:/gpt-4"
default_parameters = {
    "temperature": 0.0,
    "max_tokens": 200,
    "top_p": 1.0,
}
grading_system_prompt_template = PromptTemplate(
    """
Task:
You are an impartial judge. You will be given an input that was sent to a machine
learning model, and you will be given an output that the model produced. You
may also be given additional information that was used by the model to generate the output.

Your task is to determine a numerical score called {name} based on the input and output.
A definition of {name} and a grading rubric are provided below.
You must use the grading rubric to determine your score. You must also justify your score.

Examples could be included below for reference. Make sure to use them as references and to
understand them before completing the task.

Input:
{input}

Output:
{output}

{grading_context_columns}

Metric definition:
{definition}

Grading rubric:
{grading_prompt}

{examples}

You must return the following fields in your response one below the other:
score: Your numerical score for the model's {name} based on the rubric
justification: Your step-by-step reasoning about the model's {name} score
    """
)


@dataclass
class EvaluationModel:
    """
    Useful to compute v1 prompt for make_genai_metric
    """

    name: str
    definition: str
    grading_prompt: str
    examples: List[EvaluationExample] = None
    model: str = default_model
    parameters: Dict[str, Any] = field(default_factory=lambda: default_parameters)

    def to_dict(self):
        examples_str = (
            ""
            if self.examples is None or len(self.examples) == 0
            else f"Examples:\n{self._format_examples()}"
        )

        return {
            "model": self.model,
            "eval_prompt": grading_system_prompt_template.partial_fill(
                name=self.name,
                definition=self.definition,
                grading_prompt=self.grading_prompt,
                examples=examples_str,
            ),
            "parameters": self.parameters,
        }

    def _format_examples(self):
        return "\n".join(map(str, self.examples))


@dataclass
class AnswerSimilarityMetric:
    definition = (
        "Answer similarity is evaluated on the degree of semantic similarity of the provided "
        "output to the provided targets, which is the ground truth. Scores can be assigned based "
        "on the gradual similarity in meaning and description to the provided targets, where a "
        "higher score indicates greater alignment between the provided output and provided targets."
    )

    grading_prompt = (
        "Answer similarity: Below are the details for different scores:\n"
        "- Score 1: the output has little to no semantic similarity to the provided targets.\n"
        "- Score 2: the output displays partial semantic similarity to the provided targets on "
        "some aspects.\n"
        "- Score 3: the output has moderate semantic similarity to the provided targets.\n"
        "- Score 4: the output aligns with the provided targets in most aspects and has "
        "substantial semantic similarity.\n"
        "- Score 5: the output closely aligns with the provided targets in all significant aspects."
    )

    grading_context_columns = ["targets"]
    parameters = default_parameters
    default_model = default_model

    example_score_2 = EvaluationExample(
        input="What is MLflow?",
        output="MLflow is an open-source platform.",
        score=2,
        justification="The provided output is partially similar to the target, as it captures the "
        "general idea that MLflow is an open-source platform. However, it lacks the comprehensive "
        "details and context provided in the target about MLflow's purpose, development, and "
        "challenges it addresses. Therefore, it demonstrates partial, but not complete, "
        "semantic similarity.",
        grading_context={
            "targets": "MLflow is an open-source platform for managing the end-to-end "
            "machine learning (ML) lifecycle. It was developed by Databricks, a company "
            "that specializes in big data and machine learning solutions. MLflow is "
            "designed to address the challenges that data scientists and machine learning "
            "engineers face when developing, training, and deploying machine learning "
            "models."
        },
    )

    example_score_4 = EvaluationExample(
        input="What is MLflow?",
        output="MLflow is an open-source platform for managing machine learning workflows, "
        "including experiment tracking, model packaging, versioning, and deployment, simplifying "
        "the ML lifecycle.",
        score=4,
        justification="The provided output aligns closely with the target. It covers various key "
        "aspects mentioned in the target, including managing machine learning workflows, "
        "experiment tracking, model packaging, versioning, and deployment. While it may not include"
        " every single detail from the target, it demonstrates substantial semantic similarity.",
        grading_context={
            "targets": "MLflow is an open-source platform for managing the end-to-end "
            "machine learning (ML) lifecycle. It was developed by Databricks, a company "
            "that specializes in big data and machine learning solutions. MLflow is "
            "designed to address the challenges that data scientists and machine learning "
            "engineers face when developing, training, and deploying machine learning "
            "models."
        },
    )

    default_examples = [example_score_2, example_score_4]


@dataclass
class FaithfulnessMetric:
    definition = (
        "Faithfulness is only evaluated with the provided output and provided context, please "
        "ignore the provided input entirely when scoring faithfulness. Faithfulness assesses "
        "how much of the provided output is factually consistent with the provided context. A "
        "higher score indicates that a higher proportion of claims present in the output can be "
        "derived from the provided context. Faithfulness does not consider how much extra "
        "information from the context is not present in the output."
    )

    grading_prompt = (
        "Faithfulness: Below are the details for different scores:\n"
        "- Score 1: None of the claims in the output can be inferred from the provided context.\n"
        "- Score 2: Some of the claims in the output can be inferred from the provided context, "
        "but the majority of the output is missing from, inconsistent with, or contradictory to "
        "the provided context.\n"
        "- Score 3: Half or more of the claims in the output can be inferred from the provided "
        "context.\n"
        "- Score 4: Most of the claims in the output can be inferred from the provided context, "
        "with very little information that is not directly supported by the provided context.\n"
        "- Score 5: All of the claims in the output are directly supported by the provided "
        "context, demonstrating high faithfulness to the provided context."
    )

    grading_context_columns = ["context"]
    parameters = default_parameters
    default_model = default_model

    example_score_2 = EvaluationExample(
        input="How is MLflow related to Databricks?",
        output="Databricks is a company that specializes in big data and machine learning "
        "solutions. MLflow has nothing to do with Databricks. MLflow is an open-source platform "
        "for managing the end-to-end machine learning (ML) lifecycle.",
        score=2,
        justification='The output claims that "MLflow has nothing to do with Databricks" which is '
        'contradictory to the provided context that states "It was developed by Databricks". This '
        'is a major inconsistency. However, the output correctly identifies that "MLflow is an '
        'open-source platform for managing the end-to-end machine learning (ML) lifecycle" and '
        '"Databricks is a company that specializes in big data and machine learning solutions", '
        "which are both supported by the context. Therefore, some of the claims in the output can "
        "be inferred from the provided context, but the majority of the output is inconsistent "
        "with the provided context, leading to a faithfulness score of 2.",
        grading_context={
            "context": "MLflow is an open-source platform for managing the end-to-end machine "
            "learning (ML) lifecycle. It was developed by Databricks, a company that specializes "
            "in big data and machine learning solutions. MLflow is designed to address the "
            "challenges that data scientists and machine learning engineers face when developing, "
            "training, and deploying machine learning models."
        },
    )

    example_score_5 = EvaluationExample(
        input="How is MLflow related to Databricks?",
        output="Databricks is a company that specializes in big data and machine learning "
        "solutions.",
        score=5,
        justification='The output states that "Databricks is a company that specializes in big data'
        ' and machine learning solutions." This claim is directly supported by the context, which '
        'states "It was developed by Databricks, a company that specializes in big data and '
        'machine learning solutions." Therefore, the faithfulness score is 5 as all the claims in '
        'the output are directly supported by the provided context."',
        grading_context={
            "context": "MLflow is an open-source platform for managing the end-to-end "
            "machine learning (ML) lifecycle. It was developed by Databricks, a company "
            "that specializes in big data and machine learning solutions. MLflow is "
            "designed to address the challenges that data scientists and machine learning "
            "engineers face when developing, training, and deploying machine learning "
            "models."
        },
    )

    default_examples = [example_score_2, example_score_5]


@dataclass
class AnswerCorrectnessMetric:
    definition = (
        "Answer correctness is evaluated on the accuracy of the provided output based on the "
        "provided targets, which is the ground truth. Scores can be assigned based on the degree "
        "of semantic similarity and factual correctness of the provided output to the provided "
        "targets, where a higher score indicates higher degree of accuracy."
    )

    grading_prompt = (
        "Answer Correctness: Below are the details for different scores:\n"
        "- Score 1: the output is completely incorrect. It is completely different from or "
        "contradicts the provided targets.\n"
        "- Score 2: the output demonstrates some degree of semantic similarity and includes "
        "partially correct information. However, the output still has significant discrepancies "
        "with the provided targets or inaccuracies.\n"
        "- Score 3: the output addresses a couple of aspects of the input accurately, aligning "
        "with the provided targets. However, there are still omissions or minor inaccuracies.\n"
        "- Score 4: the output is mostly correct. It provides mostly accurate information, but "
        "there may be one or more minor omissions or inaccuracies.\n"
        "- Score 5: the output is correct. It demonstrates a high degree of accuracy and "
        "semantic similarity to the targets."
    )

    grading_context_columns = ["targets"]
    parameters = default_parameters
    default_model = default_model

    example_score_2 = EvaluationExample(
        input="How is MLflow related to Databricks?",
        output="Databricks is a data engineering and analytics platform designed to help "
        "organizations process and analyze large amounts of data. Databricks is a company "
        "specializing in big data and machine learning solutions.",
        score=2,
        justification="The output provided by the model does demonstrate some degree of semantic "
        "similarity to the targets, as it correctly identifies Databricks as a company "
        "specializing in big data and machine learning solutions. However, it fails to address "
        "the main point of the input question, which is the relationship between MLflow and "
        "Databricks. The output does not mention MLflow at all, which is a significant discrepancy "
        "with the provided targets. Therefore, the model's answer_correctness score is 2.",
        grading_context={
            "targets": "MLflow is an open-source platform for managing the end-to-end machine "
            "learning (ML) lifecycle. It was developed by Databricks, a company that specializes "
            "in big data and machine learning solutions. MLflow is designed to address the "
            "challenges that data scientists and machine learning engineers face when developing, "
            "training, and deploying machine learning models."
        },
    )

    example_score_4 = EvaluationExample(
        input="How is MLflow related to Databricks?",
        output="MLflow is a product created by Databricks to enhance the efficiency of machine "
        "learning processes.",
        score=4,
        justification="The output provided by the model is mostly correct. It correctly identifies "
        "that MLflow is a product created by Databricks. However, it does not mention that MLflow "
        "is an open-source platform for managing the end-to-end machine learning lifecycle, which "
        "is a significant part of its function. Therefore, while the output is mostly accurate, "
        "it has a minor omission, which is why it gets a score of 4 according to the grading "
        "rubric.",
        grading_context={
            "targets": "MLflow is an open-source platform for managing the end-to-end machine "
            "learning (ML) lifecycle. It was developed by Databricks, a company that specializes "
            "in big data and machine learning solutions. MLflow is designed to address the "
            "challenges that data scientists and machine learning engineers face when developing, "
            "training, and deploying machine learning models."
        },
    )

    default_examples = [example_score_2, example_score_4]
