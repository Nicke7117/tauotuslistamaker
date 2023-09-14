class CheckoutLanes:
    """
    A class representing the checkout lanes in a store.

    Attributes:
    - amount_of_checkouts (int): the total number of checkout lanes in the store.
    - most_popular_checkouts (list): a list of the most popular checkout lanes that are tried to be kept open most of the time.
    - extra_checkouts (list): a list of extra checkout lanes that can be opened if needed.
    - self_service_checkouts (list): a list of self-service checkout lanes, each represented as a dictionary with keys "name", "opening_time", and "closing_time".

    Example usage:
    - CheckoutLanes(15, [15, 14, 13], [2, 3], [{"name": "self service 1", "opening_time": "09:00", "closing_time": "20:00"}, {"name": "self service 2", "opening_time": "10:30", "closing_time": "22:00"}])
    """

    def __init__(self, amount_of_checkouts, most_popular_checkouts, extra_checkouts, self_service_checkouts):
        self.amount_of_checkouts = amount_of_checkouts
        self.most_popular_checkouts = most_popular_checkouts
        self.extra_checkouts = extra_checkouts
        self.self_service_checkouts = self_service_checkouts

