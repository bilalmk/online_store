import sys
from typing import Annotated
from shared.models.token import Token
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Depends, status, HTTPException, Form
from app import config
from jose import JWTError, jwt, ExpiredSignatureError

oauth2_authentication = OAuth2PasswordBearer(tokenUrl="token")
app = FastAPI()

"""
This endpoint of authentication microservices is used to creates a token.
This token is used to authorized the user and allow to access the multiple end-point in different microservices
"""
@app.post("/generate_token", response_model=Token)
def login(username: str = Form(...), id: int = Form(...), user_type: str = Form(...)):
    try:
        access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": username, "userid": id, "user_type": user_type}, expires_delta=access_token_expires
        )

        return Token(access_token=access_token, token_type="bearer", user_name=username, user_type=user_type)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


"""
This endpoint of authentication microservices is used to extract user data from existing token.
"""
@app.post("/get_token_data")
def get_token_data(token: str = Form(...)):
    token_data = decode_access_token(token)
    return token_data


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    This function generates an encoded JSON Web Token (JWT)
    containing the data provided as input along with an expiration time.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    """
    This function decodes a given access token using the PyJWT library with the help of a secret key.
    It extracts information such as username, userid, guid, and user_type from the token
    payload and returns the decoded payload.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    expired_token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token has expired",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        print(payload)
        sys.stdout.flush()
        username = str(payload.get("sub"))
        userid = str(payload.get("userid"))
        guid = str(payload.get("guid"))
        user_type = str(payload.get("user_type"))

        if username is None:
            raise credentials_exception

    except ExpiredSignatureError:
        raise expired_token_exception
    except JWTError:
        raise credentials_exception

    return {"username": username, "userid": userid, "guid": guid, "user_type": user_type}
