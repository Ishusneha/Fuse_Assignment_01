from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base
from app.schemas.transaction import TransactionType

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    type = Column(Enum(TransactionType))
    description = Column(String)
    date = Column(DateTime, default=func.now())
    currency = Column(String, default="USD")
    
    category_id = Column(Integer, ForeignKey("categories.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions") 