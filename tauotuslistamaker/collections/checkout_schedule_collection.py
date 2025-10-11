from ..models import TimeInterval, Checkout
from . import TimeIntervalCollection
from .schedule_collection_base import ScheduleCollectionBase
from copy import deepcopy
from typing import Union

class CheckoutScheduleCollection(ScheduleCollectionBase):

    def __init__(self, boundary_interval: TimeInterval, checkout_identifier: Union[str, int], checkout: Checkout) -> None:
        if isinstance(checkout_identifier, str):
            self.checkout_identifier = checkout_identifier
        elif isinstance(checkout_identifier, int):
            self.checkout_identifier = str(checkout_identifier)
        else:
            raise ValueError("checkout_identifier must be a string or integer")
        super().__init__(boundary_interval)
        self.intervals = TimeIntervalCollection()