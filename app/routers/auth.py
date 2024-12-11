import grp
import pwd
from datetime import datetime, timedelta
from pytz import UTC
from secrets import token_hex
from typing import List

import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from jwt import PyJWTError
from pydantic import BaseModel, Field, ValidationError
from starlette.status import HTTP_401_UNAUTHORIZED

import tools.pam as pam

router = APIRouter()

# IDEA: generate a new token on earch startup
# SECRET_KEY = token_hex(32)
SECRET_KEY = '5a031715ae22a2690ee9f2fa3acb1cc56c142062eef2b2b752c44330a4e50365'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 60  # do we need to make this configurable?


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str = ''
    scopes: List[str] = []


class User(BaseModel):
    username: str
    scopes: List[str] = Field(default_factory=list)


pam_authenticator = pam.pam()

supported_scopes = {
    "adm": "grant full access",
    "log": "grant log access",
}


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/token",
    scopes=supported_scopes
)


def get_user_groups(username: str) -> List[str]:
    return [
        user_groups.gr_name for user_groups in grp.getgrall()
        if username in user_groups.gr_mem
    ]


def get_user(username: str):
    try:
        pwd.getpwnam(username)
    except KeyError:
        return None
    groups = get_user_groups(username)
    return User(username=username, scopes=groups)


full_access_groups = set(["adm", "log", "remote"])


def create_access_token(*, data: dict, expires_delta: timedelta|None = None):
    to_encode = data.copy()
    if not (scopes := to_encode.get('scopes')):
        scopes = supported_scopes
    groups = set(get_user_groups(to_encode.get('sub', set())))
    # if the user is a member of one of the adminstrative groups and did not request
    # specific persmissions
    if any(g for g in groups if g in ("adm", "wheel", "sudo")):
        groups |= full_access_groups
    to_encode['scopes'] = [s for s in scopes if s in groups]
    # if a expiration date has been requested, use it
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(days=1)  # valid for a day by default
    to_encode.update({"exp": expire})
    print("creating token", to_encode)
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme)
):
    if security_scopes.scopes:
        authenticate_value = f"Bearer scope='{security_scopes.scope_str}'"
    else:
        authenticate_value = "Bearer"

    CREDENTIALS_ERROR = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise CREDENTIALS_ERROR
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(username=username, scopes=token_scopes)
    except (PyJWTError, ValidationError):
        raise CREDENTIALS_ERROR
    # user = get_user(username=token_data.username)
    try:
        user = User(username=token_data.username, scopes=token_data.scopes)
    except ValidationError:
        raise CREDENTIALS_ERROR
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail=f"Insufficient permissions - scope {scope} required",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)#, scopes: List[str] = None
) -> User:
    return current_user


@router.post("/token/refresh", response_model=Token)
async def refresh_access_token(current_user: User = Depends(get_current_active_user)):
    """return a newly created token if the user is authenticated by a valid token"""
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user.username, "scopes": current_user.scopes},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Oauth2 style login.

    Currently only username, password and scopes are used.

    If no scopes are given, the user receives maximum permissions if the account is a member
    of one of the administrative groups (adm, sudo, wheel).

    Otherwise the requested scopes are returned if the user is a member in the respective groups.
    """
    if not pam_authenticator.authenticate(form_data.username, form_data.password):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username, "scopes": form_data.scopes},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user
