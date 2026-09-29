"""LLM Layer Profiles (DASHBOARD_V3_PLAN.md Phase L1).

instruction.md v3 で導入された L1/L2/L3 3 層 LLM アーキテクチャを
LLMGateway 経由で扱うための layer → profile マッピング。

- L1: 常時稼働 / 知覚 / ルーティング — 高速・低コストが望まれる
       (短い response / 構造化出力 / JSON mode 主体)
- L2: 自律思考 / 統合判断            — 中コスト (chat_balanced 相当)
- L3: 深い推論 / Plan 返却           — 高品質 (long_answer 相当、
       reasoning_level=high, 大きな max_tokens)

profile 名は llm.yaml で定義。`LLMGateway.request(layer=...)` が
ここを参照して profile を解決する。
"""

from __future__ import annotations

from typing import Final, Literal

# LLM Layer の Literal 型
LLMLayer = Literal["L1", "L2", "L3"]

# Layer 名の定数 (typo 防止用)
LAYER_L1: Final = "L1"
LAYER_L2: Final = "L2"
LAYER_L3: Final = "L3"

# 有効な Layer 名の frozenset
VALID_LAYERS: Final = frozenset({LAYER_L1, LAYER_L2, LAYER_L3})

# Layer → profile_id マッピング (DASHBOARD_V3_PLAN.md Phase L1 仕様)
# profile 名は llm.yaml の profiles: に定義する想定。
LAYER_TO_PROFILE: Final = {
    LAYER_L1: "l1_default",
    LAYER_L2: "l2_default",
    LAYER_L3: "l3_default",
}

# Layer → 人間向け description
LAYER_DESCRIPTIONS: Final = {
    LAYER_L1: "常時稼働 / 知覚 / ルーティング層 (高速・低コスト)",
    LAYER_L2: "自律思考層 (中コスト)",
    LAYER_L3: "深層推論層 (高品質・reasoning 重視)",
}


def is_valid_layer(layer: str) -> bool:
    """Layer 名が有効 (L1 / L2 / L3) かどうかを判定."""
    return layer in VALID_LAYERS


def layer_to_profile(layer: str) -> str:
    """Layer 名を profile_id に変換.

    Args:
        layer: "L1" | "L2" | "L3"

    Returns:
        profile_id (例: "l1_default")

    Raises:
        ValueError: layer が不正な場合
    """
    if not is_valid_layer(layer):
        raise ValueError(
            f"Invalid LLM layer '{layer}'. Expected one of: {sorted(VALID_LAYERS)}"
        )
    return LAYER_TO_PROFILE[layer]


def layer_description(layer: str) -> str:
    """Layer の人間向け description を返す (Dashboard 表示用)."""
    if not is_valid_layer(layer):
        return f"Unknown layer: {layer}"
    return LAYER_DESCRIPTIONS[layer]


__all__ = [
    "LAYER_DESCRIPTIONS",
    "LAYER_L1",
    "LAYER_L2",
    "LAYER_L3",
    "LAYER_TO_PROFILE",
    "LLMLayer",
    "VALID_LAYERS",
    "is_valid_layer",
    "layer_description",
    "layer_to_profile",
]
