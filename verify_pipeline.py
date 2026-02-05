"""Final verification test - no emoji"""
import sys
from decision_engine.final_decision import get_final_verdict
from spam_intent.spam_engine import SpamIntentEngine

print("=" * 60)
print("FINAL VERIFICATION - PIPELINE COMPONENTS")
print("=" * 60)

# Test 1: Spam Engine
print("\n[TEST 1] Spam Intent Engine")
engine = SpamIntentEngine()
result = engine.score("your bank account blocked kyc urgent action", lang="en")
print("Spam Score: " + str(result['spam_score']))
print("Label: " + result['label'])
print("Intents: " + str(result['matched_intents']))
assert result['spam_score'] > 0
print("[PASS]\n")

# Test 2: Decision Engine
print("[TEST 2] Decision Engine")
verdict = get_final_verdict("AI", 0.95, 0.6, ["TEST"])
print("Voice Type: " + verdict['voice_type'])
print("Spam Percentage: " + str(verdict['spam_percentage']) + "%")
print("Final Label: [SPAM SCAM CALL detected]")
assert "SPAM SCAM CALL" in verdict['final_label']
print("[PASS]\n")

# Test 3: Rules
print("[TEST 3] Decision Rules")
test_cases = [
    ("AI", 0.75, "SPAM"),
    ("HUMAN", 0.75, "SUSPICIOUS"),
    ("HUMAN", 0.2, "NORMAL"),
]
for voice, spam, expected in test_cases:
    v = get_final_verdict(voice, 0.9, spam, [])
    assert expected in v['final_label']
    print(voice + " + " + str(int(spam*100)) + "% = " + expected + " [OK]")
print("[PASS]\n")

print("=" * 60)
print("ALL TESTS PASSED - PIPELINE READY")
print("=" * 60)
