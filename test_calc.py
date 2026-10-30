import sys
from sample_calc import calculate_discount

def test_calculation():
    # 15% off $200 should be $170.0
    # Buggy formula (200 - 15) gives $185.0 -> Triggers Assertion Error!
    result = calculate_discount(200.0, 15.0)
    expected = 170.0
    assert result == expected, f"Expected {expected}, got {result}"
    print("TEST PASSED: Calculation verified successfully!")

if __name__ == "__main__":
    try:
        test_calculation()
    except AssertionError as e:
        print(f"AssertionError: {e}", file=sys.stderr)
        sys.exit(1)