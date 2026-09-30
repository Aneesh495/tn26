"""Visualizations for regional seat distributions, victory margins, and geographic clusters."""
from pathlib import Path
from typing import Optional
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from tn26.config import BLOC_COLOR_MAP, PLOTS_DIR
from tn26.data_ingestion.eci_parser import ECIResultParser
from tn26.features.swing_elasticity import SwingElasticityCalculator
from tn26.visualization.style import apply_academic_style


class RegionalSeatVisualizer:
    """Renders regional seat distributions and victory margin histograms."""

    def __init__(
        self,
        parser: Optional[ECIResultParser] = None,
        calc: Optional[SwingElasticityCalculator] = None,
        output_dir: Optional[Path] = None,
    ):
        self.parser = parser or ECIResultParser()
        self.calc = calc or SwingElasticityCalculator(self.parser)
        self.output_dir = output_dir or PLOTS_DIR
        apply_academic_style()

    def plot_regional_seat_breakdown(self, filename: str = "regional_seat_distribution.png") -> Path:
        """Plot stacked regional seat totals across the 6 geopolitical zones."""
        summary = self.parser.get_regional_breakdown()
        # Drop 'All' margin row and column for plotting
        plot_data = summary.drop(index="All", columns="All", errors="ignore")

        fig, ax = plt.subplots(figsize=(10, 6))
        plot_data.plot(
            kind="barh",
            stacked=True,
            color=[BLOC_COLOR_MAP.get(c, "#808080") for c in plot_data.columns],
            ax=ax,
            edgecolor="white",
            linewidth=1.0,
        )

        ax.set_title("Tamil Nadu 2026: Regional Legislative Assembly Seat Distribution")
        ax.set_xlabel("Number of Assembly Constituencies Won")
        ax.set_ylabel("Geopolitical Region")
        ax.legend(title="Winning Alliance", loc="lower right")
        plt.tight_layout()

        out_path = self.output_dir / filename
        plt.savefig(out_path, dpi=300)
        plt.close()
        return out_path

    def plot_victory_margin_distribution(self, filename: str = "victory_margins_histogram.png") -> Path:
        """Plot histogram and kernel density of victory margins across all 234 ACs."""
        df = self.parser.load_constituency_margins()
        margins = df["margin_votes"].astype(int)

        fig, ax = plt.subplots(figsize=(9, 5))
        sns.histplot(margins, bins=35, kde=True, color="#003366", ax=ax, edgecolor="black")

        ax.axvline(1000, color="#C41E3A", linestyle="--", linewidth=1.2, label="1,000 Vote Margin")
        ax.axvline(5000, color="#FF9933", linestyle="--", linewidth=1.2, label="5,000 Vote Margin")

        ax.set_title("Distribution of Victory Margins (2026 Tamil Nadu Legislative Assembly)")
        ax.set_xlabel("Victory Margin (Votes)")
        ax.set_ylabel("Number of Constituencies")
        ax.legend(loc="upper right")
        plt.tight_layout()

        out_path = self.output_dir / filename
        plt.savefig(out_path, dpi=300)
        plt.close()
        return out_path
