import numpy as np

# Fuse facial, speech, and text emotion predictions using weighted average
def fuse_emotions(face_probs, speech_probs, text_probs):
    """
    face_probs: list of 7 floats
    speech_probs: list of 7 floats
    text_probs: list of 7 floats

    Returns:
    fused_probs: list of 7 floats (final emotion probabilities)
    """

    if not (face_probs and speech_probs and text_probs):
        raise ValueError("All three modalities (Face, Speech, Text) must be provided!")

    # Convert to numpy arrays
    face_probs = np.array(face_probs)
    speech_probs = np.array(speech_probs)
    text_probs = np.array(text_probs)

    # Weighted fusion: more trust on text model
    weights = {
        'face': 0.25,
        'speech': 0.25,
        'text': 0.50
    }

    fused_probs = (
        weights['face'] * face_probs +
        weights['speech'] * speech_probs +
        weights['text'] * text_probs
    )

    # Normalize to sum to 1
    fused_probs = fused_probs / np.sum(fused_probs)

    return fused_probs.tolist()
