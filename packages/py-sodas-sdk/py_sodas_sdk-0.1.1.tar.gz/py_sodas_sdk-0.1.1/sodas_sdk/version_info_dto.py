from typing import Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field, validator
import json
from datetime import timezone

from .core import auto_setters

class VersionInfoDTO(BaseModel):
    """Represents version information for a dataset."""
    
    id: str = Field(default="", alias="ID")
    version: str = Field(default="", alias="Version")
    version_notes: str = Field(default="", alias="VersionNotes")
    is_version_of: str = Field(default="", alias="IsVersionOf")
    previous_version_id: Optional[str] = Field(default=None, alias="PreviousVersionID")
    next_version_id: Optional[str] = Field(default=None, alias="NextVersionID")
    created: Optional[datetime] = Field(default=None, alias="Created")
    modified: Optional[datetime] = Field(default=None, alias="Modified")
    
    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True
        populate_by_name = True
        alias_generator = None
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%SZ") if v else None
        }

    @validator('created', 'modified', pre=True)
    def parse_datetime(cls, v: Any) -> Optional[datetime]:
        """Parse datetime strings and ensure UTC timezone."""
        if not v:
            return None
        if isinstance(v, str):
            try:
                dt = datetime.strptime(v, "%Y-%m-%dT%H:%M:%SZ")
                return dt.replace(tzinfo=timezone.utc)
            except ValueError:
                raise ValueError(f"Invalid datetime format: {v}")
        if isinstance(v, datetime):
            if v.tzinfo is None:
                return v.replace(tzinfo=timezone.utc)
            return v
        raise ValueError(f"Invalid datetime type: {type(v)}")

    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        """Convert to dictionary with proper field names."""
        kwargs.setdefault("exclude_none", True)
        kwargs.setdefault("exclude_unset", True)
        kwargs.setdefault("by_alias", True)
        
        data = super().dict(*args, **kwargs)
        
        # Handle datetime serialization
        for key, value in data.items():
            if isinstance(value, datetime):
                if value.tzinfo is None:
                    value = value.replace(tzinfo=timezone.utc)
                data[key] = value.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Remove empty collections
        return {k: v for k, v in data.items() if v not in (None, "", [], {})}

    def __str__(self) -> str:
        """Convert the model to a JSON string with proper handling of nested models."""
        def json_default(obj):
            if isinstance(obj, BaseModel):
                return obj.dict()
            if isinstance(obj, datetime):
                return obj.strftime("%Y-%m-%dT%H:%M:%SZ") if obj else None
            return str(obj)
        
        return json.dumps(self.dict(), indent=2, default=json_default)
