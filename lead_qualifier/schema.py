from typing import Literal

from pydantic import BaseModel, Field

Priority = Literal["A", "B", "C", "Disqualify"]


class LeadAssessment(BaseModel):
    """What a senior salesperson would decide after reading a lead."""

    priority: Priority = Field(
        description="A = contact today, B = contact this week, C = nurture, Disqualify = not a potential client"
    )
    fit_score: int = Field(ge=0, le=100, description="How well the lead fits the agency's ideal client")
    budget_signal: Literal["explicit", "implied", "none", "low"]
    urgency: Literal["high", "medium", "low"]
    decision_maker: bool
    reasoning: str = Field(description="One or two sentences explaining the priority")
    next_action: str = Field(description="The single next step for the sales team")
    email_draft: str = Field(description="A short, personal first reply to the lead (empty if Disqualify)")
