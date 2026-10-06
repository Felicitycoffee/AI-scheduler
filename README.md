# SmartOR: Integrated Staff Rostering and Supply Restock AI

Final project for the Building AI course

## Summary

Operating Rooms (ORs) are the most resource-intensive and critical units in any healthcare institution. A successful surgical schedule requires seamless synchronization between two vital pillars: compliant, well-rested clinical staff and just-in-time sterile surgical supply availability. **SmartOR** is an integrated AI-driven operations platform combining a **Multi-Objective Constraint Satisfaction Heuristic Engine** for nurse rostering with a **Predictive Dynamic Buffer Restock Engine** for surgical packs and consumables. By enforcing labor compliance (Taiwan Labor Standards Act 4-week flexible hours, 11-hour rest intervals, circadian consistency) and predicting surgical pack demand ($P = S + Q + E - O$ with holiday supply buffers and habit learning), SmartOR prevents both staff burnout and costly OR stockouts.

---

## Background

Operating room management currently faces two coupled, high-stakes operational bottlenecks:

1. **Staff Rostering Fatigue & Non-Compliance**:
   * **Regulatory Complexity**: Under 4-week flexible working hour frameworks, head nurses must adhere to strict constraints: a 160-hour total cap, at least 8 mandatory days off (4 regular leaves + 4 rest days), a maximum of 6 consecutive work days, and at least 11 consecutive hours of rest between consecutive shifts.
   * **Circadian Disruption & Monopolies**: Manual drafting often creates erratic sleep transitions (e.g., evening shift ending at 22:00 followed by an 08:00 morning shift) and unfair "shift hoarding," leading to clinical fatigue, turnover, and medical errors.
   * **High Administrative Cost**: Head nurses spend 15–25 hours every month manually drafting and revising schedules.

2. **Surgical Pack & Sterile Supply Stockouts vs. Expiration**:
   * **Asymmetric Risk**: Running out of sterile laparotomy drapes or specialty surgical packs mid-operation halts surgery immediately. Conversely, over-ordering leads to sterile shelf-life expiration (>60% waste rate in low-turnover packs) and storage crowding.
   * **Supply Chain Disruption**: Central Sterile Supply Departments (CSR/CSSD) close on weekends and statutory holidays, creating multi-day replenishment blackouts that manual ordering fails to anticipate.

By treating staff rosters and surgical supplies as a unified operational ecosystem, SmartOR guarantees that every scheduled operating theater has both qualified, well-rested personnel and necessary sterile materials.

---

## How is it used?

SmartOR serves surgical department supervisors, head nurses, and OR materials managers through a dual-module automated workflow:

1. **Personnel Rostering (Human Resource Pillar)**:
   * **Constraint & Leave Intake**: Department heads import maternity protections, weekday-only contracts, and pre-booked leaves (annual, public, wedding/bereavement).
   * **Heuristic Scheduling**: The CSP heuristic solver assigns shifts day-by-day across 28-day cycles, optimizing fairness, sleep regularity, and labor limits.
   * **Real-Time Audit**: An automated statutory diagnostics panel monitors compliance, warning against any 11-hour rest violations or consecutive day limits.

2. **Supply Restock & Forecasting (Physical Resource Pillar)**:
   * **Demand Aggregation**: Pulls next-day ($O$) and next-next-day ($N$) surgical booking requirements based on procedure bills of materials (BOM).
   * **Dynamic Inventory Calculation**: Evaluates morning shelf stock ($S$), pending orders ($Q$), and emergency restocks ($E$) to calculate post-preparation balance:
     $$P = S + Q + E - O$$
   * **Holiday-Aware Order Suggestion**: Dynamically scales the theoretical order target $T = \max(0, R - P)$ based on upcoming weekend/holiday supply gap days and learned ordering habits, outputting final orders ($U$) and daily visual check sheets ($V$).

