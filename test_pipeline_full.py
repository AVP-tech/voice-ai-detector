"""Mock test for run_pipeline.py"""
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from spam_intent.spam_engine import SpamIntentEngine
from decision_engine.final_decision import get_final_verdict

def mock_voice_prediction(audio_path):
    return {"result": "AI", "confidence": 0.92}

def test_pipeline_mock():
    print("\n" + "="*60)
    print("VOICE AI DETECTOR - FULL PIPELINE (MOCK TEST)")
    print("="*60)
    
    print("\n[STEP 1] TRANSCRIBING AUDIO...")
    transcript = "your bank account has been temporarily restricted, your account will be suspended today, security alert unusual activity detected on your account, immediate action required"
    print("[OK] Transcript: " + transcript[:70] + "...")
    
    print("\n[STEP 2] DETECTING AI vs HUMAN VOICE...")
    voice_result = mock_voice_prediction("mock_audio.wav")
    voice_type = voice_result["result"]
    voice_confidence = voice_result["confidence"]
    print("[OK] Voice Type: " + voice_type)
    print("     Confidence: " + str(int(voice_confidence*100)) + "%")
    
    print("\n[STEP 3] ANALYZING SPAM INTENT...")
    spam_engine = SpamIntentEngine()
    spam_result = spam_engine.score(transcript, lang="en")
    spam_score = spam_result["spam_score"]
    matched_intents = spam_result["matched_intents"]
    print("[OK] Spam Score: " + str(spam_score) + " (" + str(int(spam_score*100)) + "%)")
    print("     Matched Intents: " + ", ".join(set(matched_intents)) if matched_intents else "None")
    
    print("\n[STEP 4] GENERATING FINAL VERDICT...")
    final_verdict = get_final_verdict(
        voice_type=voice_type,
        voice_confidence=voice_confidence,
        spam_score=spam_score,
        matched_intents=list(set(matched_intents))
    )
    print("[OK] Final Verdict: " + final_verdict['final_label'])
    
    print("\n" + "="*60)
    print("ANALYSIS SUMMARY")
    print("="*60)
    print("Transcript: " + transcript)
    print("Voice Type: " + final_verdict['voice_type'] + " (" + str(int(final_verdict['voice_confidence']*100)) + "%)")
    print("Spam Probability: " + str(final_verdict['spam_percentage']) + "%")
    print("Matched Intents: " + ", ".join(final_verdict['matched_intents']) if final_verdict['matched_intents'] else "None")
    print("FINAL VERDICT: " + final_verdict['final_label'])
    print("="*60 + "\n")
    
    assert voice_type == "AI"
    assert spam_score >= 0.6
    assert "SPAM SCAM CALL" in final_verdict['final_label']
    
    print("[OK] ALL PIPELINE TESTS PASSED\n")

if __name__ == "__main__":
    test_pipeline_mock()
