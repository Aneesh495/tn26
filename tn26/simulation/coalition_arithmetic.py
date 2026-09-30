"""Legislative coalition assembly, floor test stability, and governing pact simulations."""
from typing import Dict, List, Optional, Union
import pandas as pd

from tn26.config import MAJORITY_SEAT_THRESHOLD, TOTAL_ASSEMBLY_SEATS


class LegislativeCoalitionSimulator:
    """Simulates post-election floor tests and confidence-and-supply governance arrangements."""

    def __init__(self, majority_threshold: int = MAJORITY_SEAT_THRESHOLD):
        self.threshold = majority_threshold
        # Official 2026 Assembly party strength
        self.party_seats = {
            "TVK": 108,
            "DMK": 58,
            "ADMK": 44,
            "INC": 8,
            "BJP": 5,
            "VCK": 4,
            "PMK": 4,
            "IUML": 2,
            "CPI": 1,
        }

    def simulate_pact(self, core_party: str, partner_parties: List[str]) -> Dict[str, Union[str, int, bool, float]]:
        """Simulate a proposed coalition arrangement and compute surplus and stability index."""
        coalition = [core_party] + partner_parties
        total_seats = sum(self.party_seats.get(p, 0) for p in coalition)
        surplus = total_seats - self.threshold
        is_viable = total_seats >= self.threshold

        # Stability index: scales with surplus cushion and penalizes heterogeneous coalition size
        # Stability = Surplus / (1 + 0.15 * (number of coalition partners - 1))
        stability_score = round(max(0.0, surplus / (1.0 + 0.15 * max(0, len(partner_parties)))), 2)

        return {
            "core_party": core_party,
            "partner_parties": partner_parties,
            "total_parties": len(coalition),
            "total_seats": total_seats,
            "majority_threshold": self.threshold,
            "surplus_cushion": surplus,
            "is_viable_majority": is_viable,
            "legislative_stability_score": stability_score,
        }

    def evaluate_all_standard_scenarios(self) -> pd.DataFrame:
        """Evaluate major political scenarios debated after the 2026 election."""
        scenarios = [
            ("TVK Minority Government with External Confidence & Supply", "TVK", ["INC", "VCK"]),
            ("TVK Centrist Progressive Coalition", "TVK", ["INC", "IUML", "CPI"]),
            ("Grand Dravidian Duopoly Coalition (DMK + ADMK)", "DMK", ["ADMK"]),
            ("Opposition Non-TVK Anti-Insurgent Front (DMK + ADMK + BJP + PMK)", "DMK", ["ADMK", "BJP", "PMK"]),
            ("TVK Standalone Single-Party Minority", "TVK", []),
        ]

        results = []
        for name, core, partners in scenarios:
            res = self.simulate_pact(core, partners)
            results.append({
                "scenario_name": name,
                "total_seats": res["total_seats"],
                "surplus": res["surplus_cushion"],
                "viable": res["is_viable_majority"],
                "stability_score": res["legislative_stability_score"],
            })

        return pd.DataFrame(results)
