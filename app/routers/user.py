from fastapi import Depends, HTTPException, APIRouter
from typing import List
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from app import schemas, dependencies, models, utils

router = APIRouter(tags=['Users'])

@router.get('/getusers', status_code=200, response_model=List[schemas.UserResponse])
def get_users(skip: int = 0, limit: int = 10, db: Session = Depends(dependencies.get_db)):
    stmt = select(models.User).offset(skip).limit(limit)
    users = db.execute(stmt).scalars().all()
    
    return users

@router.get('/getuser/{id}', status_code=200, response_model=schemas.UserResponse)
def get_user(id: int, db: Session = Depends(dependencies.get_db)):
    stmt = select(models.User).where(models.User.id == id)
    user_db = db.execute(stmt).scalar_one_or_none()
    
    if not user_db:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return user_db

@router.post('/createuser', status_code=201, response_model=schemas.UserResponse)
def create_user(user: schemas.UserBase, db: Session = Depends(dependencies.get_db)):
    user = user.model_dump()
    stmt = select(models.User).where(models.User.email == user['email'])
    existing_user = db.execute(stmt).scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="account already exists")
    
    hashed_pwd = utils.hash(user['password'])
    user['password'] = hashed_pwd
    new_user = models.User(**user)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user
    
@router.put('/updateuser/{id}', status_code=200, response_model=schemas.UserResponse)
def update_user(id: int, user: schemas.UserUpdate, db: Session = Depends(dependencies.get_db)):
    user = user.model_dump()
    
    if user['password']:
        hashed_pwd = utils.hash(user['password'])
        user['password'] = hashed_pwd
    
    stmt = update(models.User).where(models.User.id == id).values({key: value for key, value in user.items() if value is not None})
    result = db.execute(stmt)
    db.commit()
    
    if not result.rowcount:
        raise HTTPException(status_code=404, detail="account not found")
    
    stmt = select(models.User).where(models.User.id == id)
    db_user = db.execute(stmt).scalar_one_or_none()
    
    return db_user
    
@router.delete('/deleteuser/{id}')
def delete_user(id: int, db: Session = Depends(dependencies.get_db)):
    stmt = select(models.User).where(models.User.id == id)
    db_user = db.execute(stmt).scalar_one_or_none()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="user not found")
    
    db.delete(db_user)
    db.commit()
    
    return {"message": "account deleted"}