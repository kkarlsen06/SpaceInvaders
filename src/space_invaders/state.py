"""Game state management."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum, auto


class GameScreen(IntEnum):
    """Game screens/states."""
    MENU = 0
    PLAYING = auto()
    GAME_OVER = auto()
    LEVEL_COMPLETE = auto()
    LEVEL_SELECT = auto()
    QUIT_CONFIRM = auto()
    HELP = auto()
    SETTINGS = auto()


@dataclass
class GameState:
    """All mutable game state in one place."""
    # Screen / flow
    screen: GameScreen = GameScreen.MENU
    running: bool = True
    show_menu: bool = True

    # Difficulty and level
    difficulty: int = 1
    level: int = 1
    level_mode: bool = False

    # Score system
    score: int = 0
    score_multiplier: float = 1.0
    consecutive_hits: int = 0

    # UI state
    fullscreen: bool = False
    current_level_page: int = 0
    help_scroll_y: int = 0
    show_shotgun_unlock: bool = False

    # Settings
    sound_volume: float = 0.5
    music_volume: float = 0.07
    mouse_control: bool = False

    # Timers
    bonus_timer: int = 0

    def reset_for_new_game(self) -> None:
        """Reset score/lives for starting a new game."""
        self.score = 0
        self.score_multiplier = 1.0
        self.consecutive_hits = 0

    def reset_multiplier(self) -> None:
        """Reset the score multiplier."""
        self.score_multiplier = 1.0
        self.consecutive_hits = 0

    def increase_multiplier(self) -> None:
        """Increase the score multiplier on a hit."""
        self.consecutive_hits += 1
        self.score_multiplier = min(5.0, 1.0 + self.consecutive_hits * 0.1)
