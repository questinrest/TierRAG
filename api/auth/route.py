from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from api.auth.datamodels import Token, User, LoginData
from api.auth.services import get_user, get_password_hash, authenticate_user, create_access_token
from src.config import login_collection

router = APIRouter()


@router.post("/api/admin/register")
def register_user(user: User):
    if get_user(user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )
    hashed_password = get_password_hash(user.password)
    login_collection.insert_one({"username": user.username, "hashed_password": hashed_password, "namespace" : False})
    return JSONResponse(status_code=200,
                        content={
                            "detail": 'User submit the details successfully',
                            "status_code": "200"
                        })

@router.post("/api/admin/login", response_model=Token)
def login_for_access_token(login_data: LoginData):
    username = login_data.username
    password = login_data.password

    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}
