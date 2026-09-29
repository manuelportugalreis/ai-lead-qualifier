"""Compare the keyword baseline and Claude against the hand-written labels.

Usage:
    python evaluate.py            # baseline only
    python evaluate.py --llm      # baseline and Claude (needs ANTHROPIC_API_KEY)
"""
import sys

import pandas as pd

from lead_qualifier import baseline, llm
from lead_qualifier.pipeline import accuracy, qualify

leads = pd.read_csv("data/sample_leads.csv")
labels = pd.read_csv("data/labels.csv")

base = qualify(leads, baseline.assess)
print(f"Keyword baseline accuracy: {accuracy(base, labels):.0%}")

if "--llm" in sys.argv:
    ai = qualify(leads, llm.assess)
    print(f"Claude accuracy:           {accuracy(ai, labels):.0%}")
    ai.to_csv("data/claude_results.csv", index=False)
