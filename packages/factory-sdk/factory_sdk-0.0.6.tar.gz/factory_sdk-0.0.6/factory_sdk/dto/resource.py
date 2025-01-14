from pydantic import BaseModel,Field
from enum import Enum
from uuid import uuid4
from datetime import datetime,timezone
from typing import Optional, Dict, List
from abc import ABC,abstractmethod
from uuid import UUID
from pydantic import AfterValidator
from typing import Annotated



def is_valid_uuid(uuid_to_test, version=4):
    """
    Check if uuid_to_test is a valid UUID.
    
     Parameters
    ----------
    uuid_to_test : str
    version : {1, 2, 3, 4}
    
     Returns uuid_to_test is a valid UUID.
    -------
    
     Examples
    --------
    >>> is_valid_uuid('c9bf9e57-1685-4c89-bafb-ff5af830be8a')
    Correct
    >>> is_valid_uuid('c9bf9e58')
    Exception: Invalid UUID: c9bf9e58
    """
    
    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        raise ValueError(f"Invalid UUID: {uuid_to_test}")
    if not str(uuid_obj) == uuid_to_test:
        raise ValueError(f"Invalid UUID: {uuid_to_test}")
    return uuid_to_test

def is_valid_uuid_optional(uuid_to_test, version=4):
    if uuid_to_test is None:
        return None
    return is_valid_uuid(uuid_to_test,version)

class FactoryMetaState(str,Enum):
    INITIALIZED="initialized"
    READY="ready"
    READY_FOR_TRAINING="ready_for_training"
    FAILED="failed"

class FactoryRevisionState(str,Enum):
    INITIALIZED="initialized"
    PROCESSING="processing"
    READY_FOR_TRAINING="ready_for_training"
    READY="ready"
    FAILED="failed"

class FactoryResourceObject(BaseModel):
    id: str=Field(default_factory=lambda: str(uuid4()))
    name: str
    project: Annotated[Optional[str],AfterValidator(is_valid_uuid_optional)]=Field(default=None)
    tenant: Annotated[str,AfterValidator(is_valid_uuid)]
    created_at: float=Field(default_factory=lambda: datetime.now(
        timezone.utc).timestamp())
    updated_at: float=Field(default_factory=lambda: datetime.now(
        timezone.utc).timestamp())
    
    def update_timestamp(self):
        self.updated_at = datetime.now(timezone.utc).timestamp()

class FactoryResourceMeta(FactoryResourceObject):
    state: FactoryMetaState=Field(default=FactoryMetaState.INITIALIZED)
    last_revision: Annotated[Optional[str], AfterValidator(is_valid_uuid_optional)]=Field(default=None)

class FactoryResourceInitData(BaseModel):
    name: str

    @abstractmethod
    def create_meta(self,tenant_name:str,project_name:Optional[str]=None)->FactoryResourceMeta:
        raise NotImplementedError()

class FactoryResourceRevision(FactoryResourceObject):
    state: FactoryRevisionState=Field(default=FactoryRevisionState.INITIALIZED)
    meta: Annotated[str,AfterValidator(is_valid_uuid)]
    fingerprint: Optional[str]=Field(default=None)
    ext_fingerprints: Dict[str,str]=Field(default={})
    error_message: Optional[str]=Field(default=None)
    

class FactoryRevisionRef(BaseModel):
    object_id: Annotated[str,AfterValidator(is_valid_uuid)]
    revision_id: Annotated[str,AfterValidator(is_valid_uuid)]

class FileUploadRef(BaseModel):
    upload_id: str

class CompleteUploadRequest(BaseModel):
    fingerprint: str   