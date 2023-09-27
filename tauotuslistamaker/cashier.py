from datetime import datetime, timedelta
import uuid
from utils import round_time_to_nearest_quarter
import uuid
from datetime import datetime, timedelta


class Cashier:
    def __init__(self, name, start_time, end_time):
        """
        Initializes a Cashier object with a name, start time, and end time.

        Args:
        name (str): The name of the cashier.
        start_time (str): The start time of the cashier's shift in the format "HH:MM".
        end_time (str): The end time of the cashier's shift in the format "HH:MM".

        Properties:
        name (str): The name of the cashier.
        id (uuid): A unique id for the cashier.
        start_time (str): The start time of the cashier's shift in the format "HH:MM".
        end_time (str): The end time of the cashier's shift in the format "HH:MM".
        breaks (dict): A dictionary containing the name of the cashier and a list of breaks, where each break is a dictionary with a start time and end time in the format "HH:MM".
        """
        self.name = name
        self.id = uuid.uuid4()
        self.start_time = start_time
        self.end_time = end_time
        self.breaks = self.calculate_breaks()

    def calculate_breaks(self):
        """
        Calculates the breaks for the cashier's shift based on the length of the shift.
        If the shift is less than 6 hours, the cashier gets one 15 minute break.
        If the shift is between 6 and 7 hours, the cashier gets two 15 minute breaks.   
        If the shift is more than 7 hours, the cashier gets two 15 minute breaks and one 30 minute break.

        Returns:
        dict: A dictionary containing the name of the cashier and a list of breaks, where each break is a dictionary with a start time and end time in the format "HH:MM".
        """
        start_time = datetime.strptime(self.start_time, "%H:%M")
        end_time = datetime.strptime(self.end_time, "%H:%M")

        time_difference = end_time - start_time
        if time_difference.days < 0:
            time_difference = timedelta(
                days=0, seconds=time_difference.seconds, microseconds=time_difference.microseconds)
        shift_length_minutes = time_difference.total_seconds() / 60

        breaks_length = []
        if shift_length_minutes < 360:
            breaks_length.append(15)
        elif shift_length_minutes >= 360 and shift_length_minutes <= 420:
            breaks_length.append(15)
            breaks_length.append(15)
        else:
            breaks_length.append(15)
            breaks_length.append(30)
            breaks_length.append(15)

        breaks = []
        split_shift = shift_length_minutes / (len(breaks_length) + 1)
        for i in range(len(breaks_length)):
            start_time = start_time + timedelta(minutes=split_shift)
            start_time_rounded = round_time_to_nearest_quarter(start_time)
            end_time = start_time_rounded + timedelta(minutes=breaks_length[i])
            breaks.append({"start_time": start_time_rounded.strftime(
                "%H:%M"), "end_time": end_time.strftime("%H:%M")})

        return {self.name: breaks}
