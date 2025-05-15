from app.db.session import SessionLocal
from app.models.category import Category

def check_categories():
    db = SessionLocal()
    categories = db.query(Category).all()
    print("\nCategories in database:")
    for category in categories:
        print(f"ID: {category.id}, Name: {category.name}, Description: {category.description}")
    db.close()

if __name__ == "__main__":
    check_categories() 