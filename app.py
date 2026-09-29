"""Streamlit demo: upload leads, get priorities and first-reply drafts."""
import os

import pandas as pd
import streamlit as st

from lead_qualifier import baseline, llm
from lead_qualifier.pipeline import qualify, time_saved_hours

st.set_page_config(page_title="AI Lead Qualifier", layout="wide")
st.title("AI Lead Qualifier")
st.caption("Prioritise inbound leads for a digital marketing agency and draft the first reply.")

uploaded = st.file_uploader("Upload a CSV of leads (same columns as data/sample_leads.csv)", type="csv")
leads = pd.read_csv(uploaded) if uploaded else pd.read_csv("data/sample_leads.csv")
st.write(f"{len(leads)} leads loaded" + ("" if uploaded else " (sample data)"))

has_key = bool(os.environ.get("ANTHROPIC_API_KEY"))
engine = st.radio(
    "Qualification engine",
    ["Claude (LLM)", "Keyword rules (baseline)"],
    index=0 if has_key else 1,
    horizontal=True,
    help="Claude needs ANTHROPIC_API_KEY. The baseline runs offline.",
)
if engine.startswith("Claude") and not has_key:
    st.warning("Set ANTHROPIC_API_KEY to use Claude. Showing the keyword baseline instead.")
    engine = "Keyword rules (baseline)"

minutes_manual = st.sidebar.slider("Minutes a salesperson spends reading and replying to one lead", 2, 15, 6)
minutes_review = st.sidebar.slider("Minutes to review one AI assessment", 0.5, 5.0, 1.0)

if st.button("Qualify leads", type="primary"):
    assess = llm.assess if engine.startswith("Claude") else baseline.assess
    with st.spinner("Qualifying..."):
        results = qualify(leads, assess)

    counts = results["priority"].value_counts()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("A: contact today", int(counts.get("A", 0)))
    c2.metric("B: this week", int(counts.get("B", 0)))
    c3.metric("Disqualified", int(counts.get("Disqualify", 0)))
    c4.metric("Hours saved (this batch)", f"{time_saved_hours(len(leads), minutes_manual, minutes_review):.1f}")

    st.dataframe(
        results[["priority", "fit_score", "name", "company", "urgency", "budget_signal", "decision_maker", "reasoning", "next_action"]],
        width="stretch", hide_index=True,
    )

    drafts = results[results["email_draft"].str.len() > 0]
    if not drafts.empty:
        st.subheader("First-reply drafts")
        for _, row in drafts.iterrows():
            with st.expander(f"{row['priority']} · {row['name']} ({row['company']})"):
                st.write(row["email_draft"])

    st.download_button("Download results (CSV)", results.to_csv(index=False), "qualified_leads.csv")
