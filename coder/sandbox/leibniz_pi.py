from decimal import Decimal, getcontext


def calculate_pi_terms(num_terms: int) -> Decimal:
    # Set high precision to handle 1,000,000 terms accurately enough
    getcontext().prec = 50

    total = Decimal(0)
    sign = Decimal(1)

    for n in range(num_terms):
        denom = 2 * n + 1
        term = sign / Decimal(denom)
        total += term
        sign = -sign

    return total * 4


if __name__ == "__main__":
    result = calculate_pi_terms(1_000_000)
    print(result)
