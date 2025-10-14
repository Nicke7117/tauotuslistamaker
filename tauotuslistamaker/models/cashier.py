from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ..collections import CashierScheduleCollection
    from .break_assignment import BreakAssignment
    from .time_interval import TimeInterval
    from .available_interval import AvailableInterval


class Cashier:
    def __init__(self, name, schedule: "CashierScheduleCollection"):
        self.name = name
        self.schedule = schedule

    @property
    def availability(self) -> tuple["AvailableInterval", ...]:
        """Read-only snapshot of this cashier's available time intervals."""
        return tuple(self.schedule.availability)

    @property
    def breaks(self) -> tuple["BreakAssignment", ...]:
        """Read-only snapshot of this cashier's scheduled breaks."""
        return tuple(self.schedule.all_breaks)

    @property
    def events(self) -> tuple["TimeInterval", ...]:
        """Read-only snapshot of every scheduled interval for the cashier."""
        return tuple(self.schedule.all_events)

    def can_accept_interval(self, interval: "TimeInterval") -> bool:
        """Check if an interval can be added without conflicts or boundary issues."""
        return self.schedule.can_add_interval(interval)

    def add_interval(self, interval: "TimeInterval") -> None:
        """Add an interval to the cashier's schedule."""
        self.schedule.add_interval(interval)

    def try_move_interval(
        self,
        interval: "TimeInterval",
        minutes_to_move: int,
        *,
        commit: bool = True,
    ) -> tuple[bool, "AvailableInterval" | None]:
        """Attempt to move an interval while keeping validations encapsulated."""
        return self.schedule.try_move_interval(interval, minutes_to_move, commit=commit)

    def copy_schedule(self) -> "CashierScheduleCollection":
        """Provide a detached copy of the underlying schedule for simulations."""
        return deepcopy(self.schedule)
    
    def copy_availability(self) -> list["AvailableInterval"]:
        """Provide a detached copy of the current availability for simulations."""
        return deepcopy(self.availability)