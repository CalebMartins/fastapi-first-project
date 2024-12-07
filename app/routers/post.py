from fastapi import Depends, HTTPException, APIRouter
from typing import List, Optional
from sqlalchemy import select, update, func
from sqlalchemy.orm import Session
from app import schemas, dependencies, models, oauth2

router = APIRouter(tags=['Posts'])

# @router.get('/getposts', status_code=200, response_model=List[schemas.PostOut])
@router.get('/getposts', status_code=200)
def get_posts(skip: int = 0, limit: int = 10, search: Optional[str] = "", db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    # stmt = select(models.Post).offset(skip).limit(limit).where(models.Post.title.ilike(f"%{search}%"))
    stmt = (
        select(
            models.Post, 
            func.count(models.Vote.post_id).label("votes")
        )
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .offset(skip)
        .limit(limit)
        .where(models.Post.title.ilike(f"%{search}%"))
    )
    results = db.execute(stmt).all()
    
    posts_with_votes = [
        schemas.PostOut(post=Post, votes=votes)
        for Post, votes in results
    ]

    return posts_with_votes

@router.get("/getuserposts/{id}", status_code=200, response_model=List[schemas.PostResponse])
def getuser_posts(id: int, db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    db_user = db.execute(select(models.User).where(models.User.id == id)).scalar_one_or_none()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="user not found")
    
    stmt = select(models.Post).where(models.Post.owner_id == id)
    posts = db.execute(stmt).scalars().all()

    return posts

@router.get('/getpost/{id}', status_code=200, response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    # stmt = select(models.Post).where(models.Post.id == id)
    stmt = (
        select(
            models.Post, 
            func.count(models.Vote.post_id).label("votes")
        )
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .where(models.Post.id == id)
    ) 
    post = db.execute(stmt).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    post_with_vote = schemas.PostOut(post=post[0], votes=post[1])
    
    # return schemas.PostResponse.model_validate(post)
    return post_with_vote

@router.post('/createpost', status_code=201, response_model=schemas.PostResponse)
def create_post(post: schemas.Post, db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    post = post.model_dump()
    post.update({"owner_id": current_user.id})
    new_post = models.Post(**post)
    db.add(new_post) # Add the user instance to the session
    db.commit() # Commit to save the new user in the database
    db.refresh(new_post) # Refresh to get the latest state from the database
    
    return schemas.PostResponse.model_validate(new_post)

@router.put('/updatepost/{id}', status_code=200, response_model=schemas.PostResponse)
def update_post(id: int, post: schemas.UpdatePost, db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    post = post.model_dump()
    
    stmt = select(models.Post).where(models.Post.id == id)
    db_post = db.execute(stmt).scalar_one_or_none()
    
    if not db_post:
        raise HTTPException(status_code=404, detail="post not found")
    
    if db_post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="not authorized to peform request action")
    
    stmt = update(models.Post).where(models.Post.id == id).values({key: value for key, value in post.items() if value is not None})
    result = db.execute(stmt)
    db.commit()
    db.refresh(db_post)
    
    return schemas.PostResponse.model_validate(db_post)
    
@router.delete('/deletepost/{id}')
def delete_post(id: int, db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    stmt = select(models.Post).where(models.Post.id == id)
    db_post = db.execute(stmt).scalar_one_or_none()
    
    if db_post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="not authorized to perform request action")
    
    if not db_post:
        raise HTTPException(status_code=404, detail="post not found")
    
    db.delete(db_post)
    db.commit()
    
    return {"message": "post deleted"}