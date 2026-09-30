"""FastAPI application providing research endpoints for the Tamil Nadu 2026 election platform."""
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from tn26.api.schemas import (
    ConstituencyDetailResponse,
    PollingForensicResponse,
    SeatSummaryResponse,
    SwingSimulationRequest,
    SwingSimulationResponse,
)
from tn26.data_ingestion.eci_parser import ECIResultParser
from tn26.data_ingestion.poll_harvester import PollHarvester
from tn26.data_ingestion.speech_corpus_loader import SpeechCorpusLoader
from tn26.features.swing_elasticity import SwingElasticityCalculator
from tn26.models.alliance_game_theory import AllianceGameTheoreticEngine
from tn26.models.poll_bias_forensics import PollingFailureForensicEngine

app = FastAPI(
    title="Tamil Nadu 2026 Legislative Assembly Election Intelligence API",
    description="Computational Social Science and Machine Learning Platform for the Historic 2026 Election",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

parser = ECIResultParser()
calc = SwingElasticityCalculator(parser)
poll_harvester = PollHarvester()
forensics = PollingFailureForensicEngine(poll_harvester)
game_engine = AllianceGameTheoreticEngine()
speech_loader = SpeechCorpusLoader()


@app.get("/", tags=["System"])
def root():
    return {
        "project": "tn26: Tamil Nadu 2026 Election Platform",
        "description": "Academic Machine Learning, Econometrics, and Electoral Research Suite",
        "endpoints": [
            "/api/seats",
            "/api/constituencies",
            "/api/constituency/{ac_no}",
            "/api/simulate/swing",
            "/api/polls/forensics",
            "/api/speeches",
            "/api/coalition/stability",
        ],
        "status": "operational",
    }


@app.get("/api/seats", response_model=SeatSummaryResponse, tags=["Electoral Outcomes"])
def get_seat_summary():
    """Retrieve official 2026 assembly seat tallies across parties and alliances."""
    return parser.compute_seat_tallies()


@app.get("/api/constituencies", tags=["Constituencies"])
def list_constituencies(
    region: Optional[str] = Query(None, description="Filter by geopolitical region"),
    district: Optional[str] = Query(None, description="Filter by district name"),
):
    """List 234 assembly constituencies with optional regional and district filters."""
    df = parser.load_full_results_2026()
    if region:
        df = df[df["region"].str.contains(region, case=False, na=False)]
    if district:
        df = df[df["district"].str.contains(district, case=False, na=False)]
    return df.to_dict(orient="records")


@app.get("/api/constituency/{ac_no}", response_model=ConstituencyDetailResponse, tags=["Constituencies"])
def get_constituency_detail(ac_no: int):
    """Retrieve complete electoral returns and margins for a specific AC (1 to 234)."""
    df = parser.load_full_results_2026()
    match = df[df["ac_no"] == ac_no]
    if match.empty:
        raise HTTPException(status_code=404, detail=f"Constituency AC #{ac_no} not found.")
    return match.iloc[0].to_dict()


@app.post("/api/simulate/swing", response_model=SwingSimulationResponse, tags=["Simulation"])
def simulate_swing(req: SwingSimulationRequest):
    """Execute counterfactual uniform vote swing simulation."""
    res = calc.simulate_uniform_swing(
        shift_pct_points=req.shift_points,
        from_party="TVK",
        mode=req.mode,
    )
    return res


@app.get("/api/polls/forensics", tags=["Polling Forensics"])
def get_polling_forensics():
    """Retrieve statistical autopsy of 2026 opinion and exit poll agency failures."""
    audit = forensics.run_full_forensic_audit()
    return audit["error_decomposition"]


@app.get("/api/speeches", tags=["Speech NLP"])
def get_speeches():
    """Retrieve archived political speech transcripts and stylometric features."""
    return speech_loader.compute_stylometrics().to_dict(orient="records")


@app.get("/api/coalition/stability", tags=["Game Theory"])
def get_coalition_stability():
    """Retrieve game-theoretic Shapley values, Banzhaf indices, and government formation options."""
    return game_engine.evaluate_government_formation_viability()
