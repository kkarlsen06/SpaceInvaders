"""In-game heads-up display rendering."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import pygame

from space_invaders.constants import (
    BLUE,
    CYAN,
    GOLD,
    PASTEL_COLORS,
    RED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    WHITE,
    DIFFICULTY_CONFIG,
)
from space_invaders.state import GameScreen
from space_invaders.systems.scoring import get_current_high_score
from space_invaders.systems.levels import set_level_requirements

if TYPE_CHECKING:
    from space_invaders.game import Game


def draw_hud(g: Game) -> None:
    """Draw score, lives, difficulty, multiplier, and weapon panel."""
    fonts = g.assets.fonts
    screen = g.screen
    state = g.state

    # Score
    score_txt = fonts["small"].render(f"Poeng: {state.score}", True, WHITE)
    screen.blit(score_txt, (10, 10))

    # High score (normal mode only)
    if not state.level_mode:
        hs = get_current_high_score(state.difficulty, state.level, state.level_mode, g.high_scores)
        hs_txt = fonts["small"].render(f"High Score: {hs}", True, GOLD)
        screen.blit(hs_txt, (SCREEN_WIDTH - hs_txt.get_width() - 10, 10))

    # Lives
    lives_txt = fonts["small"].render(f"Liv: {g.player.lives}", True, WHITE)
    screen.blit(lives_txt, (10, 40))

    # Difficulty / level indicator
    if state.level_mode:
        lvl_txt = fonts["small"].render(f"Level: {state.level}", True, BLUE)
        screen.blit(lvl_txt, (10, 70))
    else:
        diff_cfg = DIFFICULTY_CONFIG[state.difficulty]
        colors = {1: CYAN, 2: (255, 255, 0), 3: RED, 4: (255, 0, 255)}
        c = colors.get(state.difficulty, WHITE)
        d_txt = fonts["small"].render(f"Nivå: {diff_cfg['name']}", True, c)
        screen.blit(d_txt, (10, 70))

    # Level progress bar (level mode)
    if state.level_mode and state.screen == GameScreen.PLAYING:
        reqs = set_level_requirements(state.level)
        prog = fonts["small"].render(
            f"Progress: {state.score}/{reqs['target_score']}", True, WHITE)
        screen.blit(prog, (SCREEN_WIDTH // 2 - prog.get_width() // 2, 10))

    # Multiplier
    if state.screen == GameScreen.PLAYING and state.score_multiplier > 1.0:
        m_txt = fonts["medium"].render(f"x{state.score_multiplier:.1f}", True, GOLD)
        screen.blit(m_txt, (SCREEN_WIDTH - m_txt.get_width() - 10, 40))

    # Enemy point values
    _draw_enemy_points(g)

    # Weapon panel (right side, stacked vertically)
    if state.screen == GameScreen.PLAYING:
        _draw_weapon_panel(g)


def _draw_enemy_points(g: Game) -> None:
    fonts = g.assets.fonts
    screen = g.screen
    state = g.state
    sm = state.score_multiplier

    try:
        icon_size = 25
        try:
            icon = pygame.transform.scale(g.assets.images["enemy"], (icon_size, icon_size))
        except (pygame.error, KeyError):
            icon = pygame.Surface((icon_size, icon_size))
            icon.fill(CYAN)
        screen.blit(icon, (10, 100))
        pts = fonts["small"].render(f"{int(10 * sm)} poeng", True, WHITE)
        screen.blit(pts, (40, 110))

        # Strong enemies only for hard+ or level mode level 3+
        if state.difficulty >= 3 or (state.level_mode and state.level >= 3):
            s_size = 30
            try:
                s_icon = pygame.transform.scale(g.assets.images["strong_enemy"], (s_size, s_size))
            except (pygame.error, KeyError):
                s_icon = pygame.Surface((s_size, s_size))
                s_icon.fill(RED)
            screen.blit(s_icon, (10, 130))
            s_pts = fonts["small"].render(f"{int(25 * sm)} poeng", True, WHITE)
            screen.blit(s_pts, (45, 140))
    except Exception as e:
        print(f"Error in draw_enemy_points: {e}")


def _draw_weapon_panel(g: Game) -> None:
    fonts = g.assets.fonts
    screen = g.screen
    player = g.player
    config = g.game_config

    panel_w = 130
    panel_h = 35
    spacing = 10
    start_x = SCREEN_WIDTH - panel_w - 10
    start_y = 120

    weapons = [
        {"name": "Laser", "key": "1", "type": "normal", "unlocked": True,
         "bg": (40, 60, 50), "border": PASTEL_COLORS["easy"], "text": PASTEL_COLORS["easy"]},
        {"name": "Hagle", "key": "2", "type": "shotgun",
         "unlocked": config["max_level_reached"] > 5,
         "bg": (60, 50, 40) if config["max_level_reached"] > 5 else (50, 50, 50),
         "border": PASTEL_COLORS["medium"] if config["max_level_reached"] > 5 else (120, 120, 120),
         "text": PASTEL_COLORS["medium"] if config["max_level_reached"] > 5 else (150, 150, 150),
         "locked_text": "Hagle [Lvl 5+]"},
        {"name": "Pisk", "key": "3", "type": "electric whip",
         "unlocked": config["max_level_reached"] >= 10,
         "bg": (60, 40, 40) if config["max_level_reached"] >= 10 else (50, 50, 50),
         "border": PASTEL_COLORS["hard"] if config["max_level_reached"] >= 10 else (120, 120, 120),
         "text": PASTEL_COLORS["hard"] if config["max_level_reached"] >= 10 else (150, 150, 150),
         "locked_text": "Pisk [Lvl 10+]",
         "charged": player.whip_charge >= player.whip_charge_threshold},
    ]

    for i, w in enumerate(weapons):
        py = start_y + i * (panel_h + spacing)

        is_selected = False
        if w["type"] == "electric whip":
            is_selected = w.get("charged", False) and w["unlocked"]
        else:
            is_selected = player.current_weapon == w["type"]

        pygame.draw.rect(screen, w["bg"], (start_x, py, panel_w, panel_h))

        # Whip charge bar
        if w["type"] == "electric whip" and w["unlocked"]:
            ratio = player.whip_charge / player.whip_charge_threshold
            fill_w = int(panel_w * min(max(ratio, 0), 1))
            if player.whip_charge >= player.whip_charge_threshold:
                pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1) / 2
                factor = 1.0 + 0.5 * pulse
                fill_color = (min(255, int(RED[0] * factor)),
                              min(255, int(RED[1] * factor)),
                              min(255, int(RED[2] * factor)))
                glow = (min(255, int(RED[0] * (1.0 + 0.7 * pulse))),
                        min(255, int(RED[1] * (1.0 + 0.7 * pulse))),
                        min(255, int(RED[2] * (1.0 + 0.7 * pulse))))
                pygame.draw.rect(screen, glow,
                                 (start_x - 2, py - 2, panel_w + 4, panel_h + 4), 2)
            else:
                fill_color = RED
            pygame.draw.rect(screen, fill_color, (start_x, py, fill_w, panel_h))

        pygame.draw.rect(screen, w["border"],
                         (start_x, py, panel_w, panel_h), 3 if is_selected else 1)

        label = f"{w['name']} [{w['key']}]" if w["unlocked"] else w.get("locked_text", f"{w['name']} [Låst]")
        txt = fonts["small"].render(label, True, WHITE if is_selected else w["text"])
        screen.blit(txt, (start_x + panel_w // 2 - txt.get_width() // 2,
                          py + panel_h // 2 - txt.get_height() // 2))
