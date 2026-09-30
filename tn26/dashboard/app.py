"""Interactive research and exploratory dashboard for the Tamil Nadu 2026 election platform."""
import argparse
from typing import Dict, List, Optional
import pandas as pd

from tn26.data_ingestion.eci_parser import ECIResultParser
from tn26.data_ingestion.poll_harvester import PollHarvester
from tn26.data_ingestion.speech_corpus_loader import SpeechCorpusLoader
from tn26.features.swing_elasticity import SwingElasticityCalculator
from tn26.models.alliance_game_theory import AllianceGameTheoreticEngine
from tn26.models.voter_transition_matrix import EcologicalInferenceVoterFlow


class TerminalResearchDashboard:
    """Terminal-based interactive analytics and diagnostic dashboard."""

    def __init__(self):
        self.parser = ECIResultParser()
        self.calc = SwingElasticityCalculator(self.parser)
        self.poll_harvester = PollHarvester()
        self.game_engine = AllianceGameTheoreticEngine()
        self.speech_loader = SpeechCorpusLoader()
        self.ei_flow = EcologicalInferenceVoterFlow(self.parser)

    def print_banner(self) -> None:
        print("=" * 80)
        print("  TAMIL NADU 2026 LEGISLATIVE ASSEMBLY ELECTION RESEARCH DASHBOARD (tn26)")
        print("  Computational Social Science, Econometrics & Machine Learning Monograph")
        print("=" * 80)

    def display_seat_summary(self) -> None:
        print("\n[1] OFFICIAL 2026 ECI ASSEMBLY SEAT OUTCOMES (234 Total Seats)")
        print("-" * 65)
        seats = self.parser.compute_seat_tallies()
        print(f"  * TVK (Tamilaga Vettri Kazhagam) : {seats['TVK']} seats (Plurality Winner)")
        print(f"  * DMK-led Bloc (SPA)             : {seats['DMK_led_bloc']} seats (DMK: {seats['DMK']}, INC: {seats['INC']}, VCK: {seats['VCK']})")
        print(f"  * AIADMK-led Bloc                : {seats['AIADMK_led_bloc']} seats (ADMK: {seats['ADMK']}, BJP: {seats['BJP']}, PMK: {seats['PMK']})")
        print(f"  * Majority Threshold             : 118 seats (TVK fell 10 seats short)")
        print("-" * 65)

    def display_polling_failure_summary(self) -> None:
        print("\n[2] FORENSIC AUDIT OF POLLING AGENCY FAILURES")
        print("-" * 80)
        metrics = self.poll_harvester.compute_pollster_error_metrics()
        print(metrics[["pollster", "type", "sample_size", "predicted_tvk", "actual_tvk", "abs_error_tvk", "mean_absolute_error_seats"]].to_string(index=False))
        print("-" * 80)

    def display_voter_transition_matrix(self) -> None:
        print("\n[3] ECOLOGICAL INFERENCE: 2021 TO 2026 VOTER FLOW PROBABILITIES (%)")
        print("-" * 75)
        trans_df = self.ei_flow.estimate_transition_matrix()
        print(trans_df.to_string())
        print("-" * 75)
        provenance = self.ei_flow.compute_tvk_coalition_provenance()
        print(f"  * Origin of TVK Coalition : {provenance['tvk_voters_from_aiadmk_disillusioned_pct']}% from AIADMK, {provenance['tvk_voters_from_youth_and_new_voters_pct']}% from First-time Youth")

    def display_game_theory_power(self) -> None:
        print("\n[4] POST-ELECTION LEGISLATIVE POWER INDICES (COALITION FORMATION)")
        print("-" * 65)
        shapley = self.game_engine.compute_shapley_values()
        banzhaf = self.game_engine.compute_banzhaf_power_index()
        power_df = pd.DataFrame({
            "Party": list(shapley.keys()),
            "Seats": [self.game_engine.seats[p] for p in shapley],
            "Shapley_Power": list(shapley.values()),
            "Banzhaf_Pivot_Index": list(banzhaf.values()),
        }).sort_values(by="Seats", ascending=False)
        print(power_df.to_string(index=False))
        print("-" * 65)

    def display_speech_stylometrics(self) -> None:
        print("\n[5] LEADER SPEECH STYLOMETRICS & RHETORICAL FRAMING")
        print("-" * 80)
        sty = self.speech_loader.compute_stylometrics()
        print(sty[["leader", "party", "location", "total_tokens", "lexical_diversity_ttr", "dynasty_frame_density", "welfare_frame_density", "tasmac_critique_density"]].to_string(index=False))
        print("-" * 80)

    def run_full_dashboard(self) -> None:
        self.print_banner()
        self.display_seat_summary()
        self.display_polling_failure_summary()
        self.display_voter_transition_matrix()
        self.display_game_theory_power()
        self.display_speech_stylometrics()
        print("\nResearch dashboard execution completed successfully.\n")


def main():
    dashboard = TerminalResearchDashboard()
    dashboard.run_full_dashboard()


if __name__ == "__main__":
    main()
