from fastapi import Depends, HTTPException, APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session
from app import schemas, dependencies, models, utils, oauth2

router = APIRouter(tags=['Authentication'])

@router.post('/login', status_code=200, response_model=schemas.Token)
def login(credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(dependencies.get_db)):
    stmt = select(models.User).where(models.User.email == credentials.username)
    user_db = db.execute(stmt).scalar_one_or_none()
    
    if not user_db:
        raise HTTPException(status_code=403, detail="invalid credentials")
    
    if not utils.pwd_context.verify(credentials.password, user_db.password):
        raise HTTPException(status_code=403, detail="invalid credentials")

    access_token = oauth2.create_access_token(data={"user_id": user_db.id})

    return {"access_token": access_token, "token_type": "bearer"}
    