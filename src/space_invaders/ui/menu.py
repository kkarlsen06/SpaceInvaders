"""Main menu rendering."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from space_invaders.constants import (
    PASTEL_COLORS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    WHITE,
)

if TYPE_CHECKING:
    from space_invaders.game import Game


def draw_menu(g: Game) -> None:
    """Draw the main menu screen."""
    fonts = g.assets.fonts
    screen = g.screen

    # Title
    title = fonts["xlarge"].render("SPACE INVADERS", True, WHITE)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 35))

    option_color = (240, 240, 240)
    header_color = (250, 250, 250)

    # Panel layout
    left_panel_w = int(SCREEN_WIDTH * 0.5)
    left_center = left_panel_w // 2
    right_center = left_panel_w + (SCREEN_WIDTH - left_panel_w) // 2

    # Section headers
    modes_title = fonts["medium"].render("GAME MODES", True, header_color)
    screen.blit(modes_title, (left_center - modes_title.get_width() // 2, 120))
    scores_title = fonts["medium"].render("HIGH SCORES", True, header_color)
    screen.blit(scores_title, (right_center - scores_title.get_width() // 2, 120))

    # Grid
    grid_top = 165
    grid_row_h = 70
    grid_col_w = int(left_panel_w * 0.45)
    grid_margin = 10

    # Modes box background
    modes_bw = int(left_panel_w * 0.98)
    modes_bh = int(grid_row_h * 3.6)
    modes_bx = left_center - modes_bw // 2
    modes_by = grid_top - grid_margin
    pygame.draw.rect(screen, (40, 40, 50), (modes_bx, modes_by, modes_bw, modes_bh))
    pygame.draw.rect(screen, (60, 60, 70), (modes_bx, modes_by, modes_bw, modes_bh), 2)

    cell_positions = [
        (left_center - grid_col_w - grid_margin // 2, grid_top),
        (left_center + grid_margin // 2, grid_top),
        (left_center - grid_col_w - grid_margin // 2, grid_top + grid_row_h),
        (left_center + grid_margin // 2, grid_top + grid_row_h),
        (int(left_center - grid_col_w * 0.5), grid_top + grid_row_h * 2),
    ]

    cell_h = grid_row_h - grid_margin

    # Difficulty cells
    modes = [
        ("Lett [1]", "easy", (40, 60, 50)),
        ("Middels [2]", "medium", (60, 50, 40)),
        ("Vanskelig [3]", "hard", (60, 40, 40)),
    ]
    for i, (label, key, bg) in enumerate(modes):
        color = PASTEL_COLORS[key]
        cx, cy = cell_positions[i]
        pygame.draw.rect(screen, bg, (cx, cy, grid_col_w, cell_h))
        pygame.draw.rect(screen, color, (cx, cy, grid_col_w, cell_h), 2)
        txt = fonts["medium"].render(label, True, color)
        screen.blit(txt, (cx + grid_col_w // 2 - txt.get_width() // 2,
                          cy + cell_h // 2 - txt.get_height() // 2))

    # Impossible (may be locked)
    imp_unlocked = g.game_config["unlock_impossible"]
    imp_color = PASTEL_COLORS["impossible"] if imp_unlocked else (120, 120, 120)
    imp_label = "Umulig [4]" if imp_unlocked else "Umulig [Låst]"
    cx, cy = cell_positions[3]
    pygame.draw.rect(screen, (40, 40, 60), (cx, cy, grid_col_w, cell_h))
    pygame.draw.rect(screen, imp_color, (cx, cy, grid_col_w, cell_h), 2)
    txt = fonts["medium"].render(imp_label, True, imp_color)
    screen.blit(txt, (cx + grid_col_w // 2 - txt.get_width() // 2,
                      cy + cell_h // 2 - txt.get_height() // 2))

    # Level mode (bottom row, spans both columns)
    level_color = PASTEL_COLORS["level"]
    lc_w = grid_col_w * 2 + grid_margin
    lc_x = left_center - lc_w // 2
    lc_h = int(cell_h * 1.6)
    lc_y = cell_positions[4][1]
    pygame.draw.rect(screen, (50, 40, 60), (lc_x, lc_y, lc_w, lc_h))
    pygame.draw.rect(screen, level_color, (lc_x, lc_y, lc_w, lc_h), 2)
    lm_txt = fonts["medium"].render("Level Mode [L]", True, level_color)
    screen.blit(lm_txt, (left_center - lm_txt.get_width() // 2, lc_y + 15))

    if g.game_config["max_level_reached"] > 1:
        cont = fonts["small"].render(
            f"(Fortsett fra level {g.game_config['max_level_reached']})", True, level_color)
        screen.blit(cont, (left_center - cont.get_width() // 2, lc_y + 45))

    # High scores box
    hs_bw = int(modes_bw * 0.95)
    hs_bx = right_center - hs_bw // 2
    hs_by = grid_top - grid_margin
    pygame.draw.rect(screen, (40, 40, 50), (hs_bx, hs_by, hs_bw, modes_bh))
    pygame.draw.rect(screen, (60, 60, 70), (hs_bx, hs_by, hs_bw, modes_bh), 2)

    score_spacing = modes_bh // 5
    hs_y = hs_by + score_spacing // 2 + 10
    for diff, name in [(1, "Lett"), (2, "Middels"), (3, "Vanskelig"), (4, "Umulig")]:
        key = {1: "easy", 2: "medium", 3: "hard", 4: "impossible"}[diff]
        sc = g.high_scores.get(key, 0)
        color = PASTEL_COLORS[key]
        st = fonts["medium"].render(f"{name}: {sc}", True, color)
        screen.blit(st, (right_center - st.get_width() // 2, hs_y))
        hs_y += score_spacing

    # Weapon display
    _draw_weapon_panel(g, header_color)

    # Footer
    copyright_font = pygame.font.SysFont("arial", 14)
    cr = copyright_font.render("kkarlsen_06 2025 All Rights Reserved", True, (150, 150, 150))
    ht = copyright_font.render("Help [H]", True, (200, 200, 200))
    st = copyright_font.render("Settings [I]", True, (200, 200, 200))
    screen.blit(cr, (100, SCREEN_HEIGHT - 25))
    screen.blit(ht, (SCREEN_WIDTH - 250, SCREEN_HEIGHT - 25))
    screen.blit(st, (SCREEN_WIDTH - 120, SCREEN_HEIGHT - 25))


def _draw_weapon_panel(g: Game, header_color: tuple[int, int, int]) -> None:
    fonts = g.assets.fonts
    screen = g.screen

    wp_title = fonts["medium"].render("VÅPEN", True, header_color)
    wp_y = SCREEN_HEIGHT - 150
    screen.blit(wp_title, (SCREEN_WIDTH // 2 - wp_title.get_width() // 2, wp_y))

    panel_w, panel_h = 180, 45
    spacing = 20
    total = 3 * panel_w + 2 * spacing
    start_x = (SCREEN_WIDTH - total) // 2
    y = wp_y + 35

    weapons = [
        ("Laser [1]", True, PASTEL_COLORS["easy"], (40, 60, 50)),
        (
            "Hagle [2]" if g.game_config["max_level_reached"] > 5 else "Hagle [Lvl 5+]",
            g.game_config["max_level_reached"] > 5,
            PASTEL_COLORS["medium"] if g.game_config["max_level_reached"] > 5 else (120, 120, 120),
            (60, 50, 40) if g.game_config["max_level_reached"] > 5 else (50, 50, 50),
        ),
        (
            "Pisk [3]" if g.game_config["max_level_reached"] >= 10 else "Pisk [Lvl 10+]",
            g.game_config["max_level_reached"] >= 10,
            PASTEL_COLORS["hard"] if g.game_config["max_level_reached"] >= 10 else (120, 120, 120),
            (60, 40, 40) if g.game_config["max_level_reached"] >= 10 else (50, 50, 50),
        ),
    ]

    for i, (label, unlocked, border, bg) in enumerate(weapons):
        px = start_x + i * (panel_w + spacing)
        pygame.draw.rect(screen, bg, (px, y, panel_w, panel_h))
        pygame.draw.rect(screen, border, (px, y, panel_w, panel_h), 2)
        txt = fonts["small"].render(label, True, border if unlocked else (150, 150, 150))
        screen.blit(txt, (px + panel_w // 2 - txt.get_width() // 2,
                          y + panel_h // 2 - txt.get_height() // 2))
