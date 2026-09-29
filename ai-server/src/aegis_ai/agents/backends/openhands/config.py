"""WorkspaceSpec — Phase 2.

§19 で定義された workspace 戦略 (READ_ONLY / ISOLATED / PERSISTENT) を
dataclass で表現する。OpenHands backend でのみ使用し、AEGIS core には
漏らさない (Phase 2 の import 境界を保つため)。

このモジュールは OpenHands SDK に依存しない。`adapter.py` が
WorkspaceSpec を受け取って OpenHands の `LocalWorkspace` / `RemoteAPIWorkspace`
に翻訳する役割。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

WorkspaceMode = Literal["read_only", "isolated", "persistent"]


@dataclass
class WorkspaceSpec:
    """Agent が作業する workspace の宣言 (§19 参照).

    Attributes:
        mode: "read_only" / "isolated" / "persistent" のいずれか
        path: workspace の基底ディレクトリ。None のときは default worktree を作成
        mount_ro: True のとき workspace は read-only
        protected_paths: 絶対パス。Agent はここへの書き込みを許可されない
        base_branch: ISOLATED mode で worktree を切る元 branch
        worktree_branch: ISOLATED mode で新規作成する branch 名
    """

    mode: WorkspaceMode = "isolated"
    path: str | None = None
    mount_ro: bool = False
    protected_paths: list[str] = field(default_factory=list)
    base_branch: str = "main"
    worktree_branch: str | None = None

    def is_writable(self) -> bool:
        """workspace が書き込み可能か (§19 invariant)."""
        if self.mode == "read_only":
            return False
        if self.mount_ro:
            return False
        return True

    def is_persistent(self) -> bool:
        """PERSISTENT mode のとき True. requires_approval=True 相当."""
        return self.mode == "persistent"

    def validate(self) -> list[str]:
        """manifest ロード時に検査する。違反時は list[str] で error を返す."""
        errors: list[str] = []
        if self.mode not in ("read_only", "isolated", "persistent"):
            errors.append(f"workspace.mode invalid: {self.mode!r}")
        if self.mode == "read_only" and self.mount_ro is False:
            # read_only なのに mount_ro=False は矛盾
            errors.append("workspace.mode=read_only requires mount_ro=True")
        if self.mode == "persistent" and not self.path:
            errors.append("workspace.mode=persistent requires explicit path")
        return errors
