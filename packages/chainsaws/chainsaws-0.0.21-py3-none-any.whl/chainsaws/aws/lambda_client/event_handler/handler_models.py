"""Models for AWS Lambda handler utilities.

Defines request and response structures for Lambda functions.
"""
import json
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class RequestContext(BaseModel):
    """AWS API Gateway request context."""

    identity: dict[str, Any] = Field(default_factory=dict)
    request_id: Optional[str] = None

    def get_source_ip(self) -> Optional[str]:
        """Get source IP address from request context."""
        return self.identity.get("sourceIp", None)


class ResponseHeaders(BaseModel):
    """API Gateway response headers."""

    Access_Control_Allow_Origin: str = Field(
        default="*", alias="Access-Control-Allow-Origin")
    Access_Control_Allow_Headers: str = Field(
        default="*", alias="Access-Control-Allow-Headers")
    Access_Control_Allow_Credentials: bool = Field(
        default=True, alias="Access-Control-Allow-Credentials")
    Access_Control_Allow_Methods: str = Field(
        default="*", alias="Access-Control-Allow-Methods")
    Content_Type: str = Field(default="application/json", alias="Content-Type")
    charset: str = Field(default="UTF-8")


class HandlerConfig(BaseModel):
    """Handler wrapper configuration."""

    error_receiver: Optional[Any] = None
    content_type: str = "application/json"
    use_traceback: bool = True
    ignore_app_errors: list = Field(default_factory=list)


class LambdaEvent(BaseModel):
    """AWS Lambda event structure."""

    body: Optional[str] = None
    headers: dict[str, str] = Field(default_factory=dict)
    request_context: RequestContext = Field(default_factory=RequestContext)

    model_config = ConfigDict(
        extra="allow",
        arbitrary_types_allowed=True,
    )

    def get_json_body(self) -> dict[str, Any] | None:
        """Get JSON body from event."""
        if not self.body:
            return None
        try:
            return json.loads(self.body)
        except json.JSONDecodeError:
            return None


class LambdaResponse:
    """Lambda response model."""

    def __init__(self, body: Any, status_code: int = 200, headers: dict[str, str] | None = None):
        self.body = body
        self.status_code = status_code
        self.headers = headers or {}

    @classmethod
    def create(cls, body: Any, status_code: int = 200, content_type: str = "application/json") -> dict:
        """Create formatted Lambda response."""
        headers = {
            "Content-Type": content_type,
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
        }

        # JSON 직렬화 가능한 딕셔너리 형태로 반환
        return {
            "statusCode": status_code,
            "headers": headers,
            "body": json.dumps(body) if isinstance(body, (dict, list)) else str(body)
        }
