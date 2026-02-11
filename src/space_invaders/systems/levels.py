"""Level requirements and enemy spawning."""

from __future__ import annotations

from typing import Any

import pygame

from space_invaders.config import load_config, save_config
from space_invaders.constants import DIFFICULTY_CONFIG, SHOTGUN_UNLOCK_LEVEL
from space_invaders.entities.enemies import Enemy, StrongEnemy
from space_invaders.systems.scoring import check_and_update_highscore


def set_level_requirements(level: int) -> dict[str, int]:
    """Return target score and enemy counts for a given level."""
    if level == 1:
        return {"target_score": 100, "enemy_count": 3, "strong_enemy_count": 0}
    elif level == 2:
        return {"target_score": 150, "enemy_count": 4, "strong_enemy_count": 0}
    elif level == 3:
        return {"target_score": 200, "enemy_count": 4, "strong_enemy_count": 1}
    elif level == 4:
        return {"target_score": 250, "enemy_count": 5, "strong_enemy_count": 1}
    elif level == 5:
        return {"target_score": 300, "enemy_count": 5, "strong_enemy_count": 1}
    elif level <= 10:
        base = 300
        return {
            "target_score": base + (level - 5) * 30,
            "enemy_count": 5 + (level - 5) // 2,
            "strong_enemy_count": 1,
        }
    elif level <= 20:
        base = 450
        return {
            "target_score": base + (level - 10) * 30,
            "enemy_count": 6,
            "strong_enemy_count": 1,
        }
    else:
        base = 750
        return {
            "target_score": base + (level - 20) * 30,
            "enemy_count": min(8, 6 + (level - 20) // 10),
            "strong_enemy_count": 1,
        }


def spawn_enemies(
    level_mode: bool,
    level: int,
    difficulty: int,
    enemy_image: pygame.Surface,
    strong_enemy_image: pygame.Surface,
    all_sprites: pygame.sprite.Group,
    enemy_group: pygame.sprite.Group,
) -> int:
    """Clear existing enemies and spawn a fresh wave. Returns total count."""
    for sprite in list(enemy_group):
        sprite.kill()

    if level_mode:
        reqs = set_level_requirements(level)
        normal_count = reqs["enemy_count"]
        strong_count = reqs["strong_enemy_count"]
    else:
        diff_cfg = DIFFICULTY_CONFIG[difficulty]
        normal_count = diff_cfg["enemy_count"]
        strong_count = diff_cfg["strong_enemy_count"]

    for _ in range(normal_count):
        e = Enemy(enemy_image, difficulty)
        all_sprites.add(e)
        enemy_group.add(e)
    for _ in range(strong_count):
        e = StrongEnemy(strong_enemy_image, difficulty)
        all_sprites.add(e)
        enemy_group.add(e)

    return normal_count + strong_count


def check_level_complete(
    level: int,
    score: int,
    level_mode: bool,
    difficulty: int,
    high_scores: dict[str, Any],
    game_config: dict[str, Any],
) -> tuple[bool, int, bool]:
    """Check for level completion. Returns (completed, new_level, weapon_unlocked)."""
    if not level_mode:
        return False, level, False

    reqs = set_level_requirements(level)
    if score < reqs["target_score"]:
        return False, level, False

    check_and_update_highscore(score, difficulty, high_scores, level, level_mode)
    new_level = level + 1
    weapon_unlocked = False

    if new_level > game_config["max_level_reached"]:
        game_config["max_level_reached"] = new_level

        if new_level == 5 and "level5_skin" not in game_config["unlocked_skins"]:
            game_config["unlocked_skins"].append("level5_skin")

        if new_level == SHOTGUN_UNLOCK_LEVEL + 1 and not game_config.get("shotgun_unlocked", False):
            weapon_unlocked = True
            game_config["shotgun_unlocked"] = True

        save_config(game_config)

    return True, new_level, weapon_unlocked
