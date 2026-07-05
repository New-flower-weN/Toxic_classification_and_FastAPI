from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from .routers import auth, post, comment, user
from .database import *
from sqlalchemy.orm import Session
from . import models, schemas, config

app = FastAPI()

@app.get('/')
def func():
    return {'message': 'hello, world'}

app.include_router(post.router) 
app.include_router(comment.router)
app.include_router(user.router)
app.include_router(auth.router)