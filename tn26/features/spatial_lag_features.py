"""Geospatial weight matrix operations, spatial lags, and Moran's I autocorrelation."""
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from tn26.config import DATA_GEO_DIR, TOTAL_ASSEMBLY_SEATS
from tn26.data_ingestion.eci_parser import ECIResultParser


class SpatialLagFeatureGenerator:
    """Constructs spatial lag features and evaluates spatial autocorrelation of votes."""

    def __init__(
        self,
        geo_dir: Optional[Path] = None,
        parser: Optional[ECIResultParser] = None,
    ):
        self.geo_dir = geo_dir or DATA_GEO_DIR
        self.parser = parser or ECIResultParser()
        self._adj_graph: Optional[Dict[int, List[int]]] = None

    def load_adjacency_graph(self) -> Dict[int, List[int]]:
        """Load Queen adjacency graph connecting neighbouring assembly constituencies."""
        if self._adj_graph is not None:
            return self._adj_graph

        graph_file = self.geo_dir / "ac_adjacency_graph.json"
        if not graph_file.exists():
            raise FileNotFoundError(f"Missing adjacency graph at {graph_file}")

        with graph_file.open(encoding="utf-8") as f:
            raw = json.load(f)
            # Keys are stored as strings in JSON; convert to integers
            self._adj_graph = {int(k): [int(x) for x in v] for k, v in raw.items()}
        return self._adj_graph

    def build_spatial_weight_matrix(self) -> np.ndarray:
        """Construct row-standardized spatial weights matrix W (size 234 x 234)."""
        graph = self.load_adjacency_graph()
        n = TOTAL_ASSEMBLY_SEATS
        w = np.zeros((n, n), dtype=float)

        for i in range(1, n + 1):
            neighbors = graph.get(i, [])
            if neighbors:
                weight = 1.0 / len(neighbors)
                for j in neighbors:
                    if 1 <= j <= n:
                        w[i - 1, j - 1] = weight

        return w

    def compute_spatial_lags(self, vote_series: pd.Series) -> pd.Series:
        """Calculate spatial lag W * y for a given constituency-level series."""
        w = self.build_spatial_weight_matrix()
        y = vote_series.values
        lag_y = w.dot(y)
        return pd.Series(lag_y, index=vote_series.index)

    def calculate_morans_i(self, values: np.ndarray) -> Dict[str, float]:
        """Compute Global Moran's I statistic of spatial autocorrelation.

        I = (N / S0) * (sum_i sum_j w_ij (y_i - y_bar)(y_j - y_bar)) / sum_i (y_i - y_bar)^2
        """
        w = self.build_spatial_weight_matrix()
        n = len(values)
        y = values - np.mean(values)
        denominator = np.sum(y ** 2)

        if denominator == 0:
            return {"morans_i": 0.0, "z_score": 0.0, "p_value": 1.0}

        numerator = 0.0
        for i in range(n):
            for j in range(n):
                numerator += w[i, j] * y[i] * y[j]

        s0 = np.sum(w)
        morans_i = (n / s0) * (numerator / denominator)

        # Theoretical expectation under null hypothesis of spatial randomness
        expected_i = -1.0 / (n - 1)

        # Normal approximation variance
        var_i = 1.0 / (n - 1) # Simplified analytical variance
        z_score = (morans_i - expected_i) / np.sqrt(var_i)

        return {
            "morans_i": round(float(morans_i), 4),
            "expected_i": round(float(expected_i), 4),
            "z_score": round(float(z_score), 3),
            "spatial_clustering_detected": bool(morans_i > expected_i and z_score > 1.96),
        }

    def generate_spatial_feature_matrix(self) -> pd.DataFrame:
        """Enrich 2026 ECI dataset with regional spatial lag variables."""
        df = self.parser.load_full_results_2026()
        df = df.sort_values(by="ac_no").reset_index(drop=True)

        df["spatial_lag_tvk_voteshare"] = self.compute_spatial_lags(df["tvk_vote_share_pct"])
        df["spatial_lag_dmk_voteshare"] = self.compute_spatial_lags(df["dmk_alliance_vote_share_pct"])
        df["spatial_lag_admk_voteshare"] = self.compute_spatial_lags(df["admk_alliance_vote_share_pct"])

        # Spatial Spillover Delta (Local vote share minus neighbor average)
        df["tvk_spatial_spillover_delta"] = df["tvk_vote_share_pct"] - df["spatial_lag_tvk_voteshare"]
        return df
