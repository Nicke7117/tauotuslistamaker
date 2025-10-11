from ..models import Checkout, Cashier

class CheckoutManager:
    def __init__(self, cashiers: list[Cashier], checkouts: list[Checkout]) -> None:
        self.cashiers = cashiers
        self.checkouts = checkouts

  
    def assign_checkouts_to_cashiers(self) -> None:
        pass
