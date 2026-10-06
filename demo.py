"""
SmartShift - Heuristic Shift Assignment Demonstrator
Building AI Course - Final Project (University of Helsinki & Reaktor)
"""

from typing import List, Dict

SHIFTS = {
    "D": {"start": 8.0, "duration": 8.0, "category": "DAY"},
    "E": {"start": 16.0, "duration": 8.0, "category": "EVE"},
    "N": {"start": 0.0, "duration": 8.0, "category": "NIGHT"},
}

def calculate_assignment_score(
    emp: Dict, 
    shift_code: str, 
    yesterday_shift: str, 
    consecutive_days: int, 
    dept_min_shifts: int
) -> float:
    # 1. Hard Constraint: Consecutive work days strictly capped at 6
    if consecutive_days >= 6:
        return float("inf")
    
    # 2. Hard Constraint: 11-hour minimum rest between shifts
    if yesterday_shift and yesterday_shift in SHIFTS:
        y_end = SHIFTS[yesterday_shift]["start"] + SHIFTS[yesterday_shift]["duration"]
        today_start = SHIFTS[shift_code]["start"] + 24.0
        rest_hours = today_start - y_end
        if rest_hours < 11.0:
            return float("inf") # Illegal under labor law
            
    score = 0.0
    
    # 3. Department Fairness Penalty (Anti-monopoly)
    curr_count = emp.get("shift_counts", {}).get(shift_code, 0)
    score += curr_count * 60 + (curr_count - dept_min_shifts) * 80
    
    # 4. Consecutive work day fatigue penalty
    if consecutive_days == 4:
        score += 120
    elif consecutive_days == 5:
        score += 350
        
    # 5. Circadian rhythm consistency reward
    if yesterday_shift and yesterday_shift in SHIFTS:
        if SHIFTS[yesterday_shift]["category"] == SHIFTS[shift_code]["category"]:
            score -= 25.0 # Reward consistent sleep schedule
            
    return score

if __name__ == "__main__":
    employee = {"name": "Alice", "shift_counts": {"D": 4, "E": 1}}
    score_day = calculate_assignment_score(employee, "D", yesterday_shift="D", consecutive_days=3, dept_min_shifts=2)
    score_eve = calculate_assignment_score(employee, "E", yesterday_shift="D", consecutive_days=3, dept_min_shifts=1)
    
    print("--- SmartShift Scheduling Evaluation ---")
    print(f"Candidate Shift D Score: {score_day} (Lower is better)")
    print(f"Candidate Shift E Score: {score_eve} (Lower is better)")
    print(f"Recommended Shift: {'D' if score_day < score_eve else 'E'}")
