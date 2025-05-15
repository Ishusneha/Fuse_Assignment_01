from typing import Any, List
from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.category import Category as CategoryModel
from app.schemas.category import Category as CategorySchema

router = APIRouter()

@router.get("/", response_model=List[CategorySchema], summary="List all categories")
def read_categories(
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=[]),
) -> Any:
    """
    Retrieve all categories.
    """
    categories = db.query(CategoryModel).all()
    return categories  # FastAPI will automatically convert to schema using orm_mode 