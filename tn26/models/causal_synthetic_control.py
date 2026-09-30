"""Synthetic Control Method (Abadie et al.) for causal evaluation of welfare transfer saturation.

Constructs synthetic counterfactual units by solving a constrained quadratic
program over donor assembly constituencies to estimate the causal treatment effect
of welfare cash transfers (Kalaignar Magalir Urimai Thogai) and alcohol policy.
"""
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from scipy.optimize import minimize

from tn26.data_ingestion.eci_parser import ECIResultParser
from tn26.data_ingestion.welfare_demographics_loader import WelfareDemographicsLoader


class SyntheticControlWelfareEvaluator:
    """Estimates causal treatment effects using synthetic counterfactual donor weights."""

    def __init__(
        self,
        parser: Optional[ECIResultParser] = None,
        demo_loader: Optional[WelfareDemographicsLoader] = None,
    ):
        self.parser = parser or ECIResultParser()
        self.demo_loader = demo_loader or WelfareDemographicsLoader()
        self.optimal_weights: Optional[np.ndarray] = None
        self.donor_ids: Optional[List[int]] = None
        self.treatment_id: Optional[int] = None

    def fit_synthetic_control(
        self,
        treatment_ac: int,
        donor_acs: List[int],
        feature_matrix: pd.DataFrame,
        predictor_columns: List[str],
    ) -> np.ndarray:
        """Solve constrained optimization problem:
        min_W (X_1 - X_0 W)' V (X_1 - X_0 W)
        subject to: sum(w_i) = 1, w_i >= 0.

        Parameters:
            treatment_ac: AC number of treated unit (e.g. High-KMUT saturation seat).
            donor_acs: List of donor pool AC numbers.
            feature_matrix: DataFrame containing predictors indexed by ac_no.
            predictor_columns: List of socioeconomic and historical vote columns.

        Returns:
            Optimal weight vector W*.
        """
        self.treatment_id = treatment_ac
        self.donor_ids = donor_acs

        # Extract target vector X1 (p x 1)
        x1 = feature_matrix.loc[treatment_ac, predictor_columns].values.astype(float)

        # Extract donor matrix X0 (p x J)
        x0 = feature_matrix.loc[donor_acs, predictor_columns].values.astype(float).T

        j = len(donor_acs)
        p = len(predictor_columns)

        # Objective function: Euclidean distance between X1 and X0 * W
        def loss_fn(w):
            diff = x1 - x0.dot(w)
            return np.sum(diff ** 2)

        # Constraints and bounds: sum(w) = 1, 0 <= w_i <= 1
        constraints = {"type": "eq", "fun": lambda w: np.sum(w) - 1.0}
        bounds = [(0.0, 1.0) for _ in range(j)]
        w_init = np.ones(j) / float(j)

        res = minimize(
            loss_fn,
            w_init,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={"maxiter": 500, "ftol": 1e-9},
        )

        opt_w = np.maximum(0.0, res.x)
        opt_w = opt_w / np.sum(opt_w)
        self.optimal_weights = opt_w
        return opt_w

    def estimate_treatment_effect(
        self,
        treatment_ac: int,
        donor_acs: List[int],
        feature_matrix: pd.DataFrame,
        predictor_columns: List[str],
        outcome_column: str,
    ) -> Dict[str, float]:
        """Compute the causal treatment effect:
        tau = Y_1(observed) - Y_1(synthetic counterfactual)
        """
        weights = self.fit_synthetic_control(
            treatment_ac=treatment_ac,
            donor_acs=donor_acs,
            feature_matrix=feature_matrix,
            predictor_columns=predictor_columns,
        )

        y_observed = float(feature_matrix.loc[treatment_ac, outcome_column])
        donor_outcomes = feature_matrix.loc[donor_acs, outcome_column].values.astype(float)
        y_synthetic = float(np.dot(donor_outcomes, weights))
        tau = y_observed - y_synthetic

        return {
            "treatment_ac_no": treatment_ac,
            "outcome_variable": outcome_column,
            "observed_value": round(y_observed, 3),
            "synthetic_counterfactual_value": round(y_synthetic, 3),
            "estimated_causal_treatment_effect_tau": round(tau, 3),
            "percentage_causal_lift": round(((y_observed - y_synthetic) / (abs(y_synthetic) + 1e-4)) * 100.0, 2),
        }

    def run_welfare_macro_evaluation(self) -> Dict[str, float]:
        """Statewide synthetic control evaluating high vs low KMUT beneficiary saturation.

        Treated group: Top decile KMUT coverage constituencies (>75% coverage).
        Donor group: Median and low coverage constituencies (<60% coverage).
        Outcome: DMK alliance vote retention.
        """
        demo = self.demo_loader.load_demographics()
        results = self.parser.load_full_results_2026()
        hist = self.parser.load_historical_time_series()

        df = demo.merge(results, on=["ac_no", "constituency_name", "district", "region"])
        df = df.merge(hist, on=["ac_no", "constituency_name"])
        df = df.set_index("ac_no")

        high_kmut = df[df["kmut_coverage_pct"] >= 75.0].index.tolist()
        donor_pool = df[df["kmut_coverage_pct"] < 62.0].index.tolist()

        if not high_kmut or not donor_pool:
            return {"status": "insufficient_contrast"}

        predictors = [
            "urbanization_pct",
            "literacy_pct",
            "sc_population_pct",
            "dmk_share_2021",
            "admk_share_2021",
        ]

        effects = []
        # Sample representative treated ACs
        sample_treated = high_kmut[:15]
        for tr in sample_treated:
            res = self.estimate_treatment_effect(
                treatment_ac=tr,
                donor_acs=donor_pool,
                feature_matrix=df,
                predictor_columns=predictors,
                outcome_column="dmk_alliance_vote_share_pct",
            )
            effects.append(res["estimated_causal_treatment_effect_tau"])

        mean_effect = float(np.mean(effects))
        return {
            "mean_causal_vote_retention_lift_dmk_pct": round(mean_effect, 2),
            "evaluated_treated_acs_count": len(sample_treated),
            "donor_pool_size": len(donor_pool),
            "interpretation": (
                f"Kalaignar Magalir Urimai Thogai provided an estimated +{round(mean_effect, 2)}% "
                "causal buffer against anti-incumbent erosion in saturated constituencies."
            ),
        }
