"""Econometric feature factory for direct benefit transfers, welfare saturation, and state revenue extraction."""
from typing import Dict, List, Optional
import numpy as np
import pandas as pd

from tn26.data_ingestion.eci_parser import ECIResultParser
from tn26.data_ingestion.welfare_demographics_loader import WelfareDemographicsLoader


class WelfareSaturationFeatureFactory:
    """Calculates welfare transfer elasticities, buffer scores, and extraction burdens."""

    def __init__(
        self,
        demo_loader: Optional[WelfareDemographicsLoader] = None,
        parser: Optional[ECIResultParser] = None,
    ):
        self.demo_loader = demo_loader or WelfareDemographicsLoader()
        self.parser = parser or ECIResultParser()

    def build_welfare_electoral_matrix(self) -> pd.DataFrame:
        """Merge welfare indicators with 2026 ECI election outcomes.

        Calculates:
        - Monthly transfer volume per constituency (KMUT INR value: 1000 INR/beneficiary/month)
        - Annualized welfare stimulus per AC
        - Estimated alcohol revenue extracted via TASMAC per AC
        - Net Fiscal Benefit Ratio (Annual Cash Transferred / Annual TASMAC Spent)
        - Female voter buffer elasticity
        """
        demo = self.demo_loader.load_demographics()
        results = self.parser.load_full_results_2026()

        df = demo.merge(results, on=["ac_no", "constituency_name", "district", "region"])

        # Financial valuations (INR)
        # KMUT: 1,000 INR per month = 12,000 INR per beneficiary annually
        df["annual_kmut_transfer_crores"] = (
            df["kmut_female_beneficiaries"] * 12000.0
        ) / 10000000.0

        # Education transfers: 1,000 INR per month for 10 months academic year = 10,000 INR
        total_edu_beneficiaries = (
            df["pudhumai_penn_beneficiaries"] + df["tamil_pudhalvan_beneficiaries"]
        )
        df["annual_edu_transfer_crores"] = (
            total_edu_beneficiaries * 10000.0
        ) / 10000000.0

        # Total Direct Cash Transfers
        df["total_direct_transfers_crores"] = (
            df["annual_kmut_transfer_crores"] + df["annual_edu_transfer_crores"]
        )

        # Estimated TASMAC alcohol expenditure per AC:
        # State TASMAC turnover ~45,000 Crores annually / 234 ACs weighted by outlet count
        avg_tasmac_per_ac = 45000.0 / 234.0 # ~192.3 Crores per AC
        state_total_outlets = df["tasmac_outlets_count"].sum()
        df["annual_tasmac_drain_crores"] = (
            df["tasmac_outlets_count"] / state_total_outlets
        ) * 45000.0

        # Net Fiscal Surplus Ratio (Transfers / TASMAC drain)
        # If < 1.0, the state government extracts more in liquor than it returns in welfare cash
        df["welfare_to_drain_ratio"] = (
            df["total_direct_transfers_crores"] / (df["annual_tasmac_drain_crores"] + 1e-4)
        )

        # DMK vote share retention relative to welfare ratio
        df["dmk_retention_index"] = df["dmk_alliance_vote_share_pct"] / 45.38 # Baseline 2021 share

        return df

    def compute_welfare_correlations(self) -> Dict[str, float]:
        """Compute Pearson correlation coefficients between welfare variables and vote shares."""
        df = self.build_welfare_electoral_matrix()

        corr_kmut_dmk = float(df["kmut_coverage_pct"].corr(df["dmk_alliance_vote_share_pct"]))
        corr_kmut_tvk = float(df["kmut_coverage_pct"].corr(df["tvk_vote_share_pct"]))
        corr_tasmac_tvk = float(df["annual_tasmac_drain_crores"].corr(df["tvk_vote_share_pct"]))
        corr_youth_tvk = float(df["youth_voter_share_pct"].corr(df["tvk_vote_share_pct"]))
        corr_ratio_dmk = float(df["welfare_to_drain_ratio"].corr(df["dmk_alliance_vote_share_pct"]))

        return {
            "corr_kmut_coverage_vs_dmk_vote_share": round(corr_kmut_dmk, 3),
            "corr_kmut_coverage_vs_tvk_vote_share": round(corr_kmut_tvk, 3),
            "corr_tasmac_drain_vs_tvk_vote_share": round(corr_tasmac_tvk, 3),
            "corr_youth_share_vs_tvk_vote_share": round(corr_youth_tvk, 3),
            "corr_welfare_to_drain_vs_dmk_vote_share": round(corr_ratio_dmk, 3),
        }
