from pydantic import BaseModel, ConfigDict, Field, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    password: str
    
class UserResponse(BaseModel):
    email: EmailStr
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    
####################################################################

class Post(BaseModel):
    title: str
    content: str
    published: Optional[bool] = None
    
class PostResponse(BaseModel):
    id: int
    owner_id: int
    title: str
    content: str
    published: bool
    created_at: datetime
    owner: UserResponse
    
    model_config = ConfigDict(from_attributes=True) 

class PostOut(BaseModel):
    post: PostResponse
    votes: int
    
    model_config = ConfigDict(from_attributes=True)
    
class UpdatePost(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    published: Optional[bool] = None
    
####################################################################

class Login(BaseModel):
    email: EmailStr
    password: str
    
####################################################################    

class Token(BaseModel):
    access_token: str
    token_type: str
    
    model_config = ConfigDict(from_attributes=True)

class TokenData(BaseModel):
    id: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)
    
####################################################################

class Vote(BaseModel):
    post_id: int
    dir: int = Field(..., ge=0, le=1)
    