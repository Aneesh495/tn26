#!/usr/bin/env python3
"""Econometric execution script for Synthetic Control and Difference-in-Differences models."""
from tn26.data_ingestion.eci_parser import ECIResultParser
from tn26.data_ingestion.welfare_demographics_loader import WelfareDemographicsLoader
from tn26.features.welfare_saturation import WelfareSaturationFeatureFactory
from tn26.models.causal_synthetic_control import SyntheticControlWelfareEvaluator
from tn26.models.difference_in_differences import DifferenceInDifferencesEvaluator


def main():
    print("=" * 80)
    print("  TN26 CAUSAL INFERENCE & ECONOMETRIC EVALUATION SUITE")
    print("=" * 80)

    parser = ECIResultParser()
    demo_loader = WelfareDemographicsLoader()
    welfare_factory = WelfareSaturationFeatureFactory(demo_loader=demo_loader, parser=parser)

    print("\n[1] FISCAL TRANSFERS VS REVENUE EXTRACTION CORRELATIONS")
    corrs = welfare_factory.compute_welfare_correlations()
    for k, v in corrs.items():
        print(f"  * {k:40s} : {v}")

    print("\n[2] SYNTHETIC CONTROL METHOD (Abadie et al.) ON DIRECT CASH TRANSFERS")
    sc_eval = SyntheticControlWelfareEvaluator(parser=parser, demo_loader=demo_loader)
    macro_sc = sc_eval.run_welfare_macro_evaluation()
    print(f"  * Evaluated Treated Constituencies : {macro_sc.get('evaluated_treated_acs_count', 0)}")
    print(f"  * Donor Pool Size                  : {macro_sc.get('donor_pool_size', 0)}")
    print(f"  * Mean Causal Lift on Retention    : +{macro_sc.get('mean_causal_vote_retention_lift_dmk_pct', 0.0)}%")
    print(f"  * Interpretation                   : {macro_sc.get('interpretation', '')}")

    print("\n[3] DIFFERENCE-IN-DIFFERENCES: KALLAKURICHI ILLICIT LIQUOR SHOCK")
    did_eval = DifferenceInDifferencesEvaluator(parser=parser)
    kallakurichi = did_eval.estimate_kallakurichi_liquor_shock()
    print(f"  * Treated Cluster Districts : {kallakurichi['treated_cluster_districts']}")
    print(f"  * Treatment Effect (Delta)  : {kallakurichi['did_treatment_effect_delta']}%")
    print(f"  * Clustered Standard Error  : {kallakurichi['cluster_robust_standard_error']}")
    print(f"  * P-Value                   : {kallakurichi['p_value']}")
    print(f"  * Statistically Significant : {kallakurichi['statistically_significant_at_5pct']}")

    print("\n[4] DIFFERENCE-IN-DIFFERENCES: KARUR CASH-FOR-JOBS SHOCK")
    karur = did_eval.estimate_karur_scam_shock()
    print(f"  * Treated District          : {karur['treated_cluster_districts']}")
    print(f"  * Treatment Effect (Delta)  : {karur['did_treatment_effect_delta']}%")
    print(f"  * Clustered Standard Error  : {karur['cluster_robust_standard_error']}")
    print(f"  * P-Value                   : {karur['p_value']}")
    print(f"  * Statistically Significant : {karur['statistically_significant_at_5pct']}")

    print("\n" + "=" * 80)
    print("ECONOMETRIC EVALUATION COMPLETED.")
    print("=" * 80)


if __name__ == "__main__":
    main()
