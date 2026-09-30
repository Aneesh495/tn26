"""Unit tests for data ingestion, ECI parsing, and schema validation."""
import pytest
import pandas as pd

from tn26.data_ingestion.eci_parser import ECIResultParser
from tn26.data_ingestion.poll_harvester import PollHarvester
from tn26.data_ingestion.welfare_demographics_loader import WelfareDemographicsLoader
from tn26.data_ingestion.speech_corpus_loader import SpeechCorpusLoader
from tn26.data_ingestion.social_signals_loader import SocialSignalsLoader


def test_eci_parser_totals():
    parser = ECIResultParser()
    margins = parser.load_constituency_margins()
    assert len(margins) == 234
    assert margins["ac_no"].nunique() == 234

    tallies = parser.compute_seat_tallies()
    assert tallies["TVK"] == 108
    assert tallies["DMK_led_bloc"] == 73
    assert tallies["AIADMK_led_bloc"] == 53
    assert tallies["Total_Seats"] == 234


def test_official_tvk_winners():
    parser = ECIResultParser()
    tvk = parser.load_official_tvk_winners()
    assert len(tvk) == 108
    # Perambur AC 12 check
    perambur = tvk[tvk["ac_no"] == 12]
    assert not perambur.empty
    assert "VIJAY" in perambur.iloc[0]["candidate"]


def test_poll_harvester():
    harvester = PollHarvester()
    polls = harvester.load_polls()
    assert len(polls) >= 8
    metrics = harvester.compute_pollster_error_metrics()
    assert not metrics.empty
    assert "mean_absolute_error_seats" in metrics.columns


def test_welfare_demographics_loader():
    loader = WelfareDemographicsLoader()
    demo = loader.load_demographics()
    assert len(demo) == 234
    assert "kmut_female_beneficiaries" in demo.columns
    assert "tasmac_outlets_count" in demo.columns


def test_speech_corpus_loader():
    loader = SpeechCorpusLoader()
    speeches = loader.load_speeches()
    assert len(speeches) >= 5
    sty = loader.compute_stylometrics()
    assert len(sty) == len(speeches)
    assert "lexical_diversity_ttr" in sty.columns


def test_social_signals_loader():
    loader = SocialSignalsLoader()
    df = loader.load_corpus()
    assert len(df) >= 1000
    shares = loader.compute_platform_stance_shares()
    assert not shares.empty
