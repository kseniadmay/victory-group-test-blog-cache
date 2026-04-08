from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models import Post
from app.schemas import PostCreate, PostUpdate


def create_post(db: Session, post: PostCreate):
    db_post = Post(**post.model_dump())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


def get_post(db: Session, post_id: int):
    result = db.execute(text('SELECT * FROM posts WHERE id = :id'), {'id': post_id})
    row = result.fetchone()
    return row._mapping if row else None


def update_post(db: Session, post_id: int, post: PostUpdate):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post:
        for key, value in post.model_dump().items():
            setattr(db_post, key, value)
        db.commit()
        db.refresh(db_post)
    return db_post


def delete_post(db: Session, post_id: int):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post:
        db.delete(db_post)
        db.commit()
    return db_post
