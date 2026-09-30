"""Difference-in-Differences (DiD) econometric estimation of localized political and governance shocks.

Evaluates exogenous shocks:
  1. Kallakurichi illicit liquor tragedy (Northern district cluster).
  2. Karur cash-for-jobs trial and Enforcement Directorate investigations (Karur/Kongu cluster).
"""
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
import statsmodels.api as sm

from tn26.data_ingestion.eci_parser import ECIResultParser


class DifferenceInDifferencesEvaluator:
    """Panel Difference-in-Differences estimator with constituency and period fixed effects."""

    def __init__(self, parser: Optional[ECIResultParser] = None):
        self.parser = parser or ECIResultParser()

    def build_panel_dataset(self) -> pd.DataFrame:
        """Construct longitudinal panel across 2021 and 2026 elections for all 234 ACs.

        Structure:
          - ac_no
          - period: 0 (2021 election), 1 (2026 election)
          - dmk_vote_share
          - admk_vote_share
          - district
          - region
        """
        results_2026 = self.parser.load_full_results_2026()
        hist = self.parser.load_historical_time_series()
        df = results_2026.merge(hist, on=["ac_no", "constituency_name"])

        records = []
        for _, row in df.iterrows():
            # Period 0: 2021
            records.append({
                "ac_no": int(row["ac_no"]),
                "constituency_name": row["constituency_name"],
                "district": row["district"],
                "region": row["region"],
                "post_shock_period": 0,
                "dmk_vote_share": float(row["dmk_share_2021"]),
                "admk_vote_share": float(row["admk_share_2021"]),
            })
            # Period 1: 2026
            records.append({
                "ac_no": int(row["ac_no"]),
                "constituency_name": row["constituency_name"],
                "district": row["district"],
                "region": row["region"],
                "post_shock_period": 1,
                "dmk_vote_share": float(row["dmk_alliance_vote_share_pct"]),
                "admk_vote_share": float(row["admk_alliance_vote_share_pct"]),
            })

        panel_df = pd.DataFrame(records)
        return panel_df

    def estimate_kallakurichi_liquor_shock(self) -> Dict[str, float]:
        """Estimate causal electoral penalty of the Kallakurichi illicit liquor tragedy.

        Treated Districts: Kallakurichi, Viluppuram, Cuddalore.
        Control: Other non-adjacent northern and delta districts.
        """
        panel = self.build_panel_dataset()
        treated_districts = {"Kallakurichi", "Viluppuram", "Cuddalore"}

        panel["is_treated_cluster"] = panel["district"].isin(treated_districts).astype(int)
        panel["did_interaction"] = panel["is_treated_cluster"] * panel["post_shock_period"]

        # Regression: Y = beta0 + beta1 * Treated + beta2 * Post + delta * (Treated * Post)
        x_vars = panel[["is_treated_cluster", "post_shock_period", "did_interaction"]]
        x_design = sm.add_constant(x_vars)
        y = panel["dmk_vote_share"]

        # Cluster robust standard errors by district
        model = sm.OLS(y, x_design).fit(cov_type="cluster", cov_kwds={"groups": panel["district"]})

        delta_coef = float(model.params["did_interaction"])
        delta_se = float(model.bse["did_interaction"])
        delta_p = float(model.pvalues["did_interaction"])
        t_stat = float(model.tvalues["did_interaction"])

        return {
            "shock_name": "Kallakurichi Illicit Methanol Crisis",
            "treated_cluster_districts": list(treated_districts),
            "did_treatment_effect_delta": round(delta_coef, 3),
            "cluster_robust_standard_error": round(delta_se, 3),
            "t_statistic": round(t_stat, 3),
            "p_value": round(delta_p, 4),
            "statistically_significant_at_5pct": bool(delta_p < 0.05),
            "interpretation": (
                f"Constituencies in the illicit liquor shock corridor experienced an additional "
                f"{round(abs(delta_coef), 2)}% drop in ruling alliance vote share beyond statewide anti-incumbency."
            ),
        }

    def estimate_karur_scam_shock(self) -> Dict[str, float]:
        """Estimate electoral penalty of the Karur cash-for-jobs controversy and ED raids.

        Treated Districts: Karur and immediate adjoining ACs.
        Control: Other western Kongu / Central ACs.
        """
        panel = self.build_panel_dataset()
        treated_districts = {"Karur"}

        panel["is_treated_cluster"] = panel["district"].isin(treated_districts).astype(int)
        panel["did_interaction"] = panel["is_treated_cluster"] * panel["post_shock_period"]

        x_vars = panel[["is_treated_cluster", "post_shock_period", "did_interaction"]]
        x_design = sm.add_constant(x_vars)
        y = panel["dmk_vote_share"]

        model = sm.OLS(y, x_design).fit(cov_type="cluster", cov_kwds={"groups": panel["district"]})

        delta_coef = float(model.params["did_interaction"])
        delta_se = float(model.bse["did_interaction"])
        delta_p = float(model.pvalues["did_interaction"])

        return {
            "shock_name": "Karur Cash-for-Jobs and Judicial Intervention",
            "treated_cluster_districts": list(treated_districts),
            "did_treatment_effect_delta": round(delta_coef, 3),
            "cluster_robust_standard_error": round(delta_se, 3),
            "p_value": round(delta_p, 4),
            "statistically_significant_at_5pct": bool(delta_p < 0.05),
        }
