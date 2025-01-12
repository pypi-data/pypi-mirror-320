from enum import Enum
from typing import Any, Optional, TypedDict


class SchedulerAPIConfig(TypedDict, total=False):
    """Configuration for Scheduler API."""
    region: str
    profile: Optional[str]
    role_arn: Optional[str]
    schedule_group: str


class ScheduleRequest(TypedDict, total=False):
    """Request to create a schedule."""
    name: str
    schedule_expression: str
    description: Optional[str]
    target_arn: str
    input_data: Optional[dict[str, Any]]
    state: Optional[str]


class ScheduleResponse(TypedDict):
    """Response from schedule operations."""
    name: str
    arn: str
    state: str
    group_name: str
    schedule_expression: str
    description: Optional[str]
    next_invocation: Optional[str]
    last_invocation: Optional[str]
    target_arn: str


class ScheduleListResponse(TypedDict):
    """Response from list schedules operation."""
    schedules: list[ScheduleResponse]
    next_token: Optional[str]


class ScheduleState(str, Enum):
    """Schedule state."""
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"
