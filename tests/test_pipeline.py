import pandas as pd

from lead_qualifier import baseline
from lead_qualifier.pipeline import accuracy, qualify, time_saved_hours


def test_opt_out_is_disqualified():
    lead = {"lead_id": "X", "name": "A", "company": "B", "role": "Owner", "company_size": 5,
            "message": "Not interested, please remove me from your list."}
    assert baseline.assess(lead).priority == "Disqualify"


def test_budget_urgency_and_decision_maker_is_priority_a():
    lead = {"lead_id": "X", "name": "A", "company": "B", "role": "CEO", "company_size": 200,
            "message": "We have a $10k monthly budget and need to start next month."}
    assert baseline.assess(lead).priority == "A"


def test_pipeline_runs_on_sample_data():
    leads = pd.read_csv("data/sample_leads.csv")
    results = qualify(leads, baseline.assess)
    assert len(results) == len(leads)
    assert 0 <= accuracy(results, pd.read_csv("data/labels.csv")) <= 1


def test_time_saved():
    assert time_saved_hours(60, 6, 1) == 5.0
