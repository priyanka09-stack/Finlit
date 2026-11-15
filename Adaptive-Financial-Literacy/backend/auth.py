import os

from dotenv import load_dotenv
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
TOKEN_MAX_AGE = 60 * 60 * 24 * 7  # token 7 din chalega

_serializer = URLSafeTimedSerializer(SECRET_KEY, salt="finlit-auth")


def hash_password(password):
    return generate_password_hash(password, method="pbkdf2:sha256")


def verify_password(password_hash, password):
    return check_password_hash(password_hash, password)


def make_token(user_id, role):
    return _serializer.dumps({"id": user_id, "role": role})


def read_token(token):
    try:
        return _serializer.loads(token, max_age=TOKEN_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None