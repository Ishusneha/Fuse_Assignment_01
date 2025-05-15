from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.schemas.category import Category

class TransactionType(str, Enum):
    income = "income"
    expense = "expense"

class TransactionBase(BaseModel):
    amount: float
    type: TransactionType
    description: str
    category_id: int
    currency: str = "USD"

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(TransactionBase):
    amount: Optional[float] = None
    type: Optional[TransactionType] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    currency: Optional[str] = None

class Transaction(TransactionBase):
    id: int
    date: datetime
    user_id: int
    category: Optional[Category]

    class Config:
        orm_mode = True 