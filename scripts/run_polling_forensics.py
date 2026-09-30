#!/usr/bin/env python3
"""Dedicated forensic script analyzing 2026 pre-poll and exit poll agency failures."""
import sys
from tn26.data_ingestion.poll_harvester import PollHarvester
from tn26.evaluation.pollster_scorecard import PollsterForensicScorecard
from tn26.models.poll_bias_forensics import PollingFailureForensicEngine


def main():
    print("=" * 80)
    print("  TN26 POLLING FAILURE FORENSICS AND STATISTICAL POST-MORTEM")
    print("=" * 80)

    harvester = PollHarvester()
    forensics = PollingFailureForensicEngine(harvester)
    scorecard_gen = PollsterForensicScorecard(harvester)

    audit = forensics.run_full_forensic_audit()
    decomp = audit["error_decomposition"]

    print("\n[1] SYSTEMIC BIAS ESTIMATES")
    print(f"  - Average Underestimate of TVK Seats : {decomp['mean_tvk_seat_underestimate']} seats")
    print(f"  - Average Overestimate of DMK Seats  : {decomp['mean_dmk_seat_overestimate']} seats")
    print(f"  - Average Overestimate of ADMK Seats : {decomp['mean_admk_seat_overestimate']} seats")

    print("\n[2] ROOT CAUSE DECOMPOSITION OF POLLING BREAKDOWN")
    for item in decomp["primary_failure_mechanisms"]:
        print(f"\n  * {item['mechanism']} (Share of Error: {item['contribution_pct']}%)")
        print(f"    {item['description']}")

    print("\n[3] STATISTICAL HERDING METRICS")
    herding = decomp["herding_metrics"]
    print(f"  - Inter-Pollster TVK Seat Variance : {herding['tvk_prediction_variance']}")
    print(f"  - Inter-Pollster DMK Seat Variance : {herding['dmk_prediction_variance']}")
    print(f"  - Herding Dispersion Index         : {herding['herding_index']}")

    print("\n[4] ACADEMIC REPORT CARD FOR POLLING AGENCIES")
    print("-" * 80)
    report_card = scorecard_gen.generate_full_report_card()
    print(report_card.to_string(index=False))
    print("-" * 80)


if __name__ == "__main__":
    main()
