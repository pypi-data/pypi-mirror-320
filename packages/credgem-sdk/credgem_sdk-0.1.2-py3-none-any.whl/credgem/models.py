from typing import Dict, List, Optional
from pydantic import BaseModel


class Balance(BaseModel):
    credit_type_id: str
    available: float
    held: float
    spent: float


class WalletResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    context: Dict = {}
    balances: List[Balance] = []
    created_at: str
    updated_at: str


class CreditTypeResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    created_at: str
    updated_at: str


class TransactionResponse(BaseModel):
    id: str
    wallet_id: str
    credit_type_id: str
    amount: float
    type: str
    description: Optional[str] = None
    issuer: str
    context: Dict = {}
    created_at: str 