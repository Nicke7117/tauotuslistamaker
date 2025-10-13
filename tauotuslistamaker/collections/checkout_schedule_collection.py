from ..models import TimeInterval, Checkout, AvailableInterval
from . import TimeIntervalCollection
from .schedule_collection_base import ScheduleCollectionBase

class CheckoutScheduleCollection(ScheduleCollectionBase):

    def __init__(self, boundary_interval: TimeInterval, checkout: Checkout) -> None:
        super().__init__(boundary_interval)
        self.checkout = checkout

    def _wrap_availability(self, interval):
        return AvailableInterval.for_checkout(start_time=interval.start_time, end_time=interval.end_time, checkout=self.checkout)