from sqlmodel import Field, SQLModel
from pydantic import BaseModel
import uuid as uuid_pkg


class Date(BaseModel):
    day: int
    month: int
    year: int


class TransactionResult(SQLModel, table=True):
    id: uuid_pkg.UUID = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    day: int = Field(
        ...,
        min_items=1,
        max_items=31,
        description="Day of transaction",
    )
    month: int = Field(
        ...,
        min_items=1,
        max_items=12,
        description="Month of transaction",
    )
    year: int = Field(
        ...,
        min_items=2024,
        description="Year of transaction",
    )
    amount: float = Field(
        ...,
        description="Amount of transaction",
    )
    description: str = Field(
        description="Description of transaction",
        default="",
    )
    code_id: str = Field(
        nullable=True,
        description="Code ID of transaction",
    )
