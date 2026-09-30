"""Cooperative game theory, Shapley values, Banzhaf power, and post-election coalition formation.

Models legislative bargaining and coalition stability in the 234-seat Tamil Nadu Assembly
where TVK won 108 seats, DMK alliance won 73 seats, and AIADMK alliance won 53 seats.
"""
from itertools import combinations
import math
from typing import Dict, List, Optional, Set, Tuple, Union
import pandas as pd

from tn26.config import MAJORITY_SEAT_THRESHOLD, TOTAL_ASSEMBLY_SEATS


class AllianceGameTheoreticEngine:
    """Computes cooperative game-theoretic power indices and government stability."""

    def __init__(self, seat_distribution: Optional[Dict[str, int]] = None):
        # 2026 Legislative Assembly party seat breakdown
        self.seats = seat_distribution or {
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
        self.threshold = MAJORITY_SEAT_THRESHOLD # 118 seats
        self.parties = list(self.seats.keys())
        self.n_parties = len(self.parties)

    def is_winning_coalition(self, coalition: Set[str]) -> bool:
        """Check if a subset of parties crosses the 118-seat majority threshold."""
        total = sum(self.seats[p] for p in coalition)
        return total >= self.threshold

    def compute_shapley_values(self) -> Dict[str, float]:
        """Compute exact Shapley Values for each legislative party.

        phi_i(v) = sum_{S subset N - {i}} [ |S|! (n - |S| - 1)! / n! ] * [ v(S cup {i}) - v(S) ]
        """
        n = self.n_parties
        fact_n = math.factorial(n)
        shapley = {p: 0.0 for p in self.parties}

        # Iterate over all possible subsets excluding party i
        for i_idx, p_i in enumerate(self.parties):
            other_parties = [p for p in self.parties if p != p_i]
            for s_size in range(n):
                weight = (math.factorial(s_size) * math.factorial(n - s_size - 1)) / fact_n
                for s_tuple in combinations(other_parties, s_size):
                    s_set = set(s_tuple)
                    v_s = 1 if self.is_winning_coalition(s_set) else 0
                    v_s_with_i = 1 if self.is_winning_coalition(s_set.union({p_i})) else 0
                    marginal_contribution = v_s_with_i - v_s
                    if marginal_contribution > 0:
                        shapley[p_i] += weight * marginal_contribution

        # Normalize and round
        total_val = sum(shapley.values())
        return {p: round(v / total_val, 4) for p, v in shapley.items()}

    def compute_banzhaf_power_index(self) -> Dict[str, float]:
        """Compute the normalized Banzhaf Power Index measuring voter pivotality.

        Beta_i = (Number of winning coalitions where i is critical) / (Total critical votes)
        """
        pivotal_counts = {p: 0 for p in self.parties}

        # Check all non-empty coalitions
        for k in range(1, self.n_parties + 1):
            for c_tuple in combinations(self.parties, k):
                c_set = set(c_tuple)
                if self.is_winning_coalition(c_set):
                    # Party p is pivotal if removing it causes coalition to fall below 118
                    for p in c_set:
                        sub_c = c_set - {p}
                        if not self.is_winning_coalition(sub_c):
                            pivotal_counts[p] += 1

        total_pivots = sum(pivotal_counts.values())
        if total_pivots == 0:
            return {p: 0.0 for p in self.parties}

        return {p: round(count / total_pivots, 4) for p, count in pivotal_counts.items()}

    def identify_minimal_winning_coalitions(self) -> List[Dict]:
        """Identify all Minimal Winning Coalitions (MWC) in the 2026 assembly.

        A winning coalition is minimal if no proper subset is winning (Riker's Size Principle).
        """
        mwcs = []
        for k in range(1, self.n_parties + 1):
            for c_tuple in combinations(self.parties, k):
                c_set = set(c_tuple)
                if self.is_winning_coalition(c_set):
                    # Check if minimal
                    is_minimal = True
                    for p in c_set:
                        if self.is_winning_coalition(c_set - {p}):
                            is_minimal = False
                            break
                    if is_minimal:
                        total_seats = sum(self.seats[p] for p in c_set)
                        surplus = total_seats - self.threshold
                        mwcs.append({
                            "coalition": sorted(list(c_set)),
                            "total_seats": total_seats,
                            "surplus_seats": surplus,
                            "contains_tvk": "TVK" in c_set,
                        })

        # Sort by smallest surplus (most parsimonious coalition)
        mwcs.sort(key=lambda x: (x["total_seats"], len(x["coalition"])))
        return mwcs

    def evaluate_government_formation_viability(self) -> Dict[str, Union[str, float, List]]:
        """Assess viable governing arrangements following the 2026 election."""
        mwcs = self.identify_minimal_winning_coalitions()
        shapley = self.compute_shapley_values()
        banzhaf = self.compute_banzhaf_power_index()

        # TVK needs only 10 seats to reach 118
        tvk_viable_options = [c for c in mwcs if c["contains_tvk"]]

        return {
            "assembly_status": "Hung Assembly / Plurality Breakthrough",
            "largest_party": "TVK (108 seats)",
            "seats_needed_for_majority": 10,
            "shapley_power_indices": shapley,
            "banzhaf_pivot_indices": banzhaf,
            "total_minimal_winning_coalitions": len(mwcs),
            "tvk_led_minimal_winning_coalitions": tvk_viable_options[:5],
            "grand_coalition_feasibility": "Zero (DMK-ADMK alliance is ideologically and historically intractable)",
            "primary_governing_solution": (
                "TVK formed a stable government by securing issue-based outside support "
                "from non-Dravidian centrist legislators, progressive independents, and selective regional parties."
            ),
        }
