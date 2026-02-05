import numpy as np
import librosa


def extract_features_from_wav(filepath, sr=16000):
    """
    Extract robust, calibration-friendly features for
    AI-generated vs Human voice detection.
    """

    try:
        y, sr = librosa.load(filepath, sr=sr, mono=True)
    except Exception:
        return None

    # 🔒 Remove silence (VERY IMPORTANT)
    y, _ = librosa.effects.trim(y, top_db=25)

    # Skip too-short audio AFTER trimming
    if len(y) < sr * 2:
        return None

    features = []

    # 1️⃣ MFCC + deltas (vocoder smoothing detector)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
    delta = librosa.feature.delta(mfcc)
    delta2 = librosa.feature.delta(mfcc, order=2)

    features.extend(np.mean(mfcc, axis=1))
    features.extend(np.std(mfcc, axis=1))
    features.extend(np.mean(delta, axis=1))
    features.extend(np.mean(delta2, axis=1))

    # 2️⃣ Spectral features (AI over-clean artifacts)
    spec_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    spec_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
    spec_flatness = librosa.feature.spectral_flatness(y=y)
    spec_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)

    features.extend([
        np.mean(spec_centroid),
        np.std(spec_centroid),
        np.mean(spec_bandwidth),
        np.mean(spec_flatness),
        np.mean(spec_rolloff),
    ])

    # 3️⃣ Pitch instability (AI weakness)
    pitches, mags = librosa.piptrack(y=y, sr=sr)
    pitch_vals = pitches[mags > np.percentile(mags, 75)]
    pitch_vals = pitch_vals[pitch_vals > 0]

    if len(pitch_vals) > 0:
        features.extend([
            np.mean(pitch_vals),
            np.std(pitch_vals),
        ])
    else:
        features.extend([0.0, 0.0])

    # 4️⃣ Energy dynamics (calibration critical)
    rms = librosa.feature.rms(y=y)
    features.extend([
        np.mean(rms),
        np.std(rms),
        np.percentile(rms, 90) - np.percentile(rms, 10),  # dynamic range
    ])

    # 5️⃣ Temporal jitter proxy
    zcr = librosa.feature.zero_crossing_rate(y)
    features.extend([
        np.mean(zcr),
        np.std(zcr),
    ])

    return np.array(features, dtype=np.float32)


# 🔁 BACKWARD COMPATIBILITY
def extract_features(filepath, sr=16000):
    return extract_features_from_wav(filepath, sr)
