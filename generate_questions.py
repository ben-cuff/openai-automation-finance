from answers import *
import json


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
    out_of_pocket,
    principal_a2,
    rate_a2,
    principal_b,
    rate_b,
):
    question_list = []
    question_1 = get_question_1(principal_1, interest_rate_1, term_1)
    question_list.append(question_1)

    question_2 = get_question_2(principal_1, interest_rate_1, term_1, years_elapsed_1)
    question_list.append(question_2)

    question_3 = get_question_3(principal_1, interest_rate_1, term_1, month_number_1)
    question_list.append(question_3)

    question_4 = get_question_4(
        principal_1, interest_rate_1, principal_2, interest_rate_2, term=term_1
    )
    question_list.append(question_4)

    question_5 = get_question_5(
        principal_a1=principal_1,
        rate_a1=interest_rate_1,
        principal_a2=principal_a2,
        rate_a2=rate_a2,
        principal_b=principal_b,
        rate_b=rate_b,
        term=term_1,
    )
    question_list.append(question_5)

    question_6 = get_question_6(
        principal_1,
        term_1,
        interest_rate_2,
        years_elapsed_1,
        term_2,
        interest_rate_1,
        penalty_rate,
        fees,
        out_of_pocket,
    )
    question_list.append(question_6)

    return question_list


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
        "content": (
            f"If I borrow ${principal:,.0f} at an annual interest rate of {interest_rate:.2f}% "
            f"for {term} years, and I make monthly payments that fully pay off the loan by the end, "
            f"how much will I have to pay each month?"
        ),
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
        "content": (
            f"If I get a loan for ${principal:,.0f} at {interest_rate:.2f}% interest for {term} years, "
            f"with monthly payments that fully pay it off, how much will I still owe after {years_elapsed} years?"
        ),
        "answer": round(answer, 2),
    }
    return question


def get_question_3(principal, interest_rate, term, month_number):
    """
    Generates a question dictionary about the interest portion of a specific monthly loan payment.
    Args:
        principal (float): The initial amount of the loan.
        interest_rate (float): The annual interest rate as a percentage (e.g., 5.5 for 5.5%).
        term (int): The term of the loan in years.
        month_number (int): The month number for which to calculate the interest portion of the payment.
    Returns:
        dict: A dictionary containing the question prompt and the correct answer (interest portion of the specified payment).
    """
    (answer_1, answer_2) = calculate_interest_principal_payment(
        principal, interest_rate, term, month_number
    )
    question = {
        "role": "user",
        "content": (
            f"For a loan of ${principal:,.0f} with {interest_rate:.2f}% interest over {term} years, "
            f"with monthly payments that pay off the loan completely, how much of the {month_number}th payment goes toward interest?"
        ),
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
    answer = find_incremental_rate(
        principal_1, interest_rate_1, term, principal_2, interest_rate_2
    )
    question = {
        "role": "user",
        "content": (
            f"What's the incremental interest rate (cost of borrowing) on an additional "
            f"${extra_amount:,.0f} if I go from a ${principal_1:,.0f} loan at {interest_rate_1:.2f}% "
            f"to a ${principal_2:,.0f} loan at {interest_rate_2:.2f}%, both for {term} years? "
            f"Can you solve for the interest rate that would give the same payment difference on just the "
            f"${extra_amount:,.0f}?"
        ),
        "answer": round(answer, 2),
    }
    return question


def get_question_5(
    principal_a1, rate_a1, principal_a2, rate_a2, principal_b, rate_b, term
):
    """
    Compares the total cost of two borrowing options:
    Option A: Two separate loans.
    Option B: One combined loan.
    Args:
        principal_a1 (float): Amount for first loan in Option A.
        rate_a1 (float): Interest rate for first loan in Option A.
        principal_a2 (float): Amount for second loan in Option A.
        rate_a2 (float): Interest rate for second loan in Option A.
        principal_b (float): Amount for Option B loan.
        rate_b (float): Interest rate for Option B loan.
        term (int): Loan term in years.
    Returns:
        dict: Question and answer comparing total costs.
    """
    answer = find__better_loan_option(
        principal_a1, rate_a1, principal_a2, rate_a2, principal_b, rate_b, term
    )
    question = {
        "role": "user",
        "content": (
            f"I am comparing two ways to borrow the same total amount over {term} years with monthly payments: "
            f"Option A: Two separate loans: one for ${principal_a1:,.0f} at {rate_a1:.2f}%, and another for ${principal_a2:,.0f} at {rate_a2:.2f}%. "
            f"Option B: One big loan for ${principal_b:,.0f} at {rate_b:.2f}%. "
            f"Which one ends up costing less in the long run (Option A minus Option B)"
        ),
        "answer": round(answer, 2),
    }
    return question


def get_question_6(
    principal,
    term_1,
    rate_1,
    years_elapsed,
    term_2,
    rate_2,
    penalty_rate,
    fee,
    out_of_pocket,
):
    """
    Generates a mortgage refinancing question and computes the net present value (NPV) savings or loss.
    Args:
        principal (float): The original amount of the mortgage.
        term_1 (int): The original term of the mortgage in years.
        rate_1 (float): The original annual interest rate (as a percentage).
        years_elapsed (int): The number of years since the mortgage was taken out.
        term_2 (int): The term of the new mortgage in years.
        rate_2 (float): The annual interest rate for the new mortgage (as a percentage).
        penalty_rate (float): The penalty rate (as a percentage of the remaining principal) for breaking the original mortgage.
        fee (float): Additional refinancing fees in dollars.
        out_of_pocket (bool): Indicates whether fees and penalties are paid out of pocket (True) or rolled into the new loan (False).
    Returns:
        dict: A dictionary containing:
            - "role": The role of the message sender ("user").
            - "content": The generated question string describing the refinancing scenario.
            - "answer": The calculated NPV savings (or loss, as a negative number) rounded to two decimal places.
    """
    answer = calculate_refinance_npv(
        principal,
        term_1,
        rate_1,
        years_elapsed,
        term_2,
        rate_2,
        penalty_rate,
        fee,
        out_of_pocket,
    )

    question = {
        "role": "user",
        "content": (
            f"I took out a mortgage for ${principal:,.0f}, {years_elapsed} years ago. "
            f"It’s a {term_1}-year loan with a {rate_1:.2f}% interest rate. "
            f"Today, I could get a new {term_2}-year mortgage at {rate_2:.2f}% interest, "
            f"but I’d have to pay a penalty of {penalty_rate:.0f}% of what I still owe, "
            f"plus another ${fee:,.0f} in fees. "
            f"({'Fees and penalties are paid out of pocket.' if out_of_pocket else 'Fees and penalties are rolled into the new loan.'}) "  # Not sure if this even matters, doesn't change NPV
            f"If I weigh all future payments and costs as if they happened today, how much would I save over the term of the loan if I refinance (output loss as a negative number)?"
        ),
        "answer": round(answer, 2),
    }
    return question
