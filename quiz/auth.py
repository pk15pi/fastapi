from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from config import settings
from typing import Optional
from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
import httpx


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/questions/token")
# Cache keycloak JWKS (public keys)
_keycloak_public_keys = None


# Global variables for Keycloak public keys and offline token
_keycloak_public_keys = None

async def get_keycloak_public_keys():
    global _keycloak_public_keys
    if _keycloak_public_keys is None:
        async with httpx.AsyncClient() as client:
            response = await client.get(settings.KEYCLOAK_JWKS_URL)
            _keycloak_public_keys = response.json()
    return _keycloak_public_keys


def decode_keycloak_token(token: str):
    # Validate the token using Keycloak's public keys
    try:
        jwks = get_keycloak_public_keys()
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header["kid"]
        key = next(k for k in jwks["keys"] if k["kid"] == kid)
        public_key = jwt.construct_rsa_key(key)
        
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=settings.KEYCLOAK_CLIENT_ID,
            issuer=settings.KEYCLOAK_ISSUER
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Keycloak token"
        )

# Dependency to verify offline token
async def verify_offline_token(token: str = Depends(oauth2_scheme)):
    if token != settings.KEYCLOAK_OFFLINE_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid offline token"
        )
    return token



#  Authentication using JWT
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def decode_jwt_token(token: str, secret_key: str = settings.JWT_SECRET, algorithms: list = [settings.JWT_ALGORITHM]):
    try:
        payload = jwt.decode(token, secret_key, algorithms=algorithms)
        return payload
    except JWTError:
        return None

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


def create_token(data: dict, expires_delta: Optional[timedelta] = None):
# def create_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str):
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None
