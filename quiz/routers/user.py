

# pip install python-jose passlib[bcrypt]

from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

from auth import decode_jwt_token, get_keycloak_public_keys
from database import SessionLocal, engine, Base
from models.user import User
from config import settings 
from fastapi import Depends, HTTPException, status, Request

from schemas.user import (
    UserCreate, UserOut, Token, UserGetById, UserPut, UserUpdate,
    BulkCreateUser, BulkUpdateUser, BulkDeleteUser
)

# Router Setup
router = APIRouter(prefix="/user", tags=["Users"])

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# JWT Config
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/questions/token")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}




# Endpoint resposible to authenticate
@router.get("/me", response_model=UserOut)

# for JWT only
# def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     payload = decode_token(token)
#     if not payload:
#         raise HTTPException(status_code=401, detail="Invalid token")
#     username = payload.get("sub")
#     user = db.query(User).filter(User.username == username).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user

# For JWT + Keyclock
async def get_current_user(request: Request, token: str = Depends(oauth2_scheme)):
    # 1. Try local JWT first
    jwt_user = decode_jwt_token(token, "your_jwt_secret", ["HS256"])
    if jwt_user:
        return {"auth": "local", "user": jwt_user}

    # 2. Try Keycloak
    try:
        jwks = await get_keycloak_public_keys()
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header["kid"]

        key = next(k for k in jwks["keys"] if k["kid"] == kid)

        public_key = jwt.construct_rsa_key(key)

        keycloak_user = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=settings.KEYCLOAK_CLIENT_ID,
            issuer=settings.KEYCLOAK_ISSUER
        )
        return {"auth": "keycloak", "user": keycloak_user}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )




################################################################################################################
# endpoints to perform crud on user table
################################################################################################################


# Routes
@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    new_user = User(username=user.username, hashed_password=hash_password(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# -------- GET All Users --------
@router.get("/", response_model=list[UserOut])
def get_all_users(db: Session = Depends(get_db)):
    return db.query(User).all()


# -------- GET User by ID --------
@router.get("/{user_id}", response_model=UserGetById)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# -------- CREATE User --------
@router.post("/", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# -------- FULL UPDATE (PUT) --------
@router.put("/{user_id}", response_model=UserOut)
def put_user(user_id: int, user_data: UserPut, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in user_data.dict().items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


# -------- PARTIAL UPDATE (PATCH) --------
@router.patch("/{user_id}", response_model=UserOut)
def patch_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in user_data.dict(exclude_unset=True).items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


# -------- DELETE User --------
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


# -------- BULK CREATE --------
@router.post("/bulk-create", response_model=list[UserOut])
def bulk_create_users(payload: BulkCreateUser, db: Session = Depends(get_db)):
    users = [User(**user.dict()) for user in payload.users]
    db.add_all(users)
    db.commit()
    for user in users:
        db.refresh(user)
    return users


# -------- BULK UPDATE --------
@router.patch("/bulk-update", response_model=list[UserOut])
def bulk_update_users(payload: BulkUpdateUser, db: Session = Depends(get_db)):
    updated_users = []
    for data in payload.users:
        if not data.id:
            continue  # skip users without ID
        user = db.query(User).filter(User.id == data.id).first()
        if user:
            for key, value in data.dict(exclude_unset=True).items():
                if key != "id":
                    setattr(user, key, value)
            updated_users.append(user)
    db.commit()
    for user in updated_users:
        db.refresh(user)
    return updated_users


# -------- BULK DELETE --------
@router.delete("/bulk-delete")
def bulk_delete_users(payload: BulkDeleteUser, db: Session = Depends(get_db)):
    deleted = db.query(User).filter(User.id.in_(payload.user_ids)).delete(synchronize_session=False)
    db.commit()
    return {"message": f"{deleted} user(s) deleted successfully"}