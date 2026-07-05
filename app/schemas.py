from datetime import datetime
from typing import Literal, Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True 

class PostCreate(PostBase):
    pass

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True

class PostResponse(PostBase):
    id: int
    created_at: datetime
    user_id: int
    owner: UserOut
    
    class Config:
        from_attributes = True 
    
class CommentResponse(BaseModel):
    id: int
    comment: str
    user_id: int
    post_id: int
    created_at: datetime

    class Config:
        from_attributes = True 

class CommentCreate(BaseModel):
    comment: str

class PostOut(PostResponse):
    comments: List[CommentResponse]

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None
