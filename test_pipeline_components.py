"""
Test script for the pipeline components
"""

from decision_engine.final_decision import get_final_verdict
from spam_intent.spam_engine import SpamIntentEngine

def test_pipeline():
    print("="*60)
    print("TESTING PIPELINE COMPONENTS")
    print("="*60)
    
    # Test 1: Spam Intent Engine
    print("\n[TEST 1] Spam Intent Engine")
    test_transcript = "your bank account has been blocked due to incomplete kyc, urgent action required"
    
    engine = SpamIntentEngine()
    spam_result = engine.score(test_transcript, lang="en")
    spam_score = spam_result["spam_score"]
    matched_intents = spam_result["matched_intents"]
    
    print(f"✓ Transcript: {test_transcript}")
    print(f"✓ Spam Score: {spam_score}")
    print(f"✓ Matched Intents: {matched_intents}")
    assert spam_score > 0, "Spam score should be > 0"
    assert len(matched_intents) > 0, "Should match at least one intent"
    print("✓ PASS")
    
    # Test 2: Decision Engine
    print("\n[TEST 2] Decision Engine")
    voice_type = "AI"
    voice_confidence = 0.95
    
    verdict = get_final_verdict(
        voice_type=voice_type,
        voice_confidence=voice_confidence,
        spam_score=spam_score,
        matched_intents=matched_intents
    )
    
    print(f"✓ Voice Type: {verdict['voice_type']} ({verdict['voice_confidence']:.1%})")
    print(f"✓ Spam Score: {verdict['spam_percentage']}%")
    print(f"✓ Final Label: {verdict['final_label']}")
    assert verdict['voice_type'] == "AI", "Voice type should be AI"
    assert verdict['final_label'] == "🚨 SPAM SCAM CALL", "Should be classified as spam scam"
    print("✓ PASS")
    
    # Test 3: Decision Rules
    print("\n[TEST 3] Decision Rules")
    
    # Rule 1: AI + High Spam = SPAM SCAM CALL
    # Rule 2: Medium Spam = SUSPICIOUS CALL
    # Rule 3: Low Spam = NORMAL CALL
    test_cases = [
        ("AI", 0.75, "🚨 SPAM SCAM CALL"),      # AI + high spam >= 0.6
        ("HUMAN", 0.75, "⚠️  SUSPICIOUS CALL"),  # Any + high spam >= 0.6 (not AI)
        ("AI", 0.4, "⚠️  SUSPICIOUS CALL"),      # Any + medium spam 0.3-0.6
        ("HUMAN", 0.2, "✓ NORMAL CALL"),         # Any + low spam < 0.3
    ]
    
    for voice, spam, expected_label in test_cases:
        v = get_final_verdict(voice, 0.9, spam, ["TEST"])
        print(f"✓ {voice} + {int(spam*100)}% spam = {v['final_label']}")
        assert v['final_label'] == expected_label, f"Expected {expected_label}, got {v['final_label']}"
    
    print("✓ PASS - All rules working correctly")
    
    print("\n" + "="*60)
    print("ALL TESTS PASSED ✓")
    print("="*60)

if __name__ == "__main__":
    test_pipeline()
