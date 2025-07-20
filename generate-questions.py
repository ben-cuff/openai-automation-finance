from answers import *


def get_questions_list(
    principal_1,
    interest_rate_1,
    term_1,
    years_elapsed_1,
    month_number_1,
    principal_2,
    interest_rate_2,
    term_2,
    years_elapsed_2,
    extra_amount,
    penalty_rate,
    fees,
):
    question_list = []
    question_1 = get_question_1(principal_1, interest_rate_1, term_1)
    print(question_1)
    question_list.append(question_1)

    question_2 = get_question_2(principal_1, interest_rate_1, term_1, years_elapsed_1)
    print(question_2)
    question_list.append(question_2)

    question_3 = get_question_3(principal_1, interest_rate_1, term_1, month_number_1)
    print(question_3)
    question_list.append(question_3)

    question_4 = get_question_4(principal_1, interest_rate_1, principal_2, interest_rate_2, term=term_1)
    print(question_4)
    question_list.append(question_4)


def get_question_1(principal, interest_rate, term):
    """
    Generates a loan payment question and computes the monthly payment.
    Args:
        principal (float): The amount of money borrowed.
        interest_rate (float): The annual interest rate as a percentage (e.g., 5.5 for 5.5%).
        term (int): The loan term in years.
    Returns:
        tuple: A tuple containing:
            - answer (float): The calculated monthly payment amount.
            - question (dict): A dictionary with the following keys:
                - "role" (str): The role of the message sender, set to "user".
                - "content" (str): The formatted question string.
                - "answer" (float): The rounded monthly payment amount.
    """
    answer = calculate_monthly_payment(principal, interest_rate, term)
    question = {
        "role": "user",
        "content": f"If I borrow ${principal:,.0f} at an annual interest rate of {interest_rate:.2f}% for {term} years, and I make monthly payments that fully pay off the loan by the end, how much will I have to pay each month?",
        "answer": round(answer, 2),
    }
    return question

def get_question_2(principal, interest_rate, term, years_elapsed):
    """
    Generates a loan balance question and its answer after a specified number of years.
    Args:
        principal (float): The initial amount of the loan.
        interest_rate (float): The annual interest rate as a percentage (e.g., 5.5 for 5.5%).
        term (int): The total term of the loan in years.
        years_elapsed (int): The number of years that have passed since the loan started.
    Returns:
        dict: A dictionary containing:
            - "role": The role of the message sender (always "user").
            - "content": The formatted question string.
            - "answer": The remaining loan balance after the specified years, rounded to two decimal places.
    """

    answer = calculate_remaining_balance(principal, interest_rate, term, years_elapsed)
    question = {
        "role": "user",
        "content": f"If I get a loan for ${principal:,.0f} at {interest_rate:.2f}% interest for {term} years, with monthly payments that fully pay it off, how much will I still owe after {years_elapsed} years?",
        "answer": round(answer, 2),
    }
    return question

def get_question_3(principal, interest_rate, term, month_number):
    
    (answer_1, answer_2) = calculate_interest_principal_payment(principal, interest_rate, term, month_number)
    question = {
        "role": "user",
        "content": f"For a loan of ${principal:,.0f} with {interest_rate:.2f}% interest over {term} years, with monthly payments that pay off the loan completely, how much of the {month_number}th payment goes toward interest?",
        "answer": round(answer_1, 2),
    }
    return question

def get_question_4(principal_1, interest_rate_1, principal_2, interest_rate_2, term):
    """
    Calculates the incremental interest rate (cost of borrowing) on an additional amount when increasing loan size and rate.
    Args:
        principal_1 (float): Original loan amount.
        interest_rate_1 (float): Interest rate for original loan.
        principal_2 (float): New loan amount (original + extra).
        interest_rate_2 (float): Interest rate for new loan.
        term (int): Loan term in years.
    Returns:
        dict: Question and answer about the incremental interest rate.
    """
    extra_amount = principal_2 - principal_1
    print(principal_1, interest_rate_1, principal_2, interest_rate_2, term, extra_amount)
    answer = find_incremental_rate(principal_1, interest_rate_1, term, principal_2, interest_rate_2)
    question = {
        "role": "user",
        "content": f"What's the incremental interest rate (cost of borrowing) on an additional ${extra_amount:,.0f} if I go from a ${principal_1:,.0f} loan at {interest_rate_1:.2f}% to a ${principal_2:,.0f} loan at {interest_rate_2:.2f}%, both for {term} years? Can you solve for the interest rate that would give the same payment difference on just the ${extra_amount:,.0f}?",
        "answer": round(answer, 2),
    }
    return question


get_questions_list(
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
    penalty_rate=0.02,
    fees=3000,
)

messages_list = [
    {
        "role": "user",
        "content": "If I borrow $300,000 at an annual interest rate of 2.99% for 30 years, and I make monthly payments that fully pay off the loan by the end, how much will I have to pay each month?",
        "answer": 1263.19,
    },
    {
        "role": "user",
        "content": "If I get a loan for $300,000 at 2.99% interest for 30 years, with monthly payments that fully pay it off, how much will I still owe after 5 years?",
        "answer": 266670.41,
    },
    {
        "role": "user",
        "content": "For a loan of $300,000 with 2.99% interest over 30 years, with monthly payments that pay off the loan completely, how much of the 30th payment goes toward interest?",
        "answer": 708.91,
    },
    {
        "role": "user",
        "content": "What's the incremental interest rate (cost of borrowing) on an additional $20,000 if I go from a $300,000 loan at 2.99% to a $320,000 loan at 3.51%, both for 30 years? Can you solve for the interest rate that would give the same payment difference on just the $20,000?",
        "answer": 10.00,
    },
    {
        "role": "user",
        "content": "I am comparing two ways to borrow the same total amount over 30 years with monthly payments: Option A: Two separate loans—one for $300,000 at 2.99%, and another for $150,000 at 6.75%. Option B: One big loan for $450,000 at 4.22%. Which one ends up costing less in the long run?",
        "answer": "A: $804993.07  B: $794100.02 Better option: B",
    },
    {
        "role": "user",
        "content": "I took out a mortgage for $300,000, 3 years ago. It’s a 30-year loan with a 4.75% interest rate. Today, I could get a new 30-year mortgage at 2.99% interest, but I’d have to pay a penalty of 2% of what I still owe, plus another $3,000 in fees. Is it worth refinancing?",
        "answer": "Yes, refinance, NPV: $71951.19",
    },
    {
        "role": "user",
        "content": "I have a $300,000 mortgage I took out 5 years ago as a 30-year loan with 3.51% interest. Now I can refinance with a new 25-year mortgage at 3.08% interest, but I’ll have to pay a penalty of 1% on what I still owe, plus $4,000 in fees. After all that, does refinancing actually save me money?",
        "answer": "Yes, refinance, NPV: $6123.11",
    },
]
