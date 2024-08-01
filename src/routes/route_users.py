from fastapi import APIRouter, Depends, Security, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer

from src.database.connect import Database
from src.repository.users import UserDB
from src.schemas.users import UserModel, UserResponse, TokenModel
from src.services.auth import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])
database = Database()

get_refresh_token = HTTPBearer()


async def get_email_form_refresh_token(token: str):
    try:
        payload = jwt.decode(token, auth_service.SECRET_KEY, algorithms=[auth_service.ALGORITHM])
        email = payload.get("sub")
        return email
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel,  user_db: UserDB = Depends(database.get_user_db)):
    exist_user = await user_db.get_user_by_email(email=body.email)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account with this email already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await user_db.create_user(body=body)
    return new_user


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), user_db: UserDB = Depends(database.get_user_db)):
    user = await user_db.get_user_by_email(email=body.username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email, "test": "RomboAPI"})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await user_db.update_token(user, refresh_token)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token')
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(get_refresh_token), user_db: UserDB = Depends(database.get_user_db)):
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await user_db.get_user_by_email(email=email)
    if user.refresh_token != token:
        await user_db.update_token(user, None)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await user_db.update_token(user, refresh_token)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
