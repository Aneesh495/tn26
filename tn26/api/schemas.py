"""Pydantic request and response data models for the tn26 API."""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class SeatSummaryResponse(BaseModel):
    """Overall legislative assembly seat outcome summary."""
    TVK: int
    DMK: int
    ADMK: int
    INC: int
    BJP: int
    VCK: int
    PMK: int
    IUML: int
    DMK_led_bloc: int
    AIADMK_led_bloc: int
    Total_Seats: int


class ConstituencyDetailResponse(BaseModel):
    """Detailed election returns and demographics for a single AC."""
    ac_no: int
    constituency_name: str
    district: str
    region: str
    winner_party: str
    winner_candidate: str
    winner_votes: int
    winner_vote_share_pct: float
    runner_up_party: str
    runner_up_candidate: str
    runner_up_votes: int
    runner_up_vote_share_pct: float
    margin_votes: int
    margin_pct: float
    tvk_total_votes: int
    tvk_vote_share_pct: float
    dmk_alliance_total_votes: int
    dmk_alliance_vote_share_pct: float
    admk_alliance_total_votes: int
    admk_alliance_vote_share_pct: float


class SwingSimulationRequest(BaseModel):
    """Parameters for running a uniform electoral swing simulation."""
    shift_points: float = Field(default=1.0, ge=0.0, le=15.0)
    mode: str = Field(default="transfer", pattern="^(transfer|abstain)$")


class SwingSimulationResponse(BaseModel):
    """Results of uniform swing sensitivity simulation."""
    mode: str
    shift_pct_points: float
    TVK_seats: int
    DMK_seats: int
    ADMK_seats: int
    DMK_led_bloc_seats: int
    AIADMK_led_bloc_seats: int
    TVK_seats_lost: int
    flipped_ac_numbers: List[int]


class PollingForensicResponse(BaseModel):
    """Audit of polling failure metrics and herding behavior."""
    mean_tvk_underestimate_seats: float
    mean_dmk_overestimate_seats: float
    pollster_count: int
    herding_index: float
    primary_failure_reasons: List[str]
