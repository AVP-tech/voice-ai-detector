from spam_intent.spam_engine import SpamIntentEngine

# Initialize engine (NO arguments)
ENGINE = SpamIntentEngine()

# Test text (strong spam example)
text = """
Your bank account has been blocked.
₹25,000 debited.
Immediate action required.
Click the link now.
"""

# Run spam scoring
result = ENGINE.score(text, lang="en")

# Print output
print("Spam Score:", result["spam_score"])
print("Label:", result["label"])
print("Matched Intents:", result["matched_intents"])
