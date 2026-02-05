"""
End-to-End Pipeline Runner
Audio -> STT -> Spam Intent -> AI/Human Detection -> Final Verdict
"""

import sys
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from stt.transcribe import transcribe_audio
from spam_intent.spam_engine import SpamIntentEngine
from inference.predict import predict_audio
from decision_engine.final_decision import get_final_verdict


def run_pipeline(audio_path: str, verbose: bool = True) -> dict:
    """
    Run complete pipeline on audio file.
    """

    audio_path = Path(audio_path)

    if verbose:
        print("\n" + "=" * 60)
        print("VOICE AI DETECTOR - FULL PIPELINE")
        print("=" * 60)

    # Step 1: Speech-to-Text
    if verbose:
        print("\n[STEP 1] TRANSCRIBING AUDIO...")
    try:
        transcript = transcribe_audio(str(audio_path))
        if not transcript:
            transcript = "[No speech detected]"
            if verbose:
                print("WARNING: Empty transcript")
        else:
            if verbose:
                print(
                    f"OK Transcript: {transcript[:100]}..."
                    if len(transcript) > 100
                    else f"OK Transcript: {transcript}"
                )
    except Exception as e:
        if verbose:
            print(f"ERROR STT: {e}")
        return {"error": str(e), "stage": "STT"}

    # Step 2: AI/Human Detection
    if verbose:
        print("\n[STEP 2] DETECTING AI vs HUMAN VOICE...")
    try:
        voice_result = predict_audio(str(audio_path))
        voice_type = voice_result["result"]
        voice_confidence = voice_result["confidence"]

        if verbose:
            print(f"OK Voice Type: {voice_type}")
            print(f"  Confidence: {voice_confidence:.2%}")
    except Exception as e:
        if verbose:
            print(f"ERROR Voice Detection: {e}")
        return {"error": str(e), "stage": "VOICE_DETECTION"}

    # Step 3: Spam Intent Scoring
    if verbose:
        print("\n[STEP 3] ANALYZING SPAM INTENT...")
    try:
        spam_engine = SpamIntentEngine()  # no args
        spam_result = spam_engine.score(transcript)

        spam_score = spam_result["spam_score"]
        matched_intents = spam_result["matched_intents"]

        if verbose:
            print(f"OK Spam Score: {spam_score:.2f} ({int(spam_score * 100)}%)")
            print(
                f"  Matched Intents: {', '.join(set(matched_intents))}"
                if matched_intents
                else "  Matched Intents: None"
            )

    except Exception as e:
        if verbose:
            print(f"ERROR Spam Analysis: {e}")
        return {"error": str(e), "stage": "SPAM_ANALYSIS"}

    # Step 4: Final Decision
    if verbose:
        print("\n[STEP 4] GENERATING FINAL VERDICT...")
    try:
        final_verdict = get_final_verdict(
            voice_type=voice_type,
            voice_confidence=voice_confidence,
            spam_score=spam_score,
            matched_intents=list(set(matched_intents)),
        )
        if verbose:
            print(f"OK Final Verdict: {final_verdict['final_label']}")
    except Exception as e:
        if verbose:
            print(f"ERROR Decision: {e}")
        return {"error": str(e), "stage": "DECISION"}

    # Summary
    if verbose:
        print("\n" + "=" * 60)
        print("ANALYSIS SUMMARY")
        print("=" * 60)
        print(f"Transcript: {transcript}")
        print(
            f"Voice Type: {final_verdict['voice_type']} "
            f"({final_verdict['voice_confidence']:.2%} confidence)"
        )
        print(f"Spam Probability: {final_verdict['spam_percentage']}%")
        print(
            f"Matched Intents: {', '.join(final_verdict['matched_intents'])}"
            if final_verdict["matched_intents"]
            else "Matched Intents: None"
        )
        print(f"FINAL VERDICT: {final_verdict['final_label']}")
        print("=" * 60 + "\n")

    final_verdict["transcript"] = transcript
    return final_verdict


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_pipeline.py <audio_file.wav>")
        sys.exit(1)

    audio_file = sys.argv[1]

    try:
        result = run_pipeline(audio_file)
        if "error" in result:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nPipeline interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nERROR Unexpected error: {e}")
        sys.exit(1)
