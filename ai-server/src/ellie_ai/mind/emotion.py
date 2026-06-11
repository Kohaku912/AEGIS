"""Emotion — urgency, confidence, fatigue proxy.

STATUS: Skeleton.
"""


class Emotion:
    """Ellie's emotion-like state indicators. Not real emotions — state proxies."""

    urgency: int = 0            # 0 = calm, 10 = critical
    confidence: float = 0.5     # 0.0 = uncertain, 1.0 = very confident
    fatigue_proxy: float = 0.0  # Tracks cognitive load proxy

    def update(self, urgency: int | None = None, confidence: float | None = None) -> None:
        if urgency is not None:
            self.urgency = max(0, min(10, urgency))
        if confidence is not None:
            self.confidence = max(0.0, min(1.0, confidence))

    def is_urgent(self) -> bool:
        return self.urgency >= 7
