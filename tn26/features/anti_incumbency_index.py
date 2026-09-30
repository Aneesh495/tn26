"""Multi-tier decomposition of electoral anti-incumbency and opposition fragmentation."""
from typing import Dict, List, Optional
import numpy as np
import pandas as pd

from tn26.config import TOTAL_ASSEMBLY_SEATS
from tn26.data_ingestion.eci_parser import ECIResultParser
from tn26.data_ingestion.welfare_demographics_loader import WelfareDemographicsLoader


class AntiIncumbencyDecomposer:
    """Decomposes electoral attrition into structural, local MLA, and regime components."""

    def __init__(
        self,
        parser: Optional[ECIResultParser] = None,
        demo_loader: Optional[WelfareDemographicsLoader] = None,
    ):
        self.parser = parser or ECIResultParser()
        self.demo_loader = demo_loader or WelfareDemographicsLoader()

    def build_incumbency_feature_matrix(self) -> pd.DataFrame:
        """Construct multi-level anti-incumbency feature vectors for all 234 ACs.

        Metrics calculated:
        - 2021 to 2026 Vote Swing (DMK alliance attrition)
        - 2021 to 2026 AIADMK alliance erosion (Third-place displacement)
        - Turnout shock differential
        - Local MLA seat retention status
        - Regime penalty index (composite of TASMAC density, urbanization, youth share)
        """
        results_2026 = self.parser.load_full_results_2026()
        hist = self.parser.load_historical_time_series()
        demo = self.demo_loader.load_demographics()

        # Merge datasets on ac_no
        merged = results_2026.merge(hist, on=["ac_no", "constituency_name"])
        merged = merged.merge(demo, on=["ac_no", "constituency_name", "district", "region"])

        # Compute swing against ruling party (DMK alliance)
        # DMK 2021 Assembly Share minus DMK 2026 Total Vote Share
        merged["dmk_vote_swing_2021_to_2026"] = (
            merged["dmk_share_2021"] - merged["dmk_alliance_vote_share_pct"]
        )

        # AIADMK erosion (2021 Assembly Share minus 2026 Share)
        merged["admk_vote_swing_2021_to_2026"] = (
            merged["admk_share_2021"] - merged["admk_alliance_vote_share_pct"]
        )

        # TVK penetration rate (Vote share captured by TVK in its first election)
        merged["tvk_insurgency_penetration"] = merged["tvk_vote_share_pct"]

        # Incumbent MLA flip indicator
        # 1 if seat changed winner party from 2021, 0 otherwise
        merged["seat_flipped_from_2021"] = (
            merged["winner_party_2021"] != merged["winner_party"]
        ).astype(int)

        # Composite Regime Penalty Index:
        # High youth population + High TASMAC density - KMUT buffering effect
        regime_penalty = (
            0.40 * merged["youth_voter_share_pct"]
            + 0.35 * (merged["tasmac_outlets_count"] / merged["total_electorate"] * 100000.0)
            - 0.25 * merged["kmut_coverage_pct"]
        )
        merged["regime_penalty_index"] = (regime_penalty - regime_penalty.mean()) / regime_penalty.std()

        return merged

    def summarize_statewide_attrition(self) -> Dict[str, float]:
        """Compute aggregate statewide anti-incumbency and swing statistics."""
        df = self.build_incumbency_feature_matrix()

        mean_dmk_swing = float(df["dmk_vote_swing_2021_to_2026"].mean())
        mean_admk_erosion = float(df["admk_vote_swing_2021_to_2026"].mean())
        mean_tvk_share = float(df["tvk_insurgency_penetration"].mean())
        total_seats_flipped = int(df["seat_flipped_from_2021"].sum())
        flip_rate_pct = round((total_seats_flipped / TOTAL_ASSEMBLY_SEATS) * 100.0, 2)

        return {
            "mean_dmk_alliance_vote_swing_pct": round(mean_dmk_swing, 2),
            "mean_admk_alliance_vote_erosion_pct": round(mean_admk_erosion, 2),
            "mean_tvk_vote_share_captured_pct": round(mean_tvk_share, 2),
            "total_constituencies_flipped": total_seats_flipped,
            "turnover_flip_rate_pct": flip_rate_pct,
        }
