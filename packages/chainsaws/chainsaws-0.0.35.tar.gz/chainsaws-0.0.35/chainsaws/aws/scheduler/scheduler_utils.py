import logging
import traceback
from typing import Any, Optional, Literal
from collections import defaultdict
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timedelta
from types import TracebackType

from croniter import croniter

from chainsaws.aws.scheduler.scheduler_exception import SchedulerException

logger = logging.getLogger(__name__)


@dataclass
class TaskGroup:
    """Task group information."""

    name: str
    cron: str
    tasks: set[Callable]


class GlobalExecutor:
    """Global thread pool executor manager."""

    def __init__(self, max_workers: Optional[int] = None) -> None:
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._futures: list[Future] = []
        self._task_groups: dict[str, TaskGroup] = {}
        self._group_futures: dict[str, list[Future]] = defaultdict(list)

    def submit(self, func: Callable, group_name: str = "default") -> Future:
        """Submit task to thread pool."""
        future = self._executor.submit(func)
        self._futures.append(future)
        self._group_futures[group_name].append(future)
        return future

    def join(self, group_name: Optional[str] = None) -> None:
        """Wait for tasks to complete.

        Args:
            group_name: Optional group name to wait for specific group

        """
        futures = (
            self._group_futures.get(group_name, [])
            if group_name
            else self._futures
        )

        for future in futures:
            try:
                future.result()
            except Exception as e:
                logger.exception("Task execution failed: %s", str(e))
                raise

    def register_group(self, name: str, cron: str) -> None:
        """Register a new task group."""
        self._task_groups[name] = TaskGroup(name=name, cron=cron, tasks=set())

    def add_task_to_group(self, group_name: str, task: Callable) -> None:
        """Add task to group."""
        if group_name in self._task_groups:
            self._task_groups[group_name].tasks.add(task)


# Global executor instance
_executor = GlobalExecutor()


def join(group_name: Optional[str] = None) -> None:
    """Global join function."""
    _executor.join(group_name)


class TaskRunner:
    """Task runner returned by ScheduledTask context manager."""

    def __init__(self, should_run: bool, group_name: str) -> None:
        self.should_run = should_run
        self.group_name = group_name

    def __call__(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        """Execute the task if scheduled."""
        if not self.should_run:
            return

        try:
            # Add task to group for tracking
            _executor.add_task_to_group(self.group_name, func)

            # Wrap function with args and kwargs
            def task(): return func(*args, **kwargs)
            _executor.submit(task, self.group_name)

            logger.debug(
                "Scheduled task %s in group %s",
                func.__name__,
                self.group_name,
            )
        except Exception as e:
            msg = f"Failed to schedule task {
                func.__name__} in group {self.group_name}: {e!s}"
            logger.exception(msg)
            raise SchedulerException(msg) from e


class ScheduledTask:
    """Cron-based task scheduler with context management."""

    def __init__(self, cron_expression: str, group_name: Optional[str] = None) -> None:
        """Initialize scheduled task.

        Args:
            cron_expression: Cron expression for scheduling
            group_name: Optional group name for task grouping

        """
        self.cron_expression = cron_expression
        self.group_name = group_name or "chainsaws-default"
        _executor.register_group(self.group_name, cron_expression)

    def should_run(self) -> bool:
        """Check if task should run based on cron schedule."""
        now = datetime.now() + timedelta(seconds=5)
        iter = croniter(self.cron_expression, now)
        prev_schedule = iter.get_prev(datetime)

        return all(
            getattr(prev_schedule, unit) == getattr(now, unit)
            for unit in ["year", "month", "day", "hour", "minute"]
        )

    def __enter__(self) -> TaskRunner:
        """Enter context manager and return task runner."""
        return TaskRunner(self.should_run(), self.group_name)

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[TracebackType],
    ) -> bool:
        """Exit context manager and handle any errors."""
        if exc_type:
            traceback_str = "".join(
                traceback.format_exception(exc_type, exc_val, exc_tb),
            )
            logger.error(
                "Error in scheduled task group %s: %s\n%s",
                self.group_name,
                str(exc_val),
                traceback_str,
            )
            return True

        return False


class ScheduleCron:
    """Helper for creating cron expressions."""
    @staticmethod
    def daily(hour: int = 0, minute: int = 0) -> str:
        """Daily schedule at specific time."""
        return f"cron({minute} {hour} * * ? *)"

    @staticmethod
    def weekly(day_of_week: int, hour: int = 0, minute: int = 0) -> str:
        """Weekly schedule at specific time."""
        return f"cron({minute} {hour} ? * {day_of_week} *)"

    @staticmethod
    def monthly(day_of_month: int, hour: int = 0, minute: int = 0) -> str:
        """Monthly schedule at specific time."""
        return f"cron({minute} {hour} {day_of_month} * ? *)"


