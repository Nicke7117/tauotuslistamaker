from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Tuple, Any, TYPE_CHECKING
from ..utils import time_diff_in_minutes

if TYPE_CHECKING:
    from ..models import Cashier, BreakAssignment 


# Helper to hold the results of a simulation run 
@dataclass
class AssignmentCandidate:
    cashier: "Cashier"
    total_minutes_covered: int = 0
    # Stores the list of tuples: (original_break, shifted_time_interval)
    assignments_to_commit: List[Tuple["BreakAssignment", "BreakAssignment"]] = field(default_factory=list)


class BreakManager:
    BREAK_MAX_POSTPONE_MINUTES = 30
    BONUS_PER_CONSECUTIVE_BREAK = 15 # Bonus minutes for covering consecutive breaks
    EARLY_BREAK_BONUS = 7.5
    LATE_BREAK_BONUS = 7.5
    EARLY_BREAK_BOUNDARY_HOUR = 11  # breaks ending before this hour are considered early
    LATE_BREAK_BOUNDARY_HOUR = 20  # breaks starting after this hour are considered late
    REQUIRED_MIN_COVERAGE = 60  # Minimum total minutes a cashier must cover to be considered
    
    def __init__(self, cashiers: list["Cashier"], all_breaks: List["BreakAssignment"]) -> None:
        self.cashiers = cashiers
        self.all_breaks = all_breaks
        self.breaks_schedule_list = []

    def generate_breaks_list(self) -> List[Dict[str, Any]]:
        
        available_cashiers: List["Cashier"] = self.cashiers[:]
        final_assignments = []

        while self.all_breaks:
            best_candidate = self._find_best_cashier_assignment(available_cashiers)
            
            if best_candidate and best_candidate.assignments_to_commit:
                
                final_assignments.append({
                    "tauottaja": best_candidate.cashier,
                    "breaks_covered": [orig_b for orig_b, shifted_b in best_candidate.assignments_to_commit],
                    "total_minutes": best_candidate.total_minutes_covered,
                })

                self.all_breaks = [b for b in self.all_breaks if b.cashier != best_candidate.cashier]
                                
                for original_break, shifted_break in best_candidate.assignments_to_commit:

                    break_owner = original_break.cashier
                    self.all_breaks.remove(original_break)

                    minutes_to_move = time_diff_in_minutes(original_break.start_time, shifted_break.start_time)
                                        
                    success, final_break_object = break_owner.try_move_interval(
                        original_break, minutes_to_move, commit=True
                    )

                    if not success:
                        self.all_breaks.append(original_break)
                        continue

                    # Assign the covered break to the reliever's schedule and link the reliever
                    best_candidate.cashier.add_interval(original_break)
                    original_break.tauottaja = best_candidate.cashier

            else:
                # Handle unassigned breaks
                for b in self.all_breaks:
                    final_assignments.append({
                        "tauottaja": None,
                        "breaks_covered": [b],
                        "total_minutes": b.length_in_minutes()
                    })
                break

        self.breaks_schedule_list = final_assignments
        return final_assignments
        
    def _find_best_cashier_assignment(self, available_cashiers: List["Cashier"]) -> AssignmentCandidate | None:

        best_candidate = None

        for candidate_cashier in available_cashiers:
            candidate_result = self._simulate_cashier_coverage(candidate_cashier)
            if not candidate_result.assignments_to_commit or candidate_result.total_minutes_covered < self.REQUIRED_MIN_COVERAGE:
                continue
                
            # Initialization
            if best_candidate is None:
                best_candidate = candidate_result
                continue
            
            # Primary Key: length in minutes (Greater is better)
            if candidate_result.total_minutes_covered > best_candidate.total_minutes_covered:
                best_candidate = candidate_result
        
        return best_candidate

    def _simulate_cashier_coverage(self, cashier: "Cashier") -> AssignmentCandidate:
        """
        Simulates fitting all unassigned breaks into the cashier's schedule 
        using the +/- 30 min flexibility.
        """
        
        candidate = AssignmentCandidate(cashier)
        
        # 1. CRITICAL: Get the cashier's available time blocks only once.
        available_windows = cashier.copy_availability()

        # Filter own breaks out and sort chronologically
        breaks_to_fit = sorted(
            [b for b in self.all_breaks if b.cashier is not cashier],
            key=lambda b: b.start_time
        )

        valid_shift_moves = [-30, -15, 0, 15, 30]
        last_assigned_end_time = datetime.min
        
        for break_ in breaks_to_fit:
            
            best_shift_interval = None
            best_end_time = datetime.max 
            
            for shift_move in valid_shift_moves:
                
                # Check 1: Is the shifted time valid in the break owner's schedule?
                fits_cashiers_break_schedule, new_possible_break = break_.cashier.try_move_interval(
                    break_, shift_move, commit=False
                )
                if not fits_cashiers_break_schedule:
                    continue
                
                is_available = any(
                    window.contains(new_possible_break) for window in available_windows
                )
                
                if is_available: 
                    # Tie-breaker: If this new valid shift ends earlier than the current best, select it.
                    if new_possible_break.end_time < best_end_time:
                        best_end_time = new_possible_break.end_time
                        best_shift_interval = new_possible_break

            # Commit the best found shift, if any
            if best_shift_interval:
                
                new_available_windows = []
                
                # Iterate and subtract the block from all windows it overlaps
                for window in available_windows:
                    try:
                        non_overlapping_parts = window.subtract(best_shift_interval)
                        
                        new_available_windows.extend(
                            non_overlapping_parts
                        )
                    except ValueError:
                        # If subtraction fails (no overlap), preserve the window.
                        new_available_windows.append(window)

                available_windows = new_available_windows
                bonus = 0
                
                if best_shift_interval.start_time == last_assigned_end_time:
                    bonus = self.BONUS_PER_CONSECUTIVE_BREAK
                if best_shift_interval.end_time.hour < self.EARLY_BREAK_BOUNDARY_HOUR:
                    bonus += self.EARLY_BREAK_BONUS
                elif best_shift_interval.start_time.hour >= self.LATE_BREAK_BOUNDARY_HOUR:
                    bonus += self.LATE_BREAK_BONUS
                candidate.assignments_to_commit.append((break_, best_shift_interval))
                minutes = break_.length_in_minutes() + bonus
                candidate.total_minutes_covered += minutes
                last_assigned_end_time = best_shift_interval.end_time
                
        return candidate