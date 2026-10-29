import jwt
from sample_app import verify_token

def test_token_verification():
    secret = "secret123"
    token = jwt.encode({"sub": "user_admin"}, secret, algorithm="HS256")
    payload = verify_token(token, secret)
    assert payload["sub"] == "user_admin"

if __name__ == "__main__":
    try:
        test_token_verification()
        print("TEST PASSED: Token verified successfully!")
    except Exception as e:
        import traceback
        traceback.print_exc()
        exit(1)