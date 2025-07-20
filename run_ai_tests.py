from generate_questions import get_questions_list

questions_list = get_questions_list(
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
