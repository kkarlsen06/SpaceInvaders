"""Lightweight tween / transition helpers for UI animations."""

from __future__ import annotations

from typing import Callable

import pygame


# ---------------------------------------------------------------------------
# Easing functions  (t: 0..1 -> 0..1)
# ---------------------------------------------------------------------------

def ease_out_cubic(t: float) -> float:
    return 1 - (1 - t) ** 3


def ease_out_back(t: float) -> float:
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


def ease_in_out_quad(t: float) -> float:
    if t < 0.5:
        return 2 * t * t
    return 1 - (-2 * t + 2) ** 2 / 2


# ---------------------------------------------------------------------------
# Tween
# ---------------------------------------------------------------------------

class Tween:
    """Interpolates a float value over time with an easing curve."""

    def __init__(
        self,
        start: float,
        end: float,
        duration_ms: float,
        easing: Callable[[float], float] = ease_out_cubic,
        delay_ms: float = 0,
    ) -> None:
        self.start = start
        self.end = end
        self.duration_ms = duration_ms
        self.easing = easing
        self.delay_ms = delay_ms
        self.start_time = pygame.time.get_ticks()

    def get_value(self) -> float:
        elapsed = pygame.time.get_ticks() - self.start_time - self.delay_ms
        if elapsed < 0:
            return self.start
        if self.duration_ms <= 0:
            return self.end
        t = min(elapsed / self.duration_ms, 1.0)
        eased = self.easing(t)
        return self.start + (self.end - self.start) * eased

    def is_done(self) -> bool:
        elapsed = pygame.time.get_ticks() - self.start_time - self.delay_ms
        return elapsed >= self.duration_ms


# ---------------------------------------------------------------------------
# Transition Manager
# ---------------------------------------------------------------------------

class UITransitionManager:
    """Manages named tweens for screen transitions and dialog animations."""

    def __init__(self) -> None:
        self._tweens: dict[str, Tween] = {}

    def start(self, key: str, start: float, end: float,
              duration_ms: int = 250,
              easing: Callable[[float], float] = ease_out_cubic,
              delay_ms: float = 0) -> None:
        self._tweens[key] = Tween(start, end, duration_ms, easing, delay_ms)

    def start_fade_in(self, key: str, duration_ms: int = 250) -> None:
        self.start(key, 0, 255, duration_ms)

    def start_slide_up(self, key: str, offset: int = 40,
                       duration_ms: int = 300) -> None:
        self.start(key, offset, 0, duration_ms, ease_out_back)

    def get(self, key: str, default: float = 0) -> float:
        tween = self._tweens.get(key)
        if tween is None:
            return default
        return tween.get_value()

    def is_done(self, key: str) -> bool:
        tween = self._tweens.get(key)
        return tween is None or tween.is_done()

    def clear(self, key: str) -> None:
        self._tweens.pop(key, None)
