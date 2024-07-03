from typing import Annotated
from shared.models.token import Token
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Depends, status, HTTPException, Form
from app import config
from jose import JWTError, jwt, ExpiredSignatureError

oauth2_authentication = OAuth2PasswordBearer(tokenUrl="token")
app = FastAPI()


@app.post("/generate_token", response_model=Token)
def login(username: str = Form(...), id: int = Form(...)):
    try:
        access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": username, "userid": id}, expires_delta=access_token_expires
        )

        return Token(access_token=access_token, token_type="bearer", user_name=username)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.post("/get_token_data")
def get_token_data(token: str = Form(...)):
    token_data = decode_access_token(token)
    return token_data


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
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
        username = str(payload.get("sub"))
        userid = str(payload.get("userid"))
        guid = str(payload.get("guid"))

        if username is None:
            raise credentials_exception

    except ExpiredSignatureError:
        raise expired_token_exception
    except JWTError:
        raise credentials_exception

    return {"username": username, "userid": userid, "guid": guid}
