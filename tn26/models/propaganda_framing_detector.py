"""Propaganda, narrative framing, and rhetorical agenda-setting detector.

Analyzes ideological framing strategies across 5 dominant political narratives:
  1. Dynastic Monopolization Frame (Anti-DMK)
  2. Cinema Actor / Teleprompter Inexperience Frame (Anti-TVK)
  3. Dravidian Model Welfare Protection Frame (Pro-DMK)
  4. TASMAC Moral Ruin and Liquor Mafia Frame (Anti-Incumbent)
  5. Ethnic Pure Tamil Nationalism Frame (NTK)
"""
from typing import Dict, List, Optional
import numpy as np
import pandas as pd

from tn26.data_ingestion.speech_corpus_loader import SpeechCorpusLoader


class RhetoricalFramingDetector:
    """Detects rhetorical frames and propaganda appeals in campaign discourse."""

    def __init__(self, loader: Optional[SpeechCorpusLoader] = None):
        self.loader = loader or SpeechCorpusLoader()

        self.frames = {
            "Dynastic_Monopoly_Frame": [
                "family", "dynasty", "son", "grandson", "crown", "varisu",
                "heir", "monopoly", "loot", "karunanidhi", "udhayanidhi"
            ],
            "Cinema_Inexperience_Frame": [
                "actor", "cinema", "screen", "acting", "teleprompter", "bubble",
                "novice", "script", "dialogue", "shooting", "koothadi"
            ],
            "Dravidian_Welfare_Frame": [
                "welfare", "scheme", "magalir", "1000", "free", "breakfast",
                "dravidian model", "periyar", "social justice", "banyan tree"
            ],
            "TASMAC_Moral_Ruin_Frame": [
                "tasmac", "liquor", "alcohol", "drunk", "poison", "kallakurichi",
                "methanol", "mothers", "fathers", "tears", "prohibition"
            ],
            "Pure_Tamil_Nationalism_Frame": [
                "soil", "ethnic", "tamizhan", "race", "language", "inquiry",
                "sixty years", "outsiders", "pure tamil", "seeman"
            ],
        }

    def detect_frames_in_text(self, text: str) -> Dict[str, float]:
        """Compute relative resonance scores across the 5 rhetorical frames."""
        text_lower = text.lower()
        scores = {}
        total_hits = 0

        for frame_name, keywords in self.frames.items():
            count = sum(1 for kw in keywords if kw in text_lower)
            scores[frame_name] = count
            total_hits += count

        # Normalize to probability distribution over frames
        if total_hits == 0:
            return {f: 0.20 for f in self.frames}

        return {f: round(c / total_hits, 4) for f, c in scores.items()}

    def analyze_leader_speeches(self) -> pd.DataFrame:
        """Run framing decomposition across all archived leader addresses."""
        speeches = self.loader.load_speeches()
        records = []

        for sp in speeches:
            text = f"{sp['key_theme']} {sp['core_quote']} {sp.get('rhetoric_category', '')}"
            frame_dist = self.detect_frames_in_text(text)
            dominant_frame = max(frame_dist.items(), key=lambda x: x[1])[0]

            records.append({
                "speech_id": sp["speech_id"],
                "leader": sp["leader"],
                "party": sp["party"],
                "location": sp["location"],
                "dominant_frame": dominant_frame,
                **frame_dist,
            })

        return pd.DataFrame(records)
