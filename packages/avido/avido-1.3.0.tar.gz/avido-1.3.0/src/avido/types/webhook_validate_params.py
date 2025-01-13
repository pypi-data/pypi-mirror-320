# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["WebhookValidateParams"]


class WebhookValidateParams(TypedDict, total=False):
    body: Required[object]
    """The raw JSON payload sent by the external webhook.

    Arbitrary fields are allowed; signature verification is used for security.
    """
