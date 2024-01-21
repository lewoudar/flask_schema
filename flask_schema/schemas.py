from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_serializer


class TodoInputSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: str | None = None


class TodoOutputSchema(TodoInputSchema):
    id: int
    done: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    @field_serializer('created_at', 'updated_at')
    def serialize_dt(self, dt: datetime, _info):
        return dt.isoformat()


class TodoUpdateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: Optional[str] = None
    done: Optional[bool] = None
    description: Optional[str] = None