![SmartOR System Architecture](https://raw.githubusercontent.com/Felicitycoffee/work-dey/main/app_icon_transparent.png)

```
┌─────────────────────────────────────────────────────────────┐
│                       SmartOR Platform                      │
├──────────────────────────────┬──────────────────────────────┤
│  MODULE 1: STAFF ROSTERING   │  MODULE 2: SUPPLY RESTOCK    │
├──────────────────────────────┼──────────────────────────────┤
│ • 4-Week Flexible Hours CSP  │ • Surgical Demand BOM (N, O) │
│ • 11h Rest Interval Guard    │ • Post-Prep Balance (P)      │
│ • Circadian Rhythm Buckets   │ • CSR Holiday Gap Scaling    │
│ • Dynamic Anti-Monopoly Bias │ • Bayesian Habit Learning    │
└──────────────┬───────────────┴──────────────┬───────────────┘
               ▼                              ▼
        [ Compliant OR Roster ]       [ Zero-Stockout Orders ]
```

---

## Data sources and AI methods

### Data Sources
* **Hospital Rostering Records**: Department employee lists, skill credentials, statutory leave registries, and historical weekend assignments.
* **Surgical Schedules & BOMs**: Operative schedules mapping planned surgeries to required sterile drape packs and instrument kits.
* **Inventory & CSR Restock Logs**: Morning on-shelf inventory levels ($S$), daily delivery records ($Q$), emergency supplements ($E$), and sterilization lead times.
* **Statutory Holiday APIs**: Public calendar integration (Taiwan Directorate-General of Personnel Administration) for compensatory leaves and supply blackout intervals.

### AI & Algorithmic Methods

SmartOR leverages complementary optimization and predictive modeling approaches across both pillars:

#### 1. Multi-Objective Heuristic Constraint Satisfaction (Staff Rostering)
Staff scheduling is modeled as a constrained combinatorial optimization problem solved via greedy forward heuristic search with lookahead:
* **Multi-Factor Scoring Function**: Candidate nurse $s$ on day $d$ for shift $k$ is evaluated by:
  $$	ext{Score}(s, d, k) = w_1 \cdot 	ext{HoursNorm} + w_2 \cdot 	ext{ShiftFairness}(s, k) + w_3 \cdot 	ext{CircadianJump} + w_4 \cdot 	ext{Fatigue}(s)$$
* **Circadian Biological Buckets**: Categorizes shifts into `DAY` (06:30–09:00), `MID` (09:30–12:00), `EVE` (12:30–18:00), and `NIGHT` (22:00–00:00). Penalizes rapid transitions ($\ge 3$ distinct buckets within 7 days triggers $+4,500$ penalty; identical shift time slots receive $-25$ bonus).
* **Dynamic Anti-Monopoly Weighting**: Stepped penalties ($+60 \sim +140$) prevent high-demand shifts from being captured by specific individuals.
* **Lookahead Rest Enforcement**: Hard filter blocks any shift combination resulting in $< 11$ hours of rest between consecutive calendar days.

#### 2. Dynamic Safety Stock & Habit-Learned Restock Forecasting (Supply Management)
Sterile surgical consumables replenishment requires balancing immediate availability against sterilization expiration:
* **Balance & Target Order Equation**:
  $$P = S + Q + E - O$$
  $$T = \max(0, R_{	ext{adjusted}} - P)$$
* **Holiday Gap Compensation Factor ($\kappa$)**:
  When CSR closure spans $k$ consecutive days (e.g., long holiday weekends), required safety stock $R$ dynamically expands:
  $$R_{	ext{adjusted}} = R 	imes \left(1 + \kappa \cdot \log_2(1 + k)ight)$$
* **Learned Ordering Habit Model**: Incorporates historical manual overrides and empirical order confidence scores to prevent irrational over-ordering of low-turnover specialty packs.

---

### Demonstration Code (Python Prototype)

The following runnable Python prototype demonstrates both the heuristic shift scoring engine and the dynamic surgical pack order calculator:

```python
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
```

---

## Challenges

Integrating human staffing with physical inventory introduces unique real-world complexities:

* **Surgical Delays & Acute Emergencies**: Emergency trauma procedures consume both on-call staff hours and emergency sterile packs ($E$) unpredictably, necessitating real-time re-optimization.
* **Sterile Expiration vs. Stockout Trade-off**: High-value specialty packs (e.g., neurosurgery or pediatric cardiovascular kits) have stringent expiration deadlines; over-buffering during holidays risks costly clinical waste.
* **Algorithmic Explainability & Clinical Trust**: Healthcare professionals require total transparency. Explaining *why* a particular nurse was assigned a night shift or *why* a pack order was throttled is essential for operational adoption.

---

## What next?

The evolution roadmap for SmartOR includes:

1. **Integrated Mixed Integer Linear Programming (MILP)**: Employing Google OR-Tools and SCIP solvers to co-optimize operating room schedule capacity, staff availability, and sterilization autoclave batch schedules simultaneously.
2. **Predictive Surgery Demand Forecasting**: Utilizing machine learning (XGBoost / Temporal Fusion Transformers) on historical EMR surgical case data to forecast weekly surgical pack demand directly from surgeon booking patterns.
3. **Automated RFID & Mobile Restock Verification**: Pairing mobile visual inspection sheets ($V$) with RFID cabinet sensors for real-time inventory synchronization without manual paper tallies.

---

## Acknowledgments

* **Course Affiliation**: Developed for the **Building AI** course created by the **University of Helsinki** and **Reaktor Innovations**.
* **Clinical Domain Insights**: Synthesized from hospital Operating Room operations, Central Sterile Supply Department (CSR/CSSD) logistics, and Taiwanese labor regulations (Article 30-1 Four-Week Flexible Working Hours).
* **Open Source Foundations**: Built with modern web and data tools including [Lucide Icons](https://lucide.dev/), [SheetJS](https://sheetjs.com/), and [Flatpickr](https://flatpickr.js.org/).
