from dataclasses import dataclass, field
from typing import Optional, List, Any, Dict
from datetime import datetime
import requests
import os
from pathlib import Path

from .core import MultiLanguageField, MultiLanguageKeywords, handle_request_error
from .version_info_dto import VersionInfoDTO

@dataclass
class DatasetInSeriesDTO:
    """Represents a dataset within a dataset series."""
    
    id: str = field(default="")
    title_ml: MultiLanguageField = field(default_factory=dict)
    description_ml: MultiLanguageField = field(default_factory=dict)
    resource_type: str = field(default="")
    iri: str = field(default="")
    version_notes: str = field(default="")
    version: str = field(default="")
    license: str = field(default="")
    first_id: Optional[str] = field(default=None)
    last_id: Optional[str] = field(default=None)
    previous_id: Optional[str] = field(default=None)
    next_id: Optional[str] = field(default=None)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the DTO to a dictionary representation."""
        return {
            'ID': self.id,
            'TitleML': self.title_ml,
            'DescriptionML': self.description_ml,
            'ResourceType': self.resource_type,
            'IRI': self.iri,
            'VersionNotes': self.version_notes,
            'Version': self.version,
            'License': self.license,
            'FirstID': self.first_id,
            'LastID': self.last_id,
            'PreviousID': self.previous_id,
            'NextID': self.next_id,
        }

@dataclass
class DatasetSeriesDTO:
    """Represents a series of datasets."""
    
    # Class variables for API configuration
    BEARER_TOKEN: str = field(default="", init=False)
    API_URL: str = field(default="", init=False)
    LIST_URL: str = field(default="", init=False)
    
    # Thumbnail specific fields
    thumbnail_name: Optional[str] = field(default=None)
    thumbnail_size: Optional[int] = field(default=None)
    thumbnail_type: Optional[str] = field(default=None)
    thumbnail_content: Optional[Any] = field(default=None)
    
    # Dataset series fields
    id: str = field(default="")
    datahub_id: str = field(default="")
    asset_id: str = field(default="")
    dataset_series_id: str = field(default="")
    iri: str = field(default="")
    thumbnail_path: str = field(default="")
    access_rights: str = field(default="")
    status: str = field(default="")
    version_notes: str = field(default="")
    version: str = field(default="")
    is_version_of: Optional[str] = field(default=None)
    previous_version_id: Optional[str] = field(default=None)
    next_version_id: Optional[str] = field(default=None)
    contact_point: str = field(default="")
    keyword_ml: MultiLanguageKeywords = field(default_factory=dict)
    landing_page: str = field(default="")
    theme: str = field(default="")
    conforms_to: str = field(default="")
    creator: str = field(default="")
    description_ml: MultiLanguageField = field(default_factory=dict)
    identifier: str = field(default="")
    is_referenced_by: List[str] = field(default_factory=list)
    issued: Optional[datetime] = field(default=None)
    language: List[str] = field(default_factory=list)
    license: str = field(default="")
    modified: Optional[datetime] = field(default=None)
    publisher: str = field(default="")
    rights: List[str] = field(default_factory=list)
    title_ml: MultiLanguageField = field(default_factory=dict)
    type: str = field(default="")
    has_policy: List[str] = field(default_factory=list)
    issuer_id: str = field(default="")
    profile_iri: str = field(default="")
    frequency: str = field(default="")
    spatial_resolution_in_meters: float = field(default=0.0)
    temporal_resolution: str = field(default="")
    spatial: str = field(default="")
    temporal: str = field(default="")
    was_generated_by: str = field(default="")
    in_series_id: Optional[str] = field(default=None)
    instance_value: Any = field(default=None)
    series_member: List[DatasetInSeriesDTO] = field(default_factory=list)
    version_info: List[VersionInfoDTO] = field(default_factory=list)

    @classmethod
    def initialize_api_url(cls, api_url: str) -> None:
        """Initialize the API URL for the Dataset Series DTO."""
        cls.API_URL = api_url
        cls.LIST_URL = f"{api_url}/datasetSeries"

    @classmethod
    def list_dataset_series(cls, page_number: int = 1, page_size: int = 10, 
                          sort_order: str = "DESC") -> List['DatasetSeriesDTO']:
        """List dataset series from the API."""
        headers = {"Authorization": f"Bearer {cls.BEARER_TOKEN}"}
        params = {
            "pageNumber": page_number,
            "pageSize": page_size,
            "sortOrder": sort_order
        }
        
        try:
            response = requests.get(
                cls.LIST_URL,
                headers=headers,
                params=params
            )
            response.raise_for_status()
            return [cls(**item) for item in response.json()]
        except requests.exceptions.RequestException as e:
            handle_request_error(e)

    @classmethod
    def get(cls, series_id: str) -> 'DatasetSeriesDTO':
        """Retrieve a dataset series by its ID."""
        headers = {"Authorization": f"Bearer {cls.BEARER_TOKEN}"}
        
        try:
            response = requests.get(
                f"{cls.API_URL}/datasetSeries/{series_id}",
                headers=headers
            )
            response.raise_for_status()
            return cls(**response.json())
        except requests.exceptions.RequestException as e:
            handle_request_error(e)

    def create(self) -> 'DatasetSeriesDTO':
        """Create a new dataset series via API."""
        headers = {"Authorization": f"Bearer {self.BEARER_TOKEN}"}
        
        try:
            if self.thumbnail_content:
                self.upload_thumbnail()
                
            response = requests.post(
                self.LIST_URL,
                headers=headers,
                json=self.to_dict()
            )
            response.raise_for_status()
            return self.__class__(**response.json())
        except requests.exceptions.RequestException as e:
            handle_request_error(e)

    def delete(self) -> str:
        """Delete the current dataset series."""
        headers = {"Authorization": f"Bearer {self.BEARER_TOKEN}"}
        
        try:
            response = requests.delete(
                f"{self.API_URL}/datasetSeries/{self.id}",
                headers=headers
            )
            response.raise_for_status()
            return response.json().get('message', 'Successfully deleted')
        except requests.exceptions.RequestException as e:
            handle_request_error(e)

    def upload_thumbnail(self) -> None:
        """Upload the thumbnail if content is set."""
        if not self.thumbnail_content:
            return
            
        headers = {"Authorization": f"Bearer {self.BEARER_TOKEN}"}
        files = {'file': (self.thumbnail_name, self.thumbnail_content)}
        
        try:
            response = requests.post(
                f"{self.API_URL}/datasetSeries/{self.id}/thumbnail",
                headers=headers,
                files=files
            )
            response.raise_for_status()
            self.thumbnail_path = response.json().get('thumbnail_path', '')
        except requests.exceptions.RequestException as e:
            handle_request_error(e)

    def set_thumbnail_for_browser(self, file: Any) -> None:
        """Set thumbnail information for browser environment."""
        self.thumbnail_name = file.name
        self.thumbnail_size = file.size
        self.thumbnail_type = file.type
        self.thumbnail_content = file

    def set_thumbnail_for_node(self, thumbnail_path: str) -> None:
        """Set thumbnail information for Node.js environment."""
        if not os.path.exists(thumbnail_path):
            raise FileNotFoundError(f"File not found: {thumbnail_path}")
            
        file_name = Path(thumbnail_path).name
        self.thumbnail_name = file_name
        self.thumbnail_size = os.path.getsize(thumbnail_path)
        self.thumbnail_type = ""  # Determine file type if needed
        with open(thumbnail_path, 'rb') as f:
            self.thumbnail_content = f.read()

    def add_series_member_using_dataset_resource_id(self, resource_id: str) -> None:
        """Add a series member using the provided ResourceID."""
        member = DatasetInSeriesDTO(id=resource_id)
        self.series_member.append(member)

    def switch_series_member_indexes(self, index1: int, index2: int) -> None:
        """Switch the positions of two series members."""
        if not (0 <= index1 < len(self.series_member) and 
                0 <= index2 < len(self.series_member)):
            raise IndexError("Invalid index")
            
        self.series_member[index1], self.series_member[index2] = \
            self.series_member[index2], self.series_member[index1]

    def get_version_info(self) -> List[VersionInfoDTO]:
        """Get all version information."""
        return self.version_info

    def get_version_info_by_index(self, index: int) -> Optional[VersionInfoDTO]:
        """Get version information by index."""
        if 0 <= index < len(self.version_info):
            return self.version_info[index]
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert the DTO to a dictionary representation."""
        return {
            'ID': self.id,
            'DatahubID': self.datahub_id,
            'AssetID': self.asset_id,
            'DatasetSeriesID': self.dataset_series_id,
            'IRI': self.iri,
            'ThumbnailPath': self.thumbnail_path,
            'AccessRights': self.access_rights,
            'Status': self.status,
            'VersionNotes': self.version_notes,
            'Version': self.version,
            'IsVersionOf': self.is_version_of,
            'PreviousVersionID': self.previous_version_id,
            'NextVersionID': self.next_version_id,
            'ContactPoint': self.contact_point,
            'KeywordML': self.keyword_ml,
            'LandingPage': self.landing_page,
            'Theme': self.theme,
            'ConformsTo': self.conforms_to,
            'Creator': self.creator,
            'DescriptionML': self.description_ml,
            'Identifier': self.identifier,
            'IsReferencedBy': self.is_referenced_by,
            'Issued': self.issued.isoformat() if self.issued else None,
            'Language': self.language,
            'License': self.license,
            'Modified': self.modified.isoformat() if self.modified else None,
            'Publisher': self.publisher,
            'Rights': self.rights,
            'TitleML': self.title_ml,
            'Type': self.type,
            'HasPolicy': self.has_policy,
            'IssuerID': self.issuer_id,
            'ProfileIRI': self.profile_iri,
            'Frequency': self.frequency,
            'SpatialResolutionInMeters': self.spatial_resolution_in_meters,
            'TemporalResolution': self.temporal_resolution,
            'Spatial': self.spatial,
            'Temporal': self.temporal,
            'WasGeneratedBy': self.was_generated_by,
            'InSeriesID': self.in_series_id,
            'InstanceValue': self.instance_value,
            'SeriesMember': [m.to_dict() for m in self.series_member],
            'VersionInfo': [v.to_dict() for v in self.version_info],
        }
