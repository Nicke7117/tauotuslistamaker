from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ..collections import CheckoutScheduleCollection
    
class Checkout:
    def __init__(self, identifier: Union[str, int], schedule: "CheckoutScheduleCollection", is_tobacco_checkout: bool, is_mandatory_open: bool) -> None:
        if isinstance(identifier, str): 
            self.identifier = identifier
        elif isinstance(identifier, int):
            self.identifier = str(identifier)
        else:
            raise ValueError("identifier must be a string or integer")
        self.schedule = schedule
        self.is_tobacco_checkout = is_tobacco_checkout
        self.is_mandatory_open = is_mandatory_open