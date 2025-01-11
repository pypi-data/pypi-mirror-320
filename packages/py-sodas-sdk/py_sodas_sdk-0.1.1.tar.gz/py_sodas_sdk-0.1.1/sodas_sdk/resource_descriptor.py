from typing import Optional, List, Any, Dict, ClassVar
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field, validator
import json
import requests
import os
from pathlib import Path

from .core import auto_setters, handle_request_error
from .descriptor_template_artifact import DescriptorTemplateArtifact

class ResourceDescriptorRole(str, Enum):
    """Enum for resource descriptor roles."""
    VOCABULARY = "vocabulary"
    CONSTRAINT = "constraint"
    GUIDANCE = "guidance"
    SCHEMA = "schema"
    SPECIFICATION = "specification"
    VALIDATION = "validation"
    EXAMPLE = "example"
    MAPPING = "mapping"

class ResourceDescriptor(BaseModel):
    """Represents a resource descriptor."""
    
    # Class variables for API configuration
    API_URL: ClassVar[str] = ""
    LIST_API_URL: ClassVar[str] = ""
    GET_API_URL: ClassVar[str] = ""
    CREATE_API_URL: ClassVar[str] = ""
    UPDATE_API_URL: ClassVar[str] = ""
    DELETE_API_URL: ClassVar[str] = ""
    UPLOAD_API_URL: ClassVar[str] = ""
    
    id: str = Field(default="", alias="ID")
    iri: str = Field(default="", alias="IRI")
    profile_id: str = Field(default="", alias="ProfileID")
    is_inherited_from: str = Field(default="", alias="IsInheritedFrom")
    description: str = Field(default="", alias="Description")
    has_artifact: str = Field(default="", alias="HasArtifact")
    conforms_to: str = Field(default="", alias="ConformsTo")
    format: str = Field(default="", alias="Format")
    has_role: Optional[ResourceDescriptorRole] = Field(default=None, alias="HasRole")
    issued: datetime = Field(default_factory=datetime.now, alias="Issued")
    template_artifact: Optional[DescriptorTemplateArtifact] = Field(default=None, alias="TemplateArtifact")
    file: Optional[Any] = Field(default=None, alias="File")
    file_name: str = Field(default="", alias="FileName")
    file_size: int = Field(default=0, alias="FileSize")
    file_type: str = Field(default="", alias="FileType")
    file_content: Optional[Any] = Field(default=None, alias="FileContent")
    
    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True
        populate_by_name = True
        alias_generator = None
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%SZ") if v else None,
            BaseModel: lambda v: v.dict()
        }

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

    @classmethod
    def initialize_api_url(cls, url: str) -> None:
        """Initialize API URLs."""
        prefix = "api/v1/governance/open-reference-model"
        cls.API_URL = f"{url}/{prefix}/resource-descriptor"
        cls.LIST_API_URL = f"{cls.API_URL}/list"
        cls.GET_API_URL = f"{cls.API_URL}/get"
        cls.CREATE_API_URL = f"{cls.API_URL}/create"
        cls.UPDATE_API_URL = f"{cls.API_URL}/update"
        cls.DELETE_API_URL = f"{cls.API_URL}/remove"
        cls.UPLOAD_API_URL = f"{cls.API_URL}/upload"

    @classmethod
    def parse_from_data(cls, data: Dict[str, Any]) -> 'ResourceDescriptor':
        """Parse data into a ResourceDescriptor instance."""
        has_role = (ResourceDescriptorRole(data['has_role']) 
                   if data.get('has_role') else None)
        template_artifact = (DescriptorTemplateArtifact(**data['template_artifact'])
                           if data.get('template_artifact') else None)
        
        return cls(
            id=data.get('id', ''),
            iri=data.get('iri', ''),
            profile_id=data.get('profile_id', ''),
            is_inherited_from=data.get('is_inherited_from', ''),
            description=data.get('description', ''),
            has_artifact=data.get('has_artifact', ''),
            conforms_to=data.get('conforms_to', ''),
            format=data.get('format', ''),
            has_role=has_role,
            issued=datetime.fromisoformat(data['issued']) if data.get('issued') else datetime.now(),
            template_artifact=template_artifact
        )

    @classmethod
    def get(cls, descriptor_id: str) -> 'ResourceDescriptor':
        """Get a resource descriptor by ID."""
        try:
            response = requests.get(
                f"{cls.GET_API_URL}?id={descriptor_id}"
            )
            response.raise_for_status()
            return cls.parse_from_data(response.json())
        except requests.exceptions.RequestException as e:
            handle_request_error(e)

    def create(self) -> 'ResourceDescriptor':
        """Create a new resource descriptor."""
        if self.file_content:
            self.upload_file()
            
        try:
            response = requests.post(
                self.CREATE_API_URL,
                json=self.dict()
            )
            response.raise_for_status()
            return self.parse_from_data(response.json())
        except requests.exceptions.RequestException as e:
            handle_request_error(e)

    def update(self) -> 'ResourceDescriptor':
        """Update this resource descriptor."""
        if self.file_content:
            self.upload_file()
            
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
        """Delete this resource descriptor."""
        try:
            response = requests.delete(
                f"{self.DELETE_API_URL}/{self.id}"
            )
            response.raise_for_status()
            return response.json().get('message', 'Successfully deleted')
        except requests.exceptions.RequestException as e:
            handle_request_error(e)

    def set_file_for_browser(self, file: Any) -> None:
        """Set file information for browser environment."""
        self.file = file
        self.file_name = file.name
        self.file_size = file.size
        self.file_type = file.type
        self.file_content = file

    def set_file_for_node(self, file_path: str) -> None:
        """Set file information for Node.js environment."""
        if not os.path.exists(file_path):
            raise Exception(f"File not found: {file_path}")
            
        file_name = Path(file_path).name
        self.file_name = file_name
        self.file_size = os.path.getsize(file_path)
        self.file_type = ""  # Determine file type if needed
        with open(file_path, 'rb') as f:
            self.file_content = f.read()

    def upload_file(self) -> None:
        """Upload the file if content is set."""
        if not self.file_content:
            return
            
        files = {'file': (self.file_name, self.file_content)}
        
        try:
            response = requests.post(
                self.UPLOAD_API_URL,
                files=files
            )
            response.raise_for_status()
            self.has_artifact = response.json().get('has_artifact', '')
        except requests.exceptions.RequestException as e:
            handle_request_error(e)

    @classmethod
    def list_descriptors(cls) -> List['ResourceDescriptor']:
        """List all resource descriptors."""
        try:
            response = requests.get(
                cls.LIST_API_URL
            )
            response.raise_for_status()
            return [cls.parse_from_data(item) for item in response.json()]
        except requests.exceptions.RequestException as e:
            handle_request_error(e)
