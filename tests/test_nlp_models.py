"""Unit tests for NLP sentiment, stance classification, and rhetorical framing."""
import pytest

from tn26.models.nlp_sentiment_analyzer import TamilSentimentStanceClassifier
from tn26.models.propaganda_framing_detector import RhetoricalFramingDetector


def test_tamil_sentiment_classifier():
    clf = TamilSentimentStanceClassifier()
    pos_score = clf.predict_sentiment_polarity("Vijay delivered a great and honest speech bringing hope for future victory.")
    neg_score = clf.predict_sentiment_polarity("Corrupt dynastic family looting people through tasmac poison and scam.")

    assert pos_score > 0.0
    assert neg_score < 0.0

    stance_tvk = clf.predict_stance("Vijay TVK whistle will bring real change to Tamil Nadu.")
    stance_dmk = clf.predict_stance("Stalin Dravidian model welfare 1000 rupees supports poor families.")

    assert stance_tvk == "Pro-TVK"
    assert stance_dmk == "Pro-DMK"


def test_rhetorical_framing_detector():
    detector = RhetoricalFramingDetector()
    text = "The dynastic family crown must end. We cannot allow corrupt heirs to inherit power."
    frames = detector.detect_frames_in_text(text)

    assert "Dynastic_Monopoly_Frame" in frames
    assert frames["Dynastic_Monopoly_Frame"] > frames["Cinema_Inexperience_Frame"]
