from typing import Optional, List, Any, Dict, ClassVar
from datetime import datetime, timezone
import requests
from pathlib import Path
from pydantic import BaseModel, Field, validator
from functools import lru_cache
import json
import os


from .core import MultiLanguageField, MultiLanguageKeywords, handle_request_error, auto_setters
from .distribution import Distribution
from .version_info_dto import VersionInfoDTO

@auto_setters
class DatasetDTO(BaseModel):
    """Represents a Dataset Data Transfer Object (DTO)."""
    
    # Class variables for API configuration
    API_URL: ClassVar[str] = ""
    LIST_URL: ClassVar[str] = ""
    
    # Required fields with defaults
    id: str = Field(default="", alias="ID")
    dataset_id: str = Field(default="", alias="DatasetID")
    iri: str = Field(default="", alias="IRI")
    thumbnail_path: str = Field(default="", alias="ThumbnailPath")
    access_rights: str = Field(default="", alias="AccessRights")
    status: str = Field(default="", alias="Status")
    version_notes: str = Field(default="", alias="VersionNotes")
    version: str = Field(default="", alias="Version")
    is_version_of: str = Field(default="", alias="IsVersionOf")
    previous_version_id: Optional[str] = Field(default=None, alias="PreviousVersionID")
    next_version_id: Optional[str] = Field(default=None, alias="NextVersionID")
    contact_point: str = Field(default="", alias="ContactPoint")
    keyword_ml: MultiLanguageKeywords = Field(default_factory=dict, alias="KeywordML")
    landing_page: str = Field(default="", alias="LandingPage")
    theme: str = Field(default="", alias="Theme")
    conforms_to: str = Field(default="", alias="ConformsTo")
    creator: str = Field(default="", alias="Creator")
    description_ml: MultiLanguageField = Field(default_factory=dict, alias="DescriptionML")
    identifier: str = Field(default="", alias="Identifier")
    is_referenced_by: List[Any] = Field(default_factory=list, alias="IsReferencedBy")
    issued: Optional[datetime] = Field(default=None, alias="Issued")
    language: List[Any] = Field(default_factory=list, alias="Language")
    license: str = Field(default="", alias="License")
    modified: Optional[datetime] = Field(default=None, alias="Modified")
    publisher: str = Field(default="", alias="Publisher")
    rights: List[Any] = Field(default_factory=list, alias="Rights")
    title_ml: MultiLanguageField = Field(default_factory=dict, alias="TitleML")
    type: str = Field(default="", alias="Type")
    has_policy: List[Any] = Field(default_factory=list, alias="HasPolicy")
    issuer_id: str = Field(default="", alias="IssuerID")
    profile_iri: str = Field(default="", alias="ProfileIRI")
    frequency: str = Field(default="", alias="Frequency")
    spatial_resolution_in_meters: Optional[float] = Field(default=None, alias="SpatialResolutionInMeters")
    temporal_resolution: str = Field(default="", alias="TemporalResolution")
    distribution: List[Distribution] = Field(default_factory=list, alias="Distribution")
    spatial: str = Field(default="", alias="Spatial")
    temporal: str = Field(default="", alias="Temporal")
    was_generated_by: str = Field(default="", alias="WasGeneratedBy")
    instance_value: Any = Field(default=None, alias="InstanceValue")
    datahub_id: str = Field(default="", alias="DatahubID")
    version_info: List[VersionInfoDTO] = Field(default_factory=list, alias="VersionInfo")
    
    # Thumbnail specific fields
    thumbnail_name: Optional[str] = Field(default=None, alias="ThumbnailName")
    thumbnail_size: Optional[int] = Field(default=None, alias="ThumbnailSize")
    thumbnail_type: Optional[str] = Field(default=None, alias="ThumbnailType")
    thumbnail_content: Optional[Any] = Field(default=None, exclude=True)  # Exclude from serialization

    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True
        populate_by_name = True
        alias_generator = None  # Disable automatic alias generation since we're using explicit aliases
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%SZ") if v else None,
            BaseModel: lambda v: v.dict()  # This will handle nested Pydantic models
        }

    @classmethod
    def initialize_api_url(cls, api_url: str) -> None:
        """Initialize the API URL for the Dataset DTO."""
        cls.API_URL = f"{api_url}/dataset"
        cls.LIST_URL = f"{cls.API_URL}/list"

    @classmethod
    @lru_cache(maxsize=100)  # Cache frequently accessed datasets
    def get(cls, dataset_id: str) -> 'DatasetDTO':
        """Retrieve a dataset by its ID."""
        try:
            response = requests.get(f"{cls.API_URL}/datasets/{dataset_id}")
            response.raise_for_status()
            return cls.parse_obj(response.json())
        except requests.exceptions.RequestException as e:
            handle_request_error(e)

    def upload_thumbnail(self) -> None:
        """Upload a thumbnail for the dataset."""
        if not self.thumbnail_content:
            return
            
        try:
            files = {'file': (self.thumbnail_name, self.thumbnail_content)}
            response = requests.post(Distribution.UPLOAD_API_URL, files=files)
            response.raise_for_status()
            
            object_key = response.json()['objectKey']
            self.thumbnail_path = f"{Distribution.DOWNLOAD_API_URL}/{object_key}"
        except requests.exceptions.RequestException as e:
            handle_request_error(e)

    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        """Convert the DTO to a dictionary representation with proper field names."""
        # Exclude null values and empty collections by default
        kwargs.setdefault("exclude_none", True)
        kwargs.setdefault("exclude_unset", True)
        kwargs.setdefault("by_alias", True)  # Ensure PascalCase field names
        
        data = super().dict(*args, **kwargs)
        
        # Handle datetime serialization
        for key, value in data.items():
            if isinstance(value, datetime):
                # Ensure UTC timezone and format to ISO
                if value.tzinfo is None:
                    value = value.replace(tzinfo=timezone.utc)
                data[key] = value.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Ensure list fields are never None
        for field in ['IsReferencedBy', 'HasPolicy']:
            if field not in data or data[field] is None:
                data[field] = []
        
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
    def list_datasets(cls, page_number: int = 1, page_size: int = 10, sort_order: str = "DESC") -> List['DatasetDTO']:
        """Fetches a list of DatasetDTO objects from the API."""
        params = {
            "pageNumber": page_number,
            "pageSize": page_size,
            "sortOrder": sort_order,
        }

        try:
            response = requests.get(cls.LIST_URL, params=params)
            response.raise_for_status()

            if response.json() and isinstance(response.json(), list):
                return [cls.parse_obj(item) for item in response.json()]
            raise ValueError("Unexpected response format")
        except requests.exceptions.RequestException as e:
            handle_request_error(e)

    @classmethod
    def get_full_dataset(cls, dataset_id: str) -> 'DatasetDTO':
        """Fetches a full DatasetDTO object by ID from the API."""
        try:
            response = requests.get(f"{cls.API_URL}/{dataset_id}")
            response.raise_for_status()

            if response.json():
                data = response.json()
                data['distribution'] = [Distribution.parse_obj(dist) for dist in data.get('Distribution', [])]
                return cls.parse_obj(data)
            raise ValueError("Invalid dataset data received")
        except requests.exceptions.RequestException as e:
            handle_request_error(e)

    def create_full(self) -> 'DatasetDTO':
        """Creates a DatasetDTO and its associated distributions via API."""
        try:
            dataset = self.create_basic()
            for dist in self.distribution:
                dist.set_is_distribution_of(dataset.dataset_id)
                created_distribution = dist.create()
                dataset.distribution.append(created_distribution)
            return dataset
        except requests.exceptions.RequestException as e:
            raise e

    def create_basic(self) -> 'DatasetDTO':
        """Creates a new DatasetDTO without Distributions via API."""
        try:
            # Get dictionary representation with datetime handling
            data = self.dict(exclude={'thumbnail_content'})
            
            response = requests.post(
                self.API_URL,
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            
            dataset = self.parse_obj(response.json())

            if self.thumbnail_content:
                dataset.thumbnail_content = self.thumbnail_content
                dataset.thumbnail_name = self.thumbnail_name
                dataset.upload_thumbnail()
            
            return dataset
        except requests.exceptions.RequestException as e:
            handle_request_error(e)

    # Simplified setters using Pydantic's validation
    def set_thumbnail_for_browser(self, file: Any) -> None:
        self.thumbnail_content = file
        self.thumbnail_name = file.name
        self.thumbnail_size = file.size
        self.thumbnail_type = file.type

    def set_thumbnail_for_node(self, file_path: str) -> None:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        path = Path(file_path)
        self.thumbnail_name = path.name
        self.thumbnail_size = path.stat().st_size
        self.thumbnail_type = ""
        self.thumbnail_content = path.read_bytes()

    # Simplified getters and setters using properties
    @property
    def distributions(self) -> List[Distribution]:
        """Get all distributions."""
        return self.distribution

    def get_distribution_by_index(self, index: int) -> Distribution:
        """Get a specific distribution by index."""
        if 0 <= index < len(self.distribution):
            return self.distribution[index]
        raise IndexError("Distribution index out of range")

    def add_distribution(self, dist: Distribution) -> None:
        """Add a distribution."""
        if not isinstance(dist, Distribution):
            raise TypeError("Argument must be a Distribution instance")
        self.distribution.append(dist)

    def create_distribution(self) -> Distribution:
        """Create and add a new distribution."""
        distribution = Distribution()
        self.distribution.append(distribution)
        return distribution

    def remove_distribution(self, distribution: Distribution) -> None:
        """Remove a distribution."""
        try:
            self.distribution.remove(distribution)
        except ValueError:
            raise ValueError("Distribution not found in list")

    # Helper methods for multilanguage fields
    def set_multilang_field(self, field: str, value: str, lang: str = 'ko') -> None:
        """Set a multilanguage field value."""
        if hasattr(self, field):
            setattr(self, field, {lang: value})

    def set_keyword(self, keyword: List[str], lang: str = 'ko') -> None:
        """Set keywords with language support."""
        self.keyword_ml = {lang: keyword}

    def set_description(self, description: str, lang: str = 'ko') -> None:
        """Set description with language support."""
        self.set_multilang_field('description_ml', description, lang)

    def set_title(self, title: str, lang: str = 'ko') -> None:
        """Set title with language support."""
        self.set_multilang_field('title_ml', title, lang)

    def set_instance_value(self, field: str, value: Any) -> None:
        """Set a field in the instance value dictionary."""
        if self.instance_value is None:
            self.instance_value = {}
        self.instance_value[field] = value

    def get_version_info(self) -> List[VersionInfoDTO]:
        """Get all version information."""
        return self.version_info

    def get_version_info_by_index(self, index: int) -> Optional[VersionInfoDTO]:
        """Get version information by index."""
        if 0 <= index < len(self.version_info):
            return self.version_info[index]
        return None

    # Validators
    @validator('keyword_ml', 'description_ml', 'title_ml', pre=True)
    def validate_multilang_fields(cls, v):
        """Validate multilanguage fields have proper structure."""
        if not v:
            return {}
        if not isinstance(v, dict):
            raise ValueError("Multilanguage field must be a dictionary")
        return v

    @validator('distribution', pre=True)
    def validate_distribution(cls, v):
        """Validate distribution list."""
        if not v:
            return []
        if not isinstance(v, list):
            raise ValueError("Distribution must be a list")
        return v

    @validator('spatial_resolution_in_meters')
    def validate_spatial_resolution(cls, v: Optional[float]) -> Optional[float]:
        """Validate spatial resolution is non-negative."""
        if v is not None and v < 0:
            raise ValueError("Spatial resolution cannot be negative")
        return v

    @validator('issued', 'modified', pre=True)
    def parse_datetime(cls, v: Any) -> Optional[datetime]:
        """Parse datetime strings and ensure UTC timezone."""
        if not v:
            return None
        if isinstance(v, str):
            try:
                # Parse ISO format string to datetime
                dt = datetime.strptime(v, "%Y-%m-%dT%H:%M:%SZ")
                return dt.replace(tzinfo=timezone.utc)
            except ValueError:
                raise ValueError(f"Invalid datetime format: {v}")
        if isinstance(v, datetime):
            # Ensure datetime is UTC
            if v.tzinfo is None:
                return v.replace(tzinfo=timezone.utc)
            return v
        raise ValueError(f"Invalid datetime type: {type(v)}")

    @validator('issued', 'modified')
    def validate_dates(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Validate dates are not in the future."""
        if v is not None:
            now = datetime.now(timezone.utc)
            if v > now:
                raise ValueError("Date cannot be in the future")
        return v

    @validator('is_referenced_by', 'has_policy', pre=True)
    def validate_list_fields(cls, v: Any) -> List[Any]:
        """Ensure list fields are never None."""
        if v is None:
            return []
        if not isinstance(v, list):
            raise ValueError("Field must be a list")
        return v

    @validator('previous_version_id', 'next_version_id', pre=True)
    def validate_version_ids(cls, v: Any) -> Optional[str]:
        """Handle version IDs that can be None."""
        if v is None:
            return ""
        return v

    @classmethod
    def from_api_response(cls, response_data: Dict[str, Any]) -> 'DatasetDTO':
        """Create a DatasetDTO instance from API response data with proper error handling."""
        try:
            if not response_data:
                raise ValueError("Empty response data")
                
            # Handle distribution data separately
            distribution_data = response_data.pop('Distribution', [])
            if distribution_data:
                response_data['distribution'] = [
                    Distribution.parse_obj(dist) for dist in distribution_data
                ]
                
            # Handle version info data
            version_info_data = response_data.pop('VersionInfo', [])
            if version_info_data:
                response_data['version_info'] = [
                    VersionInfoDTO.parse_obj(info) for info in version_info_data
                ]
                
            return cls.parse_obj(response_data)
        except Exception as e:
            raise ValueError(f"Failed to parse API response: {str(e)}")

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update instance fields from a dictionary."""
        for field, value in data.items():
            if hasattr(self, field):
                setattr(self, field, value)
