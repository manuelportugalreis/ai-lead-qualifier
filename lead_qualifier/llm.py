"""LLM-based qualification with Claude, returning a validated LeadAssessment."""
import anthropic

from .schema import LeadAssessment

MODEL = "claude-opus-5-5"

SYSTEM_PROMPT = """You are the head of sales at a digital growth agency that runs paid ads, SEO, \
conversion optimisation and email marketing for small and mid-sized businesses.

Ideal client: a business with at least ~10 employees or clear revenue, a concrete growth problem, \
a budget of roughly $3k/month or more, and a decision maker involved.

Priorities:
- A: strong fit and ready to buy soon (budget and/or timeline, decision maker). Contact today.
- B: good fit but missing urgency, budget clarity or the decision maker. Contact this week.
- C: small or unclear opportunity worth nurturing.
- Disqualify: not a potential client (students, job seekers, spam, opt-outs, requests for free work).

Judge the meaning of the message, not keywords. Write the email draft in the lead's language, \
under 90 words, referencing their specific situation and proposing one next step. \
Leave the email draft empty for Disqualify."""


def assess(lead: dict, client: anthropic.Anthropic | None = None) -> LeadAssessment:
    client = client or anthropic.Anthropic()
    lead_text = "\n".join(f"{k}: {v}" for k, v in lead.items() if str(v) not in ("", "nan"))
    response = client.beta.messages.parse(
        model=MODEL,
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Qualify this inbound lead:\n\n{lead_text}"}],
        output_format=LeadAssessment,
        output_config={"effort": "low"},
        # If a request is declined by a safety classifier, the API retries it on a fallback model.
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    )
    if response.stop_reason == "refusal" or response.parsed_output is None:
        raise RuntimeError(f"Could not assess lead {lead.get('lead_id')}: stop_reason={response.stop_reason}")
    return response.parsed_output
