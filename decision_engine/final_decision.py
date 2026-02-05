"""
Final Decision Engine
Combines AI/Human detection + Spam Intent scoring
Applies strict, production-safe decision rules
"""

from typing import Dict, Any, List


# 🔴 These intents are NEVER normal (industry rule)
HIGH_RISK_INTENTS = {
    "ACCOUNT_THREAT",
    "MONEY_LOSS",
    "LEGAL_THREAT",
    "SEXTORTION",
    "UTILITY_THREAT",
    "OTP_REQUEST",
    "PIN_REQUEST",
    "DELIVERY_SCAM",
}


def get_final_verdict(
    voice_type: str,
    voice_confidence: float,
    spam_score: float,
    matched_intents: List[str]
) -> Dict[str, Any]:

    # Normalize
    voice_type = voice_type.upper()
    spam_score = max(0.0, min(1.0, spam_score))
    spam_percentage = int(spam_score * 100)
    matched_set = set(matched_intents)

    # ================================
    # 🔒 HARD SAFETY RULES (DO NOT BREAK)
    # ================================

    # DEBUG LOGGING (for traceability)
    print("[DEBUG] Transcript processed for spam decision:")
    print(f"  Voice Type: {voice_type}")
    print(f"  Matched Intents: {sorted(matched_intents)}")
    print(f"  Spam Score: {spam_score:.2f} ({spam_percentage}%)")

    # RULE 1: Any high-risk intent → never NORMAL
    if matched_set & HIGH_RISK_INTENTS:
        # Delivery scam should always be SPAM
        if "DELIVERY_SCAM" in matched_set:
            final_label = "IT IS A SPAM CALL, AVOID IT"
        else:
            final_label = "IT IS A SPAM CALL, AVOID IT" if spam_score >= 0.6 else "SUSPICIOUS CALL"

    # RULE 2: High spam score alone is enough (voice_type never blocks)
    elif spam_score >= 0.6:
        final_label = "IT IS A SPAM CALL, AVOID IT"

    # RULE 3: Medium spam = suspicious
    elif spam_score >= 0.3:
        final_label = "SUSPICIOUS CALL"

    # RULE 4: Truly safe
    else:
        final_label = "NORMAL CALL"

    return {
        "voice_type": voice_type,
        "voice_confidence": round(voice_confidence, 3),
        "spam_score": round(spam_score, 2),
        "spam_percentage": spam_percentage,
        "matched_intents": sorted(matched_intents),
        "final_label": final_label
    }


# 🧪 Local sanity test (optional)
if __name__ == "__main__":
    tests = [
        ("AI", 0.96, 0.2, ["ACCOUNT_THREAT"]),
        ("HUMAN", 0.92, 0.4, ["URGENCY"]),
        ("AI", 0.88, 0.7, []),
        ("HUMAN", 0.95, 0.1, []),
    ]

    for t in tests:
        print(get_final_verdict(*t))
