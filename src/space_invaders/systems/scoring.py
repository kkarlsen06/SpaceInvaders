"""Scoring and high-score management."""

from __future__ import annotations

from typing import Any

from space_invaders.config import load_config, save_config, save_high_scores


DIFFICULTY_KEY_MAP = {1: "easy", 2: "medium", 3: "hard", 4: "impossible"}


def check_and_update_highscore(
    score: int,
    difficulty: int,
    high_scores: dict[str, Any],
    level: int,
    level_mode: bool,
) -> bool:
    """Check if score beats the high score, update and save if so."""
    updated = False

    if level_mode:
        level_key = f"level_{level}"
        if level_key not in high_scores["level_mode"] or score > high_scores["level_mode"][level_key]:
            high_scores["level_mode"][level_key] = score
            updated = True
    else:
        diff_key = DIFFICULTY_KEY_MAP.get(difficulty)
        if diff_key and score > high_scores.get(diff_key, 0):
            high_scores[diff_key] = score
            updated = True

            if diff_key == "hard" and score >= 1000:
                game_config = load_config()
                game_config["unlock_impossible"] = True
                save_config(game_config)

    if updated:
        save_high_scores(high_scores)
    return updated


def get_current_high_score(
    difficulty: int,
    level: int,
    level_mode: bool,
    high_scores: dict[str, Any],
) -> int:
    """Return the relevant high score for the current mode."""
    if level_mode:
        return high_scores["level_mode"].get(f"level_{level}", 0)
    diff_key = DIFFICULTY_KEY_MAP.get(difficulty)
    return high_scores.get(diff_key, 0)
