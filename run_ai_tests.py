from generate_questions import *
from openai import OpenAI
import dotenv
import pandas as pd
from pydantic import BaseModel
from concurrent.futures import ThreadPoolExecutor
import re
import json
from enum import Enum
from ai_models import *
import time
import random

executor = ThreadPoolExecutor()

dotenv.load_dotenv()
openai_api_key = dotenv.get_key(".env", "OPENAI_API_KEY")

openai_url = "https://api.openai.com/v1"

client = OpenAI(api_key=openai_api_key, base_url=openai_url)

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


class QuestionOutput(BaseModel):
    final_answer: str
    explanation: str


def run_ai_tests(
    question_list,
    num_iterations=1,
    ai_model=AIModels.GPT_4O,
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

    container = (
        client.containers.create(name="code-interpreter-container")
        if use_code_interpreter
        else None
    )

    def get_response(message):
        kwargs = {
            "model": ai_model,
            "input": message[0],
            "tools": (
                [{"type": "code_interpreter", "container": container.id}]
                # [{"type": "code_interpreter", "container": {"type": "auto"}}]
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

        max_retries = 5
        retry_count = 0
        base_delay = 20

        while True:
            try:
                response = client.responses.parse(**kwargs)
                print(f"Finished question: {message[1]}")
                return response.output_parsed, message[1]
            except Exception as e:
                error_msg = str(e).lower()
                if (
                    "rate limit" in error_msg or "429" in error_msg
                ) and retry_count < max_retries:
                    retry_count += 1
                    delay = base_delay * (2 ** (retry_count - 1)) + random.uniform(0, 1)
                    print(
                        f"Rate limit hit, retrying in {delay:.2f}s (attempt {retry_count}/{max_retries})"
                    )
                    time.sleep(delay)
                else:
                    print(f"Error calling OpenAI API: {str(e)}")
                    raise

    print(f"Running {len(messages)} questions with model {ai_model}")

    max_threads = 1 if use_code_interpreter else min(10, len(messages))
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
    if output_file:
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)

    print(f"Finished {len(results)} questions. Output saved to {output_file}")
    return results
