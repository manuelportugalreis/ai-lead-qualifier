"""Run a whole CSV of leads through a qualifier and compare against human labels."""
from typing import Callable

import pandas as pd

from .schema import LeadAssessment

PRIORITY_ORDER = {"A": 0, "B": 1, "C": 2, "Disqualify": 3}


def qualify(leads: pd.DataFrame, assess: Callable[[dict], LeadAssessment]) -> pd.DataFrame:
    rows = []
    for lead in leads.fillna("").to_dict(orient="records"):
        result = assess(lead).model_dump()
        rows.append({"lead_id": lead["lead_id"], "name": lead["name"], "company": lead["company"], **result})
    out = pd.DataFrame(rows)
    out["_order"] = out["priority"].map(PRIORITY_ORDER)
    return out.sort_values(["_order", "fit_score"], ascending=[True, False]).drop(columns="_order")


def accuracy(results: pd.DataFrame, labels: pd.DataFrame) -> float:
    merged = results.merge(labels, on="lead_id")
    return float((merged["priority"] == merged["expected_priority"]).mean())


def time_saved_hours(n_leads: int, minutes_manual: float = 6.0, minutes_review: float = 1.0) -> float:
    """Hours saved per batch if a salesperson only reviews the AI output instead of reading every lead."""
    return n_leads * (minutes_manual - minutes_review) / 60
