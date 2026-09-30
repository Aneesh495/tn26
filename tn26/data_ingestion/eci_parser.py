"""Parser and statistical validator for Election Commission of India (ECI) records.

Handles constituency-level returns, margin audits, alliance aggregations,
and historical time-series alignment for Tamil Nadu Assembly elections.
"""
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import pandas as pd

from tn26.config import (
    AIADMK_FRONT_PARTIES,
    DATA_RAW_DIR,
    GROUND_TRUTH_2026,
    SPA_PARTIES,
    TOTAL_ASSEMBLY_SEATS,
    TVK_PARTY,
)


class ECIResultParser:
    """Parser and statistical auditor for official ECI electoral datasets."""

    def __init__(self, raw_data_dir: Optional[Path] = None):
        self.raw_dir = raw_data_dir or DATA_RAW_DIR
        self._margins_df: Optional[pd.DataFrame] = None
        self._full_df: Optional[pd.DataFrame] = None
        self._historical_df: Optional[pd.DataFrame] = None
        self._tvk_winners_df: Optional[pd.DataFrame] = None

    def load_constituency_margins(self) -> pd.DataFrame:
        """Load and audit 234 assembly constituency margins.

        Returns:
            DataFrame containing ac_no, winner, runner-up, margins, and totals.
        """
        if self._margins_df is not None:
            return self._margins_df.copy()

        margins_path = self.raw_dir / "constituency_margins.csv"
        if not margins_path.exists():
            raise FileNotFoundError(f"Missing margin dataset at {margins_path}")

        df = pd.read_csv(margins_path, encoding="utf-8-sig")
        self._validate_margins_schema(df)
        self._margins_df = df
        return df.copy()

    def load_official_tvk_winners(self) -> pd.DataFrame:
        """Load independently verified ECI TVK winners table.

        Returns:
            DataFrame containing TVK winner candidates and vote tallies.
        """
        if self._tvk_winners_df is not None:
            return self._tvk_winners_df.copy()

        tvk_path = self.raw_dir / "official_tvk_winners.csv"
        if not tvk_path.exists():
            raise FileNotFoundError(f"Missing TVK winners dataset at {tvk_path}")

        df = pd.read_csv(tvk_path, encoding="utf-8-sig")
        assert len(df) == 108, f"Expected 108 official TVK winners, found {len(df)}"
        self._tvk_winners_df = df
        return df.copy()

    def load_full_results_2026(self) -> pd.DataFrame:
        """Load granular multi-party vote distributions for 2026."""
        if self._full_df is not None:
            return self._full_df.copy()

        full_path = self.raw_dir / "eci_2026_full_results.csv"
        if not full_path.exists():
            raise FileNotFoundError(f"Missing full 2026 results at {full_path}")

        df = pd.read_csv(full_path, encoding="utf-8")
        assert len(df) == TOTAL_ASSEMBLY_SEATS, f"Expected 234 ACs, got {len(df)}"
        self._full_df = df
        return df.copy()

    def load_historical_time_series(self) -> pd.DataFrame:
        """Load longitudinal vote shares from 2011 to 2024."""
        if self._historical_df is not None:
            return self._historical_df.copy()

        hist_path = self.raw_dir / "historical_electoral_time_series_1977_2024.csv"
        if not hist_path.exists():
            raise FileNotFoundError(f"Missing historical dataset at {hist_path}")

        df = pd.read_csv(hist_path, encoding="utf-8")
        assert len(df) == TOTAL_ASSEMBLY_SEATS
        self._historical_df = df
        return df.copy()

    def _validate_margins_schema(self, df: pd.DataFrame) -> None:
        """Perform formal accounting integrity checks on ECI returns."""
        assert len(df) == TOTAL_ASSEMBLY_SEATS, f"Dataset has {len(df)} rows, expected 234"
        assert df["ac_no"].nunique() == TOTAL_ASSEMBLY_SEATS, "AC numbers are not unique"

        # Check arithmetic consistency: Winner Votes - Runner-up Votes == Margin
        calc_margin = df["winner_votes"].astype(int) - df["runner_up_votes"].astype(int)
        mismatches = df[calc_margin != df["margin_votes"].astype(int)]
        if not mismatches.empty:
            raise ValueError(f"Margin arithmetic failure in ACs: {mismatches['ac_no'].tolist()}")

        # Ensure valid total votes constraint
        invalid_totals = df[df["total_votes"].astype(int) < (df["winner_votes"].astype(int) + df["runner_up_votes"].astype(int))]
        if not invalid_totals.empty:
            raise ValueError(f"Total votes less than top two candidates in ACs: {invalid_totals['ac_no'].tolist()}")

    def compute_seat_tallies(self) -> Dict[str, int]:
        """Compute aggregate seat counts by party and by alliance bloc.

        Returns:
            Dictionary containing individual party seats and alliance totals.
        """
        df = self.load_constituency_margins()
        party_counts = df["winner_party_abbreviation"].value_counts().to_dict()

        tvk_seats = party_counts.get("TVK", 0)
        dmk_bloc_seats = sum(count for party, count in party_counts.items() if party in SPA_PARTIES)
        admk_bloc_seats = sum(count for party, count in party_counts.items() if party in AIADMK_FRONT_PARTIES)

        # Confirm exact alignment with ground truth
        assert tvk_seats == GROUND_TRUTH_2026["TVK"], f"TVK seat mismatch: {tvk_seats} != 108"
        assert dmk_bloc_seats == GROUND_TRUTH_2026["DMK_led_bloc"], f"DMK bloc mismatch: {dmk_bloc_seats} != 73"
        assert admk_bloc_seats == GROUND_TRUTH_2026["AIADMK_led_bloc"], f"AIADMK bloc mismatch: {admk_bloc_seats} != 53"

        return {
            "TVK": tvk_seats,
            "DMK": party_counts.get("DMK", 0),
            "ADMK": party_counts.get("ADMK", 0),
            "INC": party_counts.get("INC", 0),
            "BJP": party_counts.get("BJP", 0),
            "VCK": party_counts.get("VCK", 0),
            "PMK": party_counts.get("PMK", 0),
            "IUML": party_counts.get("IUML", 0),
            "DMK_led_bloc": dmk_bloc_seats,
            "AIADMK_led_bloc": admk_bloc_seats,
            "Total_Seats": len(df),
        }

    def classify_bloc(self, party: str) -> str:
        """Classify a political party into its 2026 alliance bloc."""
        if party == TVK_PARTY:
            return "TVK"
        if party in SPA_PARTIES:
            return "DMK-led bloc"
        if party in AIADMK_FRONT_PARTIES:
            return "AIADMK-led bloc"
        return "Other"

    def get_close_contests(self, threshold_votes: int = 5000) -> pd.DataFrame:
        """Extract razor-thin constituencies decided by less than threshold votes."""
        df = self.load_constituency_margins()
        close = df[df["margin_votes"].astype(int) <= threshold_votes].copy()
        close = close.sort_values(by="margin_votes", ascending=True)
        return close

    def get_regional_breakdown(self) -> pd.DataFrame:
        """Compute seat distributions grouped across the 6 geopolitical regions."""
        df = self.load_full_results_2026()
        df["winner_bloc"] = df["winner_party"].apply(self.classify_bloc)
        summary = pd.crosstab(df["region"], df["winner_bloc"], margins=True)
        return summary
