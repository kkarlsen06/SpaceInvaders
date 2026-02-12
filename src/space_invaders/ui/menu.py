"""Main menu rendering."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import pygame

from space_invaders.constants import (
    Colors,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from space_invaders.ui.draw_utils import (
    draw_button,
    draw_glow_text,
    draw_panel,
    draw_separator,
    draw_spaced_text,
    draw_text,
)

if TYPE_CHECKING:
    from space_invaders.game import Game


def draw_menu(g: Game) -> None:
    """Draw the main menu screen."""
    fonts = g.assets.fonts
    screen = g.screen
    mouse = g.state.mouse_pos
    buttons: dict[str, pygame.Rect] = {}

    # ---------- Animated glowing title ----------
    t = pygame.time.get_ticks() / 1000.0
    pulse = 0.7 + 0.3 * ((math.sin(t * 1.5) + 1) / 2)
    glow_alpha = int(50 * pulse)
    draw_spaced_text(
        screen, "SPACE INVADERS", fonts["xlarge"], Colors.PRIMARY_LIGHT,
        SCREEN_WIDTH // 2, 22, spacing=6, shadow=True,
        glow_color=(*Colors.PRIMARY[:3], glow_alpha),
    )

    # Subtitle
    draw_text(screen, "ARCADE EDITION", fonts["tiny"], Colors.TEXT_MUTED,
              (SCREEN_WIDTH // 2, 80), anchor="midtop")

    # Two-column layout
    left_panel_w = int(SCREEN_WIDTH * 0.5)
    left_center = left_panel_w // 2
    right_center = left_panel_w + (SCREEN_WIDTH - left_panel_w) // 2

    # Section headers
    draw_glow_text(screen, "GAME MODES", fonts["medium"], Colors.TEXT_SECONDARY,
                   (left_center, 108), glow_color=(*Colors.PRIMARY[:3], 20),
                   glow_radius=4)
    draw_separator(screen, left_center - 80, 138, 160, Colors.BORDER_MEDIUM)

    draw_glow_text(screen, "HIGH SCORES", fonts["medium"], Colors.TEXT_SECONDARY,
                   (right_center, 108), glow_color=(*Colors.SECONDARY[:3], 20),
                   glow_radius=4)
    draw_separator(screen, right_center - 80, 138, 160, Colors.BORDER_MEDIUM)

    # Grid layout for difficulty buttons
    grid_top = 155
    grid_row_h = 70
    grid_col_w = int(left_panel_w * 0.44)
    grid_margin = 12

    # Modes panel background
    modes_bw = int(left_panel_w * 0.96)
    modes_bh = int(grid_row_h * 3.6)
    modes_bx = left_center - modes_bw // 2
    modes_by = grid_top - 10
    draw_panel(screen, (modes_bx, modes_by, modes_bw, modes_bh),
               Colors.BG_CARD, Colors.BORDER_SUBTLE, radius=14, gradient_top=True)

    cell_positions = [
        (left_center - grid_col_w - grid_margin // 2, grid_top),
        (left_center + grid_margin // 2, grid_top),
        (left_center - grid_col_w - grid_margin // 2, grid_top + grid_row_h),
        (left_center + grid_margin // 2, grid_top + grid_row_h),
    ]

    cell_h = grid_row_h - grid_margin

    # Difficulty buttons
    tier_data = [
        ("Lett", "easy", Colors.EASY, Colors.EASY_BG),
        ("Middels", "medium", Colors.MEDIUM, Colors.MEDIUM_BG),
        ("Vanskelig", "hard", Colors.HARD, Colors.HARD_BG),
    ]
    for i, (label, key, accent, bg) in enumerate(tier_data):
        cx, cy = cell_positions[i]
        r = pygame.Rect(cx, cy, grid_col_w, cell_h)
        draw_button(screen, r, label, fonts["medium"],
                    bg_color=bg, border_color=accent,
                    text_color=accent, border_hover_color=accent,
                    bg_hover_color=_lighten(bg, 18),
                    radius=10, mouse_pos=mouse)
        buttons[key] = r

    # Impossible button (may be locked)
    imp_unlocked = g.game_config["unlock_impossible"]
    imp_label = "Umulig" if imp_unlocked else "Umulig (Låst)"
    cx, cy = cell_positions[3]
    r = pygame.Rect(cx, cy, grid_col_w, cell_h)
    draw_button(screen, r, imp_label, fonts["medium"],
                bg_color=Colors.IMPOSSIBLE_BG, border_color=Colors.IMPOSSIBLE,
                text_color=Colors.IMPOSSIBLE, border_hover_color=Colors.IMPOSSIBLE,
                bg_hover_color=_lighten(Colors.IMPOSSIBLE_BG, 18),
                radius=10, disabled=not imp_unlocked, mouse_pos=mouse)
    buttons["impossible"] = r

    # Level mode button (spans both columns)
    lc_w = grid_col_w * 2 + grid_margin
    lc_x = left_center - lc_w // 2
    lc_h = cell_h
    lc_y = grid_top + grid_row_h * 2
    lr = pygame.Rect(lc_x, lc_y, lc_w, lc_h)

    draw_button(screen, lr, "Level Mode", fonts["medium"],
                bg_color=Colors.LEVEL_BG, border_color=Colors.LEVEL,
                text_color=Colors.LEVEL, border_hover_color=Colors.LEVEL,
                bg_hover_color=_lighten(Colors.LEVEL_BG, 18),
                radius=10, mouse_pos=mouse)
    buttons["level_mode"] = lr

    if g.game_config["max_level_reached"] > 1:
        cont_txt = f"(Fortsett fra level {g.game_config['max_level_reached']})"
        draw_text(screen, cont_txt, fonts["tiny"], Colors.TEXT_MUTED,
                  (left_center, lc_y + lc_h + 4), anchor="midtop")

    # High scores panel
    hs_bw = int(modes_bw * 0.95)
    hs_bx = right_center - hs_bw // 2
    hs_by = grid_top - 10
    draw_panel(screen, (hs_bx, hs_by, hs_bw, modes_bh),
               Colors.BG_CARD, Colors.BORDER_SUBTLE, radius=14, gradient_top=True)

    score_spacing = modes_bh // 5
    hs_y = hs_by + score_spacing // 2 + 12
    tier_keys = [
        (1, "Lett", "easy"),
        (2, "Middels", "medium"),
        (3, "Vanskelig", "hard"),
        (4, "Umulig", "impossible"),
    ]
    tier_color_map = {
        "easy": Colors.EASY,
        "medium": Colors.MEDIUM,
        "hard": Colors.HARD,
        "impossible": Colors.IMPOSSIBLE,
    }
    for _diff, name, key in tier_keys:
        sc = g.high_scores.get(key, 0)
        color = tier_color_map[key]
        # Score label
        draw_text(screen, name, fonts["small"], Colors.TEXT_MUTED,
                  (right_center - 50, hs_y))
        # Score value
        draw_text(screen, str(sc), fonts["medium"], color,
                  (right_center + 50, hs_y - 2))
        hs_y += score_spacing

    # Weapon panel
    _draw_weapon_panel(g, mouse, buttons)

    # Footer
    draw_text(screen, "kkarlsen_06 2025", fonts["tiny"],
              Colors.TEXT_MUTED, (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 22),
              anchor="midtop")

    # Help button
    help_r = pygame.Rect(SCREEN_WIDTH - 270, SCREEN_HEIGHT - 34, 70, 24)
    draw_button(screen, help_r, "Help", fonts["tiny"],
                bg_color=(0, 0, 0, 0), border_color=Colors.BORDER_SUBTLE,
                text_color=Colors.TEXT_SECONDARY,
                border_hover_color=Colors.PRIMARY,
                text_hover_color=Colors.PRIMARY_LIGHT,
                bg_hover_color=(0, 0, 0, 0),
                radius=6, mouse_pos=mouse, shadow=False)
    buttons["help"] = help_r

    # Settings button
    settings_r = pygame.Rect(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 34, 90, 24)
    draw_button(screen, settings_r, "Settings", fonts["tiny"],
                bg_color=(0, 0, 0, 0), border_color=Colors.BORDER_SUBTLE,
                text_color=Colors.TEXT_SECONDARY,
                border_hover_color=Colors.PRIMARY,
                text_hover_color=Colors.PRIMARY_LIGHT,
                bg_hover_color=(0, 0, 0, 0),
                radius=6, mouse_pos=mouse, shadow=False)
    buttons["settings"] = settings_r

    g.state.menu_buttons = buttons


def _draw_weapon_panel(g: Game, mouse: tuple[int, int],
                       buttons: dict[str, pygame.Rect]) -> None:
    fonts = g.assets.fonts
    screen = g.screen

    draw_glow_text(screen, "VÅPEN", fonts["medium"], Colors.TEXT_SECONDARY,
                   (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 155),
                   glow_color=(*Colors.PRIMARY[:3], 15), glow_radius=3)
    draw_separator(screen, SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 128,
                   100, Colors.BORDER_MEDIUM)

    panel_w, panel_h = 180, 48
    spacing = 20
    total = 3 * panel_w + 2 * spacing
    start_x = (SCREEN_WIDTH - total) // 2
    y = SCREEN_HEIGHT - 118

    max_lvl = g.game_config["max_level_reached"]
    weapon_keys = ["weapon_laser", "weapon_shotgun", "weapon_whip"]
    weapons = [
        ("Laser", True, Colors.EASY, Colors.EASY_BG),
        (
            "Hagle" if max_lvl > 5 else "Hagle (Lvl 5+)",
            max_lvl > 5,
            Colors.MEDIUM if max_lvl > 5 else Colors.LOCKED,
            Colors.MEDIUM_BG if max_lvl > 5 else Colors.BG_DEEP,
        ),
        (
            "Pisk" if max_lvl >= 10 else "Pisk (Lvl 10+)",
            max_lvl >= 10,
            Colors.HARD if max_lvl >= 10 else Colors.LOCKED,
            Colors.HARD_BG if max_lvl >= 10 else Colors.BG_DEEP,
        ),
    ]

    for i, (label, unlocked, accent, bg) in enumerate(weapons):
        px = start_x + i * (panel_w + spacing)
        r = pygame.Rect(px, y, panel_w, panel_h)
        draw_button(screen, r, label, fonts["small"],
                    bg_color=bg, border_color=accent,
                    text_color=accent if unlocked else Colors.LOCKED_TEXT,
                    border_hover_color=accent,
                    bg_hover_color=_lighten(bg, 18),
                    radius=10, disabled=not unlocked, mouse_pos=mouse)
        buttons[weapon_keys[i]] = r


def _lighten(color: tuple[int, ...], amount: int) -> tuple[int, ...]:
    """Return a slightly brighter version of a color."""
    return tuple(min(255, c + amount) for c in color[:3])
