from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemas, models, utils, oauth2
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

router = APIRouter(
    tags=["authentication"]
)

@router.post('/login/')
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session=Depends(get_db)):
    user = db.query(models.User).filter(models.User.email==user_credentials.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")
    
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")
    
    acces_token = oauth2.create_access_token(data={"user_id": user.id})

    return {"access_token": acces_token, "token_type": "bearer"}

#  Эндпоинт /login
# python
# @router.post('/login/')
# def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session=Depends(get_db)):
# OAuth2PasswordRequestForm — это класс FastAPI, который автоматически извлекает из тела запроса поля username и password

# Важно: В Swagger UI поле называется username, но вы используете его как email

# 2. Поиск пользователя
# python
# user = db.query(models.User).filter(models.User.email==user_credentials.username).first()
# Ищем пользователя по email (который передается как username)

# 3. Проверка пароля
# python
# if not utils.verify(user_credentials.password, user.password):
# utils.verify() — ваша функция для проверки хешированного пароля

# 4. Создание токена
# python
# acces_token = oauth2.create_access_token(data={"user_id": user.id})
# Создаем JWT токен с ID пользователя

# 5. Ответ
# python
# return {"access_token": acces_token, "token_type": "bearer"}
# Возвращаем токен в формате, ожидаемом OAuth2