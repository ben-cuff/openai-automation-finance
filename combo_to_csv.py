import pandas as pd
import json
import sys


def convert_json_to_csv(
    json_data, question_number=-1, output_file="loan_responses.csv"
):
    """
    Convert loan calculation data from JSON format to CSV

    Parameters:
    json_data (list): List of dictionaries containing loan data
    output_file (str): Path to the output CSV file

    Returns:
    pd.DataFrame: The data converted to a DataFrame
    """
    flattened_data = []

    for entry in json_data:
        model = entry.get("model", "")
        interest_rate = entry.get("interest_rate", "")
        loan_amount = entry.get("loan_amount", "")
        loan_term = entry.get("loan_term", "")
        run_code = entry.get("run_code", "")

        question_obj = entry.get("question", {})
        expected_answer = question_obj.get("answer", "")

        for response in entry["ai_response"]:
            if isinstance(response, str):
                print(entry)
                continue

            flattened_entry = {
                "model": model,
                "interest_rate": interest_rate,
                "loan_amount": loan_amount,
                "loan_term": loan_term,
                "run_code": run_code,
                "expected_answer": expected_answer,
                "actual_answer": float(response["actual_answer"]),
            }
            flattened_data.append(flattened_entry)

    df = pd.DataFrame(flattened_data)
    df["question_number"] = question_number
    df.to_csv(output_file, index=False)
    return df


with open("test_results_question_1.json", "r") as file:
    data = json.load(file)

df = convert_json_to_csv(data, 1)
print(f"Converted {len(df)} rows to CSV")
