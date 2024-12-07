from fastapi import Depends, HTTPException, APIRouter
from typing import List
from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from app import schemas, dependencies, models, utils, oauth2

router = APIRouter(tags=['Votes'])

@router.post('/vote', status_code=201)
def vote(vote: schemas.Vote, db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    stmt = select(models.Post).where(models.Post.id == vote.post_id)
    db_post = db.execute(stmt).scalar_one_or_none()
    
    if not db_post:
        raise HTTPException(status_code=404, detail="post not found")
    
    stmt = select(models.Vote).where(
        and_(models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id)
        )
    db_vote = db.execute(stmt).scalar_one_or_none()
    
    if vote.dir == 1:
        if db_vote:
            raise HTTPException(status_code=404, detail="you've already voted on this post")
        new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message": "successfully added vote"}
    else:
        if not db_vote:
            raise HTTPException(status_code=404, detail="vote not found")
        
        db.delete(db_vote)
        db.commit()
        
        return {"message": "vote successfuly removed"}


