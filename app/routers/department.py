from fastapi import APIRouter, HTTPException

department_router = APIRouter()


@department_router.get("/")
async def root():
    return {"message": "Hello World"}
