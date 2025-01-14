# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["PaginatedEvaluationTopic", "Data", "Pagination"]


class Data(BaseModel):
    id: str
    """Unique identifier of the evaluation topic"""

    baseline: Optional[float] = None
    """Optional baseline score for this topic"""

    created_at: str = FieldInfo(alias="createdAt")
    """When the topic was created"""

    modified_at: str = FieldInfo(alias="modifiedAt")
    """When the topic was last modified"""

    org_id: str = FieldInfo(alias="orgId")
    """Organization ID that owns this topic"""

    title: str
    """Title of the evaluation topic"""


class Pagination(BaseModel):
    limit: float
    """Number of items per page"""

    skip: float
    """Number of items skipped"""

    total: float
    """Total number of items"""

    total_pages: float = FieldInfo(alias="totalPages")
    """Total number of pages"""


class PaginatedEvaluationTopic(BaseModel):
    data: List[Data]

    pagination: Pagination
    """Pagination information in response"""
