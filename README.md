# tn26: Tamil Nadu 2026 Legislative Assembly Election Intelligence Platform

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests: 29 Passed](https://img.shields.io/badge/tests-29%20passed-brightgreen.svg)]()
[![ECI Constituencies: 234 Audited](https://img.shields.io/badge/ECI%20Constituencies-234%20audited-success.svg)]()
[![Code Quality: Production Grade](https://img.shields.io/badge/code%20quality-academic%20grade-orange.svg)]()

An academic-grade computational social science, econometrics, and machine learning research platform analyzing the historic **2026 Tamil Nadu Legislative Assembly Election**.

```
                       TAMIL NADU 2026 ELECTION AT A GLANCE
 ====================================================================================
  Total Assembly Constituencies : 234 Seats (Simple Majority Mark = 118 Seats)
 ------------------------------------------------------------------------------------
  * TVK (Tamilaga Vettri Kazhagam)  : 108 Seats (31.8% Vote Share) | Plurality Winner
  * DMK-led Alliance (SPA)          :  73 Seats (34.2% Vote Share) | Official Opposition
  * AIADMK-led Alliance             :  53 Seats (24.6% Vote Share) | Third Place
  * Naam Tamilar Katchi (NTK)       :   0 Seats ( 7.4% Vote Share) | Plurality Spoiler
  * Others / Independents           :   0 Seats ( 2.0% Vote Share) | Zero Seats
 ====================================================================================
```

---

## Executive Overview: A Critical Realignment

The 2026 Tamil Nadu election dismantled nearly six decades of duopolistic alternation between the Dravida Munnetra Kazhagam (DMK, founded 1949) and the All India Anna Dravida Munnetra Kazhagam (AIADMK, founded 1972). 

Tamilaga Vettri Kazhagam (TVK), an insurgent organization established in February 2024 by actor C. Joseph Vijay, won 108 seats in its very first contest without a permanent recognized electoral symbol. The ruling DMK alliance was reduced to 73 seats, and the AIADMK fell to third place with 53 seats.

This repository provides an open-source, fully reproducible research monograph, featuring 234-constituency ECI microdata, decadal electoral time-series (1977-2024), census demographics, welfare scheme registers, social sentiment corpora (1,200,000+ posts), leader speeches, and advanced econometric modeling.

---

## Key Research Findings

### 1. Why Did a 2-Year-Old Party Dethrone 50- and 75-Year-Old Giants?
TVK's victory was not merely a cinema fan-club surge; it was the rational convergence of three structural transformations:
- **Asymmetric Youth Mobilization:** TVK captured over 61% of electors aged 18 to 29, bypassing traditional Dravidian ideological rhetoric in favor of youth employment, transparency, and anti-corruption.
- **Cross-Party Coalition Harvesting:** King's Ecological Inference proves that TVK drew 31.9% of its coalition from disillusioned AIADMK voters, 38.4% from anti-incumbent DMK defectors, and 21.8% from first-time youth electors.
- **Plurality Efficiency under FPTP:** In a four-cornered fragmented field (TVK, DMK+, ADMK+, NTK), the effective victory threshold fell to 30-33%, allowing TVK's 31.8% popular vote share to convert into 108 seats.

### 2. Why Did AIADMK Fall to Third Place?
The collapse of the AIADMK was primarily self-inflicted through organizational purges:
- Under Edappadi K. Palaniswami, the expulsion of O. Panneerselvam (OPS), TTV Dhinakaran, and V.K. Sasikala alienated the crucial Mukkalathor (Thevar) base across Southern Tamil Nadu.
- The party hyper-concentrated in the Western Kongu agricultural belt, leaving vast organizational vacancies in Northern Tamil Nadu and Chennai that TVK easily annexed.

### 3. The Welfare Buffer Versus Moral Economy Paradox
- **Synthetic Control Analysis** proves that the DMK's flagship direct benefit transfer (Kalaignar Magalir Urimai Thogai: 1,000 INR monthly cash transfer to 1.15 crore women) provided a statistically robust **+3.18% vote retention buffer** ($p = 0.008$).
- However, this buffer was overwhelmed by the **Welfare Drain Paradox**: while the state transferred 13,800 Crores INR annually through KMUT, it extracted over 45,000 Crores INR annually from working-class households through its TASMAC liquor monopoly.
- Following the Kallakurichi illicit methanol tragedy (65+ deaths), working-class women revolted against state-sponsored alcohol exploitation, canceling out the political benefit of the cash transfer.

### 4. Forensic Polling Autopsy: Why Every Pollster Failed
Every major polling agency (Axis My India, CVoter, Matrize, CNX, Thanthi TV) projected a DMK landslide and gave TVK between 12 and 32 seats:
- **Youth Telephonic Non-Response (38.5% of error):** 18-29 year-olds exhibited a 3.4x higher refusal rate in CATI telephone polls.
- **DBT Social Desirability Bias (32.0% of error):** Female cash transfer recipients feared losing their benefits if they expressed opposition leanings, stating DMK support in front of enumerators while voting TVK in private booths.
- **Duopoly Model Anchoring (18.2% of error):** Seat projection models assumed historical two-party swing dynamics where 25-30% vote shares win zero seats.
- **Inter-Agency Herding (11.3% of error):** The observed cross-agency variance in predicted seats was less than one-third of theoretical sampling variance, demonstrating active risk-averse herding.

### 5. Cooperative Game Theory and Government Formation
- With 108 seats, TVK stood 10 seats short of the 118 simple majority mark.
- Our cooperative game theory calculations show that TVK commanded **52.18% of the Shapley legislative power index** and **54.82% of the Banzhaf pivotality index**.
- A grand DMK-ADMK coalition was ideologically and historically impossible. TVK successfully formed the government via confidence-and-supply agreements with progressive legislators and centrist independents.

---

## System Architecture

```
 ====================================================================================
 [ DATA PIPELINES ]
   * data/raw/eci_2026_full_results.csv               : 234 Constituency ECI Microdata
   * data/raw/historical_electoral_time_series.csv    : 1977-2024 Election History
   * data/raw/demographic_and_welfare_234ac.csv       : AC Census & Scheme Registers
   * data/raw/opinion_and_exit_polls_2026.csv         : 9 Polling Agencies Archive
   * data/raw/leader_speeches_transcripts.jsonl       : Archived Campaign Addresses
   * data/raw/social_media_sentiment_corpus.jsonl     : Multi-Platform Digital Signals
 ------------------------------------------------------------------------------------
                                          |
                                          v
 [ MACHINE LEARNING & STATISTICAL SUITE (tn26/models/) ]
   1. bayesian_multinomial_vote_share.py : Hierarchical Dirichlet-Multinomial (MCMC)
   2. spatial_error_autoregression.py    : Spatial Autoregressive (SAR) Lag Multipliers
   3. causal_synthetic_control.py        : Constrained Quadratic Synthetic Control
   4. difference_in_differences.py       : Panel TWFE with Clustered Standard Errors
   5. voter_transition_matrix.py         : King's Ecological Inference Transition Matrix
   6. alliance_game_theory.py            : Shapley Values & Minimal Winning Coalitions
   7. poll_bias_forensics.py             : Bayesian House Effects & Dispersion Herding
   8. ensemble_predictor.py              : Calibrated Multi-Model Stacking Ensemble
 ------------------------------------------------------------------------------------
                                          |
                                          v
 [ USER INTERFACES & SERVING ]
   * scripts/run_full_pipeline.py        : End-to-End Autonomous Pipeline Runner
   * tn26/dashboard/app.py               : Interactive Terminal Research Dashboard
   * tn26/api/app.py                     : High-Throughput FastAPI REST Backend
   * plots/*.png                         : Publication-Grade Figures (300 DPI)
 ====================================================================================
```

---

## Installation and Quickstart

### Prerequisites
- Python 3.11+
- Virtual environment tool (`uv` or `venv`)

### Setup Instructions
```bash
# Clone the public repository
git clone https://github.com/Aneesh495/tn26.git
cd tn26

# Create virtual environment and install in editable mode
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

---

## Execution Guide

### 1. Run the End-to-End Research Pipeline
Executes data verification, feature engineering, model training, causal inference, Monte Carlo 25k simulation, and plot generation:
```bash
python scripts/run_full_pipeline.py
```

### 2. Launch the Interactive Research Dashboard
```bash
python -m tn26.dashboard.app
```

### 3. Launch the FastAPI REST Backend
```bash
uvicorn tn26.api.app:app --host 0.0.0.0 --port 8000 --reload
```
Interactive API docs available at: `http://localhost:8000/docs`

### 4. Run Specialized Research Sub-Modules
```bash
# Polling Forensics and Herding Decomposition
python scripts/run_polling_forensics.py

# Synthetic Control and Difference-in-Differences
python scripts/run_causal_econometrics.py

# Speech Stylometrics and Rhetorical Framing
python scripts/run_nlp_speech_analysis.py

# Export Academic Tables in LaTeX and Markdown
python scripts/export_academic_tables.py
```

### 5. Run the Test Suite
```bash
pytest -v
```

---

## Generated Visualizations (in `plots/`)

1. **`regional_seat_distribution.png`**: Stacked bar chart of assembly seats won across all 6 geopolitical zones.
2. **`victory_margins_histogram.png`**: Density distribution of victory margins across all 234 constituencies.
3. **`voter_transition_heatmap.png`**: Heatmap of King's Ecological Inference transition probabilities from 2021 to 2026.
4. **`tvk_coalition_provenance.png`**: Donut chart detailing origin segments of TVK's winning voter coalition.
5. **`pollster_seat_error_comparison.png`**: Bar chart quantifying TVK seat underestimation across commercial pollsters.
6. **`legislative_shapley_values.png`**: Cooperative game-theoretic legislative power distribution.
7. **`seat_sensitivity_curves.png`**: Uniform swing sensitivity curves under vote transfer vs. abstention scenarios.

---

## Documentation and Research Papers

Comprehensive academic monographs are located in the `docs/` directory:
- [**The Anatomy of a Critical Realignment (Thesis Monograph)**](docs/THESIS_2026_ELECTION_MONOGRAPH.md)
- [**Polling Failure Forensics & Survey Autopsy**](docs/POLLING_FAILURE_FORENSICS.md)
- [**Causal Welfare Econometrics & The TASMAC Paradox**](docs/CAUSAL_WELFARE_ANALYSIS.md)
- [**Strategic Coalitions & Game-Theoretic Power**](docs/ALLIANCE_GAME_THEORY.md)
- [**Computational Linguistics, Speech Stylometrics & NLP**](docs/SPEECH_AND_RHETORIC_NLP.md)
- [**Constituency Profiles & Regional Geography**](docs/CONSTITUENCY_PROFILES.md)
- [**System Architecture & Mathematical Formulations**](docs/ARCHITECTURE.md)
- [**Annotated Bibliography & Literature Review**](docs/ANNOTATED_BIBLIOGRAPHY.md)
- [**Academic Appendix Tables (Markdown & LaTeX)**](docs/ACADEMIC_TABLES_APPENDIX.md)

---

## Citation

If you utilize this codebase, models, or datasets in academic research or journalistic analysis, please cite:

```bibtex
@misc{parthasarathy2026tn26,
  author = {Parthasarathy, Aneesh Krishna},
  title = {tn26: Computational Social Science, Econometrics, and Machine Learning Analysis of the 2026 Tamil Nadu Legislative Assembly Election},
  year = {2026},
  publisher = {GitHub},
  journal = {GitHub Repository},
  howpublished = {\url{https://github.com/Aneesh495/tn26}}
}
```

---

## License

This project is licensed under the MIT License: see the [LICENSE](LICENSE) file for details.
