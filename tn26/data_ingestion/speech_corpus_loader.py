"""Loader, tokenizer, and stylometric processor for political speech corpora."""
from collections import Counter
import json
from pathlib import Path
import re
from typing import Dict, List, Optional
import pandas as pd

from tn26.config import DATA_RAW_DIR


class SpeechCorpusLoader:
    """Processor for political speech transcripts and stylometric metrics."""

    def __init__(self, raw_data_dir: Optional[Path] = None):
        self.raw_dir = raw_data_dir or DATA_RAW_DIR
        self._speeches: Optional[List[Dict]] = None

    def load_speeches(self) -> List[Dict]:
        """Load JSONL corpus of transcribed leader addresses."""
        if self._speeches is not None:
            return self._speeches

        speech_file = self.raw_dir / "leader_speeches_transcripts.jsonl"
        if not speech_file.exists():
            raise FileNotFoundError(f"Missing speech corpus at {speech_file}")

        records = []
        with speech_file.open(encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line.strip()))
        self._speeches = records
        return records

    def to_dataframe(self) -> pd.DataFrame:
        """Convert speech records to structured DataFrame."""
        return pd.DataFrame(self.load_speeches())

    def tokenize_tamil_and_english(self, text: str) -> List[str]:
        """Tokenize mixed Tamil, Tanglish, and English political discourse."""
        cleaned = re.sub(r"[^\w\s\u0B80-\u0BFF]", " ", text.lower())
        tokens = [t.strip() for t in cleaned.split() if len(t.strip()) > 1]
        return tokens

    def compute_stylometrics(self) -> pd.DataFrame:
        """Extract quantitative stylometric and rhetorical features for each leader address.

        Features:
        - Word count and vocabulary size
        - Type-Token Ratio (TTR) measuring lexical richness
        - Rhetorical frame markers:
          * Dynasty / Nepotism framing
          * Welfare / Governance claims
          * Anti-TASMAC / Moral economy appeals
          * Tamil identity / Self-respect markers
          * Youth aspiration / Generational change cues
        """
        speeches = self.load_speeches()
        results = []

        dynasty_markers = {"family", "dynasty", "son", "grandson", "crown", "varisu"}
        welfare_markers = {"scheme", "welfare", "magalir", "1000", "free", "breakfast", "fund"}
        tasmac_markers = {"tasmac", "liquor", "alcohol", "drunk", "poison", "loot"}
        identity_markers = {"tamil", "dravidian", "periyar", "kamarajar", "ambedkar", "soil", "self-respect"}
        youth_markers = {"youth", "young", "future", "change", "chance", "actor", "son", "brothers", "sisters"}

        for sp in speeches:
            text = f"{sp['key_theme']} {sp['core_quote']} {sp.get('rhetoric_category', '')}"
            tokens = self.tokenize_tamil_and_english(text)
            n_tokens = len(tokens)
            n_types = len(set(tokens))
            ttr = round(n_types / max(1, n_tokens), 4)

            # Count marker occurrences
            counts = Counter(tokens)
            dynasty_count = sum(counts[w] for w in dynasty_markers if w in counts)
            welfare_count = sum(counts[w] for w in welfare_markers if w in counts)
            tasmac_count = sum(counts[w] for w in tasmac_markers if w in counts)
            identity_count = sum(counts[w] for w in identity_markers if w in counts)
            youth_count = sum(counts[w] for w in youth_markers if w in counts)

            results.append({
                "speech_id": sp["speech_id"],
                "leader": sp["leader"],
                "party": sp["party"],
                "location": sp["location"],
                "estimated_attendance": sp["estimated_attendance"],
                "duration_minutes": sp["duration_minutes"],
                "total_tokens": n_tokens,
                "lexical_diversity_ttr": ttr,
                "dynasty_frame_density": round(dynasty_count / max(1, n_tokens), 4),
                "welfare_frame_density": round(welfare_count / max(1, n_tokens), 4),
                "tasmac_critique_density": round(tasmac_count / max(1, n_tokens), 4),
                "identity_frame_density": round(identity_count / max(1, n_tokens), 4),
                "youth_mobilization_density": round(youth_count / max(1, n_tokens), 4),
                "baseline_sentiment_score": sp.get("sentiment_score", 0.5),
            })

        return pd.DataFrame(results)
