<!-- This is the markdown template for the final project of the Building AI course, 
created by Reaktor Innovations and University of Helsinki. 
Copy the template, paste it to your GitHub README and edit! -->

# SmartShift: Intelligent Auto-Scheduler for Shift Workers

Final project for the Building AI course (University of Helsinki & Reaktor)

---

## Summary

SmartShift is an intelligent constraint-satisfaction scheduling system that automates 4-week flexible work shifts under strict statutory labor regulations. It balances departmental staffing demands, guarantees mandatory rest periods and circadian consistency, and dynamically eliminates shift monopolies across team members.

---

## Background

Managing staff rosters in healthcare, retail, and 24/7 service departments is notoriously complex and labor-intensive. In many jurisdictions—such as Taiwan's Labor Standards Act Article 30-1 (Four-Week Flexible Working Hours)—schedulers must satisfy intricate mathematical and statutory rules:

* **Legal non-compliance risks**: A 4-week cycle must strictly cap total working hours at 160 hours, guarantee at least 8 mandatory days off (4 regular leaves + 4 rest days), and limit consecutive workdays to 6 days.
* **Circadian disruption and worker fatigue**: Poor manual scheduling often causes severe biological rhythm shifts (e.g., finishing an evening shift at 22:00 and starting an early morning shift at 08:00 with less than 11 hours of rest).
* **Shift monopoly and unfairness**: Certain staff members often monopolize favorable or lucrative shifts ("shift hoarding"), while others are disproportionately assigned unpopular weekend or night duties.
* **Administrative overhead**: Department heads and head nurses typically spend 15 to 25 hours every month manually drafting and revising schedules.

---

## How is it used?

SmartShift is designed for department supervisors, head nurses, and HR managers. The scheduling workflow operates in four clear stages:

1. **Input & Lock**: Import staff constraints (e.g., maternity night-shift bans, weekday-only workers) and pre-booked annual/medical leaves.
2. **AI Schedule Generation**: The heuristic constraint-satisfaction engine assigns shifts day-by-day using multi-objective scoring and lookahead evaluation.
3. **Interactive Visual Review**: Supervisors inspect the interactive 28-day calendar grid, using a brush toolbar for micro-adjustments.
4. **Statutory Compliance Audit**: An automated diagnostics panel evaluates each staff member's total hours, legal days off, and resting intervals, reporting pass/violation metrics in real time.

![System Architecture & Workflow](https://raw.githubusercontent.com/Felicitycoffee/work-dey/main/app_icon_transparent.png)

```
[ Pre-Booked Leaves & Rules ] ──► [ Heuristic CSP Engine ] ──► [ Collapsible Legal Audit ] ──► [ Export / Print ]
                                       ▲
[ Circadian & Fairness Penalty ] ──────┘
```

---

## Data sources and AI methods

### Data Sources
* **Internal Rosters**: Employee profiles, skill certifications, special legal constraints, and department requirements.
* **Statutory Holiday Calendars**: Integrated open data from government administrative APIs (e.g., Taiwan Directorate-General of Personnel Administration) for automatic public holiday compensatory leave calculations.
* **Historical Schedule Records**: Cached monthly assignment matrices stored locally to track cumulative weekend distribution.

### AI & Algorithmic Methods
SmartShift frames monthly nurse and personnel rostering as a **Multi-Objective Constraint Satisfaction Problem (CSP)** combined with **Heuristic Search Optimization**:

1. **Greedy Heuristic Assignment with Lookahead**:
   The engine scores candidate staff $s$ for each shift on day $d$ using a multi-factor objective function:
   $$\text{Score}(s, d, \text{shift}) = w_1 \cdot \Delta_{\text{hours}} + w_2 \cdot \text{Fairness}(s) + w_3 \cdot \text{CircadianJump} + w_4 \cdot \text{ConsecutiveDays}$$
2. **Dynamic Reverse-Weight Fairness Balancing**:
   Tracks real-time shift frequencies across the department. Staff with higher assignments of specific shifts receive stepped penalty weights ($+60 \sim +140$), preventing "fixed shift monopolies".
3. **Circadian Rhythm Modeling (Biological Time Buckets)**:
   Shifts are classified into chronological clusters (`DAY`: 06:30–09:00, `MID`: 09:30–12:00, `EVE`: 12:30–18:00, `NIGHT`: 22:00–00:00). Introducing $\ge 3$ distinct clusters within a single week triggers a heavy penalty ($+4,500$) to protect sleep health.
4. **Hard Lookahead Constraints**:
   Evaluates day $d-1$ (backward) and day $d+1$ (forward). Any transition providing $< 11$ hours of consecutive rest is filtered out immediately.

---

### Demonstration Code (Python Prototype)

The core heuristic scoring and assignment pipeline can be demonstrated with the following self-contained Python script:

```python
"""
SmartShift - Heuristic Shift Assignment Demonstrator
Calculates priority scores based on fairness, consecutive work days, and circadian consistency.
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

# Example Execution
if __name__ == "__main__":
    employee = {"name": "Alice", "shift_counts": {"D": 4, "E": 1}}
    score_day = calculate_assignment_score(employee, "D", yesterday_shift="D", consecutive_days=3, dept_min_shifts=2)
    score_eve = calculate_assignment_score(employee, "E", yesterday_shift="D", consecutive_days=3, dept_min_shifts=1)
    
    print(f"Candidate Shift D Score: {score_day} (Lower is better)")
    print(f"Candidate Shift E Score: {score_eve} (Lower is better)")
    print(f"Recommended Shift: {'D' if score_day < score_eve else 'E'}")
```

---

## Challenges

While SmartShift automates schedule construction and ensures labor compliance, several domain challenges remain:

* **Unpredictable Short-Term Leaves**: The system plans static monthly schedules; sudden emergency medical leaves or acute hospital surges still require on-call substitutions.
* **Mathematical Infeasibility**: If a department's total headcount falls below the mathematical lower bound required for 24/7 staffing, no algorithm can satisfy all legal constraints without overtime or auxiliary personnel.
* **Algorithmic Trust & Ethical Transparency**: Employees must trust that assignment distributions are fair. Providing transparent diagnostic breakdowns is essential to prevent perceived bias.

---

## What next?

Future developments for SmartShift include:

1. **Integer Linear Programming (ILP) & Hybrid SAT Solvers**: Integrating Google OR-Tools to verify global Pareto optimality alongside heuristic speed.
2. **Peer-to-Peer Shift Swap Engine**: Using recommendation algorithms to facilitate mutual shift exchanges that preserve compliance without manager intervention.
3. **Mobile & Messaging Bot Integration**: Exporting schedules directly into calendar subscriptions (iCal/Google Calendar) and LINE notifications for real-time leave requests.

---

## Acknowledgments

* **Course Inspiration**: Developed as part of the *Building AI* curriculum by the **University of Helsinki** and **Reaktor Innovations**.
* **Statutory Framework**: Guided by the **Labor Standards Act of Taiwan** (Article 30-1 Four-Week Flexible Working Hours regulations).
* **Open Source Tools**: Powered by [Lucide Icons](https://lucide.dev/) (ISC License), [SheetJS](https://sheetjs.com/) (Apache 2.0), and [Flatpickr](https://flatpickr.js.org/) (MIT License).
