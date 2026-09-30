"""Visualization of voter transition flows, Markov matrices, and coalition provenance."""
from pathlib import Path
from typing import Optional
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from tn26.config import PLOTS_DIR
from tn26.models.voter_transition_matrix import EcologicalInferenceVoterFlow
from tn26.visualization.style import apply_academic_style


class VoterFlowVisualizer:
    """Generates voter transition heatmaps and demographic flow diagrams."""

    def __init__(
        self,
        ei_model: Optional[EcologicalInferenceVoterFlow] = None,
        output_dir: Optional[Path] = None,
    ):
        self.ei_model = ei_model or EcologicalInferenceVoterFlow()
        self.output_dir = output_dir or PLOTS_DIR
        apply_academic_style()

    def plot_transition_matrix_heatmap(self, filename: str = "voter_transition_heatmap.png") -> Path:
        """Render annotated heatmap of 2021 to 2026 voter transition probabilities."""
        df_trans = self.ei_model.estimate_transition_matrix()

        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(
            df_trans,
            annot=True,
            fmt=".1f",
            cmap="Blues",
            cbar_kws={"label": "Transition Probability (%)"},
            ax=ax,
            linewidths=0.5,
        )

        ax.set_title("Voter Transition Matrix: 2021 Base to 2026 Assembly Returns")
        ax.set_xlabel("2026 Destination Vote Choice")
        ax.set_ylabel("2021 Baseline Political Alignment")
        plt.tight_layout()

        out_path = self.output_dir / filename
        plt.savefig(out_path, dpi=300)
        plt.close()
        return out_path

    def plot_tvk_provenance_breakdown(self, filename: str = "tvk_coalition_provenance.png") -> Path:
        """Render donut chart showing origin of TVK's winning voter coalition."""
        provenance = self.ei_model.compute_tvk_coalition_provenance()

        labels = [
            "AIADMK Disillusioned Base",
            "DMK Anti-Incumbent Leakers",
            "Youth & First-Time Voters",
            "NTK / Independent Discontents",
        ]
        values = [
            provenance["tvk_voters_from_aiadmk_disillusioned_pct"],
            provenance["tvk_voters_from_dmk_anti_incumbents_pct"],
            provenance["tvk_voters_from_youth_and_new_voters_pct"],
            provenance["tvk_voters_from_ntk_tamil_youth_pct"],
        ]
        colors = ["#00873E", "#003366", "#C41E3A", "#8B0000"]

        fig, ax = plt.subplots(figsize=(7, 7))
        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            autopct="%1.1f%%",
            pctdistance=0.75,
            colors=colors,
            startangle=140,
            wedgeprops=dict(width=0.45, edgecolor="white", linewidth=1.5),
        )

        ax.set_title("Provenance of TVK Winning Coalition (2026 Election)")
        plt.tight_layout()

        out_path = self.output_dir / filename
        plt.savefig(out_path, dpi=300)
        plt.close()
        return out_path
