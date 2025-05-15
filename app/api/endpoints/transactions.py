from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.transaction import Transaction
from app.schemas.transaction import Transaction as TransactionSchema
from app.schemas.transaction import TransactionCreate, TransactionUpdate

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

@router.get("/", response_model=List[TransactionSchema], summary="List all transactions")
def read_transactions(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Security(get_current_user, scopes=[]),
) -> Any:
    """
    Retrieve all transactions for the current user.

    - **skip**: Number of transactions to skip (pagination)
    - **limit**: Maximum number of transactions to return
    """
    transactions = (
        db.query(Transaction)
        .options(joinedload(Transaction.category))
        .filter(Transaction.user_id == current_user.id)
        .order_by(Transaction.date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return transactions

@router.post("/", response_model=TransactionSchema, summary="Create new transaction")
def create_transaction(
    *,
    db: Session = Depends(get_db),
    transaction_in: TransactionCreate,
    current_user: User = Security(get_current_user, scopes=[]),
) -> Any:
    """
    Create a new transaction for the current user.

    - **amount**: Transaction amount (required)
    - **type**: INCOME or EXPENSE (required)
    - **description**: Transaction description (required)
    - **currency**: Currency code, defaults to USD
    - **category_id**: ID of the category (required)
    """
    transaction = Transaction(
        **transaction_in.dict(),
        user_id=current_user.id
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    # Reload the transaction with category
    transaction = (
        db.query(Transaction)
        .options(joinedload(Transaction.category))
        .filter(Transaction.id == transaction.id)
        .first()
    )
    return transaction

@router.put("/{transaction_id}", response_model=TransactionSchema, summary="Update transaction")
def update_transaction(
    *,
    db: Session = Depends(get_db),
    transaction_id: int,
    transaction_in: TransactionUpdate,
    current_user: User = Security(get_current_user, scopes=[]),
) -> Any:
    """
    Update a transaction.

    - **transaction_id**: ID of the transaction to update
    - **amount**: New amount (optional)
    - **type**: New type (optional)
    - **description**: New description (optional)
    - **currency**: New currency (optional)
    - **category_id**: New category ID (optional)
    """
    transaction = (
        db.query(Transaction)
        .options(joinedload(Transaction.category))
        .filter(Transaction.id == transaction_id, Transaction.user_id == current_user.id)
        .first()
    )
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    for field, value in transaction_in.dict(exclude_unset=True).items():
        setattr(transaction, field, value)
    
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    # Reload the transaction with category
    transaction = (
        db.query(Transaction)
        .options(joinedload(Transaction.category))
        .filter(Transaction.id == transaction.id)
        .first()
    )
    return transaction

@router.delete("/{transaction_id}", summary="Delete transaction")
def delete_transaction(
    *,
    db: Session = Depends(get_db),
    transaction_id: int,
    current_user: User = Security(get_current_user, scopes=[]),
) -> Any:
    """
    Delete a transaction.

    - **transaction_id**: ID of the transaction to delete
    """
    transaction = (
        db.query(Transaction)
        .filter(Transaction.id == transaction_id, Transaction.user_id == current_user.id)
        .first()
    )
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    db.delete(transaction)
    db.commit()
    return {"status": "success"} 