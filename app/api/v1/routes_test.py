from fastapi import APIRouter

router = APIRouter(prefix="/test")

@router.get("/greet")
def greet():
    return{"greeting":"Hello, GoodMorning!"}