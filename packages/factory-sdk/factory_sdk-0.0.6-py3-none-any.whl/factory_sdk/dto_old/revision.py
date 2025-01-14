from pydantic import BaseModel,Field
from uuid import uuid4
from datetime import datetime
from factory_sdk.dto_old.state import FactoryState
from typing import Optional, Dict

class Revision(BaseModel):
    id: str=Field(default_factory=lambda: str(uuid4()))
    state: FactoryState=Field(default=FactoryState.INITIALIZED)
    created_at: float=Field(default_factory=lambda: datetime.now().timestamp())
    updated_at: float=Field(default_factory=lambda: datetime.now().timestamp())
    fingerprints: Dict=Field(default={})