from pydantic import BaseModel, condecimal
from typing import Optional
from datetime import datetime
from enum import Enum
from app.schemas.category import Category

class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"

class TransactionBase(BaseModel):
    amount: condecimal(max_digits=10, decimal_places=2)
    type: TransactionType
    description: str
    currency: str = "USD"
    category_id: int

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(TransactionBase):
    amount: Optional[condecimal(max_digits=10, decimal_places=2)] = None
    type: Optional[TransactionType] = None
    description: Optional[str] = None
    currency: Optional[str] = None
    category_id: Optional[int] = None

class Transaction(TransactionBase):
    id: int
    date: datetime
    user_id: int
    category: Optional[Category]

    class Config:
        orm_mode = True 