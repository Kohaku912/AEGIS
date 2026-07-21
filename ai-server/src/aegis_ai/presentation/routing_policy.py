"""Structured routing policy for proactive presentations."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PresentationRoutingContext:
    """Facts used to choose presentation surfaces without inspecting prose."""

    importance: str = "normal"
    urgency: str = "normal"
    requires_action: bool = False
    user_presence: str = "unknown"
    active_device: str = "unknown"
    user_attention: str = "unknown"
    privacy: str = "normal"
    expected_usefulness: float = 0.5
    interruption_cost: float = 0.5
    available_surfaces: frozenset[str] = field(
        default_factory=lambda: frozenset({"dashboard", "pc", "android"})
    )


@dataclass(frozen=True)
class PresentationRoutingDecision:
    targets: tuple[str, ...]
    interrupt: bool
    reason: str
    display_eligible: bool = True


class PresentationRoutingPolicy:
    """Route structured presentation facts to the least disruptive surfaces."""

    def decide(self, context: PresentationRoutingContext) -> PresentationRoutingDecision:
        available = context.available_surfaces
        privacy = context.privacy.lower()
        urgent = context.urgency.lower() in {"urgent", "critical"}
        important = context.importance.lower() in {"high", "critical"}
        occupied = context.user_attention.lower() in {"focused", "occupied", "sleeping"}

        if privacy in {"sensitive", "local_only"}:
            private_targets = tuple(
                target for target in self._ordered_active_targets(context) if target in available
            )
            targets = private_targets[:1] or (("dashboard",) if "dashboard" in available else tuple())
            return PresentationRoutingDecision(
                targets=targets,
                interrupt=bool(context.requires_action or urgent),
                reason="Sensitive content is restricted to the active private surface.",
                display_eligible=False,
            )

        if urgent:
            targets = tuple(target for target in ("dashboard", "pc", "android") if target in available)
            return PresentationRoutingDecision(
                targets=targets,
                interrupt=True,
                reason="Urgent information is sent to every available user surface.",
            )

        if context.requires_action:
            ordered = self._ordered_active_targets(context)
            targets = [target for target in ordered if target in available]
            if "dashboard" in available and "dashboard" not in targets:
                targets.append("dashboard")
            return PresentationRoutingDecision(
                targets=tuple(targets[:2]),
                interrupt=not occupied,
                reason="Action-required information follows the active device and remains in the dashboard.",
            )

        should_interrupt = (
            important
            and not occupied
            and context.expected_usefulness >= context.interruption_cost
        )
        if should_interrupt:
            target = next(
                (item for item in self._ordered_active_targets(context) if item in available),
                "dashboard",
            )
            targets = ("dashboard", target) if target != "dashboard" and "dashboard" in available else (target,)
            return PresentationRoutingDecision(
                targets=targets,
                interrupt=True,
                reason="High-value information is timely and the user is interruptible.",
            )

        return PresentationRoutingDecision(
            targets=("dashboard",) if "dashboard" in available else tuple(),
            interrupt=False,
            reason="Normal proactive output is stored without interrupting the user.",
        )

    @staticmethod
    def _ordered_active_targets(context: PresentationRoutingContext) -> tuple[str, ...]:
        if context.active_device.lower() == "android" or context.user_presence.lower() in {"away", "mobile"}:
            return ("android", "pc", "dashboard")
        if context.active_device.lower() in {"pc", "desktop"}:
            return ("pc", "android", "dashboard")
        return ("android", "pc", "dashboard")
