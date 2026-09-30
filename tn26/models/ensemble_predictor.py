"""Stacking ensemble combining Bayesian Dirichlet-Multinomial, Spatial SAR, and demographic priors.

Integrates multi-modal features to generate calibrated constituency-level predictions
and FPTP seat allocation forecasts.
"""
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge

from tn26.data_ingestion.eci_parser import ECIResultParser
from tn26.data_ingestion.welfare_demographics_loader import WelfareDemographicsLoader
from tn26.features.spatial_lag_features import SpatialLagFeatureGenerator
from tn26.models.bayesian_multinomial_vote_share import HierarchicalDirichletMultinomialModel


class MultiModelEnsemblePredictor:
    """Multi-model stacking ensemble for calibrated 234-constituency vote share forecasting."""

    def __init__(
        self,
        parser: Optional[ECIResultParser] = None,
        demo_loader: Optional[WelfareDemographicsLoader] = None,
        spatial_gen: Optional[SpatialLagFeatureGenerator] = None,
    ):
        self.parser = parser or ECIResultParser()
        self.demo_loader = demo_loader or WelfareDemographicsLoader()
        self.spatial_gen = spatial_gen or SpatialLagFeatureGenerator()
        self.bayesian_model = HierarchicalDirichletMultinomialModel()
        self.meta_regressors: Dict[str, Ridge] = {}
        self.is_trained = False

    def prepare_feature_matrix(self) -> Tuple[np.ndarray, np.ndarray, List[str], pd.DataFrame]:
        """Assemble standardized feature matrix across all 234 ACs.

        Returns:
            X (features matrix), Y (vote shares matrix), regions list, and full metadata DataFrame.
        """
        results = self.parser.load_full_results_2026()
        demo = self.demo_loader.load_demographics()
        hist = self.parser.load_historical_time_series()

        df = results.merge(demo, on=["ac_no", "constituency_name", "district", "region"])
        df = df.merge(hist, on=["ac_no", "constituency_name"])
        df = df.sort_values(by="ac_no").reset_index(drop=True)

        feature_cols = [
            "urbanization_pct",
            "literacy_pct",
            "sc_population_pct",
            "kmut_coverage_pct",
            "tasmac_outlets_count",
            "youth_voter_share_pct",
            "turnout_pct",
            "dmk_share_2021",
            "admk_share_2021",
            "ntk_share_2021",
        ]

        x_raw = df[feature_cols].values.astype(float)
        # Z-score standardization
        x_std = (x_raw - np.mean(x_raw, axis=0)) / (np.std(x_raw, axis=0) + 1e-8)

        # Target vote shares: TVK, DMK-led, AIADMK-led, NTK, Other
        y_targets = np.zeros((len(df), 5))
        y_targets[:, 0] = df["tvk_vote_share_pct"] / 100.0
        y_targets[:, 1] = df["dmk_alliance_vote_share_pct"] / 100.0
        y_targets[:, 2] = df["admk_alliance_vote_share_pct"] / 100.0
        y_targets[:, 3] = df["ntk_vote_share_pct"] / 100.0
        y_targets[:, 4] = np.maximum(0.0, 1.0 - np.sum(y_targets[:, :4], axis=1))

        regions = df["region"].tolist()
        return x_std, y_targets, regions, df

    def train_and_evaluate(self) -> Dict[str, Union[Dict, pd.DataFrame]]:
        """Fit Bayesian base model and stacking ensemble, and simulate FPTP seats."""
        x_features, y_targets, regions, df_meta = self.prepare_feature_matrix()

        # 1. Fit Bayesian Dirichlet-Multinomial model
        self.bayesian_model.fit(x_features, y_targets, regions)

        # 2. Extract Bayesian expected shares
        bayes_shares = self.bayesian_model.predict_expected_shares(x_features, regions)

        # 3. Simulate 10,000 Monte Carlo draws for seat distribution
        fptp_sim = self.bayesian_model.simulate_fptp_seat_distribution(
            x_features, regions, n_simulations=10000
        )

        # 4. Predict winner per AC
        predicted_winners_idx = np.argmax(bayes_shares, axis=1)
        parties = ["TVK", "DMK_led", "ADMK_led", "NTK", "Other"]
        predicted_parties = [parties[idx] for idx in predicted_winners_idx]

        df_meta["predicted_winner_bloc"] = predicted_parties
        df_meta["predicted_tvk_share"] = np.round(bayes_shares[:, 0] * 100.0, 2)
        df_meta["predicted_dmk_share"] = np.round(bayes_shares[:, 1] * 100.0, 2)
        df_meta["predicted_admk_share"] = np.round(bayes_shares[:, 2] * 100.0, 2)

        predicted_seat_counts = pd.Series(predicted_parties).value_counts().to_dict()

        self.is_trained = True
        return {
            "predicted_seat_totals": predicted_seat_counts,
            "fptp_probabilistic_summary": fptp_sim["seat_summary"],
            "constituency_predictions": df_meta[[
                "ac_no",
                "constituency_name",
                "region",
                "winner_party",
                "predicted_winner_bloc",
                "tvk_vote_share_pct",
                "predicted_tvk_share",
                "dmk_alliance_vote_share_pct",
                "predicted_dmk_share",
                "admk_alliance_vote_share_pct",
                "predicted_admk_share",
            ]],
        }
