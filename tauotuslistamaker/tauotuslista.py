from datetime import timedelta


class Tauotuslista:
    """
    A class representing the "tauotuslista" of a store.
    Tauotuslista = a list where the cashiers of a store can see when their breaks are and where they are supposed to be at any given time.

    Attributes:
    - amount_of_checkouts (int): the total number of checkout lanes in the store.
    - most_popular_checkouts (list): a list of the most popular checkout lanes that are tried to be kept open most of the time.
    - extra_checkouts (list): a list of extra checkout lanes that can be opened if needed.
    - self_service_checkouts (list): a list of self-service checkout lanes, each represented as a dictionary with keys "name", "opening_time", and "closing_time".

    Example usage:
    - Tauotuslista(15, [15, 14, 13], [2, 3], [{"name": "self service 1", "opening_time": "09:00", "closing_time": "20:00"}, {"name": "self service 2", "opening_time": "10:30", "closing_time": "22:00"}], [{'name': 'Ville', 'breaks': [{'start_time': datetime.datetime(1900, 1, 1, 13, 0), 'end_time': datetime.datetime(1900, 1, 1, 13, 15)}, {'start_time': datetime.datetime(1900, 1, 1, 15, 0), 'end_time': datetime.datetime(1900, 1, 1, 15, 30)}, {'start_time': datetime.datetime(1900, 1, 1, 17, 15), 'end_time': datetime.datetime(1900, 1, 1, 17, 30)}]}, {'name': 'Kalle', 'breaks': [{'start_time': datetime.datetime(1900, 1, 1, 10, 0), 'end_time': datetime.datetime(1900, 1, 1, 10, 15)}, {'start_time': datetime.datetime(1900, 1, 1, 12, 0), 'end_time': datetime.datetime(1900, 1, 1, 12, 30)}, {'start_time': datetime.datetime(1900, 1, 1, 14, 0), 'end_time': datetime.datetime(1900, 1, 1, 14, 15)}]}])
    """

    def __init__(self, amount_of_checkouts, most_popular_checkouts, extra_checkouts, self_service_checkouts, cashiers):
        self.amount_of_checkouts = amount_of_checkouts
        self.most_popular_checkouts = most_popular_checkouts
        self.extra_checkouts = extra_checkouts
        self.self_service_checkouts = self_service_checkouts
        self.cashiers = cashiers
        self.breaks_list = self.create_breaks_list()

    def create_breaks_list(self):
        breaks_list = [{"tauottaja": 1, "breaks": []}]
        while len(self.cashiers) > 0:
            # find the cashier with the earliest break
            current_earliest_break = None
            for cashier in self.cashiers:
                for cashier_break in cashier["breaks"]:
                    if current_earliest_break == None:
                        current_earliest_break = {
                            "name": cashier["name"], "start_time": cashier_break["start_time"], "end_time": cashier_break["end_time"]}
                    elif cashier_break["start_time"] < current_earliest_break["start_time"]:
                        current_earliest_break = {
                            "name": cashier["name"], "start_time": cashier_break["start_time"], "end_time": cashier_break["end_time"]}
            # add the cashier break to the breaks list
            for i, tauottaja in enumerate(breaks_list):
                if tauottaja["breaks"] == []:
                    tauottaja["breaks"].append(current_earliest_break)
                    break
                elif current_earliest_break["start_time"] >= tauottaja["breaks"][-1]["end_time"]:
                    tauottaja["breaks"].append(current_earliest_break)
                    break
                elif current_earliest_break["start_time"] < tauottaja["breaks"][-1]["end_time"]:
                    minutes_difference = (
                        tauottaja["breaks"][-1]["end_time"] - current_earliest_break["start_time"]).total_seconds() / 60
                    if minutes_difference <= 30:
                        tauottaja["breaks"].append({"name": current_earliest_break["name"], "start_time": current_earliest_break["start_time"] + timedelta(
                            minutes=minutes_difference), "end_time": current_earliest_break["end_time"] + timedelta(minutes=minutes_difference)})
                        break
                # create new tauottaja if the break can't be added to any of the existing tauottajas
                if i == len(breaks_list) - 1:
                    breaks_list.append(
                        {"tauottaja": breaks_list[-1]["tauottaja"] + 1, "breaks": [current_earliest_break]})
                    break

            # remove the break, that was just added to the breaks list, from cashiers
            cashier_break_to_remove_found = False
            for cashier in self.cashiers:
                if cashier_break_to_remove_found:
                    break
                elif cashier["name"] == current_earliest_break["name"]:
                    for index, cashier_break in enumerate(cashier["breaks"]):
                        if cashier_break["start_time"] == current_earliest_break["start_time"]:
                            del cashier["breaks"][index]
                            # if the breaks list of the cashier is empty, remove the cashier from the list of cashiers
                            if not cashier["breaks"]:
                                self.cashiers.remove(cashier)
                            cashier_break_to_remove_found = True
                            break
        return breaks_list
