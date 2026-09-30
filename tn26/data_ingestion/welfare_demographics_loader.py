"""Loader and feature processor for socioeconomic, demographic, and welfare datasets."""
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np
import pandas as pd

from tn26.config import DATA_RAW_DIR, TOTAL_ASSEMBLY_SEATS


class WelfareDemographicsLoader:
    """Loader and transformer for constituency-level socioeconomic and scheme data."""

    def __init__(self, raw_data_dir: Optional[Path] = None):
        self.raw_dir = raw_data_dir or DATA_RAW_DIR
        self._demo_df: Optional[pd.DataFrame] = None

    def load_demographics(self) -> pd.DataFrame:
        """Load demographic, reservation, and welfare scheme indicators."""
        if self._demo_df is not None:
            return self._demo_df.copy()

        demo_path = self.raw_dir / "demographic_and_welfare_234ac.csv"
        if not demo_path.exists():
            raise FileNotFoundError(f"Missing demographic dataset at {demo_path}")

        df = pd.read_csv(demo_path, encoding="utf-8")
        assert len(df) == TOTAL_ASSEMBLY_SEATS, f"Expected 234 ACs, got {len(df)}"
        self._demo_df = df
        return df.copy()

    def get_welfare_elasticity_features(self) -> pd.DataFrame:
        """Extract and normalize key welfare penetration indicators.

        Computes:
        - KMUT female beneficiary ratio
        - Higher education scheme coverage (Pudhumai Penn / Tamil Pudhalvan)
        - TASMAC outlet density per 100,000 electorate
        - Youth demographic pressure ratio
        """
        df = self.load_demographics()
        df["kmut_per_electorate"] = df["kmut_female_beneficiaries"] / df["total_electorate"]
        df["education_aid_per_electorate"] = (
            df["pudhumai_penn_beneficiaries"] + df["tamil_pudhalvan_beneficiaries"]
        ) / df["total_electorate"]
        df["tasmac_per_100k_electorate"] = (df["tasmac_outlets_count"] / df["total_electorate"]) * 100000.0

        # Z-score standardization of welfare saturation
        welfare_cols = [
            "kmut_coverage_pct",
            "education_aid_per_electorate",
            "tasmac_per_100k_electorate",
            "youth_voter_share_pct",
            "urbanization_pct",
        ]
        for col in welfare_cols:
            mean_val = df[col].mean()
            std_val = df[col].std() + 1e-8
            df[f"{col}_zscore"] = (df[col] - mean_val) / std_val

        return df

    def get_district_level_aggregates(self) -> pd.DataFrame:
        """Compute district-level sums and population-weighted averages."""
        df = self.load_demographics()
        agg = df.groupby("district").agg({
            "total_electorate": "sum",
            "kmut_female_beneficiaries": "sum",
            "tasmac_outlets_count": "sum",
            "urbanization_pct": "mean",
            "turnout_pct": "mean",
            "youth_voter_share_pct": "mean",
        }).reset_index()
        return agg
