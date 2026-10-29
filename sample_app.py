import jwt

def verify_token(token: str, secret: str):
    # Fixed: Added algorithms=['HS256'] to satisfy PyJWT v2+ requirements
    # and prevent jwt.exceptions.DecodeError.
    return jwt.decode(token, secret, algorithms=['HS256'])