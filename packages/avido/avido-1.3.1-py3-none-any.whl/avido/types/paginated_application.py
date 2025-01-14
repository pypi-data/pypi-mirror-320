# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["PaginatedApplication", "Data", "Pagination"]


class Data(BaseModel):
    id: str
    """Unique identifier of the application"""

    context: str
    """Context/instructions for the application"""

    created_at: str = FieldInfo(alias="createdAt")
    """When the application was created"""

    description: str
    """Description of the application"""

    environment: Literal["DEV", "PROD"]
    """Environment of the application. Defaults to DEV."""

    modified_at: str = FieldInfo(alias="modifiedAt")
    """When the application was last modified"""

    monitoring_enabled: bool = FieldInfo(alias="monitoringEnabled")
    """Whether monitoring is enabled for the application"""

    org_id: str = FieldInfo(alias="orgId")
    """Organization ID that owns this application"""

    slug: str
    """URL-friendly slug for the application"""

    title: str
    """Title of the application"""

    type: Literal["CHATBOT", "AGENT"]
    """Type of the application"""


class Pagination(BaseModel):
    limit: float
    """Number of items per page"""

    skip: float
    """Number of items skipped"""

    total: float
    """Total number of items"""

    total_pages: float = FieldInfo(alias="totalPages")
    """Total number of pages"""


class PaginatedApplication(BaseModel):
    data: List[Data]

    pagination: Pagination
    """Pagination information in response"""
