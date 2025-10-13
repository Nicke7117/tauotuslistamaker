from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from ..utils import time_diff_in_minutes
from typing import List, Dict, Tuple, Any, TYPE_CHECKING

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
                available_cashiers.remove(best_candidate.cashier)  

                # Remove all breaks of this tauottaja from further consideration
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

                    best_candidate.cashier.add_interval(original_break)
                    original_break.tauottaja = best_candidate.cashier

                    # Also remove the cashier whose break was just added from available_cashiers
                    if original_break.cashier in available_cashiers:
                        available_cashiers.remove(original_break.cashier)

            else:
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
        """Searches all cashiers and returns the one who can cover the most minutes."""
        
        best_candidate = None

        for candidate_cashier in available_cashiers:
            candidate_result = self._simulate_cashier_coverage(candidate_cashier)
            
            if not best_candidate or candidate_result.total_minutes_covered > best_candidate.total_minutes_covered:
                best_candidate = candidate_result

        return best_candidate

    def _simulate_cashier_coverage(self, cashier: "Cashier") -> AssignmentCandidate:
        """
        Simulates fitting all unassigned breaks into the cashier's schedule 
        using the +/- 30 min flexibility.
        """
        
        candidate = AssignmentCandidate(cashier)
        temp_schedule = cashier.copy_schedule()
        
        # Filter own breaks out and sort chronologically
        breaks_to_fit = sorted(
            [b for b in self.all_breaks if b.cashier is not cashier],
            key=lambda b: b.start_time
        )

        valid_shift_moves = [-30, -15, 0, 15, 30]
        MAX_DATETIME = datetime.max

        for break_ in breaks_to_fit:
            
            best_shift_interval = None
            best_end_time = MAX_DATETIME 
                        
            # Find the best non-conflicting shift
            for shift_move in valid_shift_moves:
                
                # Check 1: Is the shifted time valid in the break owner's schedule?
                fits_cashiers_break_schedule, new_possible_break = break_.cashier.try_move_interval(
                    break_, shift_move, commit=False
                )

                if not fits_cashiers_break_schedule:
                    continue

                # Check 2: Does the shifted break conflict with anything in the reliever's temp schedule?
                can_add_to_temp_schedule = temp_schedule.can_add_interval(new_possible_break) 
                
                if can_add_to_temp_schedule: 
                    
                    # Tie-breaker: If this new valid shift ends earlier than the current best, select it.
                    if new_possible_break.end_time < best_end_time:
                        best_end_time = new_possible_break.end_time
                        best_shift_interval = new_possible_break

            # Commit the best found shift, if any
            if best_shift_interval:
                
                # Add the best shift interval to the temporary schedule to block time 
                temp_schedule.add_interval(best_shift_interval)
                                
                # Record the assignment tuple (original_break, best_shift_interval)
                candidate.assignments_to_commit.append((break_, best_shift_interval))
                
                # Update total covered minutes
                minutes = break_.length_in_minutes()
                candidate.total_minutes_covered += minutes
                
        return candidate
