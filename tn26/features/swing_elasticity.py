"""Mathematical calculator for seat-vote elasticity, FPTP hurdle rates, and uniform swing curves."""
from collections import Counter
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd

from tn26.config import AIADMK_FRONT_PARTIES, SPA_PARTIES, TOTAL_ASSEMBLY_SEATS, TVK_PARTY
from tn26.data_ingestion.eci_parser import ECIResultParser


class SwingElasticityCalculator:
    """Computes electoral swing dynamics, seat sensitivity, and FPTP elasticity."""

    def __init__(self, parser: Optional[ECIResultParser] = None):
        self.parser = parser or ECIResultParser()

    def simulate_uniform_swing(
        self,
        shift_pct_points: float,
        from_party: str = "TVK",
        mode: str = "transfer",
    ) -> Dict[str, Union[float, int, List[int]]]:
        """Simulate a uniform percentage point shift across all 234 ACs.

        Parameters:
            shift_pct_points: Percentage points of total constituency ballots to shift.
            from_party: Party whose vote share is altered (default TVK).
            mode: 'transfer' adds shifted votes to the local strongest non-TVK rival;
                  'abstain' removes votes without reallocation.

        Returns:
            Dictionary with resulting seat totals and flipped constituency IDs.
        """
        df = self.parser.load_constituency_margins()
        parties = Counter()
        lost_acs = []

        for _, row in df.iterrows():
            ac_no = int(row["ac_no"])
            winner = row["winner_party_abbreviation"]
            margin = int(row["margin_votes"])
            total = int(row["total_votes"])

            # Compute margin reduction
            removed_votes = total * (shift_pct_points / 100.0)
            threshold = removed_votes * (2.0 if mode == "transfer" else 1.0)

            if winner == from_party and margin < threshold:
                winner = row["runner_up_party_abbreviation"]
                lost_acs.append(ac_no)

            parties[winner] += 1

        dmk_bloc = sum(count for p, count in parties.items() if p in SPA_PARTIES)
        admk_bloc = sum(count for p, count in parties.items() if p in AIADMK_FRONT_PARTIES)

        return {
            "mode": mode,
            "shift_pct_points": shift_pct_points,
            "TVK_seats": parties[TVK_PARTY],
            "DMK_seats": parties["DMK"],
            "ADMK_seats": parties["ADMK"],
            "DMK_led_bloc_seats": dmk_bloc,
            "AIADMK_led_bloc_seats": admk_bloc,
            "TVK_seats_lost": len(lost_acs),
            "flipped_ac_numbers": sorted(lost_acs),
        }

    def generate_sensitivity_curve(
        self,
        points_range: Optional[List[float]] = None,
    ) -> pd.DataFrame:
        """Generate seat vulnerability schedules across transfer and abstention modes."""
        if points_range is None:
            points_range = [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0]

        records = []
        for mode in ("transfer", "abstain"):
            for pt in points_range:
                res = self.simulate_uniform_swing(pt, mode=mode)
                records.append({
                    "mode": mode,
                    "shift_points": pt,
                    "tvk_seats": res["TVK_seats"],
                    "dmk_bloc_seats": res["DMK_led_bloc_seats"],
                    "admk_bloc_seats": res["AIADMK_led_bloc_seats"],
                    "seats_lost_by_tvk": res["TVK_seats_lost"],
                })

        return pd.DataFrame(records)

    def compute_seat_vote_elasticity(self, delta_pct: float = 1.0) -> Dict[str, float]:
        """Compute the empirical seat-vote elasticity parameter:
        e = (% change in seats) / (% change in votes)
        under First-Past-The-Post (FPTP) multi-cornered contest rules.
        """
        baseline = self.simulate_uniform_swing(0.0, mode="transfer")
        swung = self.simulate_uniform_swing(delta_pct, mode="transfer")

        s0 = baseline["TVK_seats"]
        s1 = swung["TVK_seats"]

        pct_seat_change = ((s1 - s0) / s0) * 100.0
        elasticity = abs(pct_seat_change / delta_pct)

        return {
            "baseline_tvk_seats": s0,
            "swung_tvk_seats": s1,
            "seats_lost_per_point_transfer": s0 - s1,
            "seat_vote_elasticity": round(elasticity, 3),
        }

    def compute_constituency_vulnerability_profile(self) -> pd.DataFrame:
        """Classify all 234 ACs into vulnerability tiers based on victory margin."""
        df = self.parser.load_constituency_margins()
        df["margin_pct"] = (df["margin_votes"].astype(int) / df["total_votes"].astype(int)) * 100.0

        def tier(margin_pct):
            if margin_pct < 1.0:
                return "Hyper-Marginal (<1%)"
            elif margin_pct < 3.0:
                return "Marginal (1-3%)"
            elif margin_pct < 7.0:
                return "Moderate (3-7%)"
            elif margin_pct < 15.0:
                return "Comfortable (7-15%)"
            return "Dominant (>15%)"

        df["vulnerability_tier"] = df["margin_pct"].apply(tier)
        return df
