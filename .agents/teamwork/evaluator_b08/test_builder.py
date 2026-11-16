import json
import sys
from pathlib import Path

ROOT = Path("/Users/janis.schultz/Library/CloudStorage/OneDrive-Accenture/Private/Projects/Screener")
sys.path.insert(0, str(ROOT))

from screener.bulk_scorer import validate_company_evaluation
from screener.gates import compute_initial_cap_from_scores, compute_final_cap_from_scores

print("Imports succeeded!")
