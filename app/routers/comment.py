from .. import models, schemas, oauth2
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from collections import defaultdict
from ..database import get_db
from sqlalchemy.orm import Session, selectinload
from typing import List, Optional
from sqlalchemy import func
from ..ml.model import toxicity_model

router = APIRouter(
    prefix='/comments',
    tags=['comments']
)

@router.get("/{id_post}", status_code=status.HTTP_200_OK, response_model=List[schemas.CommentResponse])
def get_comments(id_post: int, db: Session=Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    got_comments = db.query(models.Comment).filter(models.Comment.post_id==id_post).all()

    print(got_comments)

    if not got_comments:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} is not found") 
    
    return got_comments

@router.get("/{id_post}/{id_comment}", status_code=status.HTTP_200_OK, response_model=schemas.CommentResponse)
def get_comment(id_post: int, id_comment: int, db: Session=Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    got_comment = db.query(models.Comment).filter(models.Comment.post_id==id_post,
                                                  models.Comment.id==id_comment).first()                                                                                
    
    if not got_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} is not found") 
    
    return got_comment

@router.post("/{id_post}", status_code=status.HTTP_201_CREATED, response_model=schemas.CommentCreate)
def post_comment(comment: schemas.CommentCreate, id_post: int, db: Session=Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    new_comment = models.Comment(user_id=current_user.id, post_id=id_post, **comment.model_dump())

    res = toxicity_model.predict_single(new_comment.comment)['is_toxic']

    if res == True:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                            detail=f"toxicity detected")

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment

@router.delete("/{id_post}/{id_comment}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(id_post: int, id_comment: int, db: Session=Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    comment_query = db.query(models.Comment).filter(models.Comment.post_id==id_post,
                                                  models.Comment.id==id_comment)

    comment = comment_query.first()

    if comment == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with {id} does not exist')

    if comment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not authorized to perform requested action")

    comment_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT) 

@router.put("/{id_post}/{id_comment}", status_code=status.HTTP_200_OK, response_model=schemas.CommentResponse)
def update_comment(id_post: int, id_comment: int, updated_post: schemas.CommentCreate, db: Session=Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    comment_query = db.query(models.Comment).filter(models.Comment.post_id==id_post,
                                                  models.Comment.id==id_comment)

    comment = comment_query.first()

    if comment == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with {id_post} and {id_comment} does not exist')

    if comment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not authorized to perform requested action")

    res = toxicity_model.predict_single(comment.content)['is_toxic']

    if res == True:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                            detail=f"toxicity detected")

    comment_query.update(updated_post.model_dump(), synchronize_session=False) 
    db.commit()

    return comment_query.first()
