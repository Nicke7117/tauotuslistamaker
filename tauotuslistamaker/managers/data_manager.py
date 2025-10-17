import json
from datetime import datetime, timedelta, time
from typing import TYPE_CHECKING, List, Dict, Any
from pathlib import Path

from ..models import TimeInterval
from ..models import Cashier, Checkout
from ..collections import CashierScheduleCollection, CheckoutScheduleCollection

if TYPE_CHECKING:
    from ..models import BreakAssignment

TimeBoundary = time 

class DataManager:

    ROOT_FOLDER = Path(__file__).parent.parent

    def __init__(self):
        self.cashiers: List[Cashier] = []
        self.checkouts: List[Checkout] = []
        self.config: Dict[str, Any] = {}

    # --- Properties ---
    @property
    def all_breaks(self) -> list["BreakAssignment"]:
        all_breaks = []
        for cashier in self.cashiers:
            all_breaks.extend(cashier.breaks)
        return all_breaks
    
    @property
    def all_availabilities(self) -> list["TimeInterval"]:
        all_availabilities = []
        for cashier in self.cashiers:
            all_availabilities.extend(cashier.all_availabilities)
        return all_availabilities
    
    def load_data(self, file_name: str) -> None:
        try:
            with open(self.ROOT_FOLDER / file_name, "r") as json_file:
                # self.cashiers temporarily holds raw JSON list
                self.cashiers = json.load(json_file)
                self._validate_cashiers_data()
                self._transform_cashiers_shift_intervals_to_TimeInterval_objects()
                self._transform_cashiers_to_cashier_objects()
        except FileNotFoundError:
            raise FileNotFoundError(f"{file_name} not found")
        except json.decoder.JSONDecodeError:
            raise ValueError(f"{file_name} is not a valid json file")
        except Exception as e:
            raise Exception(f"Error loading cashier data: {e}")

    def load_config(self, file_name: str) -> None:
        try:
            with open(self.ROOT_FOLDER / file_name, "r") as json_file:
                self.config = json.load(json_file)
                self._validate_config_data()
                self._validate_tobacco_ratio_pool() 
                self._transform_checkouts_to_checkout_objects()
                
        except FileNotFoundError:
            raise FileNotFoundError(f"{file_name} not found")
        except json.decoder.JSONDecodeError:
            raise ValueError(f"{file_name} is not a valid json file")
        except Exception as e:
            raise Exception(f"Error loading configuration: {e}")
            
    def get_checkout_config(self) -> dict:
        """Returns the processed configuration dictionary."""
        return self.config

    def _is_valid_time_format(self, time_str: str) -> bool:
        try:
            datetime.strptime(time_str, "%H:%M")
            return True
        except ValueError:
            return False
        
    def _check_required_keys(self, dictionary: dict, required_keys: list) -> None:
        for key in required_keys:
            if key not in dictionary:
                raise KeyError(f"Missing required key: '{key}'. Required keys for dictionary: {required_keys}")
    
    def _is_whole_number(self, number) -> bool:
        return isinstance(number, int) and number >= 0

    def _validate_cashiers_data(self):
        for cashier in self.cashiers:
            if not isinstance(cashier, dict):
                raise ValueError("Each cashier must be a dictionary.")
            if "shift_start" not in cashier or "shift_end" not in cashier or "name" not in cashier:
                raise KeyError("Each cashier must have 'shift_start', 'shift_end' and 'name' keys.")
            if not self._is_valid_time_format(cashier["shift_start"]) or not self._is_valid_time_format(cashier["shift_end"]):
                raise ValueError("Shift start and end must be in 'HH:MM' format.")

    def _transform_cashiers_shift_intervals_to_TimeInterval_objects(self):
        for cashier in self.cashiers:
            cashier_shift_start = datetime.strptime(cashier["shift_start"], "%H:%M")
            cashier_shift_end = datetime.strptime(cashier["shift_end"], "%H:%M")
            if cashier_shift_start >= cashier_shift_end:
                cashier_shift_end = cashier_shift_end + timedelta(days=1)
            
            cashier["shift_interval"] = TimeInterval(cashier_shift_start, cashier_shift_end)
            del cashier["shift_start"]
            del cashier["shift_end"]
    
    def _transform_cashiers_to_cashier_objects(self):
        cashier_objects = []
        for cashier in self.cashiers:
            cashier_obj = Cashier(cashier["name"], None)
            schedule = CashierScheduleCollection(cashier["shift_interval"], cashier_obj) 
            cashier_obj.schedule = schedule
            schedule.setup_initial_breaks()
            cashier_objects.append(cashier_obj)

        self.cashiers = cashier_objects

    def _validate_config_data(self):
        """Validates the new structured configuration data, including the new 'tobacco_ratio_pool'."""
        
        config_required_keys = ["checkout_time_groups", "checkouts_filling_order", "tobacco_checkouts", "tobacco_checkout_ratios", "tobacco_ratio_pool"]
        self._check_required_keys(self.config, config_required_keys)

        # 2. Validate checkout_time_groups structure and times
        if not isinstance(self.config["checkout_time_groups"], list):
            raise ValueError("'checkout_time_groups' must be a list.")

        all_checkouts = []
        for i, group in enumerate(self.config["checkout_time_groups"]):
            group_required_keys = ["opening_time", "closing_time", "checkouts"]
            self._check_required_keys(group, group_required_keys)

            if not self._is_valid_time_format(group["opening_time"]) or not self._is_valid_time_format(group["closing_time"]):
                raise ValueError(f"Group {i} times must be in 'HH:MM' format.") 

            if not isinstance(group["checkouts"], list) or not group["checkouts"]:
                raise ValueError(f"Group {i} 'checkouts' must be a non-empty list of IDs/names.")

            # Validate checkout identifiers and check for duplicates
            for identifier in group["checkouts"]:
                if not isinstance(identifier, (int, str)):
                    raise ValueError(f"Checkout identifier '{identifier}' in group {i} must be an integer or a string.")
                if identifier in all_checkouts:
                    raise ValueError(f"Duplicate checkout identifier found: '{identifier}'.")
                all_checkouts.append(identifier)

            # Check mandatory_open type if present
            if "mandatory_open" in group and not isinstance(group["mandatory_open"], bool):
                raise ValueError(f"Group {i} 'mandatory_open' must be a boolean.")

        # 3. Validate Filling Order and Tobacco Checkouts consistency
        standard_checkouts = set(c for c in all_checkouts if isinstance(c, int))

        if set(self.config["checkouts_filling_order"]) != standard_checkouts:
            raise ValueError("'checkouts_filling_order' must contain all unique standard (int) checkout IDs and only those IDs.")

        if not set(self.config["tobacco_checkouts"]).issubset(standard_checkouts):
            raise ValueError("'tobacco_checkouts' contains IDs that are not standard (int) checkouts or not listed in 'checkout_time_groups'.")

        # 4. Validate Tobacco Ratio structure
        for ratio in self.config["tobacco_checkout_ratios"]:
            self._check_required_keys(ratio, ["max_total_checkouts", "tobacco_checkouts"])
            if not self._is_whole_number(ratio["max_total_checkouts"]) or not self._is_whole_number(ratio["tobacco_checkouts"]):
                raise ValueError("'tobacco_checkout_ratios' values must be non-negative whole numbers.")
                
        # 5. Validate Tobacco Ratio Pool items
        if not isinstance(self.config["tobacco_ratio_pool"], list) or not self.config["tobacco_ratio_pool"]:
            raise ValueError("'tobacco_ratio_pool' must be a non-empty list of checkout IDs.")
            
        for identifier in self.config["tobacco_ratio_pool"]:
            if identifier not in all_checkouts:
                raise ValueError(f"Checkout identifier '{identifier}' in 'tobacco_ratio_pool' is not listed in any 'checkout_time_groups'.")
                
    def _validate_tobacco_ratio_pool(self):
        """
        Ensures the tobacco ratio pool can satisfy the highest tobacco checkout requirement.
        It also cleans the pool list by converting all IDs to strings for consistency in the manager.
        """
        tobacco_checkouts_in_pool = [c for c in self.config["tobacco_ratio_pool"] if c in self.config["tobacco_checkouts"]]
        
        # 1. Check if the number of tobacco checkouts in the pool is sufficient
        max_tobacco_needed = 0
        for ratio in self.config["tobacco_checkout_ratios"]:
            if ratio["tobacco_checkouts"] > max_tobacco_needed:
                max_tobacco_needed = ratio["tobacco_checkouts"]
                
        if len(tobacco_checkouts_in_pool) < max_tobacco_needed:
            raise ValueError(f"The 'tobacco_ratio_pool' contains only {len(tobacco_checkouts_in_pool)} tobacco checkouts, but the 'tobacco_checkout_ratios' require a maximum of {max_tobacco_needed}. Please ensure the pool contains enough tobacco-authorized checkouts.")
            
        # 2. Transform all pool IDs to strings for easy comparison in CheckoutManager
        self.config["tobacco_ratio_pool"] = [str(identifier) for identifier in self.config["tobacco_ratio_pool"]]


    def _transform_checkouts_to_checkout_objects(self):
        """
        Processes time groups, creates all Checkout objects, and calculates 
        the final simulation boundaries as datetime.time objects.
        """
        
        checkout_objects: List[Checkout] = []
        tobacco_checkouts_set = set(self.config["tobacco_checkouts"])
        
        # Lists to track all boundary times for simulation min/max
        all_opening_times: List[datetime] = []
        all_closing_times: List[datetime] = []

        for group in self.config["checkout_time_groups"]:
            
            start_time_str = group["opening_time"]
            closing_time_str = group["closing_time"]
            is_mandatory_open = group.get("mandatory_open", False)

            # 1. Convert time strings to datetime objects for interval calculation
            start_dt_for_interval = datetime.strptime(start_time_str, "%H:%M")
            end_dt_for_interval = datetime.strptime(closing_time_str, "%H:%M")
            
            # 2. Handle closing time that is on the next day (e.g., 00:00)
            if start_dt_for_interval >= end_dt_for_interval:
                end_dt_for_interval += timedelta(days=1)

            # 3. Store time objects and simulation boundaries
            opening_time_obj = start_dt_for_interval
            closing_time_obj = end_dt_for_interval
            
            all_opening_times.append(opening_time_obj)
            all_closing_times.append(closing_time_obj)
            
            group["opening_time"] = opening_time_obj
            group["closing_time"] = closing_time_obj
            
            # Create the boundary TimeInterval for the CheckoutScheduleCollection
            boundary_interval = TimeInterval(start_dt_for_interval, end_dt_for_interval)

            for identifier in group["checkouts"]:
                is_tobacco_authorized = isinstance(identifier, int) and (identifier in tobacco_checkouts_set)

                schedule = CheckoutScheduleCollection(boundary_interval, None)
                
                checkout_obj = Checkout(
                    identifier,
                    schedule,
                    is_tobacco_authorized,
                    is_mandatory_open
                )
                schedule.checkout = checkout_obj
                checkout_objects.append(checkout_obj)

        self.checkouts = checkout_objects
        
        # Calculate final simulation boundaries using the converted time objects
        self.config["simulation_start_time"] = min(all_opening_times)
        self.config["simulation_end_time"] = max(all_closing_times)
        
        # Clean up config by removing the entire time groups structure
        del self.config["checkout_time_groups"]