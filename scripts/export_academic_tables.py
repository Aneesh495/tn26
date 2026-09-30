#!/usr/bin/env python3
"""Export academic LaTeX and Markdown publication tables for the tn26 monograph."""
from pathlib import Path
from tn26.config import DOCS_DIR
from tn26.data_ingestion.eci_parser import ECIResultParser
from tn26.data_ingestion.poll_harvester import PollHarvester
from tn26.data_ingestion.speech_corpus_loader import SpeechCorpusLoader
from tn26.models.alliance_game_theory import AllianceGameTheoreticEngine
from tn26.models.voter_transition_matrix import EcologicalInferenceVoterFlow


def export_tables():
    print("Exporting academic LaTeX and Markdown tables to docs directory...")
    output_file = DOCS_DIR / "ACADEMIC_TABLES_APPENDIX.md"
    latex_file = DOCS_DIR / "ACADEMIC_TABLES_LATEX.tex"

    parser = ECIResultParser()
    poll_harvester = PollHarvester()
    ei_flow = EcologicalInferenceVoterFlow(parser)
    game_engine = AllianceGameTheoreticEngine()
    speech_loader = SpeechCorpusLoader()

    seat_summary = parser.compute_seat_tallies()
    poll_metrics = poll_harvester.compute_pollster_error_metrics()
    trans_matrix = ei_flow.estimate_transition_matrix()
    shapley = game_engine.compute_shapley_values()
    banzhaf = game_engine.compute_banzhaf_power_index()
    stylometrics = speech_loader.compute_stylometrics()

    # Write Markdown Tables
    with output_file.open("w", encoding="utf-8") as f:
        f.write("# Academic Appendix: Statistical Tables and Econometric Models\n\n")

        f.write("## Table 1: Official 2026 Legislative Assembly Outcomes\n\n")
        f.write("| Political Entity / Coalition | Seats Won | Vote Share (%) | Status |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        f.write(f"| TVK (Tamilaga Vettri Kazhagam) | {seat_summary['TVK']} | 31.8% | Plurality / Largest Party |\n")
        f.write(f"| DMK-led Alliance (SPA) | {seat_summary['DMK_led_bloc']} | 34.2% | Official Opposition |\n")
        f.write(f"| AIADMK-led Alliance | {seat_summary['AIADMK_led_bloc']} | 24.6% | Third Place |\n")
        f.write(f"| Naam Tamilar Katchi (NTK) | 0 | 7.4% | Standalone / Zero Seats |\n")
        f.write(f"| Others / Independents | 0 | 2.0% | Zero Seats |\n")
        f.write(f"| **Total Legislative Seats** | **234** | **100.0%** | **Majority = 118** |\n\n")

        f.write("## Table 2: Polling Agency Forensic Scorecard and Seat Errors\n\n")
        f.write("| Polling Organization | Survey Type | Sample Size | TVK Pred | TVK Error | DMK Error | Seat MAE |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for _, row in poll_metrics.iterrows():
            f.write(f"| {row['pollster']} | {row['type']} | {row['sample_size']:,} | {row['predicted_tvk']} | {row['error_tvk']:+d} | {row['error_dmk_bloc']:+d} | {row['mean_absolute_error_seats']:.2f} |\n")
        f.write("\n")

        f.write("## Table 3: King's Ecological Inference Voter Transition Matrix (2021 to 2026)\n\n")
        f.write("| 2021 Origin Alignment | Flow to TVK (%) | Flow to DMK (%) | Flow to ADMK (%) | Flow to NTK (%) | Flow to Other (%) |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for orig in trans_matrix.index:
            r = trans_matrix.loc[orig]
            f.write(f"| {orig} | {r['TVK_2026']:.1f}% | {r['DMK_2026']:.1f}% | {r['ADMK_2026']:.1f}% | {r['NTK_2026']:.1f}% | {r['Other_2026']:.1f}% |\n")
        f.write("\n")

        f.write("## Table 4: Cooperative Game-Theoretic Legislative Power Indices\n\n")
        f.write("| Party | Assembly Seats | Shapley Value (phi) | Banzhaf Pivot Index (Beta) |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        for p in shapley:
            seats = game_engine.seats[p]
            f.write(f"| {p} | {seats} | {shapley[p]:.4f} | {banzhaf[p]:.4f} |\n")
        f.write("\n")

        f.write("## Table 5: Leader Speech Stylometrics and Rhetorical Density\n\n")
        f.write("| Leader | Party | Event Location | Tokens | TTR Richness | Dynasty Frame | Welfare Frame | TASMAC Frame |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for _, row in stylometrics.iterrows():
            f.write(f"| {row['leader']} | {row['party']} | {row['location']} | {row['total_tokens']} | {row['lexical_diversity_ttr']:.3f} | {row['dynasty_frame_density']:.3f} | {row['welfare_frame_density']:.3f} | {row['tasmac_critique_density']:.3f} |\n")
        f.write("\n")

    # Write LaTeX Tables
    with latex_file.open("w", encoding="utf-8") as f:
        f.write("% Academic Publication Tables for LaTeX Articles\n\n")
        f.write("\\begin{table}[htbp]\n\\centering\n\\caption{Official 2026 Legislative Assembly Outcomes}\n")
        f.write("\\begin{tabular}{lrrr}\n\\hline\nAlliance & Seats & Vote Share (\\%) & Status \\\\\n\\hline\n")
        f.write(f"TVK & {seat_summary['TVK']} & 31.8 & Plurality Winner \\\\\n")
        f.write(f"DMK-led Alliance (SPA) & {seat_summary['DMK_led_bloc']} & 34.2 & Opposition \\\\\n")
        f.write(f"AIADMK-led Alliance & {seat_summary['AIADMK_led_bloc']} & 24.6 & Third Place \\\\\n")
        f.write(f"NTK & 0 & 7.4 & Zero Seats \\\\\n")
        f.write("\\hline\n\\end{tabular}\n\\end{table}\n\n")

    print(f"Exported tables to {output_file} and {latex_file}")


def main():
    export_tables()


if __name__ == "__main__":
    main()
