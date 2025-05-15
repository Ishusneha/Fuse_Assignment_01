from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.category import Category

def init_db(db: Session) -> None:
    """Initialize the database with default data."""
    # Create default categories if they don't exist
    default_categories = [
        {"name": "Food & Dining", "description": "Restaurants, groceries, and food delivery"},
        {"name": "Shopping", "description": "Retail purchases and online shopping"},
        {"name": "Transportation", "description": "Gas, public transit, and ride sharing"},
        {"name": "Bills & Utilities", "description": "Electricity, water, internet, and phone"},
        {"name": "Entertainment", "description": "Movies, games, and hobbies"},
        {"name": "Health", "description": "Medical expenses and healthcare"},
        {"name": "Travel", "description": "Flights, hotels, and vacations"},
        {"name": "Education", "description": "Tuition, books, and courses"},
        {"name": "Salary", "description": "Regular employment income"},
        {"name": "Investments", "description": "Investment returns and dividends"},
        {"name": "Gifts", "description": "Received gifts and bonuses"},
        {"name": "Other Income", "description": "Miscellaneous income sources"},
    ]

    for category_data in default_categories:
        category = db.query(Category).filter(Category.name == category_data["name"]).first()
        if not category:
            category = Category(**category_data)
            db.add(category)
    
    db.commit() 