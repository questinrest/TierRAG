from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str


class User(BaseModel):
    username: str
    password: str

class LoginData(BaseModel):
    username: str
    password: str