def generate_schedule_name(
    function_name: str,
    prefix: Optional[str] = None,
) -> str:
    """Generate unique schedule name."""
    name_parts = [part for part in [prefix, function_name] if part]
    return "-".join(name_parts)


class ScheduleBuilder:
    """Fluent builder for schedule expressions."""

    def __init__(self) -> None:
        self._minute = "*"
        self._hour = "*"
        self._day = "?"
        self._month = "*"
        self._day_of_week = "?"
        self._year = "*"

    @classmethod
    def every(cls) -> "ScheduleBuilder":
        """Start building a schedule."""
        return cls()

    def minute(self, minute: int) -> "ScheduleBuilder":
        """Set specific minute (0-59)."""
        if not 0 <= minute <= 59:
            raise ValueError("Minute must be between 0 and 59")
        self._minute = str(minute)
        return self

    def minutes(self, interval: int) -> "ScheduleBuilder":
        """Run every n minutes."""
        if not 1 <= interval <= 59:
            raise ValueError("Minute interval must be between 1 and 59")
        self._minute = f"*/{interval}"
        return self

    def hour(self, hour: int) -> "ScheduleBuilder":
        """Set specific hour (0-23)."""
        if not 0 <= hour <= 23:
            raise ValueError("Hour must be between 0 and 23")
        self._hour = str(hour)
        return self

    def hours(self, interval: int) -> "ScheduleBuilder":
        """Run every n hours."""
        if not 1 <= interval <= 23:
            raise ValueError("Hour interval must be between 1 and 23")
        self._hour = f"*/{interval}"
        return self

    def day_of_month(self, day: int) -> "ScheduleBuilder":
        """Set specific day of month (1-31)."""
        if not 1 <= day <= 31:
            raise ValueError("Day must be between 1 and 31")
        self._day = str(day)
        self._day_of_week = "?"  # Reset day of week when using day of month
        return self

    def month(self, month: int) -> "ScheduleBuilder":
        """Set specific month (1-12)."""
        if not 1 <= month <= 12:
            raise ValueError("Month must be between 1 and 12")
        self._month = str(month)
        return self

    def day_of_week(
        self,
        day: int | Literal["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
    ) -> "ScheduleBuilder":
        """Set specific day of week (0-6 or SUN-SAT)."""
        days = {
            "SUN": "1", "MON": "2", "TUE": "3", "WED": "4",
            "THU": "5", "FRI": "6", "SAT": "7",
            0: "1", 1: "2", 2: "3", 3: "4", 4: "5", 5: "6", 6: "7"
        }

        if isinstance(day, str):
            day = day.upper()
            if day not in days:
                raise ValueError("Day must be SUN-SAT")
            self._day_of_week = days[day]
        else:
            if not 0 <= day <= 6:
                raise ValueError("Day must be between 0 and 6")
            self._day_of_week = days[day]

        self._day = "?"  # Reset day of month when using day of week
        return self

    def at(self, time: str) -> "ScheduleBuilder":
        """Set specific time (HH:MM)."""
        try:
            hour, minute = map(int, time.split(":"))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError
        except (ValueError, IndexError):
            raise ValueError("Time must be in HH:MM format (00:00-23:59)")

        self._hour = str(hour)
        self._minute = str(minute)
        return self

    def on_weekdays(self) -> "ScheduleBuilder":
        """Run Monday through Friday."""
        self._day_of_week = "2-6"
        self._day = "?"
        return self

    def on_weekends(self) -> "ScheduleBuilder":
        """Run Saturday and Sunday."""
        self._day_of_week = "1,7"
        self._day = "?"
        return self

    def build(self) -> str:
        """Build the final cron expression."""
        return f"cron({self._minute} {self._hour} {self._day} {self._month} {self._day_of_week} {self._year})"

    def to_rate(
        self,
        value: int,
        unit: Literal["minute", "minutes", "hour", "hours", "day", "days"]
    ) -> str:
        """Convert to rate expression.

        Args:
            value: Number of time units
            unit: Time unit (minute, minutes, hour, hours, day, days)

        Returns:
            str: Rate expression

        Raises:
            ValueError: If value is less than 1
        """
        if value < 1:
            raise ValueError("Rate value must be positive")
        return f"rate({value} {unit})"
