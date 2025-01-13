from datetime import datetime
from typing import NotRequired, TypedDict
from uuid import UUID


class Consumer(TypedDict):
    id: UUID
    first_name: str
    last_name: str
    phone_number: str
    email: NotRequired[str]

    # User attributes
    user_id: UUID
    notification_ids: list[UUID]
    active_status: bool
    created_datetime: datetime
    updated_datetime: datetime
