"""Test pipeline components"""
import sys
from decision_engine.final_decision import get_final_verdict
from spam_intent.spam_engine import SpamIntentEngine

def test_pipeline():
    print("=" * 60)
    print("TESTING PIPELINE COMPONENTS")
    print("=" * 60)
    
    print("\n[TEST 1] Spam Intent Engine")
    test_transcript = "your bank account has been blocked due to incomplete kyc, urgent action required"
    engine = SpamIntentEngine()
    spam_result = engine.score(test_transcript, lang="en")
    spam_score = spam_result["spam_score"]
    matched_intents = spam_result["matched_intents"]
    
    print("[OK] Transcript: " + test_transcript)
    print("[OK] Spam Score: " + str(spam_score))
    print("[OK] Matched Intents: " + str(matched_intents))
    assert spam_score > 0
    assert len(matched_intents) > 0
    print("[OK] Test 1 PASS\n")
    
    print("[TEST 2] Decision Engine")
    voice_type = "AI"
    voice_confidence = 0.95
    verdict = get_final_verdict(voice_type, voice_confidence, spam_score, matched_intents)
    print("[OK] Voice Type: " + verdict['voice_type'])
    print("[OK] Confidence: " + str(verdict['voice_confidence']))
    print("[OK] Spam Percentage: " + str(verdict['spam_percentage']) + "%")
    print("[OK] Final Label: " + verdict['final_label'])
    assert verdict['voice_type'] == "AI"
    assert "SPAM SCAM CALL" in verdict['final_label']
    print("[OK] Test 2 PASS\n")
    
    print("[TEST 3] Decision Rules")
    test_cases = [
        ("AI", 0.75, "SPAM SCAM CALL"),
        ("HUMAN", 0.75, "SUSPICIOUS CALL"),
        ("AI", 0.4, "SUSPICIOUS CALL"),
        ("HUMAN", 0.2, "NORMAL CALL"),
    ]
    
    for voice, spam, expected in test_cases:
        v = get_final_verdict(voice, 0.9, spam, ["TEST"])
        print("[OK] " + voice + " + " + str(int(spam*100)) + "% spam = " + v['final_label'])
        assert expected in v['final_label']
    print("[OK] Test 3 PASS\n")
    
    print("=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)

if __name__ == "__main__":
    test_pipeline()
