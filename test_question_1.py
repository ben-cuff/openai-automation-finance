import run_ai_tests as test
from generate_questions import get_question_1
from ai_models import *
import json
import logging
import time


output_file = "test_results_question_123.json"


def generate_test_combinations(
    interest_rates, loan_amounts, loan_terms, code_capable_models, non_code_models
):
    test_combinations = []

    for model in code_capable_models:
        for rate in interest_rates:
            for amount in loan_amounts:
                for term in loan_terms:
                    test_combinations.append(
                        {
                            "model": model,
                            "interest_rate": rate,
                            "loan_amount": amount,
                            "loan_term": term,
                            "run_code": True,
                        }
                    )

                    test_combinations.append(
                        {
                            "model": model,
                            "interest_rate": rate,
                            "loan_amount": amount,
                            "loan_term": term,
                            "run_code": False,
                        }
                    )

    for model in non_code_models:
        for rate in interest_rates:
            for amount in loan_amounts:
                for term in loan_terms:
                    test_combinations.append(
                        {
                            "model": model,
                            "interest_rate": rate,
                            "loan_amount": amount,
                            "loan_term": term,
                            "run_code": False,
                        }
                    )

    for combo in test_combinations:
        combo["question"] = get_question_1(
            combo["loan_amount"],
            combo["interest_rate"],
            combo["loan_term"],
        )

    return test_combinations


def run_tests_for_combinations(combinations):
    for combo in combinations:
        try:
            ai_response = test.run_ai_tests(
                [combo["question"]],
                num_iterations=5,
                ai_model=combo["model"],
                use_code_interpreter=combo["run_code"],
                output_file=None,
            )
        except Exception as e:
            print(f"Error testing combination {combo}: {str(e)}")
            ai_response = {"error": str(e)}
        combo["ai_response"] = ai_response
        try:
            with open(output_file, "w") as f:
                json.dump(combinations, f, indent=4)
            print(f"Results written to {output_file}")
        except Exception as e:
            print(f"Error writing results to {output_file}: {e}")
    return combinations


# interest_rates = list(range(1, 11))
# loan_amounts = list(range(300000, 1300000, 100000))
# loan_terms = [15, 30]
interest_rates = [2]
loan_amounts = [1100000]
loan_terms = [30]


code_capable_models = [
    #     AIModels.GPT_5.value,
    #     AIModels.GPT_4O.value,
]
non_code_models = [AIModels.O4_MINI.value]


combinations = generate_test_combinations(
    interest_rates, loan_amounts, loan_terms, code_capable_models, non_code_models
)

start_time = time.time()
combinations_with_ai = run_tests_for_combinations(combinations)
end_time = time.time()
print(f"Total time to run: {end_time - start_time:.2f} seconds")

try:
    with open(output_file, "w") as f:
        json.dump(combinations_with_ai, f, indent=4)
    print(f"Results written to {output_file}")
except Exception as e:
    print(f"Error writing results to {output_file}: {e}")
