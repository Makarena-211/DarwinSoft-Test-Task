from fastapi import APIRouter

router = APIRouter(
    prefix = '/paintings',
    tags=['Paintings']
)