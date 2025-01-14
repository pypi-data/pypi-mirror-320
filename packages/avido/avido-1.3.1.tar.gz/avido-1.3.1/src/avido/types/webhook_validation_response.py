# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.


from .._models import BaseModel

__all__ = ["WebhookValidationResponse"]


class WebhookValidationResponse(BaseModel):
    valid: bool
    """Indicates if the webhook payload was successfully validated."""
