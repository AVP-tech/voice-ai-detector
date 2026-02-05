import json
import re
from pathlib import Path
from typing import Dict, List
class SpamIntentEngine:
    def __init__(self):
        base_dir = Path(__file__).resolve().parent
        intent_path = base_dir / "data" / "spam_intents.json"

        with open(intent_path, "r", encoding="utf-8") as f:
            self.intents = json.load(f)

        # Manual phrases that must always be treated as spam (exact/near-exact match)
        self.manual_spam_phrases = [
            "abhinandan aalu",
            "amazon offer",
            "me bank account kyc gadhvi movie shinde account",
            "prabhutv kotha padam malayalam smartphone",
        ]

        # Quick native-script keyword triggers for Tamil/Telugu/Malayalam
        # (fast fix for missed matches in those languages)
        self.native_lang_keywords = {
            "ta": {
                "ACCOUNT_THREAT": ["கணக்கு", "முடக்க", "சஸ்பெண்ட்", "தடை", "KYC", "சந்தேகம்"],
                "OTP_REQUEST": ["otp", "ஓடிபி", "உறுதிப்படுத்தும் குறியீடு"],
                "PIN_REQUEST": ["pin", "பின்", "upi pin"],
                "TOO_GOOD_TO_BE_TRUE": ["வெற்றி", "லாட்டரி", "பரிசு", "இலவச", "ஜாக்பாட்", "கேஷ்பேக்", "ஆஃபர்"],
                "MONEY_LOSS": ["பணம்", "நிதி", "ரூபாய்", "கட்டணம்", "டெபிட்", "கழித்த", "இழப்பு"],
                "DELIVERY_SCAM": ["டெலிவரி", "பார்சல்", "சரக்கு", "கூரியர்", "கட்டணம்", "OTP"],
            },
            "te": {
                "ACCOUNT_THREAT": ["ఖాతా", "బ్లాక్", "సస్పెండ్", "KYC", "సందేహ", "నిలిపి"],
                "OTP_REQUEST": ["otp", "ఓటిపి", "వెరిఫికేషన్ కోడ్"],
                "PIN_REQUEST": ["pin", "పిన్", "upi pin", "ఎంపిన్"],
                "TOO_GOOD_TO_BE_TRUE": ["లాటరీ", "బహుమతి", "ఉచితం", "జాక్పాట్", "ఆఫర్", "విజేత"],
                "MONEY_LOSS": ["డబ్బు", "నష్టం", "రూపాయలు", "చెల్లింపు", "డెబిట్", "కట్"],
                "DELIVERY_SCAM": ["డెలివరీ", "ప్యాకేజీ", "పార్సెల్", "కూరియర్", "ఫీజు", "OTP"],
            },
            "ml": {
                "ACCOUNT_THREAT": ["അക്കൗണ്ട്", "ബ്ലോക്ക്", "സസ്പെൻഡ്", "KYC", "സംശയം", "നിർത്തലാക്കും"],
                "OTP_REQUEST": ["otp", "ഓടിപി", "സ്ഥിരീകരണ കോഡ്"],
                "PIN_REQUEST": ["pin", "പിന്", "upi pin", "എംപിൻ"],
                "TOO_GOOD_TO_BE_TRUE": ["ലോട്ടറി", "സമ്മാനം", "ഫ്രീ", "ജാക്ക്പോട്ട്", "ഓഫർ", "വിജയി"],
                "MONEY_LOSS": ["പണം", "നഷ്ടം", "രൂപ", "ചാർജ്", "ഡെബിറ്റ്", "കുറവ്"],
                "DELIVERY_SCAM": ["ഡെലിവറി", "പാക്കേജ്", "പാർസൽ", "കൂറിയർ", "ഫീസ്", "OTP"],
            },
        }

        # Harmless phrases that should not trigger INSTRUCTION intent
        self.safe_phrases = [
            "call me back",
            "please call me back",
            "call me when you can",
            "please call me",
            "give me a call",
            "call me later",
            "call kar lena",
            "baad me call karna",
            "call karlena",
        ]

        # Regex patterns for semantic scam detection
        self.regex_patterns = {
            "LEGAL_THREAT": [
                r"\bsocial security\b",
                r"\bssn\b",
                r"\bunder investigation\b",
                r"\blegal action\b",
                r"\blaw enforcement\b",
                r"\bpolice\b",
                r"\barrest warrant\b",
                r"\bcourt notice\b",
                r"\bgovernment office\b",
                r"\bcase registered\b",
                r"நீதிமன்றம்",
                r"சட்டம்",
                r"கோர்ட்",
                r"పోలీసు",
                r"కోర్టు",
                r"നിയമം",
                r"കോടതി",
                r"अदालत",
                r"पुलिस",
                r"कानूनी",
            ],
            "MONEY_LOSS": [
                r"\brs\.?\s*\d+",
                r"\brupees?\s*\d+",
                r"\b\d+\s*(?:rupees|rs\.?)",
                r"\brs\s*\d+",
                r"\brupee\s*\d+",
                r"\b\d+\s*(?:pounds|gbp)\b",
                r"\bdebited\b",
                r"\bwithdrawn\b",
                r"\bmoney taken\b",
                r"\bfunds transferred\b",
                r"\bamount deducted\b",
                r"\bpayment\b",
                r"\btransaction\b",
                r"\brefund\b",
                r"\bbank details\b",
                r"\btransfer\b",
                r"பணம்",
                r"ரூபாய்",
                r"கட்டணம்",
                r"டெபிட்",
                r"డబ్బు",
                r"రూపాయ",
                r"ചാർജ്",
                r"രൂപ",
                r"पैसा",
                r"रुपये",
                r"भुगतान",
            ],
            "OTP_REQUEST": [
                r"\botp\b",
                r"\bone[-\s]?time password\b",
                r"\b\d{4,8}\s*digit\b",
                r"\b\d{4,8}\s*digits\b",
                r"\b\d{4,8}\b\s*(?:ka|ki)?\s*otp",
                r"\bshare\s*otp\b",
                r"\btell\s*otp\b",
                r"ஓடிபி",
                r"ఓటిపి",
                r"ഓടിപി",
                r"ओटीपी",
            ],
            "PIN_REQUEST": [
                r"\bpin\b",
                r"\bupi\s*pin\b",
                r"\btransaction\s*pin\b",
                r"\bmpin\b",
                r"\bcvv\b",
                r"\bpassword\b",
                r"பின்",
                r"పిన్",
                r"പിന്",
                r"पिन",
            ],
            "DELIVERY_SCAM": [
                r"\bdelivery\b",
                r"\bparcel\b",
                r"\bcourier\b",
                r"\bpackage\b",
                r"\bamazon\b",
                r"\bflipkart\b",
                r"\bmeesho\b",
                r"\bmyntra\b",
                r"\bdelivery\s*cancel\b",
                r"\bparcel\s*cancel\b",
                r"டெலிவரி",
                r"பார்சல்",
                r"డెలివరీ",
                r"పార్సెల్",
                r"ഡെലിവറി",
                r"പാർസൽ",
                r"डिलिवरी",
                r"पार्सल",
            ],
            "ACCOUNT_THREAT": [
                r"\baccount\b.*\bkyc\b",
                r"\bkyc\b.*\baccount\b",
                r"\bkyc\b",
                r"\bbank\b.*\baccount\b.*\blocked\b",
                r"\baccount\b.*\blocked\b",
                r"\baccount\b.*\blocked\b.*\bsuspicious\b",
                r"\bsuspicious activity\b",
                r"\bverify\b.*\bidentity\b",
                r"\bidentity\b.*\bverify\b",
                r"\baccount\b.*\btemporarily locked\b",
                r"\btemporarily locked\b",
                r"கணக்கு",
                r"முடக்க",
                r"సస్పెండ్",
                r"బ్లాక్",
                r"അക്കൗണ്ട്",
                r"ബ്ലോക്ക്",
                r"खाता",
                r"ब्लॉक",
                r"केवाईसी",
            ],
            "TOO_GOOD_TO_BE_TRUE": [
                r"\bamazon\b.*\boffer\b",
                r"\boffer\b.*\bamazon\b",
                r"\blucky\s*draw\b",
                r"\blottery\b",
                r"\bjackpot\b",
                r"\bwon\b.*\bprize\b",
                r"\bcongratulations\b",
                r"\bkbc\b",
                r"\bjeet\b",
                r"\binaam\b",
                r"\binam\b",
                r"\bpuraskar\b",
                r"\btax\s*refund\b",
                r"\brefund\b",
                r"வெற்றி",
                r"லாட்டரி",
                r"பரிசு",
                r"இலவச",
                r"ஆஃபர்",
                r"கேஷ்பேக்",
                r"ലോട്ടറി",
                r"സമ്മാനം",
                r"വിജയി",
                r"ഫ്രീ",
                r"ഓഫർ",
                r"లాటరీ",
                r"బహుమతి",
                r"విజేత",
                r"ఆఫర్",
                r"लॉटरी",
                r"इनाम",
            ],
            "INSTRUCTION": [
                r"\bwhatsapp\b",
                r"\bcall\b",
                r"\bcontact\b",
                r"\bmessage\b",
                r"\bmsg\b",
                r"\bnumber\b",
                r"\bclick here\b",
                r"\bclick\b",
                r"\bregister\b",
                r"\bregistration fee\b",
                r"\bprocessing fee\b",
                r"\bpay\b.*\bfee\b",
                r"கிளிக்",
                r"அழைக்க",
                r"தொடர்பு",
                r"வாட்ஸ்அப்",
                r"பதிவு",
                r"క్లిక్",
                r"కాల్",
                r"వాట్సాప్",
                r"రెజిస్టర్",
                r"ക്ലിക്ക്",
                r"വിളിക്കുക",
                r"ബന്ധപ്പെടുക",
                r"വാട്ട്സാപ്പ്",
                r"രജിസ്റ്റർ",
                r"कॉल",
                r"क्लिक",
                r"व्हाट्सएप",
                r"रजिस्टर",
                r"संपर्क",
            ],
        }


        # Strong money context keywords
        self.money_keywords = [
            "rs", "rupee", "rupees",
            "debit", "debited", "credit", "credited",
            "withdrawn", "payment", "transaction",
            "amount", "balance", "transfer", "upi"
        ]

        # Explicit NON-money contexts
        self.non_money_context = [
            "years old", "year old", "age", "aged",
            "years", "months", "days",
            "minutes", "hours"
        ]

    def _has_money_context(self, text: str) -> bool:
        return any(k in text for k in self.money_keywords)

    def _has_non_money_context(self, text: str) -> bool:
        return any(p in text for p in self.non_money_context)

    def _normalize(self, text: str) -> str:
        text = text.lower()
        # Keep unicode letters/digits so non-English phrases can match
        text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def score(self, text: str) -> Dict:
        raw_text = text.lower()
        text = self._normalize(text)
        score = 0.0
        matched_intents = set()

        # Intents that can be matched with short phrases (delivery scam needs stronger context)
        high_risk_intents = {"ACCOUNT_THREAT", "MONEY_LOSS", "LEGAL_THREAT", "OTP_REQUEST", "PIN_REQUEST", "MANUAL_SPAM"}

        # 0) Manual spam phrase matches (force spam)
        for phrase in self.manual_spam_phrases:
            if self._normalize(phrase) and self._normalize(phrase) in text:
                matched_intents.add("MANUAL_SPAM")
                score = max(score, 0.9)
                break

        # 1) PHRASE-BASED MATCHING (multi-language)
        for intent, data in self.intents.items():
            weight = data["weight"]
            phrases = data["phrases"]

            for lang_key, lang_phrases in phrases.items():
                for phrase in lang_phrases:
                    norm_phrase = self._normalize(phrase)
                    if not norm_phrase:
                        continue
                    # B) Skip very short phrases to reduce false positives
                    if len(norm_phrase.split()) <= 2:
                        if intent not in high_risk_intents:
                            continue
                        if intent == "DELIVERY_SCAM":
                            continue
                    if norm_phrase in text:
                        score += weight
                        matched_intents.add(intent)
                        break
                if intent in matched_intents:
                    break

        # 1.5) Native-script keyword quick match (Tamil/Telugu/Malayalam)
        for _lang, lang_map in self.native_lang_keywords.items():
            for intent, keywords in lang_map.items():
                if any(k in raw_text for k in keywords):
                    score += 0.3
                    matched_intents.add(intent)

        # 2) REGEX-BASED SEMANTIC DETECTION (context-aware)
        for intent, patterns in self.regex_patterns.items():
            for pattern in patterns:
                if not re.search(pattern, raw_text):
                    continue

                # MONEY_LOSS - strict context filtering
                if intent == "MONEY_LOSS":
                    if self._has_non_money_context(text) and not self._has_money_context(text):
                        continue

                    if not self._has_money_context(text):
                        continue

                    score += 0.2
                    matched_intents.add(intent)
                    break

                # LEGAL_THREAT - softer boost
                if intent == "LEGAL_THREAT":
                    score += 0.25
                    matched_intents.add(intent)
                    break

                # OTP/PIN requests are high risk on human calls
                if intent in {"OTP_REQUEST", "PIN_REQUEST"}:
                    score += 0.35
                    matched_intents.add(intent)
                    break

                # Delivery scams need scam context (avoid false positives on normal delivery mentions)
                if intent == "DELIVERY_SCAM":
                    scam_context = [
                        "otp", "code", "pin", "payment", "pay", "fee", "charge",
                        "refund", "cancel", "cancellation", "link", "address",
                        "verification", "kyc", "hold", "blocked"
                    ]
                    if not any(k in raw_text for k in scam_context):
                        continue
                    score += 0.35
                    matched_intents.add(intent)
                    break

                score += 0.3
                matched_intents.add(intent)
                break

        # Remove INSTRUCTION if only harmless intent phrases are present
        if "INSTRUCTION" in matched_intents:
            if any(p in raw_text for p in self.safe_phrases):
                matched_intents.discard("INSTRUCTION")
                score = max(0.0, score - 0.2)

        # Clamp score
        score = min(score, 1.0)

        # 3) Label logic
        # A) Require at least 2 intents for SPAM unless high-risk intent is present
        has_high_risk = bool(matched_intents & high_risk_intents)
        if score >= 0.6 and (has_high_risk or len(matched_intents) >= 2):
            label = "SPAM SCAM CALL"
        elif score >= 0.3:
            label = "SUSPICIOUS CALL"
        else:
            label = "NORMAL CALL"

        return {
            "spam_score": round(score, 2),
            "label": label,
            "matched_intents": sorted(matched_intents),
        }
        
