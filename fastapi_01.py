from turtle import pos

from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from git import Optional
from pydantic import BaseModel
from random import randrange

# uvicorn fastapi_lesson.fastapi_01:app --reload

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True # if not provided then True is defauolt calue
    rating: Optional[int] = None #[type is int] and default is None

my_posts = [{"title": "title of post1", "content": "content of post 1", "id": 1}, 
            {"title": "food", "content": "pizza", "id": 2}            
]

def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p
    return None

def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            return i
    return None

# path operation 
# function -> returns data that gets back to the user, fastapi converts in to json
# decorator -> turns function into path operator
# get -> http method 
@app.get("/") # "/" -> path path of our url
async def root():
    return {'message': 'op dsfasd'}

@app.get('/posts')
def get_posts():
    return {"data": my_posts}

# @app.post("/createposts")
# def create_posts(payload: dict = Body(...)): # extracts all the fields from body & converts it into python dictionary
#     print(payload)
#     return {"new_post": f"title {payload['title']} content {payload['content']}"}
# title str, content str -> that's what we want

# instead of what we have on top we can do that:
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post): # throws an error if there're no required fields or data type is wrong or tries to convert it to str
    print(post, post.title, post.published)
    print(post.model_dump()) # dumps as a dictionary
    
    post_dict = post.model_dump()
    post_dict['id'] = randrange(0, 1000000)
    my_posts.append(post_dict)
    return {"data": post_dict} # automatically change it into json as it get sent


# CRUD -> main functions of any application
# Create Read Update Delete
# @app.post("/posts")
# @app.get("/posts/{id}") # one post
# @app.get("/posts") 
# @app.put("/posts/{id}")
# @app.delete("/posts/{id}")

@app.get("/posts/{id}") # {id} -> just some variable FastAPI cant tell differenc between this & "/posts/latest" -> order matter
def get_post(id: int, response: Response): # id has type of str so like this we convert automatically into int if it can be converted
    print(id)
    post = find_post(int(id))
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} is not found") # does the same thing as the code below
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {'message': f"post with id {id} is not found"}
    return{"post_detail": post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    index = find_index_post(id)

    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with {id} does not exist')

    my_posts.pop(index)
    # return {'message': "post was succesfully deleted"} # this does not gets sent back
    return Response(status_code=status.HTTP_204_NO_CONTENT) # while deleting there're no info that should get sent back

@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    print(post)

    index = find_index_post(id)

    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with {id} does not exist')

    post_dict = post.model_dump() 
    post_dict['id'] = id
    my_posts[index] = post_dict
    return {"data": post_dict}