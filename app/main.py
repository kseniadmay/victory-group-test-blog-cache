from fastapi import FastAPI, Depends, HTTPException, status
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session

from app.database import get_db, Base, engine
from app.schemas import PostCreate, PostUpdate, PostResponse
from app.crud import create_post, get_post, update_post, delete_post
from app.cache import get_post_from_cache, set_post_to_cache, invalidate_cache


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title='Blog Cache Test API', lifespan=lifespan)


@app.post('/posts/', response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post_endpoint(post: PostCreate, db: Session = Depends(get_db)):
    return create_post(db, post)


@app.get('/posts/{post_id}', response_model=PostResponse)
async def get_post_endpoint(post_id: int, db: Session = Depends(get_db)):
    cached = get_post_from_cache(post_id)
    if cached:
        return cached

    post = get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail='Пост не найден')

    post_dict = dict(post)
    set_post_to_cache(post_dict)
    return post_dict


@app.put('/posts/{post_id}', response_model=PostResponse)
async def update_post_endpoint(post_id: int, post: PostUpdate, db: Session = Depends(get_db)):
    updated = update_post(db, post_id, post)
    if not updated:
        raise HTTPException(status_code=404, detail='Пост не найден')
    invalidate_cache(post_id)
    return updated


@app.delete('/posts/{post_id}')
async def delete_post_endpoint(post_id: int, db: Session = Depends(get_db)):
    deleted = delete_post(db, post_id)
    if not deleted:
        raise HTTPException(status_code=404, detail='Пост не найден')
    invalidate_cache(post_id)
    return {'message': 'Пост успешно удалён'}
