"""
SmartOR - Integrated Staff Rostering & Surgical Supply AI Demonstrator
Building AI Course - Final Project (University of Helsinki & Reaktor)
"""

from typing import Dict, Any

# ==========================================
# Module 1: Nurse Rostering Heuristic Solver
# ==========================================
SHIFTS = {
    "D": {"start": 8.0, "duration": 8.0, "category": "DAY"},
    "E": {"start": 16.0, "duration": 8.0, "category": "EVE"},
    "N": {"start": 0.0, "duration": 8.0, "category": "NIGHT"},
}

def evaluate_shift_candidate(
    nurse: Dict[str, Any],
    candidate_shift: str,
    yesterday_shift: str,
    consecutive_workdays: int,
    dept_min_shift_count: int
) -> float:
    # Hard constraint: maximum 6 consecutive work days
    if consecutive_workdays >= 6:
        return float("inf")

    # Hard constraint: minimum 11 hours rest interval
    if yesterday_shift and yesterday_shift in SHIFTS:
        y_end = SHIFTS[yesterday_shift]["start"] + SHIFTS[yesterday_shift]["duration"]
        today_start = SHIFTS[candidate_shift]["start"] + 24.0
        if (today_start - y_end) < 11.0:
            return float("inf")

    score = 0.0

    # Department fairness penalty (prevents shift monopoly)
    current_count = nurse.get("shift_counts", {}).get(candidate_shift, 0)
    score += current_count * 60.0 + (current_count - dept_min_shift_count) * 80.0

    # Fatigue penalty for consecutive days
    if consecutive_workdays >= 4:
        score += (consecutive_workdays - 3) * 150.0

    # Circadian consistency bonus
    if yesterday_shift and yesterday_shift in SHIFTS:
        if SHIFTS[yesterday_shift]["category"] == SHIFTS[candidate_shift]["category"]:
            score -= 30.0

    return score

# ==========================================
# Module 2: Surgical Supply Restock Predictor
# ==========================================
def calculate_surgical_restock(
    item_name: str,
    shelf_stock_morning: int,   # S
    prev_day_order_qty: int,    # Q
    emergency_restock: int,     # E
    today_prep_required: int,   # O
    standard_stock: int,        # R
    holiday_gap_days: int = 0
) -> Dict[str, Any]:
    # Post-preparation remaining balance P = S + Q + E - O
    post_prep_balance = shelf_stock_morning + prev_day_order_qty + emergency_restock - today_prep_required

    # Dynamic safety stock adjustment for holiday/weekend CSR closure
    buffer_multiplier = 1.0 + (0.35 * holiday_gap_days if holiday_gap_days > 0 else 0.0)
    adjusted_standard_stock = int(standard_stock * buffer_multiplier)

    # Theoretical order requirement T = max(0, R_adjusted - P)
    target_order_qty = max(0, adjusted_standard_stock - post_prep_balance)

    return {
        "item": item_name,
        "post_prep_balance_P": post_prep_balance,
        "adjusted_standard_stock": adjusted_standard_stock,
        "recommended_order_U": target_order_qty
    }

# ==========================================
# Integrated System Execution
# ==========================================
if __name__ == "__main__":
    print("=========================================================")
    print(" SmartOR: Integrated Staff Rostering & Restock Engine    ")
    print("=========================================================\n")

    # 1. Staff Rostering Test
    nurse = {"name": "Nurse Lin", "shift_counts": {"D": 5, "E": 2}}
    score_d = evaluate_shift_candidate(nurse, "D", yesterday_shift="D", consecutive_workdays=3, dept_min_shift_count=3)
    score_e = evaluate_shift_candidate(nurse, "E", yesterday_shift="D", consecutive_workdays=3, dept_min_shift_count=2)
    print(f"[Staff] Evaluation for {nurse["name"]}:")
    print(f"  - Shift D Score: {score_d:.1f} | Shift E Score: {score_e:.1f}")
    print(f"  -> Recommended: {"Shift D" if score_d < score_e else "Shift E"} (Lower is better)\n")

    # 2. Supply Restock Test (Laparotomy Pack with a 2-day CSR holiday gap)
    restock = calculate_surgical_restock(
        item_name="Laparotomy Drape Pack",
        shelf_stock_morning=12,
        prev_day_order_qty=8,
        emergency_restock=0,
        today_prep_required=14,
        standard_stock=20,
        holiday_gap_days=2
    )
    print(f"[Supply] Restock Recommendation for {restock["item"]}:")
    print(f"  - Post-Prep Balance (P): {restock["post_prep_balance_P"]} packs")
    print(f"  - Adjusted Standard Target (R): {restock["adjusted_standard_stock"]} packs (with 2-day holiday buffer)")
    print(f"  -> Recommended Order Qty (U): {restock["recommended_order_U"]} packs")
    print("=========================================================")
