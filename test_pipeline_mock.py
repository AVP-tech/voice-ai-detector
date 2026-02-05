"""
Mock test for run_pipeline.py - tests the pipeline logic without actual audio
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from stt.transcribe import transcribe_audio
from spam_intent.spam_engine import SpamIntentEngine
from decision_engine.final_decision import get_final_verdict


def mock_voice_prediction(audio_path):
    """Mock the AI/Human voice prediction"""
    # For testing purposes, return mock data
    return {
        "result": "AI",
        "confidence": 0.92
    }


def test_pipeline_mock():
    """Test the pipeline with mock data (no actual audio needed)"""
    
    print("\n" + "="*60)
    print("VOICE AI DETECTOR - FULL PIPELINE (MOCK TEST)")
    print("="*60)
    
    # Mock transcript
    print("\n[STEP 1] TRANSCRIBING AUDIO...")
    transcript = "your bank account has been temporarily restricted, your account will be suspended today, security alert unusual activity detected on your account, immediate action required"
    print(f"✓ Transcript: {transcript}")
    
    # Get AI/Human detection (using mock)
    print("\n[STEP 2] DETECTING AI vs HUMAN VOICE...")
    voice_result = mock_voice_prediction("mock_audio.wav")
    voice_type = voice_result["result"]
    voice_confidence = voice_result["confidence"]
    print(f"✓ Voice Type: {voice_type}")
    print(f"  Confidence: {voice_confidence:.2%}")
    
    # Get Spam Intent Scoring
    print("\n[STEP 3] ANALYZING SPAM INTENT...")
    spam_engine = SpamIntentEngine()
    spam_result = spam_engine.score(transcript, lang="en")
    spam_score = spam_result["spam_score"]
    matched_intents = spam_result["matched_intents"]
    print(f"✓ Spam Score: {spam_score} ({int(spam_score*100)}%)")
    print(f"  Matched Intents: {', '.join(set(matched_intents))}")
    
    # Get Final Decision
    print("\n[STEP 4] GENERATING FINAL VERDICT...")
    final_verdict = get_final_verdict(
        voice_type=voice_type,
        voice_confidence=voice_confidence,
        spam_score=spam_score,
        matched_intents=list(set(matched_intents))
    )
    print(f"✓ Final Verdict: {final_verdict['final_label']}")
    
    # Print Summary
    print("\n" + "="*60)
    print("ANALYSIS SUMMARY")
    print("="*60)
    print(f"Transcript: {transcript}")
    print(f"Voice Type: {final_verdict['voice_type']} ({final_verdict['voice_confidence']:.2%} confidence)")
    print(f"Spam Probability: {final_verdict['spam_percentage']}%")
    print(f"Matched Intents: {', '.join(final_verdict['matched_intents'])}")
    print(f"FINAL VERDICT: {final_verdict['final_label']}")
    print("="*60 + "\n")
    
    # Verify expected results
    assert voice_type == "AI", "Expected AI voice"
    assert spam_score >= 0.6, f"Expected high spam score, got {spam_score}"
    assert "🚨 SPAM SCAM CALL" in final_verdict['final_label'], "Expected SPAM SCAM CALL label"
    
    print("✓ ALL PIPELINE TESTS PASSED\n")


if __name__ == "__main__":
    test_pipeline_mock()
