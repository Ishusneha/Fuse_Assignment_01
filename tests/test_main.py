import sys
import os
from pathlib import Path
import pytest
from datetime import datetime
from decimal import Decimal
import uuid
from typing import Generator

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from app.main import app
from app.db.base import Base
from app.core.config import settings
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.user import User
from app.core.security import get_password_hash, verify_password
from app.db.session import get_db
from app.schemas.user import UserCreate

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool  # This ensures single connection
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

def override_get_db():
    """Override the database dependency."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override the database dependency
app.dependency_overrides[get_db] = override_get_db

# Test client
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    """Setup fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db() -> Generator[Session, None, None]:
    """Get database session for tests."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def test_user(db: Session) -> dict:
    """Create a test user and return user data with password."""
    email = f"test_{uuid.uuid4()}@example.com"
    password = "testpass123"
    
    # Create user through the API endpoint
    user_data = {
        "email": email,
        "password": password,
        "full_name": "Test User"
    }
    
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 200, f"Registration failed: {response.text}"
    
    # Get the created user from database
    user = db.query(User).filter(User.email == email).first()
    assert user is not None, "User was not created in database"
    assert verify_password(password, user.hashed_password), "Password verification failed"
    
    return {
        "user": user,
        "email": email,
        "password": password
    }

@pytest.fixture
def auth_headers(test_user) -> dict:
    """Get authentication headers for a test user."""
    # Create form data
    form_data = {
        "username": test_user["email"],
        "password": test_user["password"],
        "grant_type": "password"
    }
    
    # Send as form data
    response = client.post(
        "/auth/token",
        data=form_data,  # Use data instead of json for form data
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == 200, f"Login failed: {response.text}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def test_category(db: Session) -> Category:
    """Create a test category."""
    category = Category(
        name="Test Category",
        description="Test category description"
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

def test_read_main():
    """Test the main endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to Finance Tracker API",
        "docs": "/docs",
        "redoc": "/redoc"
    }

def test_user_registration(db: Session):
    """Test user registration process."""
    email = f"new_user_{uuid.uuid4()}@example.com"
    password = "testpass123"
    
    user_data = {
        "email": email,
        "password": password,
        "full_name": "New Test User"
    }
    
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 200, f"Registration failed: {response.text}"
    assert "id" in response.json()
    
    # Verify user exists in database
    user = db.query(User).filter(User.email == email).first()
    assert user is not None, "User was not created in database"
    assert user.full_name == user_data["full_name"]
    assert verify_password(password, user.hashed_password)

def test_user_login(test_user):
    """Test user login process."""
    # Create form data
    form_data = {
        "username": test_user["email"],
        "password": test_user["password"],
        "grant_type": "password"
    }
    
    # Send as form data
    response = client.post(
        "/auth/token",
        data=form_data,  # Use data instead of json for form data
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_create_transaction(db: Session, test_user, auth_headers, test_category):
    """Test creating a new transaction."""
    transaction_data = {
        "amount": 100.50,
        "type": "income",
        "description": "Test transaction",
        "category_id": test_category.id,
        "currency": "USD"
    }
    
    response = client.post(
        "/api/v1/transactions/",
        json=transaction_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200, f"Failed to create transaction: {response.text}"
    data = response.json()
    assert float(data["amount"]) == transaction_data["amount"]
    assert data["type"] == transaction_data["type"]
    assert data["description"] == transaction_data["description"]

def test_read_transactions(auth_headers):
    """Test reading transactions list."""
    response = client.get("/api/v1/transactions/", headers=auth_headers)
    assert response.status_code == 200, f"Failed to read transactions: {response.text}"
    assert isinstance(response.json(), list)

def test_read_categories(auth_headers):
    """Test reading categories list."""
    response = client.get("/api/v1/categories/", headers=auth_headers)
    assert response.status_code == 200, f"Failed to read categories: {response.text}"
    assert isinstance(response.json(), list)

def test_transaction_summary(db: Session, test_user, auth_headers, test_category):
    """Test transaction calculations."""
    # Create test transactions
    transactions = [
        {"amount": 1000.00, "type": "income", "description": "Salary", "category_id": test_category.id, "currency": "USD"},
        {"amount": 500.00, "type": "expense", "description": "Rent", "category_id": test_category.id, "currency": "USD"},
        {"amount": 200.00, "type": "expense", "description": "Groceries", "category_id": test_category.id, "currency": "USD"}
    ]
    
    # Add transactions through API
    for transaction_data in transactions:
        response = client.post(
            "/api/v1/transactions/",
            json=transaction_data,
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed to create transaction: {response.text}"
    
    # Get all transactions
    response = client.get("/api/v1/transactions/", headers=auth_headers)
    assert response.status_code == 200, f"Failed to read transactions: {response.text}"
    
    # Calculate totals
    transactions = response.json()
    total_income = sum(float(t["amount"]) for t in transactions if t["type"] == "income")
    total_expenses = sum(float(t["amount"]) for t in transactions if t["type"] == "expense")
    
    assert total_income == 1000.00
    assert total_expenses == 700.00