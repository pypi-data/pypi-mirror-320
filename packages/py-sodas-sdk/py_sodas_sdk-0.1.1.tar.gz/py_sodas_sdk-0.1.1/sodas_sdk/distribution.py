from typing import Optional, List, Any, Dict, ClassVar, Union
from datetime import datetime, timezone
import requests
import os
from pathlib import Path
import mimetypes
import json
from pydantic import BaseModel, Field, validator, model_validator

from .core import MultiLanguageField, handle_request_error, auto_setters

@auto_setters
class Distribution(BaseModel):
    """Represents a Distribution Data Transfer Object (DTO)."""
    
    # Class variables for API configuration
    API_URL: ClassVar[str] = ""
    LIST_URL: ClassVar[str] = ""
    UPLOAD_API_URL: ClassVar[str] = ""
    DOWNLOAD_API_URL: ClassVar[str] = ""
    
    # File-related fields
    file_name: str = Field(default="")
    file_size: int = Field(default=0)
    file_type: str = Field(default="")
    file_content: Optional[Any] = Field(default=None, exclude=True)
    
    # Distribution metadata fields
    id: str = Field(default="", alias="ID")
    iri: str = Field(default="", alias="IRI")
    access_service: Optional[Any] = Field(default=None, alias="AccessService")
    access_service_id: Optional[Any] = Field(default=None, alias="AccessServiceID")
    access_url: str = Field(default="", alias="AccessUrl")
    byte_size: int = Field(default=0, alias="ByteSize")
    compress_format: str = Field(default="", alias="CompressFormat")
    download_url: str = Field(default="", alias="DownloadUrl")
    media_type: str = Field(default="", alias="MediaType")
    package_format: str = Field(default="", alias="PackageFormat")
    spatial_resolution_in_meters: float = Field(default=0.0, alias="SpatialResolutionInMeters")
    temporal_resolution: str = Field(default="", alias="TemporalResolution")
    access_rights: str = Field(default="", alias="AccessRights")
    conforms_to: str = Field(default="", alias="ConformsTo")
    description_ml: Dict[str, str] = Field(default_factory=dict, alias="DescriptionML")
    format: str = Field(default="", alias="Format")
    issued: Optional[datetime] = Field(default=None, alias="Issued")
    license: str = Field(default="", alias="License")
    modified: Optional[datetime] = Field(default=None, alias="Modified")
    rights: List[Any] = Field(default_factory=list, alias="Rights")
    title_ml: Dict[str, str] = Field(default_factory=dict, alias="TitleML")
    has_policy: List[Any] = Field(default_factory=list, alias="HasPolicy")
    checksum: str = Field(default="", alias="Checksum")
    is_distribution_of: Optional[Any] = Field(default=None, alias="IsDistributionOf")

    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True
        populate_by_name = True
        alias_generator = None
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%SZ") if v else None,
            BaseModel: lambda v: v.dict()
        }
        validate_default = True

    @model_validator(mode='before')
    def validate_null_fields(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Handle null values for dictionary and list fields."""
        if values.get('DescriptionML') is None:
            values['DescriptionML'] = {}
        if values.get('Rights') is None:
            values['Rights'] = []
        if values.get('HasPolicy') is None:
            values['HasPolicy'] = []
        return values

    @validator('issued', 'modified', pre=True)
    def parse_datetime(cls, v: Any) -> Optional[datetime]:
        """Parse datetime strings and ensure UTC timezone."""
        if not v or v == "0001-01-01T00:00:00Z":  # Handle empty or "zero" datetime
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
        """Convert the Distribution to a dictionary with proper field names."""
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
    def initialize_api_url(cls, url: str) -> None:
        """Initialize the API URLs for the Distribution DTO."""
        cls.API_URL = f"{url}/distribution"
        cls.LIST_URL = f"{cls.API_URL}/list"
        cls.UPLOAD_API_URL = f"{url}/data/upload"
        cls.DOWNLOAD_API_URL = f"{url}/data/download"

    def upload_file(self) -> None:
        """Upload the file content associated with this distribution."""
        if not self.file_content:
            return

        try:
            files = {'file': (self.file_name, self.file_content)}
            response = requests.post(
                self.UPLOAD_API_URL,
                files=files
            )
            response.raise_for_status()
            
            data = response.json()
            object_key = data.get('objectKey')
            self.download_url = f"{self.DOWNLOAD_API_URL}/{object_key}"
            
        except requests.exceptions.RequestException as e:
            handle_request_error(e)

    def create(self) -> 'Distribution':
        """Create a new Distribution via API."""
        try:
            # Upload file if present
            self.upload_file()
            
            # Convert to dictionary with proper field names
            data = self.dict()
            
            response = requests.post(
                self.API_URL,
                json=data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            return Distribution.parse_obj(response.json())
            
        except requests.exceptions.RequestException as e:
            handle_request_error(e)

    def delete(self) -> str:
        """Delete the current Distribution instance via API."""
        try:
            url = f"{self.API_URL}/{self.id}"
            response = requests.delete(
                url,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            if response.status_code == 204:
                return "Distribution deletion successful"
            else:
                raise Exception("Distribution deletion failed")
                
        except requests.exceptions.RequestException as e:
            handle_request_error(e)

    def set_file_for_browser(self, file: Any) -> None:
        """Set file information for browser environment."""
        self.file_name = file.name
        self.file_size = file.size
        self.file_type = file.type
        self.file_content = file

    def set_file_for_node(self, file_path: str) -> None:
        """Set file information for Node.js environment."""
        file_path = Path(file_path)
        file_name = file_path.name
        file_type = file_path.suffix[1:] if file_path.suffix else ""
        file_stats = file_path.stat()
        
        with open(file_path, 'rb') as f:
            file_content = f.read()
            
        self.file_name = file_name
        self.file_size = file_stats.st_size
        self.file_type = file_type
        self.file_content = file_content

    def set_iri(self, iri: str) -> None:
        """Set the IRI for the distribution."""
        self.iri = iri

    def set_access_service(self, access_service: Any) -> None:
        """Set the access service for the distribution."""
        self.access_service = access_service

    def set_access_service_id(self, access_service_id: Any) -> None:
        """Set the access service ID for the distribution."""
        self.access_service_id = access_service_id

    def set_access_url(self, access_url: str) -> None:
        """Set the access URL for the distribution."""
        self.access_url = access_url

    def set_byte_size(self, byte_size: int) -> None:
        """Set the byte size for the distribution."""
        self.byte_size = byte_size

    def set_compress_format(self, compress_format: str) -> None:
        """Set the compression format for the distribution."""
        self.compress_format = compress_format

    def set_download_url(self, download_url: str) -> None:
        """Set the download URL for the distribution."""
        self.download_url = download_url

    def set_media_type(self, media_type: str) -> None:
        """Set the media type for the distribution."""
        self.media_type = media_type

    def set_package_format(self, package_format: str) -> None:
        """Set the package format for the distribution."""
        self.package_format = package_format

    def set_spatial_resolution_in_meters(self, resolution: float) -> None:
        """Set the spatial resolution in meters for the distribution."""
        self.spatial_resolution_in_meters = resolution

    def set_temporal_resolution(self, resolution: str) -> None:
        """Set the temporal resolution for the distribution."""
        self.temporal_resolution = resolution

    def set_access_rights(self, access_rights: str) -> None:
        """Set the access rights for the distribution."""
        self.access_rights = access_rights

    def set_conforms_to(self, conforms_to: str) -> None:
        """Set the conformance for the distribution."""
        self.conforms_to = conforms_to

    def set_description(self, description: str) -> None:
        """Set the description of the distribution."""
        if not self.description_ml:
            self.description_ml = {}
        self.description_ml["ko"] = description

    def set_format(self, format: str) -> None:
        """Set the format of the distribution."""
        self.format = format

    def set_issued(self, issued: Optional[datetime]) -> None:
        """Set the issued date for the distribution."""
        self.issued = issued

    def set_license(self, license: str) -> None:
        """Set the license for the distribution."""
        self.license = license

    def set_modified(self, modified: Optional[datetime]) -> None:
        """Set the modified date for the distribution."""
        self.modified = modified

    def set_rights(self, rights: List[Any]) -> None:
        """Set the rights for the distribution."""
        self.rights = rights

    def set_title(self, title: str) -> None:
        """Set the title of the distribution."""
        if not self.title_ml:
            self.title_ml = {}
        self.title_ml["ko"] = title

    def set_has_policy(self, has_policy: List[Any]) -> None:
        """Set the policies associated with the distribution."""
        self.has_policy = has_policy

    def set_checksum(self, checksum: str) -> None:
        """Set the checksum for the distribution."""
        self.checksum = checksum

    def set_is_distribution_of(self, is_distribution_of: str) -> None:
        """Set the reference to the dataset this distribution belongs to."""
        self.is_distribution_of = is_distribution_of
