import jwt

def verify_token(token: str, secret: str):
    # Buggy: Missing algorithms parameter triggers failure in PyJWT v2+
    return jwt.decode(token, secret)
