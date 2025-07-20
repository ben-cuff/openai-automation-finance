from scipy import optimize


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
        annual_interest_rate: Annual interest rate as a decimal
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
        annual_interest_rate: Annual interest rate as a decimal
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
