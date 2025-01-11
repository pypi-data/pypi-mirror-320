from typing import Optional, List, Any, Dict, ClassVar
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field, validator
import json
from dataclasses import dataclass, field

from .core import auto_setters, MultiLanguageField
from .descriptor_template_artifact import (
    DescriptorTemplateArtifact,
    MappingPriority,
    MAPPING_SCHEMA_COLUMNS
)
from .resource_descriptor import ResourceDescriptor, ResourceDescriptorRole

class ProfileType(str, Enum):
    """Profile type enumeration."""
    Float = "Float"
    Int = "Int"
    Text = "Text"
    Boolean = "Boolean"
    Date = "Date"
    Blob = "Blob"
    JSON = "JSON"

class ProfileTarget(str, Enum):
    """Profile target enumeration."""
    RESOURCE = "resource"
    DISTRIBUTION = "distribution"

@dataclass
class ProfileSchema:
    """Schema for profile properties."""
    name: str
    type: ProfileType
    description: str
    required: bool
    additional_properties: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MappingSchema:
    """Schema for mapping between profiles."""
    source_field_name: str
    source_profile_iri: str
    target_field_name: str
    target_field_profile_iri: str
    mapping_priority: MappingPriority

@auto_setters
class Profile(BaseModel):
    """Represents a metadata profile."""
    
    # Class variables for API configuration
    API_URL: ClassVar[str] = ""
    LIST_API_URL: ClassVar[str] = ""
    GET_API_URL: ClassVar[str] = ""
    CREATE_API_URL: ClassVar[str] = ""
    UPDATE_API_URL: ClassVar[str] = ""
    DELETE_API_URL: ClassVar[str] = ""
    
    id: str = Field(default="", alias="ID")
    iri: str = Field(default="", alias="IRI")
    target: ProfileTarget = Field(default=ProfileTarget.DISTRIBUTION, alias="Target")
    is_profile_of: str = Field(default="", alias="IsProfileOf")
    keyword_ml: MultiLanguageField = Field(default_factory=dict, alias="KeywordML")
    name: str = Field(default="", alias="Name")
    description: str = Field(default="", alias="Description")
    has_token: str = Field(default="", alias="HasToken")
    issued: Optional[datetime] = Field(default=None, alias="Issued")
    resource_descriptors: List[ResourceDescriptor] = Field(default_factory=list, alias="ResourceDescriptors")
    
    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True
        populate_by_name = True
        alias_generator = None
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%SZ") if v else None,
            BaseModel: lambda v: v.dict()
        }

    @validator('issued', pre=True)
    def parse_datetime(cls, v: Any) -> Optional[datetime]:
        """Parse datetime strings and ensure UTC timezone."""
        if not v:
            return None
        if isinstance(v, str):
            try:
                dt = datetime.strptime(v, "%Y-%m-%dT%H:%M:%SZ")
                return dt.replace(tzinfo=datetime.timezone.utc)
            except ValueError:
                raise ValueError(f"Invalid datetime format: {v}")
        if isinstance(v, datetime):
            if v.tzinfo is None:
                return v.replace(tzinfo=datetime.timezone.utc)
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
                    value = value.replace(tzinfo=datetime.timezone.utc)
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

    def set_description(self, description: str, lang: str = 'ko') -> None:
        """Set description with language support."""
        if not self.description_ml:
            self.description_ml = {}
        self.description_ml[lang] = description

    def set_title(self, title: str, lang: str = 'ko') -> None:
        """Set title with language support."""
        if not self.title_ml:
            self.title_ml = {}
        self.title_ml[lang] = title

    @classmethod
    def initialize_api_url(cls, url: str) -> None:
        """Initialize API URLs."""
        prefix = "api/v1/governance/open-reference-model"
        cls.API_URL = f"{url}/{prefix}/profile"
        cls.LIST_API_URL = f"{cls.API_URL}/list"
        cls.GET_API_URL = f"{cls.API_URL}/get"
        cls.CREATE_API_URL = f"{cls.API_URL}/create"
        cls.UPDATE_API_URL = f"{cls.API_URL}/update"
        cls.DELETE_API_URL = f"{cls.API_URL}/remove"

    @classmethod
    async def get_full_profile_using_api(cls, iri: str) -> 'Profile':
        """Get a full profile by IRI."""
        params = {'iri': iri}
        profile = cls()
        
        try:
            response = await retry_request(lambda: requests.get(
                cls.GET_API_URL,
                params=params
            ))
            
            data = response.json()
            if data and data.get('id'):
                profile.id = data['id']
                profile.iri = data['iri']
                profile.target = data['target']
                profile.is_profile_of = data['isProfileOf']
                profile.keyword_ml = data['keywordMl']
                profile.name = data['name']
                profile.description = data['description']
                profile.has_token = data['hasToken']
                profile.issued = datetime.fromisoformat(data['issued']) if data.get('issued') else None
            
            await profile.initialize_resource_descriptors()
            return profile
        except Exception as e:
            handle_request_error(e)

    @classmethod
    async def delete_profile_using_api(cls, iri: str) -> str:
        """Delete a profile by IRI."""
        data = {'option': 'cascade'}
        
        try:
            response = await retry_request(lambda: requests.post(
                cls.DELETE_API_URL,
                json=data
            ))
            
            if response.json() and response.json().get('result') == 'success':
                return "Profile deletion successful"
            else:
                raise Exception("Profile deletion failed")
        except Exception as e:
            handle_request_error(e)

    @classmethod
    async def get_extending_full_profile_using_api(cls, iri: str) -> 'Profile':
        """Get an extending full profile by IRI."""
        try:
            extended_full_profile = await cls.get_full_profile_using_api(iri)
            extending_resource_descriptors = []
            
            for extended_resource_descriptor in extended_full_profile.resource_descriptors:
                extending_resource_descriptor = ResourceDescriptor(
                    is_inherited_from=extended_resource_descriptor.id,
                    description=extended_resource_descriptor.description,
                    has_artifact=extended_resource_descriptor.has_artifact,
                    conforms_to=extended_resource_descriptor.conforms_to,
                    format=extended_resource_descriptor.format,
                    has_role=extended_resource_descriptor.has_role
                )
                
                if extended_resource_descriptor.template_artifact:
                    extended_template_artifact = extended_resource_descriptor.template_artifact
                    extending_template_artifact = DescriptorTemplateArtifact(
                        name=extended_template_artifact.name,
                        columns=extended_template_artifact.columns,
                        value=extended_template_artifact.value
                    )
                    extending_resource_descriptor.set_template_artifact(extending_template_artifact)
                
                extending_resource_descriptors.append(extending_resource_descriptor)

            return cls(
                target=extended_full_profile.target,
                is_profile_of=extended_full_profile.iri,
                keyword_ml=extended_full_profile.keyword_ml,
                name=extended_full_profile.name,
                description=extended_full_profile.description,
                has_token=extended_full_profile.has_token,
                resource_descriptors=extending_resource_descriptors
            )
        except Exception as e:
            handle_request_error(e)

    @classmethod
    async def list_profile_using_api(
        cls,
        target: ProfileTarget,
        page_number: int = 1,
        page_size: int = 10,
        sort_order: str = "DESC"
    ) -> List['Profile']:
        """List profiles with pagination."""
        try:
            response = await retry_request(lambda: requests.get(
                cls.LIST_API_URL,
                params={
                    'target': target,
                    'offset': (page_number - 1) * page_size,
                    'limit': page_size,
                    'ordered': sort_order
                }
            ))
            
            if response.json() and isinstance(response.json().get('results'), list):
                return [
                    cls(
                        id=item.get('id'),
                        iri=item.get('iri'),
                        target=item.get('target'),
                        keyword_ml=item.get('keywordMl'),
                        name=item.get('name'),
                        description=item.get('description'),
                        has_token=item.get('hasToken'),
                        is_profile_of=item.get('isProfileOf'),
                        issued=datetime.fromisoformat(item.get('issued')) if item.get('issued') else None
                    )
                    for item in response.json()['results']
                ]
            else:
                raise Exception("Unexpected response format")
        except Exception as e:
            handle_request_error(e)

    @classmethod
    async def list_full_profile_using_api(
        cls,
        target: ProfileTarget,
        page_number: int = 1,
        page_size: int = 10,
        sort_order: str = "DESC"
    ) -> List['Profile']:
        """List full profiles with pagination."""
        try:
            profiles = await cls.list_profile_using_api(target, page_number, page_size, sort_order)
            full_profiles = []
            
            for profile in profiles:
                await profile.initialize_resource_descriptors()
                full_profiles.append(profile)
            
            return full_profiles
        except Exception as e:
            handle_request_error(e)

    async def create_basic_profile_using_api(self) -> 'Profile':
        """Create a basic profile."""
        data = {
            'target': self.target,
            'isProfileOf': self.is_profile_of,
            'keywordMl': self.keyword_ml,
            'name': self.name,
            'description': self.description,
            'hasToken': self.has_token
        }
        
        try:
            response = await retry_request(lambda: requests.post(
                self.CREATE_API_URL,
                json=data
            ))
            
            if response.json() and response.json().get('id'):
                self.id = response.json()['id']
                self.iri = response.json()['iri']
                return self
            else:
                raise Exception("ID not returned in the response")
        except Exception as e:
            handle_request_error(e)

    async def create_full_profile_using_api(self) -> 'Profile':
        """Create a full profile."""
        await self.create_basic_profile_using_api()
        
        for resource_descriptor in self.resource_descriptors:
            resource_descriptor.set_profile_id(self.id)
            await resource_descriptor.set_template_artifact_using_api()
            await resource_descriptor.create_resource_descriptor_using_api()
        
        return self

    async def update_basic_profile_using_api(self) -> 'Profile':
        """Update basic profile information."""
        data = {
            'id': self.id,
            'target': self.target,
            'isProfileOf': self.is_profile_of,
            'keywordMl': self.keyword_ml,
            'name': self.name,
            'description': self.description,
            'hasToken': self.has_token
        }
        
        # Save current template artifacts to prevent axios side effects
        current_template_artifacts_data = [
            descriptor.template_artifact.parse_to_data() if descriptor.template_artifact else None
            for descriptor in self.resource_descriptors
        ]
        
        try:
            response = await retry_request(lambda: requests.post(
                self.UPDATE_API_URL,
                json=data
            ))
            
            # Restore template artifacts
            for descriptor, template_data in zip(self.resource_descriptors, current_template_artifacts_data):
                if template_data:
                    descriptor.template_artifact = DescriptorTemplateArtifact.parse_from_data(template_data)
            
            if response.json() and response.json().get('id'):
                return self
            else:
                raise Exception("ID not returned in the response")
        except Exception as e:
            handle_request_error(e)

    async def update_full_profile_using_api(self) -> None:
        """Update full profile information."""
        await self.update_basic_profile_using_api()
        
        current_template_artifacts_data = [
            descriptor.template_artifact.parse_to_data() if descriptor.template_artifact else None
            for descriptor in self.resource_descriptors
        ]
        
        for resource_descriptor in self.resource_descriptors:
            if resource_descriptor.profile_id:
                await resource_descriptor.update_resource_descriptor_using_api()
            else:
                resource_descriptor.set_profile_id(self.id)
                await resource_descriptor.set_template_artifact_using_api()
                await resource_descriptor.create_resource_descriptor_using_api()
            
            # Restore template artifacts
            for descriptor, template_data in zip(self.resource_descriptors, current_template_artifacts_data):
                if template_data:
                    descriptor.template_artifact = DescriptorTemplateArtifact.parse_from_data(template_data)

    async def extend_full_profile_api_call(self, extending_profile: 'Profile') -> None:
        """Extend a full profile."""
        pass

    async def initialize_resource_descriptors(self) -> None:
        """Initialize resource descriptors."""
        self.resource_descriptors = await ResourceDescriptor.list_resource_descriptor_using_api(self.id)

    def get_template_columns(self, role: ResourceDescriptorRole) -> Optional[Dict[str, Any]]:
        """Get template columns for a specific role."""
        return None

    def get_template_value(self, role: ResourceDescriptorRole) -> Optional[List[Dict[str, Any]]]:
        """Get template value for a specific role."""
        target_resource_descriptor = self.get_resource_descriptor_of(role)
        target_template = target_resource_descriptor.template_artifact if target_resource_descriptor else None
        
        if target_template:
            return target_template.value
        return None

    def get_resource_descriptors(self) -> List[ResourceDescriptor]:
        """Get all resource descriptors."""
        return self.resource_descriptors

    def get_resource_descriptor(self, index: int) -> ResourceDescriptor:
        """Get a resource descriptor by index."""
        if index < 0 or index >= len(self.resource_descriptors):
            raise IndexError("Index out of bounds")
        return self.resource_descriptors[index]

    def set_resource_descriptor(self, index: int, descriptor: ResourceDescriptor) -> None:
        """Set a resource descriptor at a specific index."""
        if index < 0:
            raise ValueError("Index cannot be negative")
        
        if index >= len(self.resource_descriptors):
            self.resource_descriptors.extend([None] * (index - len(self.resource_descriptors) + 1))
        
        self.resource_descriptors[index] = descriptor

    def add_resource_descriptor(self, resource_descriptor: ResourceDescriptor) -> None:
        """Add a resource descriptor."""
        if not isinstance(resource_descriptor, ResourceDescriptor):
            raise TypeError("The provided object is not an instance of ResourceDescriptor")
        self.resource_descriptors.append(resource_descriptor)

    def create_resource_descriptor(self) -> ResourceDescriptor:
        """Create and add a new resource descriptor."""
        new_resource_descriptor = ResourceDescriptor()
        self.resource_descriptors.append(new_resource_descriptor)
        return new_resource_descriptor

    def remove_resource_descriptor(self, resource_descriptor: ResourceDescriptor) -> None:
        """Remove a resource descriptor."""
        try:
            self.resource_descriptors.remove(resource_descriptor)
        except ValueError:
            raise ValueError("ResourceDescriptor not found in the list")

    def add_template(
        self,
        name: str,
        description: str,
        role: ResourceDescriptorRole,
        columns: Dict[str, str],
        value: List[Dict[str, Any]]
    ) -> None:
        """Add a template to the profile."""
        resource_descriptor = self.create_resource_descriptor()
        resource_descriptor.set_description(description)
        resource_descriptor.set_has_role(role)
        template_artifact = resource_descriptor.create_template_artifact()
        template_artifact.set_name(name)
        template_artifact.set_columns(columns)
        template_artifact.set_value(value)

    def add_schema_template(
        self,
        name: str,
        description: str,
        columns: Dict[str, str],
        value: List[ProfileSchema]
    ) -> None:
        """Add a schema template."""
        self.add_template(
            name,
            description,
            ResourceDescriptorRole.SCHEMA,
            columns,
            value
        )

    def add_mapping_template(
        self,
        name: str,
        description: str,
        value: List[MappingSchema]
    ) -> None:
        """Add a mapping template."""
        self.add_template(
            name,
            description,
            ResourceDescriptorRole.MAPPING,
            MAPPING_SCHEMA_COLUMNS,
            value
        )

    def get_resource_descriptor_of(self, role: ResourceDescriptorRole) -> Optional[ResourceDescriptor]:
        """Get a resource descriptor by role."""
        return next(
            (descriptor for descriptor in self.resource_descriptors if descriptor.has_role == role),
            None
        )
