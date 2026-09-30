#!/usr/bin/env python3
"""Execution script for Tamil and Tanglish NLP, speech stylometrics, and rhetorical framing."""
from tn26.data_ingestion.social_signals_loader import SocialSignalsLoader
from tn26.data_ingestion.speech_corpus_loader import SpeechCorpusLoader
from tn26.models.nlp_sentiment_analyzer import TamilSentimentStanceClassifier
from tn26.models.propaganda_framing_detector import RhetoricalFramingDetector


def main():
    print("=" * 80)
    print("  TN26 MULTILINGUAL NLP, SPEECH STYLOMETRICS & RHETORICAL FRAMING")
    print("=" * 80)

    speech_loader = SpeechCorpusLoader()
    framing_detector = RhetoricalFramingDetector(speech_loader)
    social_loader = SocialSignalsLoader()
    sentiment_clf = TamilSentimentStanceClassifier(social_loader)

    print("\n[1] STYLOMETRIC ANALYSIS OF ARCHIVED LEADER SPEECHES")
    print("-" * 80)
    stylometrics = speech_loader.compute_stylometrics()
    print(stylometrics[["leader", "party", "location", "total_tokens", "lexical_diversity_ttr", "dynasty_frame_density", "welfare_frame_density", "tasmac_critique_density"]].to_string(index=False))
    print("-" * 80)

    print("\n[2] DOMINANT RHETORICAL FRAMING IN MAJOR CAMPAIGN ADDRESSES")
    print("-" * 80)
    frames_df = framing_detector.analyze_leader_speeches()
    print(frames_df[["leader", "party", "dominant_frame", "Dynastic_Monopoly_Frame", "Cinema_Inexperience_Frame", "Dravidian_Welfare_Frame", "TASMAC_Moral_Ruin_Frame"]].to_string(index=False))
    print("-" * 80)

    print("\n[3] CROSS-PLATFORM DIGITAL STANCE & ENGAGEMENT ANALYSIS")
    print("-" * 80)
    platform_stances = social_loader.compute_platform_stance_shares()
    print(platform_stances.head(15).to_string(index=False))
    print("-" * 80)

    print("\n[4] STATEWIDE WEIGHTED DIGITAL SENTIMENT SUMMARY")
    weighted_sentiment = social_loader.get_weighted_sentiment_summary()
    for stance, data in weighted_sentiment.items():
        print(f"  * {stance:22s} : Share of Voice: {data['share_of_voice_pct']:5.2f}% | Mean Polarity: {data['mean_polarity']:+5.3f} | Sample: {data['sample_volume']}")

    print("\n" + "=" * 80)
    print("NLP DISCOURSE ANALYSIS COMPLETED.")
    print("=" * 80)


if __name__ == "__main__":
    main()
