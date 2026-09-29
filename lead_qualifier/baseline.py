"""Rule-based baseline: what many small agencies do today with keyword rules.

It runs without an API key, so the demo always works, and it gives the LLM
something to beat.
"""
import re

from .schema import LeadAssessment

DISQUALIFY = ["not interested", "unsubscribe", "remove me"]
URGENT = ["asap", "urgent", "this week", "next week", "next month"]
DECISION_ROLES = ["owner", "founder", "ceo", "coo", "vp", "director", "head", "partner", "broker"]


def _has_any(text: str, words: list[str]) -> bool:
    return any(w in text for w in words)


def assess(lead: dict) -> LeadAssessment:
    msg = str(lead.get("message", "")).lower()
    role = str(lead.get("role", "")).lower()
    size = lead.get("company_size")
    try:
        size = int(size)
    except (TypeError, ValueError):
        size = 0

    if _has_any(msg, DISQUALIFY) or len(msg.split()) < 4:
        return LeadAssessment(
            priority="Disqualify", fit_score=0, budget_signal="none", urgency="low",
            decision_maker=False, reasoning="Matched a disqualifying keyword or the message is too short.",
            next_action="Archive", email_draft="",
        )

    budget = "explicit" if re.search(r"\$\s?\d", msg) or "budget" in msg else "none"
    urgency = "high" if _has_any(msg, URGENT) else "low"
    decision_maker = _has_any(role, DECISION_ROLES)

    score = 30
    score += 25 if budget == "explicit" else 0
    score += 20 if urgency == "high" else 0
    score += 15 if decision_maker else 0
    score += 10 if size >= 50 else 0

    priority = "A" if score >= 75 else "B" if score >= 55 else "C"
    return LeadAssessment(
        priority=priority, fit_score=min(score, 100), budget_signal=budget, urgency=urgency,
        decision_maker=decision_maker, reasoning=f"Keyword score {score}.",
        next_action="Call today" if priority == "A" else "Email this week" if priority == "B" else "Add to nurture list",
        email_draft="",
    )
