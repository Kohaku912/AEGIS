"""Intake deduplicator — Phase 4 (instruction.md §11).

`TaskManager._incident_fingerprint()` の考えを intake 層に持ち込む。
最近 N 件の fingerprint を保持し、新規 event の fingerprint と一致したら
「重複」とみなす。

判定ルール:
- 単純な `(source, description[:80])` のタプルでも dedup 可能
- もしくは classifier から得た `intake_result.novelty` を使う
- 両方サポート
"""
from __future__ import annotations

import hashlib
import logging
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Deque

logger = logging.getLogger("aegis_ai.intake.deduplicator")


@dataclass
class IntakeDeduplicator:
    """イベント重複排除器.

    Attributes:
        window_size: 直近何件の fingerprint を保持するか.
        novelty_threshold: novelty スコアがこの値未満なら重複とみなす.
    """

    window_size: int = 64
    novelty_threshold: float = 0.3
    _fingerprints: Deque[str] = field(default_factory=deque)

    def __post_init__(self) -> None:
        if self.window_size < 0:
            raise ValueError("window_size must be >= 0")
        # 初期 deque の maxlen を window_size に固定
        self._fingerprints = deque(maxlen=max(1, self.window_size))

    # ------------------------------------------------------------------
    # Fingerprint
    # ------------------------------------------------------------------

    @staticmethod
    def make_fingerprint(event: dict[str, Any]) -> str:
        """event 辞書から決定論的な fingerprint を作る.

        `(source, description[:80])` の正規化文字列を SHA-256 で
        ハッシュする。`description` がないときは空文字扱い。
        """
        source = str(event.get("source") or event.get("kind") or "").strip().lower()
        description = str(event.get("description") or event.get("text") or "")[:80].strip().lower()
        canonical = f"{source}|{description}"
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def has_seen(self, event: dict[str, Any]) -> bool:
        """`event` の fingerprint が直近 window にあれば True."""
        return self.make_fingerprint(event) in self._fingerprints

    def record(self, event: dict[str, Any]) -> None:
        """`event` の fingerprint を記録."""
        self._fingerprints.append(self.make_fingerprint(event))

    # ------------------------------------------------------------------
    # Combined check
    # ------------------------------------------------------------------

    def is_duplicate(
        self,
        event: dict[str, Any],
        *,
        novelty: float | None = None,
    ) -> bool:
        """重複とみなすなら True.

        - `novelty` スコアが与えられたときは閾値と比較 (低いほど重複)
        - スコア未指定のときは fingerprint の window マッチを使う
        - 両方を渡したときは **両方 OK** で重複扱い (OR)
        """
        fingerprint_dup = self.has_seen(event)
        novelty_dup = (
            novelty is not None and float(novelty) < self.novelty_threshold
        )
        return bool(fingerprint_dup or novelty_dup)

    def stats(self) -> dict[str, int]:
        return {"window_used": len(self._fingerprints), "window_size": self.window_size}


__all__ = ["IntakeDeduplicator"]
