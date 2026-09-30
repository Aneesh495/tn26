"""End-to-end integration and API tests for the tn26 platform."""
import pytest
from fastapi.testclient import TestClient

from tn26.api.app import app
from tn26.evaluation.metrics import ElectoralEvaluationMetrics
from tn26.evaluation.backtesting import HistoricalElectionBacktester


client = TestClient(app)


def test_api_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"


def test_api_seats_endpoint():
    response = client.get("/api/seats")
    assert response.status_code == 200
    data = response.json()
    assert data["TVK"] == 108
    assert data["DMK_led_bloc"] == 73
    assert data["AIADMK_led_bloc"] == 53


def test_api_constituency_endpoint():
    response = client.get("/api/constituency/12")
    assert response.status_code == 200
    data = response.json()
    assert data["ac_no"] == 12
    assert "PERAMBUR" in data["constituency_name"]


def test_api_simulate_swing_endpoint():
    response = client.post("/api/simulate/swing", json={"shift_points": 1.0, "mode": "transfer"})
    assert response.status_code == 200
    data = response.json()
    assert "TVK_seats" in data
    assert data["TVK_seats"] < 108


def test_api_forensics_endpoint():
    response = client.get("/api/polls/forensics")
    assert response.status_code == 200
    data = response.json()
    assert "mean_tvk_seat_underestimate" in data


def test_historical_backtesting():
    backtester = HistoricalElectionBacktester()
    df = backtester.run_historical_backtests()
    assert len(df) == 3
    assert 2021 in df["election_year"].values
