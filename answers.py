from scipy import optimize
import numpy as np
import numpy_financial as npf


def calculate_monthly_payment(principal, annual_interest_rate, loan_term_years):
    """
    Calculate monthly payment for a fully amortized loan.

    Args:
        principal: The loan amount
        annual_interest_rate: Annual interest rate as a decimal (e.g., 9.00 for 9%)
        loan_term_years: Loan term in years

    Returns:
        Monthly payment amount
    """
    num_payments = loan_term_years * 12
    monthly_interest_rate = annual_interest_rate / 12 / 100

    monthly_payment = (monthly_interest_rate * principal) / (
        1 - (1 + monthly_interest_rate) ** (-num_payments)
    )

    return monthly_payment


def calculate_remaining_balance(
    principal, annual_interest_rate, loan_term_years, years_elapsed
):
    """
    Calculate the remaining loan balance after a specified number of years.

    Args:
        principal: The original loan amount
        annual_interest_rate: Annual interest rate as whole number
        loan_term_years: Total loan term in years
        years_elapsed: Number of years that have passed
        payment: monthly payment for the loan

    Returns:
        Remaining balance
    """
    payment = calculate_monthly_payment(
        principal, annual_interest_rate, loan_term_years
    )
    monthly_interest_rate = annual_interest_rate / 12 / 100
    payments_made = years_elapsed * 12

    remaining_balance = principal * (1 + monthly_interest_rate) ** payments_made - (
        payment
        * ((1 + monthly_interest_rate) ** payments_made - 1)
        / monthly_interest_rate
    )

    return remaining_balance


def calculate_interest_principal_payment(
    principal, annual_interest_rate, loan_term_years, month_number
):
    """
    Calculate the breakdown of interest and principal for a specific month's payment.

    Args:
        principal: The original loan amount
        annual_interest_rate: Annual interest rate as a whole number
        loan_term_years: Total loan term in years
        month_number: The specific month for which to calculate the breakdown
        payment: Monthly payment for the loan

    Returns:
        Tuple of (interest_payment, principal_payment)
    """
    monthly_interest_rate = annual_interest_rate / 12 / 100
    payment = calculate_monthly_payment(
        principal, annual_interest_rate, loan_term_years
    )

    if month_number > 1:
        months_elapsed = month_number - 1
        years_elapsed = months_elapsed / 12
        remaining_balance = calculate_remaining_balance(
            principal, annual_interest_rate, loan_term_years, years_elapsed
        )
    else:
        remaining_balance = principal

    interest_payment = remaining_balance * monthly_interest_rate

    principal_payment = payment - interest_payment

    return interest_payment, principal_payment


def find_incremental_rate(
    principal_1,
    interest_rate_1,
    term,
    principal_2,
    interest_rate_2,
):
    """
    Calculate the incremental interest rate between two loan scenarios.
    This function determines the effective interest rate associated with the incremental principal and payment
    when moving from one loan scenario to another, both with the same term but potentially different principals
    and interest rates. It uses a root-finding algorithm to solve for the rate that equates the incremental
    monthly payment to the payment for the incremental principal.
    Args:
        principal_1 (float): The principal amount of the first loan.
        interest_rate_1 (float): The annual interest rate (in percent) of the first loan.
        term (int): The loan term in years.
        principal_2 (float): The principal amount of the second loan.
        interest_rate_2 (float): The annual interest rate (in percent) of the second loan.
    Returns:
        float: The incremental annual interest rate (in percent) corresponding to the difference in principal and payment.\
    """
    incremental_principal = principal_2 - principal_1
    payment_1 = calculate_monthly_payment(principal_1, interest_rate_1, term)
    payment_2 = calculate_monthly_payment(principal_2, interest_rate_2, term)
    incremental_payment = payment_2 - payment_1

    def payment_function(rate_percent):
        monthly_rate = rate_percent / 12 / 100
        num_payments = term * 12
        return (monthly_rate * incremental_principal) / (
            1 - (1 + monthly_rate) ** (-num_payments)
        ) - incremental_payment

    result = optimize.newton(payment_function, 5.0, tol=1e-8, maxiter=100)
    return float(result)


def find__better_loan_option(
    principal_a1, rate_a1, principal_a2, rate_a2, principal_b, rate_b, term
):
    """
    Compares two loan options (A and B) by calculating the difference in their total costs over a given term.
    Loan option A consists of two separate loans (a1 and a2), while loan option B is a single loan.
    The function uses the `calculate_remaining_balance` function to determine the total cost for each loan.
    Args:
        principal_a1 (float): Principal amount for loan A1.
        rate_a1 (float): Annual interest rate (as a percent) for loan A1.
        principal_a2 (float): Principal amount for loan A2.
        rate_a2 (float): Annual interest rate (as a percent) for loan A2.
        principal_b (float): Principal amount for loan B.
        rate_b (float): Annual interest rate (as a percent) for loan B.
        term (int): Loan term in years or months (depending on `calculate_remaining_balance` implementation).
    Returns:
        float: The difference in total cost between loan option A (sum of A1 and A2) and loan option B.
               A positive value indicates option A is more expensive; a negative value indicates option B is more expensive.
    """
    total_cost_a1 = calculate_monthly_payment(principal_a1, rate_a1, term) * term * 12
    total_cost_a2 = calculate_monthly_payment(principal_a2, rate_a2, term) * term * 12
    total_cost_b = calculate_monthly_payment(principal_b, rate_b, term) * term * 12

    total_cost_a = total_cost_a1 + total_cost_a2

    return total_cost_a - total_cost_b


def calculate_refinance_npv(
    principal,
    term_1,
    rate_1,
    years_elapsed,
    term_2,
    rate_2,
    penalty_rate,
    fee,
    out_of_pocket=True,
):
    """
    Calculate the NPV of refinancing a loan using numpy's npv calculation.

    Args:
        principal: Original loan amount
        term_1: Original loan term (years)
        rate_1: Original annual interest rate (percent)
        years_elapsed: Years passed on original loan
        term_2: New loan term (years)
        rate_2: New annual interest rate (percent)
        penalty_rate: Prepayment penalty rate (percent)
        fee: Refinance fee (absolute amount)
        out_of_pocket: If True, fees are paid upfront; if False, fees are rolled into the new loan

    Returns:
        Net Present Value (NPV) of refinancing
    """
    payment_now = calculate_monthly_payment(principal, rate_1, term_1)
    remaining_balance = calculate_remaining_balance(
        principal, rate_1, term_1, years_elapsed
    )

    if out_of_pocket:
        refinance_principal = remaining_balance
        upfront_cost = fee + remaining_balance * penalty_rate / 100
    else:
        refinance_principal = (
            remaining_balance + fee + remaining_balance * penalty_rate / 100
        )
        upfront_cost = 0

    payment_refinance = calculate_monthly_payment(refinance_principal, rate_2, term_2)
    monthly_gain = payment_now - payment_refinance

    discount_rate = rate_2 / 12 / 100

    cash_flows = (
        [-upfront_cost]
        + [monthly_gain] * int((term_1 - years_elapsed) * 12)
        + [-payment_refinance] * int((term_2 - (term_1 - years_elapsed)) * 12)
    )

    npv = npf.npv(discount_rate, cash_flows)

    return float(npv)
