"""Ingestion and empirical bias audit for pre-poll and exit poll agencies."""
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np
import pandas as pd

from tn26.config import DATA_RAW_DIR, GROUND_TRUTH_2026


class PollHarvester:
    """Ingestion engine and statistical auditor for polling surveys."""

    def __init__(self, raw_data_dir: Optional[Path] = None):
        self.raw_dir = raw_data_dir or DATA_RAW_DIR
        self._polls_df: Optional[pd.DataFrame] = None

    def load_polls(self) -> pd.DataFrame:
        """Load archived opinion and exit polls dataset."""
        if self._polls_df is not None:
            return self._polls_df.copy()

        poll_path = self.raw_dir / "opinion_and_exit_polls_2026.csv"
        if not poll_path.exists():
            raise FileNotFoundError(f"Missing poll dataset at {poll_path}")

        df = pd.read_csv(poll_path, encoding="utf-8")
        self._polls_df = df
        return df.copy()

    def compute_pollster_error_metrics(self) -> pd.DataFrame:
        """Compute forensic error metrics for each polling organization.

        Evaluates:
        - TVK Absolute Error (Seats)
        - DMK Alliance Absolute Error (Seats)
        - AIADMK Alliance Absolute Error (Seats)
        - Total Variation Distance (TVD) across seat allocations
        - Pro-Incumbent Bias Index
        """
        df = self.load_polls()
        actual_tvk = GROUND_TRUTH_2026["TVK"]
        actual_dmk = GROUND_TRUTH_2026["DMK_led_bloc"]
        actual_admk = GROUND_TRUTH_2026["AIADMK_led_bloc"]

        metrics = []
        for _, row in df.iterrows():
            err_tvk = row["tvk_seats_mid"] - actual_tvk
            err_dmk = row["dmk_front_seats_mid"] - actual_dmk
            err_admk = row["admk_front_seats_mid"] - actual_admk

            abs_err_tvk = abs(err_tvk)
            abs_err_dmk = abs(err_dmk)
            abs_err_admk = abs(err_admk)
            mae = (abs_err_tvk + abs_err_dmk + abs_err_admk) / 3.0

            # Total Variation Distance (TVD) on seat shares
            pred_shares = np.array([row["tvk_seats_mid"], row["dmk_front_seats_mid"], row["admk_front_seats_mid"]]) / 234.0
            actual_shares = np.array([actual_tvk, actual_dmk, actual_admk]) / 234.0
            tvd = 0.5 * np.sum(np.abs(pred_shares - actual_shares))

            # Directional Pro-Incumbent Bias Index (Positive indicates pro-DMK tilt)
            bias_index = err_dmk - err_tvk

            metrics.append({
                "pollster": row["pollster"],
                "type": row["type"],
                "sample_size": row["sample_size"],
                "predicted_tvk": row["tvk_seats_mid"],
                "actual_tvk": actual_tvk,
                "error_tvk": err_tvk,
                "abs_error_tvk": abs_err_tvk,
                "predicted_dmk_bloc": row["dmk_front_seats_mid"],
                "actual_dmk_bloc": actual_dmk,
                "error_dmk_bloc": err_dmk,
                "predicted_admk_bloc": row["admk_front_seats_mid"],
                "actual_admk_bloc": actual_admk,
                "error_admk_bloc": err_admk,
                "mean_absolute_error_seats": round(mae, 2),
                "total_variation_distance": round(tvd, 4),
                "pro_incumbent_bias_index": round(bias_index, 2),
                "house_effect_classification": row["house_effect_bias"],
            })

        metrics_df = pd.DataFrame(metrics).sort_values(by="mean_absolute_error_seats", ascending=True)
        return metrics_df

    def detect_herding_behavior(self) -> Dict[str, float]:
        """Statistical test for pollster herding (clustering around a false consensus).

        If the variance of seat predictions across independent pollsters is significantly
        smaller than expected under binomial sampling variance, it indicates herding.
        """
        df = self.load_polls()
        # Exclude post-hoc academic study for pre-election herding test
        pre_exit_polls = df[df["pollster"] != "PollsMap Computational Model"]

        tvk_preds = pre_exit_polls["tvk_seats_mid"].values
        dmk_preds = pre_exit_polls["dmk_front_seats_mid"].values

        tvk_variance = float(np.var(tvk_preds, ddof=1))
        dmk_variance = float(np.var(dmk_preds, ddof=1))

        # Expected variance under binomial sampling with average sample size ~35,000
        avg_n = pre_exit_polls["sample_size"].mean()
        # Expected seat variance if pollsters sampled truly independently
        p_dmk_pred = dmk_preds.mean() / 234.0
        theoretical_sampling_sd_shares = np.sqrt(p_dmk_pred * (1 - p_dmk_pred) / avg_n)
        theoretical_seat_sd = theoretical_sampling_sd_shares * 234.0

        return {
            "mean_predicted_tvk_seats": round(float(np.mean(tvk_preds)), 1),
            "tvk_prediction_variance": round(tvk_variance, 2),
            "tvk_prediction_std": round(float(np.std(tvk_preds, ddof=1)), 2),
            "mean_predicted_dmk_seats": round(float(np.mean(dmk_preds)), 1),
            "dmk_prediction_variance": round(dmk_variance, 2),
            "dmk_prediction_std": round(float(np.std(dmk_preds, ddof=1)), 2),
            "theoretical_binomial_seat_sd": round(float(theoretical_seat_sd), 2),
            "herding_index": round(float(tvk_variance / (dmk_variance + 1e-6)), 3),
        }
