"""Academic publication plotting style definitions and aesthetic configurations."""
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns


def apply_academic_style() -> None:
    """Set rigorous publication-standard aesthetics for all figures."""
    plt.rcParams.update({
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
        "font.size": 10,
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
        "axes.labelsize": 10,
        "axes.labelweight": "medium",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.8,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        "legend.frameon": False,
        "figure.titlesize": 14,
        "figure.titleweight": "bold",
        "grid.color": "#E5E5E5",
        "grid.linestyle": "--",
        "grid.linewidth": 0.5,
    })
    sns.set_palette(["#C41E3A", "#003366", "#00873E", "#FF9933", "#8B0000", "#808080"])
