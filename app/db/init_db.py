from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Category

def init_db(db: Session) -> None:
    # Create default categories
    default_categories = [
        {"name": "Groceries", "description": "Food and household items"},
        {"name": "Transportation", "description": "Public transport, fuel, etc."},
        {"name": "Utilities", "description": "Electricity, water, internet, etc."},
        {"name": "Entertainment", "description": "Movies, games, dining out"},
        {"name": "Salary", "description": "Regular income"},
        {"name": "Investment", "description": "Returns from investments"},
        {"name": "Shopping", "description": "Clothing, electronics, etc."},
        {"name": "Healthcare", "description": "Medical expenses, medicines"},
        {"name": "Education", "description": "Books, courses, tuition"},
        {"name": "Other", "description": "Miscellaneous expenses"}
    ]

    for category_data in default_categories:
        category = db.query(Category).filter(Category.name == category_data["name"]).first()
        if not category:
            category = Category(**category_data)
            db.add(category)
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise e 