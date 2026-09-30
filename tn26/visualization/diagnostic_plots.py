"""Diagnostic plots for polling errors, Shapley power indices, and seat sensitivity curves."""
from pathlib import Path
from typing import Optional
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from tn26.config import PLOTS_DIR
from tn26.data_ingestion.poll_harvester import PollHarvester
from tn26.features.swing_elasticity import SwingElasticityCalculator
from tn26.models.alliance_game_theory import AllianceGameTheoreticEngine
from tn26.visualization.style import apply_academic_style


class ForensicDiagnosticPlots:
    """Renders forensic diagnostic plots for academic evaluation."""

    def __init__(
        self,
        harvester: Optional[PollHarvester] = None,
        game_engine: Optional[AllianceGameTheoreticEngine] = None,
        calc: Optional[SwingElasticityCalculator] = None,
        output_dir: Optional[Path] = None,
    ):
        self.harvester = harvester or PollHarvester()
        self.game_engine = game_engine or AllianceGameTheoreticEngine()
        self.calc = calc or SwingElasticityCalculator()
        self.output_dir = output_dir or PLOTS_DIR
        apply_academic_style()

    def plot_pollster_seat_errors(self, filename: str = "pollster_seat_error_comparison.png") -> Path:
        """Render bar chart comparing TVK seat underestimation across all major pollsters."""
        metrics = self.harvester.compute_pollster_error_metrics()
        # Filter out theoretical post-election models
        field_polls = metrics[metrics["pollster"] != "PollsMap Computational Model"].copy()
        field_polls = field_polls.sort_values(by="abs_error_tvk", ascending=False)

        fig, ax = plt.subplots(figsize=(10, 5.5))
        sns.barplot(
            data=field_polls,
            x="abs_error_tvk",
            y="pollster",
            color="#C41E3A",
            ax=ax,
            edgecolor="black",
        )

        ax.set_title("Systemic Polling Failure: TVK Seat Underestimation by Agency")
        ax.set_xlabel("Absolute Error in TVK Assembly Seats (Actual = 108)")
        ax.set_ylabel("Polling Organization")
        plt.tight_layout()

        out_path = self.output_dir / filename
        plt.savefig(out_path, dpi=300)
        plt.close()
        return out_path

    def plot_shapley_power_indices(self, filename: str = "legislative_shapley_values.png") -> Path:
        """Render bar chart of cooperative game-theoretic Shapley Values."""
        shapley = self.game_engine.compute_shapley_values()
        df_power = pd.DataFrame(list(shapley.items()), columns=["Party", "Shapley_Value"])
        df_power = df_power.sort_values(by="Shapley_Value", ascending=False)

        fig, ax = plt.subplots(figsize=(8, 4.5))
        sns.barplot(
            data=df_power,
            x="Shapley_Value",
            y="Party",
            color="#003366",
            ax=ax,
            edgecolor="black",
        )

        ax.set_title("Post-Election Legislative Bargaining Power (Shapley Value)")
        ax.set_xlabel("Normalized Shapley Value (Probability of Pivotal Contribution)")
        ax.set_ylabel("Political Party")
        plt.tight_layout()

        out_path = self.output_dir / filename
        plt.savefig(out_path, dpi=300)
        plt.close()
        return out_path

    def plot_seat_sensitivity_curves(self, filename: str = "seat_sensitivity_curves.png") -> Path:
        """Render uniform vote swing sensitivity curves for TVK, DMK+, and AIADMK+."""
        curve_df = self.calc.generate_sensitivity_curve()

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), sharey=True)

        transfer_df = curve_df[curve_df["mode"] == "transfer"]
        ax1.plot(transfer_df["shift_points"], transfer_df["tvk_seats"], marker="o", color="#C41E3A", label="TVK Seats")
        ax1.plot(transfer_df["shift_points"], transfer_df["dmk_bloc_seats"], marker="s", color="#003366", label="DMK Alliance")
        ax1.plot(transfer_df["shift_points"], transfer_df["admk_bloc_seats"], marker="^", color="#00873E", label="AIADMK Alliance")
        ax1.axhline(118, color="black", linestyle="--", linewidth=0.8, label="118 Majority Mark")
        ax1.set_title("Mode A: Vote Transfer to Closest Rival")
        ax1.set_xlabel("Percentage Points Shifted Away from TVK")
        ax1.set_ylabel("Assembly Seats Won")
        ax1.legend()

        abstain_df = curve_df[curve_df["mode"] == "abstain"]
        ax2.plot(abstain_df["shift_points"], abstain_df["tvk_seats"], marker="o", color="#C41E3A", label="TVK Seats")
        ax2.plot(abstain_df["shift_points"], abstain_df["dmk_bloc_seats"], marker="s", color="#003366", label="DMK Alliance")
        ax2.plot(abstain_df["shift_points"], abstain_df["admk_bloc_seats"], marker="^", color="#00873E", label="AIADMK Alliance")
        ax2.axhline(118, color="black", linestyle="--", linewidth=0.8)
        ax2.set_title("Mode B: Voter Abstention (Votes Removed)")
        ax2.set_xlabel("Percentage Points Removed from TVK")
        plt.tight_layout()

        out_path = self.output_dir / filename
        plt.savefig(out_path, dpi=300)
        plt.close()
        return out_path
