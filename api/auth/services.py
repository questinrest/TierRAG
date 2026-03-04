from datetime import datetime, timezone, timedelta
from jose import jwt
from src.config import login_collection, SECRET_KEY, ALGORITHM, pwd_context


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password[:72], hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password[:72])

def get_user(username: str):
    return login_collection.find_one({"username": username})

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if user and verify_password(password, user['hashed_password']):
        return user
    return None

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(seconds=86400)
    to_encode["exp"] = expire
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

