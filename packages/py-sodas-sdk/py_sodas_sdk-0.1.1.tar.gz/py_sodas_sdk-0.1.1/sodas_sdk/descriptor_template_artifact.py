from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field, validator
import requests
import json

from .core import handle_request_error

class MappingPriority(str, Enum):
    """Enum for mapping priorities."""
    MANDATORY = "mandatory"
    OPTIONAL = "optional"

# Schema column definitions
MAPPING_SCHEMA_COLUMNS = {
    "sourceFieldName": "필드명",
    "sourceProfileIRI": "프로파일",
    "targetFieldName": "타겟 필드명",
    "targetFieldProfileIRI": "타겟 프로파일",
    "mappingPriority": "매핑 우선순위",
}

BASIC_PROFILE_SCHEMA_COLUMNS = {
    "name": "이름",
    "description": "설명",
    "type": "타입",
    "required": "팔수",
}

DISTRIBUTION_PROFILE_SCHEMA_COLUMNS = {
    "name": "이름",
    "description": "설명",
    "type": "타입",
    "regex": "정규식",
    "example": "예제",
    "required": "팔수",
}

RESOURCE_PROFILE_SCHEMA_COLUMNS = {
    "name": "이름",
    "description": "설명",
    "type": "타입",
    "vocabulary": "어휘",
    "term": "용어",
    "required": "팔수",
}

class DescriptorTemplateArtifact(BaseModel):
    """Represents a descriptor template artifact."""
    
    # Class variables for API configuration
    API_URL: str = Field(default="", init=False)
    LIST_API_URL: str = Field(default="", init=False)
    GET_API_URL: str = Field(default="", init=False)
    CREATE_API_URL: str = Field(default="", init=False)
    UPDATE_API_URL: str = Field(default="", init=False)
    DELETE_API_URL: str = Field(default="", init=False)
    
    # Instance fields
    id: str = Field(default="", alias="ID")
    iri: str = Field(default="", alias="IRI")
    name: str = Field(default="", alias="Name")
    conforms_to: str = Field(default="", alias="Conforms To")
    columns: Dict[str, str] = Field(default_factory=dict, alias="Columns")
    value: List[Dict[str, Any]] = Field(default_factory=list, alias="Value")
    issued: datetime = Field(default_factory=datetime.now, alias="Issued")

    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True
        populate_by_name = True
        alias_generator = None
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%SZ") if v else None,
            BaseModel: lambda v: v.dict()
        }

    @validator('value')
    def validate_value(cls, v, values):
        """Validate that all objects in value contain the required columns."""
        if 'columns' in values:
            column_keys = set(values['columns'].keys())
            if not all(set(item.keys()).issubset(column_keys) for item in v):
                raise ValueError("Each object in 'value' must contain the keys specified in 'columns'.")
        return v

    @classmethod
    def initialize_api_url(cls, api_url: str) -> None:
        """Initialize API URLs."""
        cls.API_URL = api_url
        cls.LIST_API_URL = f"{api_url}/descriptorTemplateArtifacts"
        cls.GET_API_URL = f"{api_url}/descriptorTemplateArtifacts"
        cls.CREATE_API_URL = f"{api_url}/descriptorTemplateArtifacts"
        cls.UPDATE_API_URL = f"{api_url}/descriptorTemplateArtifacts"
        cls.DELETE_API_URL = f"{api_url}/descriptorTemplateArtifacts"

    @classmethod
    def parse_from_data(cls, data: Dict[str, Any]) -> 'DescriptorTemplateArtifact':
        """Parse data into a DescriptorTemplateArtifact instance."""
        return cls(
            id=data.get('id', ''),
            iri=data.get('iri', ''),
            name=data.get('name', ''),
            conforms_to=data.get('conforms_to', ''),
            columns=data.get('columns', {}),
            value=data.get('value', []),
            issued=datetime.fromisoformat(data['issued']) if data.get('issued') else datetime.now()
        )

    @classmethod
    def get(cls, artifact_id: str) -> 'DescriptorTemplateArtifact':
        """Retrieve a descriptor template artifact by ID."""
        try:
            response = requests.get(f"{cls.GET_API_URL}/{artifact_id}")
            response.raise_for_status()
            return cls.parse_from_data(response.json())
        except requests.exceptions.RequestException as e:
            handle_request_error(e)

    @classmethod
    def list_artifacts(cls) -> List['DescriptorTemplateArtifact']:
        """List all descriptor template artifacts."""
        try:
            response = requests.get(cls.LIST_API_URL)
            response.raise_for_status()
            return [cls.parse_from_data(item) for item in response.json()]
        except requests.exceptions.RequestException as e:
            handle_request_error(e)

    def create(self) -> 'DescriptorTemplateArtifact':
        """Create a new descriptor template artifact."""
        try:
            response = requests.post(
                self.CREATE_API_URL,
                json=self.dict()
            )
            response.raise_for_status()
            return self.parse_from_data(response.json())
        except requests.exceptions.RequestException as e:
            handle_request_error(e)

    def update(self) -> 'DescriptorTemplateArtifact':
        """Update the current descriptor template artifact."""
        try:
            response = requests.put(
                f"{self.UPDATE_API_URL}/{self.id}",
                json=self.dict()
            )
            response.raise_for_status()
            return self.parse_from_data(response.json())
        except requests.exceptions.RequestException as e:
            handle_request_error(e)

    def delete(self) -> str:
        """Delete the current descriptor template artifact."""
        try:
            response = requests.delete(f"{self.DELETE_API_URL}/{self.id}")
            response.raise_for_status()
            return response.json().get('message', 'Successfully deleted')
        except requests.exceptions.RequestException as e:
            handle_request_error(e)

    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        """Convert to dictionary with proper field names."""
        kwargs.setdefault("exclude_none", True)
        kwargs.setdefault("exclude_unset", True)
        kwargs.setdefault("by_alias", True)
        
        data = super().dict(*args, **kwargs)
        
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
