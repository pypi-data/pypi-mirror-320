from pydantic import BaseModel, Field, AfterValidator
from datetime import datetime
from typing import List, Annotated
from uuid import uuid4
from factory_sdk.dto.resource import is_valid_uuid


class NewProject(BaseModel):
    name: str

class Project(BaseModel):
    id: str=Field(default_factory=lambda: str(uuid4()))
    name: str
    tenant: Annotated[str, AfterValidator(is_valid_uuid)]
    created_at: float=Field(default_factory=lambda: datetime.now().timestamp())
    updated_at: float=Field(default_factory=lambda: datetime.now().timestamp())
    