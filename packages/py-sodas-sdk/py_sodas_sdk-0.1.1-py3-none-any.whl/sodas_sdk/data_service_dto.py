from dataclasses import dataclass, field
from typing import Optional, List, Any, Dict
from datetime import datetime
import requests
import os
from pathlib import Path

from .core import MultiLanguageField, MultiLanguageKeywords, handle_request_error
from .version_info_dto import VersionInfoDTO

@dataclass
class DataServiceDTO:
    """Represents a Data Service DTO."""
    
    # Class variables for API configuration
    BEARER_TOKEN: str = field(default="", init=False)
    API_URL: str = field(default="", init=False)
    LIST_URL: str = field(default="", init=False)
    
    # Thumbnail specific fields
    thumbnail_name: Optional[str] = field(default=None)
    thumbnail_size: Optional[int] = field(default=None)
    thumbnail_type: Optional[str] = field(default=None)
    thumbnail_content: Optional[Any] = field(default=None)
    
    # Data Service specific fields
    id: str = field(default="")
    data_service_id: str = field(default="")
    endpoint_url: str = field(default="")
    endpoint_description: str = field(default="")
    asset_id: str = field(default="")
    datahub_id: str = field(default="")
    iri: str = field(default="")
    thumbnail_path: str = field(default="")
    access_rights: str = field(default="")
    status: str = field(default="")
    version_notes: str = field(default="")
    version: str = field(default="")
    is_version_of: str = field(default="")
    previous_version_id: str = field(default="")
    next_version_id: str = field(default="")
    contact_point: str = field(default="")
    keyword_ml: MultiLanguageKeywords = field(default_factory=dict)
    landing_page: str = field(default="")
    theme: str = field(default="")
    conforms_to: str = field(default="")
    creator: str = field(default="")
    description_ml: MultiLanguageField = field(default_factory=dict)
    identifier: str = field(default="")
    is_referenced_by: List[Any] = field(default_factory=list)
    issued: Optional[datetime] = field(default=None)
    language: List[Any] = field(default_factory=list)
    license: str = field(default="")
    modified: Optional[datetime] = field(default=None)
    publisher: str = field(default="")
    rights: List[Any] = field(default_factory=list)
    title_ml: MultiLanguageField = field(default_factory=dict)
    type: str = field(default="")
    has_policy: List[Any] = field(default_factory=list)
    issuer_id: str = field(default="")
    version_info: List[VersionInfoDTO] = field(default_factory=list)

    @classmethod
    def initialize_api_url(cls, api_url: str) -> None:
        """Initialize the API URL for the Data Service DTO.
        
        Args:
            api_url: Base API URL for data service operations
        """
        cls.API_URL = api_url
        cls.LIST_URL = f"{api_url}/dataservices"

    @classmethod
    def get(cls, data_service_id: str) -> 'DataServiceDTO':
        """Retrieve a data service by its ID.
        
        Args:
            data_service_id: The ID of the data service to retrieve
            
        Returns:
            DataServiceDTO: The retrieved data service
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        headers = {"Authorization": f"Bearer {cls.BEARER_TOKEN}"}
        
        try:
            response = requests.get(
                f"{cls.API_URL}/dataservices/{data_service_id}",
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            return cls(**data)
        except requests.exceptions.RequestException as e:
            handle_request_error(e)

    def upload_thumbnail(self, file_path: str) -> None:
        """Upload a thumbnail for the data service.
        
        Args:
            file_path: Path to the thumbnail file
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            requests.exceptions.RequestException: If the request fails
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_name = Path(file_path).name
        files = {'file': (file_name, open(file_path, 'rb'))}
        headers = {"Authorization": f"Bearer {self.BEARER_TOKEN}"}
        
        try:
            response = requests.post(
                f"{self.API_URL}/dataservices/{self.data_service_id}/thumbnail",
                headers=headers,
                files=files
            )
            response.raise_for_status()
            
            # Update thumbnail information
            self.thumbnail_name = file_name
            self.thumbnail_path = response.json().get('thumbnail_path', '')
            
        except requests.exceptions.RequestException as e:
            handle_request_error(e)
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert the DTO to a dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the DTO
        """
        return {
            'ID': self.id,
            'DataServiceID': self.data_service_id,
            'EndpointUrl': self.endpoint_url,
            'EndpointDescription': self.endpoint_description,
            'AssetID': self.asset_id,
            'DatahubID': self.datahub_id,
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
            'VersionInfo': [v.to_dict() for v in self.version_info],
        }
