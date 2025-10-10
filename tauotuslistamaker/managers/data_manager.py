import json
from datetime import datetime, timedelta
from typing import TYPE_CHECKING
from ..models import TimeInterval
from ..models import Cashier
from ..collections import CashierScheduleCollection
from pathlib import Path

if TYPE_CHECKING:
    from ..models import CashierBreak

class DataManager:

    ROOT_FOLDER = Path(__file__).parent.parent

    def __init__(self):
        self.cashiers = []
        self.config = {}

    @property
    def all_breaks(self) -> list["CashierBreak"]:
        all_breaks = []
        for cashier in self.cashiers:
            all_breaks.extend(cashier.breaks)
        return all_breaks

    def load_data(self, file_name: str) -> None:
        try:
            with open(self.ROOT_FOLDER / file_name, "r") as json_file:
                self.cashiers = json.load(json_file)
                # keep validation and data transformation in separate methods to keep the code clean and maintainable
                self._validate_cashiers_data()
                self._transform_cashiers_shift_intervals_to_TimeInterval_objects()
                self._transform_cashiers_to_cashier_objects()
        except FileNotFoundError:
            raise FileNotFoundError(f"{file_name} not found")
        except json.decoder.JSONDecodeError:
            raise ValueError(f"{file_name} is not a valid json file")
        except Exception as e:
            raise Exception(f"Error: {e}")
        
    def _is_valid_time_format(self, time_str: str) -> bool:
        try:
            datetime.strptime(time_str, "%H:%M")
            return True
        except ValueError:
            return False
        
    def _check_required_keys(self, dictionary: dict, required_keys: list) -> None:
        for key in required_keys:
            if key not in dictionary:
                raise KeyError(f"Required keys for dictionary: {required_keys}")
    
    def _validate_cashiers_data(self):
        for cashier in self.cashiers:
            if not isinstance(cashier, dict):
                raise ValueError("Each cashier must be a dictionary.")
            if "shift_start" not in cashier or "shift_end" not in cashier or "name" not in cashier:
                raise KeyError("Each cashier must have 'shift_start'. 'shift_end' and 'name' keys.")
            if not self._is_valid_time_format(cashier["shift_start"]) or not self._is_valid_time_format(cashier["shift_end"]):
                raise ValueError("Shift start and end must be in 'HH:MM' format.")
        
    def _transform_cashiers_shift_intervals_to_TimeInterval_objects(self):
        for cashier in self.cashiers:
            cashier_shift_start = datetime.strptime(
                cashier["shift_start"], "%H:%M")
            cashier_shift_end = datetime.strptime(cashier["shift_end"], "%H:%M")

            # If the shift ends at 00:00 or later, it means that the shift ends the next day
            if cashier["shift_start"] > cashier["shift_end"]:
                cashier_shift_end = cashier_shift_end + timedelta(days=1)
            
            cashier["shift_interval"] = TimeInterval(cashier_shift_start, cashier_shift_end)
            # remove the original shift start and end times
            del cashier["shift_start"]
            del cashier["shift_end"]
    
    def _transform_cashiers_to_cashier_objects(self):
        cashier_objects = []
        for cashier in self.cashiers:
            # Build a CashierScheduleCollection using the shift interval as the boundary
            cashier_obj = Cashier(cashier["name"], None)
            schedule = CashierScheduleCollection(cashier["shift_interval"], cashier_obj)
            cashier_obj.schedule = schedule
            schedule.setup_initial_breaks()
            cashier_objects.append(cashier_obj)

        self.cashiers = cashier_objects
        
    def load_config(self, file_name: str) -> None:
        try:
            with open(self.ROOT_FOLDER / file_name, "r") as json_file:
                self.config = json.load(json_file)
                # keep validation and data transformation in separate methods to keep the code clean and maintainable
                self._validate_config_data()
                self._transform_config_time_intervals_to_TimeInterval_objects()
        except FileNotFoundError:
            raise FileNotFoundError(f"{file_name} not found")
        except json.decoder.JSONDecodeError:
            raise ValueError(f"{file_name} is not a valid json file")
        except Exception as e:
            raise Exception(f"Error: {e}")
        
    def _validate_config_data(self):
        # Check that all required keys are present
        config_required_keys = ["opening_hours", "checkout_lanes_filling_order", "most_popular_checkouts", "least_popular_checkouts", "extra_checkouts", "self_service_checkouts"]
        self._check_required_keys(self.config, config_required_keys)

        # Check that all keys containing values for checkout lanes are integers
        keys_for_lists_with_whole_numbers = ["checkout_lanes_filling_order", "most_popular_checkouts", "least_popular_checkouts", "extra_checkouts"]
        for key in keys_for_lists_with_whole_numbers:
            for element in self.config[key]:
                if not self._is_whole_number(element):
                    raise ValueError("All elements in 'checkout_lanes_filling_order', 'most_popular_checkouts', 'least_popular_checkouts' and 'extra_checkouts' must be whole numbers.")
    
        # Check that store opening_hours contain required keys and that the values are in correct format
        opening_hours_required_keys = ["opening_time", "closing_time"]
        self._check_required_keys(self.config["opening_hours"], opening_hours_required_keys)
        if not self._is_valid_time_format(self.config["opening_hours"]["opening_time"]) or not self._is_valid_time_format(self.config["opening_hours"]["closing_time"]):
            raise ValueError("Store opening and closing times must be in 'HH:MM' format.")
        if self.config["opening_hours"]["opening_time"] >= self.config["opening_hours"]["closing_time"]:
            raise ValueError("Store must open before it closes.")
        
        # Check that all self service checkouts contain required keys and that the values are in correct format
        self_service_checkouts_required_keys = ["name", "opening_time", "closing_time"]
        for self_service_checkout in self.config["self_service_checkouts"]:
            self._check_required_keys(self_service_checkout, self_service_checkouts_required_keys)
            for key in self_service_checkout:
                self_service_checkout_value = self_service_checkout[key]
                match key:
                    case "name":
                        if not isinstance(self_service_checkout_value, str):
                            raise ValueError("Self service checkout 'name' must be a string.")
                    case "opening_time" | "closing_time":
                        if not self._is_valid_time_format(self_service_checkout_value):
                            raise ValueError("'opening_time' and 'closing_time' must be in 'HH:MM' format.")
                    case _:
                        raise KeyError("Invalid key in self service checkout.")
    
    def _transform_config_time_intervals_to_TimeInterval_objects(self):
        # Remove the original opening and closing times and replace them with a TimeInterval object
        self.config["store_opening_hours_interval"] = TimeInterval(
            datetime.strptime(self.config["opening_hours"]["opening_time"], "%H:%M"), datetime.strptime(self.config["opening_hours"]["closing_time"], "%H:%M"))
        del self.config["opening_hours"]

        # Remove the original opening and closing times for each self service checkout and replace them with a TimeInterval object
        for self_service_checkout in self.config["self_service_checkouts"]:
            self_service_checkout_opening_time = datetime.strptime(
                self_service_checkout["opening_time"], "%H:%M")
            self_service_checkout_closing_time = datetime.strptime(
                self_service_checkout["closing_time"], "%H:%M")
            # If the self service checkout closes before it opens, it means that it closes the next day
            if self_service_checkout["opening_time"] > self_service_checkout["closing_time"]:
                self_service_checkout_closing_time = self_service_checkout_closing_time + timedelta(days=1)
            self_service_checkout["opening_hours_interval"] = TimeInterval(self_service_checkout_opening_time, self_service_checkout_closing_time)

            del self_service_checkout["opening_time"]
            del self_service_checkout["closing_time"]

    def _is_whole_number(self, number) -> bool:
        return isinstance(number, int) and number >= 0