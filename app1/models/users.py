from datetime import datetime

from sqlmodel import SQLModel, Field as SQLField

from pydantic import Field, EmailStr


class User(SQLModel, table=True):
    id: int | None = SQLField(default=None, nullable=False, primary_key=True)
    username: str
    email: EmailStr
    created_at: datetime = Field(nullable=False)

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "1",
                "username": "elonmask",
                "email": "elonmask@spacex.com",
                "created_at": "22-10-2024",
            }
        }
    }
