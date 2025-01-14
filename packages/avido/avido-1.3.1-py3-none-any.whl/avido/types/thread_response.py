# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from .._models import BaseModel

__all__ = ["ThreadResponse", "Data"]


class Data(BaseModel):
    application_id: str
    """Application ID (UUID)."""

    org_id: str
    """Organization ID"""

    thread_id: str
    """Unique Thread ID (UUID)."""

    timestamp: str
    """ISO-8601 datetime when the thread was triggered/created."""

    input: Optional[Dict[str, object]] = None
    """JSON describing the initial input that started the thread.

    Strings will be automatically parsed as JSON or wrapped in a message object.
    """

    metadata: Optional[Dict[str, object]] = None
    """Arbitrary metadata for this thread (e.g., userId, source, etc.)."""

    test_id: Optional[str] = None
    """Optional test/evaluation ID for the thread."""


class ThreadResponse(BaseModel):
    data: Data
    """
    A thread groups all traces that are related, such as one agent interaction,
    conversation etc.
    """
