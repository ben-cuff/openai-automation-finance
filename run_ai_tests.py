from generate_questions import get_questions_list
from openai import OpenAI
import dotenv
import pandas as pd
from pydantic import BaseModel
from concurrent.futures import ThreadPoolExecutor
import re
import json
from enum import Enum

executor = ThreadPoolExecutor()

dotenv.load_dotenv()
openai_api_key = dotenv.get_key(".env", "OPENAI_API_KEY")

openai_url = "https://api.openai.com/v1"

client = OpenAI(api_key=openai_api_key, base_url=openai_url)

questions_list_1 = get_questions_list(
    principal_1=300000,
    interest_rate_1=2.99,
    term_1=30,
    years_elapsed_1=5,
    month_number_1=30,
    principal_2=320000,
    interest_rate_2=3.51,
    term_2=30,
    years_elapsed_2=5,
    extra_amount=20000,
    penalty_rate=2,
    fees=3000,
    out_of_pocket=True,
    principal_a2=150000,
    rate_a2=6.75,
    principal_b=450000,
    rate_b=4.22,
)

questions_list_2 = get_questions_list(
    principal_1=250000,
    interest_rate_1=3.25,
    term_1=20,
    years_elapsed_1=3,
    month_number_1=24,
    principal_2=270000,
    interest_rate_2=3.75,
    term_2=25,
    years_elapsed_2=4,
    extra_amount=15000,
    penalty_rate=1.5,
    fees=2500,
    out_of_pocket=False,
    principal_a2=120000,
    rate_a2=5.5,
    principal_b=350000,
    rate_b=3.95,
)

questions_list_3 = get_questions_list(
    principal_1=400000,
    interest_rate_1=3.85,
    term_1=25,
    years_elapsed_1=7,
    month_number_1=60,
    principal_2=420000,
    interest_rate_2=4.1,
    term_2=30,
    years_elapsed_2=6,
    extra_amount=25000,
    penalty_rate=1.75,
    fees=3500,
    out_of_pocket=True,
    principal_a2=180000,
    rate_a2=7.25,
    principal_b=500000,
    rate_b=4.5,
)

questions_list = questions_list_1 + questions_list_2 + questions_list_3

ASSISTANT_INSTRUCTIONS_CODE = (
    "You are trying to help people that are not very knowledgeable about finance answer questions about their mortgage. "
    "Answer the questions to the best of your ability, and make sure to get the calculations correct. "
    "Do not use any special delimiters in your response. "
    "Provide the final answer as a plain number only (no commas, percent signs, or currency symbols). "
    "If you save money, it should be a positive number; if you lose money, make sure it is negative. "
    "Also include a clear, concise explanation of how you arrived at the answer. "
    "Use the Python tool to generate code to perform calculations. "
)

ASSISTANT_INSTRUCTIONS = (
    "You are trying to help people that are not very knowledgeable about finance answer questions about their mortgage. "
    "Answer the questions to the best of your ability, and make sure to get the calculations correct. "
    "Do not use any special delimiters in your response. "
    "Provide the final answer as a plain number only (no commas, percent signs, or currency symbols). "
    "If you save money, it should be a positive number; if you lose money, make sure it is negative. "
    "Also include a clear, concise explanation of how you arrived at the answer. "
)


class AIModels(Enum):
    DEEPSEEK_CHAT = "deepseek-chat"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GPT_4 = "gpt-4"
    O1_MINI = "o1-mini"
    O4_MINI = "o4-mini"
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    O3_MINI = "o3-mini"
    O1 = "o1"
    O1_PREVIEW = "o1-preview"
    GPT_4_5_PREVIEW = "gpt-4.5-preview"
    GPT_4_1 = "gpt-4.1"
    GPT_5 = "gpt-5"
    GPT_5_MINI = "gpt-5-mini"
    GPT_5_NANO = "gpt-5-turbo"


class QuestionOutput(BaseModel):
    final_answer: str
    explanation: str


def run_ai_tests(
    question_list,
    num_iterations=1,
    ai_model=AIModels.GPT_5,
    use_code_interpreter=False,
    output_file="ai_responses.json",
):
    """
    Runs a series of AI-powered tests on a list of finance-related questions, specifically focused on mortgage calculations.
    Args:
        question_list (list): A list of dictionaries, each containing a 'content' key with the question text and an 'answer' key with the expected answer.
        num_iterations (int, optional): The number of times to repeat the test set. Defaults to 1.
        ai_model (str, optional): The identifier of the AI model to use for generating responses. o3-mini.
        use_code_interpreter: Whether or not to enable code interpreter in OpenAI API
        output_file: The filename to output responses to
    Returns:
        list: A list of dictionaries, each containing:
            - 'question': The question text.
            - 'expected_answer': The expected answer for the question.
            - 'ai_response': The full response from the AI model.
            - 'code': The code the AI model generated if applicable
            - 'actual_answer': The numeric answer extracted from the AI's response.
    """

    messages = [
        (
            [{"role": msg["role"], "content": msg["content"]}],
            idx + iteration * len(question_list),
        )
        for iteration in range(num_iterations)
        for idx, msg in enumerate(question_list)
    ]

    def get_response(message):
        kwargs = {
            "model": ai_model,
            "input": message[0],
            "tools": (
                [{"type": "code_interpreter", "container": {"type": "auto"}}]
                if use_code_interpreter
                else []
            ),
            "instructions": (
                ASSISTANT_INSTRUCTIONS_CODE
                if use_code_interpreter
                else ASSISTANT_INSTRUCTIONS
            ),
            "text_format": QuestionOutput,
        }

        response = client.responses.parse(**kwargs)

        print(f"Finished question: {message[1]}")
        return response.output_parsed, message[1]

    print(f"Running {len(messages)} questions with model {ai_model}")

    max_threads = min(10, len(messages))
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [executor.submit(get_response, msg) for msg in messages]
        responses_parallel = [future.result() for future in futures]

    responses_parallel.sort(key=lambda x: x[1])

    results = []
    for idx, (resp, _) in enumerate(responses_parallel):
        question_data = question_list[idx % len(question_list)]
        result = {
            "question": question_data["content"],
            "expected_answer": question_data["answer"],
            "ai_response": getattr(resp, "explanation", None),
            "actual_answer": getattr(resp, "final_answer", None),
        }
        results.append(result)

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Finished {len(results)} questions. Output saved to {output_file}")
    return results


ai_responses = run_ai_tests(
    questions_list,
    num_iterations=4,
    ai_model=AIModels.GPT_4_1.value,
    use_code_interpreter=True,
    output_file="assistant_with_python.json",
)

# ai_responses = run_ai_tests(
#     questions_list,
#     num_iterations=4,
#     ai_model=AIModels.GPT_4_1.value,
#     use_code_interpreter=False,
#     output_file="assistant_without_python.json",
# )

# ai_responses = run_ai_tests(
#     questions_list,
#     num_iterations=4,
#     ai_model=AIModels.O4_MINI.value,
#     use_code_interpreter=False,
#     output_file="o4-mini-responses.json",
# )
