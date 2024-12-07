from app.config import settings
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from app import schemas, models, dependencies
from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

def create_access_token(data: dict):
    to_encode = data.copy()
    
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def verify_access_token(token: str, credential_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("user_id")
        
        if not id:
            raise credential_exception
        
        token_data = schemas.TokenData(id=id)
    except JWTError as error:
        # print(error)
        raise credential_exception
    
    return token_data
    
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(dependencies.get_db)):
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials",  headers={"WW-Authenticate": "Bearer"})
    
    token_payload = verify_access_token(token, credentials_exception)
    
    stmt = select(models.User).where(models.User.id == token_payload.id)
    user = db.execute(stmt).scalar_one_or_none()
    
    return user