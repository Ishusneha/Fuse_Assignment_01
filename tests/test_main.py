import sys
import os
from pathlib import Path
import pytest
from datetime import datetime
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
from app.core.security import get_password_hash
from app.db.session import get_db
from app.schemas.user import UserCreate

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables for each test
@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Test client
client = TestClient(app)

@pytest.fixture
def db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def test_user() -> dict:
    """Create a test user and return user data with password."""
    email = f"test_{uuid.uuid4()}@example.com"
    password = "testpass123"
    
    user_in = UserCreate(
        email=email,
        password=password,
        full_name="Test User"
    )
    
    response = client.post("/auth/register", json=user_in.dict())
    assert response.status_code == 200, f"Registration failed: {response.text}"
    
    return {
        "user": response.json(),
        "email": email,
        "password": password
    }

@pytest.fixture
def auth_headers(test_user) -> dict:
    """Get authentication headers for a test user."""
    form_data = {
        "username": test_user["email"],
        "password": test_user["password"],
        "grant_type": "password"
    }
    
    response = client.post(
        "/auth/token",
        data=form_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == 200, f"Login failed: {response.text}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def test_category(db: Session) -> Category:
    """Create a test category."""
    category = Category(
        name=f"Test Category {uuid.uuid4()}",
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

def test_user_registration():
    """Test user registration process."""
    email = f"new_user_{uuid.uuid4()}@example.com"
    password = "testpass123"
    
    user_in = UserCreate(
        email=email,
        password=password,
        full_name="New Test User"
    )
    
    response = client.post("/auth/register", json=user_in.dict())
    assert response.status_code == 200, f"Registration failed: {response.text}"
    data = response.json()
    assert "id" in data
    assert data["email"] == email
    assert data["full_name"] == user_in.full_name

def test_user_login(test_user):
    """Test user login process."""
    form_data = {
        "username": test_user["email"],
        "password": test_user["password"],
        "grant_type": "password"
    }
    
    response = client.post(
        "/auth/token",
        data=form_data,
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
    assert data["user_id"] == test_user["user"]["id"]

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
    transactions = [
        {
            "amount": 1000.00,
            "type": "income",
            "description": "Salary",
            "category_id": test_category.id,
            "currency": "USD"
        },
        {
            "amount": 500.00,
            "type": "expense",
            "description": "Rent",
            "category_id": test_category.id,
            "currency": "USD"
        },
        {
            "amount": 200.00,
            "type": "expense",
            "description": "Groceries",
            "category_id": test_category.id,
            "currency": "USD"
        }
    ]
    
    for transaction_data in transactions:
        response = client.post(
            "/api/v1/transactions/",
            json=transaction_data,
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed to create transaction: {response.text}"
    
    response = client.get("/api/v1/transactions/", headers=auth_headers)
    assert response.status_code == 200, f"Failed to read transactions: {response.text}"
    
    transactions = response.json()
    total_income = sum(float(t["amount"]) for t in transactions if t["type"] == "income")
    total_expenses = sum(float(t["amount"]) for t in transactions if t["type"] == "expense")
    
    assert total_income == 1000.00
    assert total_expenses == 700.00