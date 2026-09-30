"""Loader and signal harvester for multi-platform digital and social media corpora."""
import json
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np
import pandas as pd

from tn26.config import DATA_RAW_DIR


class SocialSignalsLoader:
    """Processor and aggregator for cross-platform voter sentiment signals."""

    def __init__(self, raw_data_dir: Optional[Path] = None):
        self.raw_dir = raw_data_dir or DATA_RAW_DIR
        self._corpus_df: Optional[pd.DataFrame] = None

    def load_corpus(self) -> pd.DataFrame:
        """Load JSONL social media posts and engagement metrics."""
        if self._corpus_df is not None:
            return self._corpus_df.copy()

        corpus_file = self.raw_dir / "social_media_sentiment_corpus.jsonl"
        if not corpus_file.exists():
            raise FileNotFoundError(f"Missing social corpus at {corpus_file}")

        records = []
        with corpus_file.open(encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line.strip())
                    metrics = item.get("engagement_metrics", {})
                    # Engagement score calculation
                    # Likes + 3 * Retweets + 2 * Comments
                    engagement = (
                        metrics.get("likes", 0)
                        + 3 * metrics.get("retweets_or_shares", 0)
                        + 2 * metrics.get("comments", 0)
                    )
                    records.append({
                        "post_id": item["post_id"],
                        "platform": item["platform"],
                        "text": item["text"],
                        "stance": item["stance"],
                        "sentiment_polarity": float(item.get("sentiment_polarity", 0.0)),
                        "likes": metrics.get("likes", 0),
                        "retweets": metrics.get("retweets_or_shares", 0),
                        "comments": metrics.get("comments", 0),
                        "composite_engagement": engagement,
                        "timestamp": item.get("timestamp", ""),
                    })

        df = pd.DataFrame(records)
        self._corpus_df = df
        return df.copy()

    def compute_platform_stance_shares(self) -> pd.DataFrame:
        """Calculate weighted stance breakdown across individual digital platforms."""
        df = self.load_corpus()
        summary = (
            df.groupby(["platform", "stance"])
            .agg(
                post_count=("post_id", "count"),
                mean_sentiment=("sentiment_polarity", "mean"),
                total_engagement=("composite_engagement", "sum"),
            )
            .reset_index()
        )
        # Platform-level share percentage
        platform_totals = summary.groupby("platform")["total_engagement"].transform("sum")
        summary["engagement_share_pct"] = (summary["total_engagement"] / platform_totals) * 100.0
        return summary

    def get_weighted_sentiment_summary(self) -> Dict[str, float]:
        """Compute statewide engagement-weighted digital sentiment scores by political stance."""
        df = self.load_corpus()
        total_eng = df["composite_engagement"].sum() + 1e-6
        results = {}
        for stance, group in df.groupby("stance"):
            weight = group["composite_engagement"].sum() / total_eng
            mean_polarity = group["sentiment_polarity"].mean()
            results[stance] = {
                "share_of_voice_pct": round(weight * 100.0, 2),
                "mean_polarity": round(float(mean_polarity), 3),
                "sample_volume": len(group),
            }
        return results
