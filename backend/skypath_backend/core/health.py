"""Health check router"""
from fastapi import APIRouter

default_router = APIRouter(prefix="/health")


@default_router.get("/")
def health_check():
    """Health check endpoint."""
    return {"status": "OK"}
