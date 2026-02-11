"""Configuration and high-score persistence."""

from __future__ import annotations

import copy
import json
import os
from pathlib import Path
from typing import Any

# Resolve paths relative to the project root (two levels up from this file
# when installed as a package under src/space_invaders/, but the JSON files
# live next to the assets/ folder at the repo root).
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

CONFIG_FILE = _PROJECT_ROOT / "game_config.json"
HIGH_SCORE_FILE = _PROJECT_ROOT / "high_scores.json"

DEFAULT_CONFIG: dict[str, Any] = {
    "unlock_impossible": False,
    "unlocked_skins": ["default"],
    "active_skin": "default",
    "max_level_reached": 1,
    "shotgun_unlocked": False,
    "sound_volume": 0.5,
    "music_volume": 0.07,
    "fullscreen_enabled": False,
    "mouse_control": False,
}

DEFAULT_HIGH_SCORES: dict[str, Any] = {
    "easy": 0,
    "medium": 0,
    "hard": 0,
    "impossible": 0,
    "level_mode": {},
}


def load_config() -> dict[str, Any]:
    """Load game configuration, creating defaults if missing."""
    config = copy.deepcopy(DEFAULT_CONFIG)
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                if isinstance(loaded, dict):
                    config.update(loaded)
        except (OSError, json.JSONDecodeError):
            return config
    else:
        save_config(config)
    return config


def save_config(config: dict[str, Any]) -> None:
    """Persist game configuration to disk."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)


def load_high_scores() -> dict[str, Any]:
    """Load high scores, creating defaults if missing."""
    scores = copy.deepcopy(DEFAULT_HIGH_SCORES)
    if HIGH_SCORE_FILE.exists():
        try:
            with open(HIGH_SCORE_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                if isinstance(loaded, dict):
                    scores.update(loaded)
                    if not isinstance(scores.get("level_mode"), dict):
                        scores["level_mode"] = {}
        except (OSError, json.JSONDecodeError):
            return scores
    else:
        save_high_scores(scores)
    return scores


def save_high_scores(scores: dict[str, Any]) -> None:
    """Persist high scores to disk."""
    with open(HIGH_SCORE_FILE, "w", encoding="utf-8") as f:
        json.dump(scores, f, indent=4)
