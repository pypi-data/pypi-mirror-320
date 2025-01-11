from typing import Optional, List, Any, Dict
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field, validator
import json
from .core import auto_setters, MultiLanguageField
from .resource_descriptor import ResourceDescriptorRole

class TemplateExtras(BaseModel):
    """Represents template extra fields."""
    key: str = Field(default="", alias="Key")
    value: str = Field(default="", alias="Value")
    required: bool = Field(default=False, alias="Required")

@auto_setters
class Template(BaseModel):
    """Represents a template for resource descriptors."""
    
    id: str = Field(default="", alias="ID")
    role: Optional[ResourceDescriptorRole] = Field(default=None, alias="Role")
    description: str = Field(default="", alias="Description")
    name: str = Field(default="", alias="Name")
    extras: Optional[List[TemplateExtras]] = Field(default=None, alias="Extras")
    
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

    @classmethod
    async def list_template_using_api(
        cls,
        role: Optional[ResourceDescriptorRole] = None
    ) -> List['Template']:
        """List all templates with optional role filter.
        
        Args:
            role: Optional role filter
            
        Returns:
            List[Template]: List of templates
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        try:
            params = {'role': role} if role else None
            response = await retry_request(lambda: requests.get(
                cls.LIST_API_URL,
                params=params
            ))
            
            if response.json() and isinstance(response.json().get('results'), list):
                templates = []
                for item in response.json()['results']:
                    template = cls(
                        ID=item.get('id', ''),
                        Role=item.get('role'),
                        Description=item.get('description', ''),
                        Name=item.get('name', ''),
                        Extras=item.get('extras')
                    )
                    templates.append(template)
                return templates
            else:
                raise Exception("Unexpected response format")
        except requests.exceptions.RequestException as e:
            handle_request_error(e)
            return []

    @classmethod
    async def get_template_using_api(cls, template_id: str) -> 'Template':
        """Get a template by ID.
        
        Args:
            template_id: ID of the template to retrieve
            
        Returns:
            Template: Retrieved template
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        try:
            response = await retry_request(lambda: requests.get(
                f"{cls.GET_API_URL}?id={template_id}"
            ))
            
            data = response.json()
            if data and data.get('id'):
                return cls(
                    ID=data.get('id', ''),
                    Role=data.get('role'),
                    Description=data.get('description', ''),
                    Name=data.get('name', ''),
                    Extras=data.get('extras')
                )
            else:
                raise Exception("Unexpected response format: ID not found")
        except requests.exceptions.RequestException as e:
            handle_request_error(e)

    async def create_template_using_api(self) -> Optional['Template']:
        """Create a new template.
        
        Returns:
            Optional[Template]: Created template or None if creation fails
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        data = {
            'role': self.Role,
            'description': self.Description,
            'name': self.Name,
            'extras': self.Extras
        }
        
        try:
            response = await retry_request(lambda: requests.post(
                self.CREATE_API_URL,
                json=data
            ))
            
            data = response.json()
            if data and data.get('id'):
                self.ID = data['id']
                return self
            else:
                raise Exception("ID not returned in the response")
        except requests.exceptions.RequestException as e:
            handle_request_error(e)

    async def update_template_using_api(self) -> Optional['Template']:
        """Update this template.
        
        Returns:
            Optional[Template]: Updated template or None if update fails
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        data = {
            'id': self.ID,
            'role': self.Role,
            'description': self.Description,
            'name': self.Name,
            'extras': self.Extras
        }
        
        try:
            response = await retry_request(lambda: requests.post(
                self.UPDATE_API_URL,
                json=data
            ))
            
            data = response.json()
            if data and data.get('id'):
                self.ID = data['id']
                return self
            else:
                raise Exception("ID not returned in the response")
        except requests.exceptions.RequestException as e:
            handle_request_error(e)

    @classmethod
    async def delete_template_using_api(cls, template_id: str) -> str:
        """Delete a template by ID.
        
        Args:
            template_id: ID of the template to delete
            
        Returns:
            str: Success message
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        data = {'id': template_id}
        
        try:
            response = await retry_request(lambda: requests.post(
                cls.DELETE_API_URL,
                json=data
            ))
            
            if response.status_code == 204:
                return "Template deletion successful"
            else:
                raise Exception("Template deletion failed")
        except requests.exceptions.RequestException as e:
            handle_request_error(e)
