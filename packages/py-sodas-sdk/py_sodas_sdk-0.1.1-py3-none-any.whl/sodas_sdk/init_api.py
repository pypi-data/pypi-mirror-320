import logging
from typing import Optional

# These will be imported when the respective modules are created
from .dataset_dto import DatasetDTO
from .dataset_series_dto import DatasetSeriesDTO
from .data_service_dto import DataServiceDTO
from .distribution import Distribution
from .profile import Profile
from .resource_descriptor import ResourceDescriptor
from .descriptor_template_artifact import DescriptorTemplateArtifact
from .template import Template

logger = logging.getLogger(__name__)

def initialize_api_urls(datahub_api_url: str, governance_portal_api_url: str) -> None:
    """
    Initializes API URLs for various DTO classes by removing trailing slashes
    and setting them as base URLs for API interactions.
    
    Args:
        datahub_api_url: The base API URL for the DataHub services.
        governance_portal_api_url: The base API URL for the Governance Portal services.
    """
    # Remove trailing slashes
    clean_datahub_url = datahub_api_url.rstrip('/')
    clean_governance_url = governance_portal_api_url.rstrip('/')
    
    if datahub_api_url:
        Distribution.initialize_api_url(clean_datahub_url)
        DatasetDTO.initialize_api_url(clean_datahub_url)
        DatasetSeriesDTO.initialize_api_url(clean_datahub_url)
        DataServiceDTO.initialize_api_url(clean_datahub_url)
    else:
        logger.error("DATAHUB_API_URL not provided")
    
    if governance_portal_api_url:
        Profile.initialize_api_url(clean_governance_url)
        ResourceDescriptor.initialize_api_url(clean_governance_url)
        DescriptorTemplateArtifact.initialize_api_url(clean_governance_url)
        # Template.initialize_api_url(clean_governance_url)
    else:
        logger.error("GOVERNANCE_PORTAL_API_URL not provided")

def set_bearer_token(token: str) -> None:
    """
    Sets the Bearer token for API authentication across multiple DTO classes.
    
    Args:
        token: The Bearer token used for API authentication.
    """
    DatasetDTO.BEARER_TOKEN = token
    DataServiceDTO.BEARER_TOKEN = token
    DatasetSeriesDTO.BEARER_TOKEN = token
    Distribution.BEARER_TOKEN = token
    Profile.BEARER_TOKEN = token
    DescriptorTemplateArtifact.BEARER_TOKEN = token
    ResourceDescriptor.BEARER_TOKEN = token
    Template.BEARER_TOKEN = token
