from typing import Any, List
from fastapi import APIRouter, Depends, Security, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.category import Category as CategoryModel
from app.schemas.category import Category as CategorySchema
from app.schemas.category import CategoryCreate

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

@router.post("/", response_model=CategorySchema, summary="Create new category")
def create_category(
    *,
    db: Session = Depends(get_db),
    category_in: CategoryCreate,
    current_user: User = Security(get_current_user, scopes=[]),
) -> Any:
    """
    Create a new category.
    """
    # Check if category with same name exists
    existing_category = db.query(CategoryModel).filter(CategoryModel.name == category_in.name).first()
    if existing_category:
        raise HTTPException(
            status_code=400,
            detail="Category with this name already exists"
        )
    
    category = CategoryModel(**category_in.dict())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category 