from generate_questions import get_questions_list
from openai import OpenAI
import dotenv
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import re
import json

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

ai_models = [
    "deepseek-chat",  # 0
    "gpt-3.5-turbo",  # 1
    "gpt-4",  # 2
    "o1-mini",  # 3
    "gpt-4o",  # 4
    "gpt-4o-mini",  # 5
    "o3-mini",  # 6
    "o1",  # 7
    "o1-preview",  # 8
    "gpt-4.5-preview",  # 9
    "gpt-4.1" # 10
]


def run_ai_tests(
    question_list,
    num_iterations=1,
    ai_model="o3-mini",
    use_assistant=False,
    output_file="ai_responses.json",
):
    """
    Runs a series of AI-powered tests on a list of finance-related questions, specifically focused on mortgage calculations.
    Args:
        question_list (list): A list of dictionaries, each containing a 'content' key with the question text and an 'answer' key with the expected answer.
        num_iterations (int, optional): The number of times to repeat the test set. Defaults to 1.
        ai_model (str, optional): The identifier of the AI model to use for generating responses. o3-mini.
        use_assistant: Whether or not to use the assistants API and thus the code interpreter
        output_file: The filename to output responses to
    Returns:
        list: A list of dictionaries, each containing:
            - 'question': The question text.
            - 'expected_answer': The expected answer for the question.
            - 'ai_response': The full response from the AI model.
            - 'actual_answer': The numeric answer extracted from the AI's response.
    """

    messages = [
        (
            [
                {
                    "role": "system",
                    "content": "You are trying to help people that are not very knowledgeable about finance answer questions about their mortgage. "
                    + "Answer the questions to the best of your ability, and make sure to get the calculations correct. "
                    + "Format the answer like @@@answer_here@@@. For example, if your final answer was 158, you would include @@@158@@@. "
                    + "Only include one instance of @@@xyz@@@ in your response as this will be used to automatically parse for your final answer. "
                    + "Make sure to only wrap your final answer in @@@ and not anything else during your response. "
                    + "Only include the number in your final response. @@@answer@@@ should not include any commas (,), percent signs (%),"
                    + "money signs ($), or any ambiguous text. Only include the number like @@@-185000@@@. "
                    + "The answer does not need to be your only output, just make sure that your final answer is wrapped in @@@. "
                    + "Please also explain your answer, so if you get it wrong we can try to see where things went wrong.",
                },
                {"role": msg["role"], "content": msg["content"]},
            ],
            idx + iteration * len(question_list),
        )
        for iteration in range(num_iterations)
        for idx, msg in enumerate(question_list)
    ]

    assistant_instructions = (
        "You are trying to help people that are not very knowledgeable about finance answer questions about their mortgage. "
        "Answer the questions to the best of your ability, and make sure to get the calculations correct. "
        "Format the answer like @@@answer_here@@@. For example, if your final answer was 158, you would include @@@158@@@. "
        "Only include one instance of @@@xyz@@@ in your response as this will be used to automatically parse for your final answer. "
        "Make sure to only wrap your final answer in @@@ and not anything else during your response. "
        "Only include the number in your final response. @@@answer@@@ should not include any commas (,), percent signs (%),"
        "money signs ($), or any ambiguous text. Only include the number like @@@-185000@@@. "
        "The answer does not need to be your only output, just make sure that your final answer is wrapped in @@@. "
        "Please also explain your answer, so if you get it wrong we can try to see where things went wrong. "
        "You can use Python code to perform calculations and explain your reasoning."
    )

    def get_response(message):
        if use_assistant:
            response = client.responses.create(
                model=ai_model,
                tools=[{"type": "code_interpreter", "container": {"type": "auto"}}],
                instructions=assistant_instructions,
                input=message[0][1]["content"],
            )
            combined_text = ""
            for item in response.output:
                if hasattr(item, "content"):
                    for content_item in item.content:
                        if hasattr(content_item, "text"):
                            combined_text += content_item.text + "\n"
                elif hasattr(item, "code"):
                    combined_text += item.code + "\n"
            print(f"Finished question: {message[1]}")
            return (combined_text, message[1])

        temperature = 1
        max_completion_tokens = 20000
        reasoning_effort = ["low", "medium", "high"]
        response = client.chat.completions.create(
            model=ai_model,
            temperature=temperature,
            # max_completion_tokens=max_completion_tokens,
            messages=message[0],
            # reasoning_effort=reasoning_effort[1]
        )
        print(f"Finished question: {message[1]}")
        return (response.choices[0].message.content, message[1])

    print(f"Running {len(messages)} questions")
    futures = [executor.submit(get_response, message) for message in messages]
    responses_parallel = [future.result() for future in futures]

    print(f"Finished running {len(responses_parallel)} questions")
    responses_parallel = sorted(responses_parallel, key=lambda x: x[1])

    def extract_answer(text):
        match = re.search(r"@@@\s*(-?[\d,]+(?:\.\d+)?)(?=\s*@@@)", text)
        if match:
            return match.group(1)
        return None

    answers = [extract_answer(resp[0]) for resp in responses_parallel]

    results = []
    for idx, (resp, _) in enumerate(responses_parallel):
        result = {
            "question": question_list[idx % len(question_list)]["content"],
            "expected_answer": question_list[idx % len(question_list)]["answer"],
            "ai_response": resp,
            "actual_answer": float(answers[idx]),
        }
        results.append(result)
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    return results

ai_responses = run_ai_tests(
    questions_list,
    num_iterations=4,
    ai_model=ai_models[10],
    use_assistant=True,
    output_file="assistant_with_python.json",
)

ai_responses = run_ai_tests(
    questions_list,
    num_iterations=4,
    ai_model=ai_models[10],
    use_assistant=False,
    output_file="assistant_without_python.json",
)
