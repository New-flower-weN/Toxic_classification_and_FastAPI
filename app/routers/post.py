from .. import models, schemas, oauth2
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from collections import defaultdict
from ..database import get_db
from sqlalchemy.orm import Session, selectinload
from typing import List, Optional
from sqlalchemy import func
from ..ml.model import toxicity_model

router = APIRouter(
    prefix='/posts',
    tags=['posts']
)

@router.get('/', status_code=status.HTTP_200_OK, response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    posts = db.query(models.Post).options(
        selectinload(models.Post.comments)
    ).all()
    
    return posts

# options() в SQLAlchemy — это метод, который позволяет настроить способ загрузки связанных данных в одном запросе. 
# Он решает проблему N+1 запросов.
# Что делает options(selectinload(...))?
# Без options:
# python
# posts = db.query(models.Post).all()
# for post in posts:
#     comments = post.comments  # Здесь выполняется ДОПОЛНИТЕЛЬНЫЙ запрос к БД!
# Это создает N+1 запросов:
# 1 запрос для получения всех постов
# N запросов для получения комментариев к каждому посту
# С options(selectinload(...)):
# python
# posts = db.query(models.Post).options(
#     selectinload(models.Post.comments)
# ).all()
# Выполняется всего 2 запроса:
# SELECT * FROM posts
# SELECT * FROM comments WHERE post_id IN (1, 2, 3, ...) — одним запросом для всех постов
# options()	Метод для применения стратегий	query.options(...)
# selectinload()	Стратегия загрузки (IN-запрос)	selectinload(Model.relation)
# joinedload()	Стратегия загрузки (JOIN)	joinedload(Model.relation)
# subqueryload()	Стратегия загрузки (подзапрос)	subqueryload(Model.relation)

# @router.get("/{id}", response_model=schemas.PostResponse) # {id} -> just some variable FastAPI cant tell differenc between this & "/posts/latest" -> order matter
@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.PostOut)
def get_post(id: int, db: Session=Depends(get_db), current_user: int = Depends(oauth2.get_current_user)): 

    got_post = db.query(models.Post).options(selectinload(models.Post.comments)).filter(models.Post.id==id).first()

    if not got_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} is not found")

    return got_post

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.PostCreate)
def post_post(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    new_post = models.Post(user_id=current_user.id, **post.model_dump())

    res_1 = toxicity_model.predict_single(new_post.content)['is_toxic']
    res_2 = toxicity_model.predict_single(new_post.title)['is_toxic']

    if res_1 == True or res_2 == True:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                            detail=f"toxicity detected")

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session=Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id==id)

    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with {id} does not exist')

    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not authorized to perform requested action")

    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT) 

@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.PostResponse)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session=Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id==id)

    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with {id} does not exist')

    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not authorized to perform requested action")

    res_1 = toxicity_model.predict_single(updated_post.content)['is_toxic']
    res_2 = toxicity_model.predict_single(updated_post.title)['is_toxic']

    if res_1 == True or res_2 == True:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                            detail=f"toxicity detected")

    post_query.update(updated_post.model_dump(), synchronize_session=False)
    db.commit()

    return post_query.first()