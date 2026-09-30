"""Academic report card and grading engine for pre-poll and exit poll agencies."""
from typing import Dict, List, Optional
import pandas as pd

from tn26.data_ingestion.poll_harvester import PollHarvester


class PollsterForensicScorecard:
    """Evaluates and assigns forensic academic grades to polling agencies for 2026."""

    def __init__(self, harvester: Optional[PollHarvester] = None):
        self.harvester = harvester or PollHarvester()

    def generate_full_report_card(self) -> pd.DataFrame:
        """Assign letter grades (A+ to F) based on statistical error and bias."""
        metrics = self.harvester.compute_pollster_error_metrics()

        grades = []
        for _, row in metrics.iterrows():
            mae = row["mean_absolute_error_seats"]
            tvk_err = abs(row["abs_error_tvk"])

            # Assign academic grade
            if mae < 15.0:
                grade = "A+"
                comment = "Accurately captured ground reality and TVK wave"
            elif mae < 30.0:
                grade = "A"
                comment = "Strong predictive fidelity with minor margin discrepancies"
            elif mae < 50.0:
                grade = "B"
                comment = "Detected general direction but underestimated third-force seat conversion"
            elif mae < 70.0:
                grade = "C"
                comment = "Substantial error anchored in historical duopoly assumptions"
            elif mae < 85.0:
                grade = "D"
                comment = "Severe systemic failure; massive pro-incumbent distortion"
            else:
                grade = "F"
                comment = "Catastrophic forecasting breakdown; completely missed historical election wave"

            grades.append({
                "pollster": row["pollster"],
                "type": row["type"],
                "sample_size": row["sample_size"],
                "mae_seats": mae,
                "tvk_error": tvk_err,
                "grade": grade,
                "forensic_critique": comment,
            })

        return pd.DataFrame(grades)
