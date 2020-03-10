import grp
import pwd
from datetime import datetime, timedelta
from typing import List

import jwt
from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from jwt import PyJWTError
from pydantic import BaseModel, ValidationError
from starlette.status import HTTP_401_UNAUTHORIZED

from datetime import timedelta
from systemd import journal

import tools.pam as pam

router = APIRouter()

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "aab3804c0c7fcd0253b0fc996665ff2d1575da212993df5fcb9c9b210640c246"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str = None
    scopes: List[str] = []


class User(BaseModel):
    username: str
    scopes: List[str]


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

def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if not (scopes := to_encode.get('scopes')):
        scopes = supported_scopes
    groups = set(get_user_groups(to_encode.get('sub')))
    # if the user is a member of one of the adminstrative groups and did not request
    # specific persmissions
    if any(g for g in groups if g in ("adm", "wheel", "sudo")):
        groups |= full_access_groups
    to_encode['scopes'] = [s for s in scopes if s in groups]
    # if a expiration date has been requested, use it
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
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
        authenticate_value = f"Bearer"
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(username=username, scopes=token_scopes)
    except (PyJWTError, ValidationError):
        raise credentials_exception
    # user = get_user(username=token_data.username)
    user = User(username=token_data.username, scopes=token_data.scopes)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Insufficient permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user), scopes: List[str] = []
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


# TODO: move to own module
@router.get("/logs/vdr/")
async def read_scope(
    current_user: User = Security(get_current_active_user, scopes=["log"])):
    r = journal.Reader()
    #r.seek_monotonic(timedelta(minutes=-1))
    r.this_boot()
    #events = [e for e in r.get_next()]
    r.add_match("SYSLOG_IDENTIFIER=vdr")
    #events = list(r)
    return list(r)
