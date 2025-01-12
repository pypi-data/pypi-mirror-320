from typing import TypedDict
from uuid import UUID


class Bill(TypedDict):
    id: UUID
    business_id: UUID
    amount: float
