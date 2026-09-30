"""Tamil, Tanglish, and English sentiment and ideological stance classifier.

Evaluates public political discourse across multi-platform corpora (X, YouTube, Reddit,
Instagram, News Forums) using lexical sentiment dictionaries and stance scoring.
"""
import re
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from tn26.data_ingestion.social_signals_loader import SocialSignalsLoader


class TamilSentimentStanceClassifier:
    """Classifies sentiment polarity and political stance for Tamil and Tanglish text."""

    def __init__(self, loader: Optional[SocialSignalsLoader] = None):
        self.loader = loader or SocialSignalsLoader()

        # Tamil and English sentiment and stance lexicons
        self.positive_lexicon = {
            "good", "great", "change", "hope", "genuine", "honest", "thalaiva",
            "support", "win", "victory", "future", "clean", "brave", "nalla",
            "vetri", "valthukkal", "semma", "mass", "save", "solution", "neethi",
        }
        self.negative_lexicon = {
            "bad", "scam", "corrupt", "loot", "family", "dynasty", "fake",
            "fail", "loss", "poison", "tasmac", "death", "bribe", "theft",
            "drogam", "mosam", "kodumai", "panam", "kolla", "ozhiga", "waste",
        }

        # Stance indicator terms
        self.tvk_markers = {"vijay", "tvk", "thalaiva", "thalapathy", "whistle", "ymca", "vikravandi", "actor"}
        self.dmk_markers = {"dmk", "stalin", "udhayanidhi", "dravidian", "kalaignar", "murasoli", "sun"}
        self.admk_markers = {"admk", "aiadmk", "eps", "edappadi", "mgr", "jayalalithaa", "twoli", "leaves"}
        self.ntk_markers = {"ntk", "seeman", "naam tamilar", "vivasayi", "puratchi"}

    def clean_text(self, text: str) -> str:
        """Standardize text, remove URLs, and lowercase."""
        text = re.sub(r"http\S+|www\S+", "", text)
        text = re.sub(r"[^\w\s\u0B80-\u0BFF]", " ", text.lower())
        return text.strip()

    def predict_sentiment_polarity(self, text: str) -> float:
        """Compute continuous sentiment polarity score in [-1.0, 1.0]."""
        cleaned = self.clean_text(text)
        tokens = cleaned.split()
        if not tokens:
            return 0.0

        pos_count = sum(1 for t in tokens if t in self.positive_lexicon)
        neg_count = sum(1 for t in tokens if t in self.negative_lexicon)

        total_emotional = pos_count + neg_count
        if total_emotional == 0:
            return 0.0

        polarity = (pos_count - neg_count) / float(total_emotional)
        return float(np.clip(polarity, -1.0, 1.0))

    def predict_stance(self, text: str) -> str:
        """Infer targeted political stance based on lexical resonance."""
        cleaned = self.clean_text(text)
        tokens = set(cleaned.split())

        has_tvk = bool(tokens.intersection(self.tvk_markers))
        has_dmk = bool(tokens.intersection(self.dmk_markers))
        has_admk = bool(tokens.intersection(self.admk_markers))
        has_ntk = bool(tokens.intersection(self.ntk_markers))

        polarity = self.predict_sentiment_polarity(text)

        # Anti-incumbency or Anti-Duopoly cues
        if "tasmac" in tokens or "dynasty" in tokens or "scam" in tokens or "loot" in tokens:
            if has_dmk or not has_tvk:
                return "Anti-Incumbent"

        if has_tvk:
            return "Pro-TVK" if polarity >= 0.0 else "Neutral / Undecided"
        elif has_dmk:
            return "Pro-DMK" if polarity >= 0.0 else "Anti-Incumbent"
        elif has_admk:
            return "Pro-ADMK" if polarity >= 0.0 else "Anti-Duopoly"
        elif has_ntk:
            return "Pro-NTK"

        if "change" in tokens or "two sides" in tokens or "duopoly" in tokens:
            return "Anti-Duopoly"

        return "Neutral / Undecided"

    def evaluate_corpus_sentiment(self) -> pd.DataFrame:
        """Process and classify the full social media corpus."""
        df = self.loader.load_corpus()
        predicted_polarities = []
        predicted_stances = []

        for text in df["text"]:
            pol = self.predict_sentiment_polarity(text)
            st = self.predict_stance(text)
            predicted_polarities.append(pol)
            predicted_stances.append(st)

        df["computed_polarity"] = predicted_polarities
        df["predicted_stance"] = predicted_stances
        return df
