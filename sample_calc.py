def calculate_discount(price: float, discount_pct: float) -> float:
    # Buggy: Subtracts raw percentage value instead of percentage of price
    return price - discount_pct
