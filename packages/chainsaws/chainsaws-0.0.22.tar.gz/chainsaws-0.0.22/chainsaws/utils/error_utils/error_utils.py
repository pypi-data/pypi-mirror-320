"""Error handling utilities for external error monitoring and reporting."""

import pprint
import traceback
from typing import Any, Final

from chainsaws.utils.error_utils.error_utils_models import AppError, ErrorDescription

# Constant for max payload length for error message
MAX_PAYLOAD_LENGTH: Final[int] = 3000


def make_error_description(event: dict[str, Any]) -> str:
    """Create formatted error description from event."""
    return _create_error_description(event).format()


def _create_error_description(event: dict[str, Any]) -> ErrorDescription:
    """Internal function to create ErrorDescription instance."""
    try:
        payload_str = _format_payload(event)

        return ErrorDescription(
            request_id="unknown",
            request_payload=payload_str,
            error_traceback=traceback.format_exc(),
        )
    except Exception as e:
        # Fallback for invalid events
        return ErrorDescription(
            request_id="unknown",
            request_payload=str(event),
            error_traceback=f"Event parsing failed: {
                e!s}\n{traceback.format_exc()}",
        )


def _format_payload(event: dict[str, Any]) -> str:
    """Format event payload for display."""
    return pprint.pformat(event, indent=1)


if __name__ == "__main__":
    sample_event = {
        "requestContext": {
            "requestId": "test-request-id",
            "identity": {
                "sourceIp": "127.0.0.1",
                "userAgent": "Mozilla/5.0",
            },
        },
        "body": "test body",
    }

    error = AppError(
        code="S00005",
        message="Invalid S3 Query Command",
        details={"query": "SELECT * FROM invalid_table"},
    )
