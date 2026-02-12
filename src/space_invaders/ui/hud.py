"""In-game heads-up display rendering."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import pygame

from space_invaders.constants import (
    Colors,
    DIFFICULTY_CONFIG,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from space_invaders.state import GameScreen
from space_invaders.systems.scoring import get_current_high_score
from space_invaders.systems.levels import set_level_requirements
from space_invaders.ui.draw_utils import draw_glass_bar, draw_slider, draw_text

if TYPE_CHECKING:
    from space_invaders.game import Game


def draw_hud(g: Game) -> None:
    """Draw the minimalist HUD with glassmorphism bars."""
    fonts = g.assets.fonts
    screen = g.screen
    state = g.state

    top_h = 36
    bottom_h = 40

    # Top bar — glass style with accent line at bottom
    draw_glass_bar(screen, (0, 0, SCREEN_WIDTH, top_h),
                   alpha=150, accent_color=Colors.PRIMARY, accent_side="bottom")

    # Score (top-left)
    draw_text(screen, "SCORE", fonts["tiny"], Colors.TEXT_MUTED, (14, 4))
    draw_text(screen, str(state.score), fonts["small"], Colors.SECONDARY, (14, 16))

    # Difficulty / level indicator
    if state.level_mode:
        draw_text(screen, f"LEVEL {state.level}", fonts["small"],
                  Colors.LEVEL, (160, 9))
    else:
        diff_cfg = DIFFICULTY_CONFIG[state.difficulty]
        tier_colors = {
            1: Colors.EASY, 2: Colors.MEDIUM,
            3: Colors.HARD, 4: Colors.IMPOSSIBLE,
        }
        c = tier_colors.get(state.difficulty, Colors.TEXT_PRIMARY)
        # Glowing colored dot + text
        dot_x, dot_y = 155, top_h // 2
        # Glow ring
        glow_surf = pygame.Surface((18, 18), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*c[:3], 40), (9, 9), 9)
        screen.blit(glow_surf, (dot_x - 9, dot_y - 9))
        pygame.draw.circle(screen, c, (dot_x, dot_y), 4)
        draw_text(screen, diff_cfg['name'], fonts["tiny"], c, (dot_x + 10, 10))

    # Level progress bar (center, level mode)
    if state.level_mode and state.screen == GameScreen.PLAYING:
        reqs = set_level_requirements(state.level)
        target = reqs['target_score']
        progress = min(state.score / target, 1.0) if target > 0 else 0
        bar_w = 200
        bar_rect = pygame.Rect(SCREEN_WIDTH // 2 - bar_w // 2, 10, bar_w, 12)
        draw_slider(screen, bar_rect, progress,
                    fill_color=Colors.PRIMARY, show_handle=False)
        draw_text(screen, f"{state.score}/{target}", fonts["tiny"],
                  Colors.TEXT_MUTED,
                  (SCREEN_WIDTH // 2, 24), anchor="midtop")

    # High score (top-right, normal mode only)
    if not state.level_mode:
        hs = get_current_high_score(
            state.difficulty, state.level, state.level_mode, g.high_scores,
        )
        draw_text(screen, "BEST", fonts["tiny"],
                  Colors.TEXT_MUTED, (SCREEN_WIDTH - 14, 4), anchor="topright")
        draw_text(screen, str(hs), fonts["small"],
                  Colors.TEXT_SECONDARY, (SCREEN_WIDTH - 14, 16), anchor="topright")

    # Bottom bar — glass style with accent at top
    draw_glass_bar(
        screen, (0, SCREEN_HEIGHT - bottom_h, SCREEN_WIDTH, bottom_h),
        alpha=150, accent_color=Colors.PRIMARY, accent_side="top",
    )

    by = SCREEN_HEIGHT - bottom_h

    # Multiplier (bottom-left) with pulsing glow
    if state.screen == GameScreen.PLAYING and state.score_multiplier > 1.0:
        m_text = f"x{state.score_multiplier:.1f}"

        # Glow behind multiplier
        m_font = fonts["medium"]
        m_surf = m_font.render(m_text, True, Colors.SECONDARY)
        glow = m_surf.copy()
        glow.set_alpha(35)
        for ox, oy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            screen.blit(glow, (16 + ox, by + 7 + oy))

        draw_text(screen, m_text, fonts["medium"], Colors.SECONDARY,
                  (16, by + 7), shadow=True)

    # Weapon selector (bottom-center)
    if state.screen == GameScreen.PLAYING:
        _draw_weapon_bar(g, by)

    # Lives (bottom-right)
    if state.screen == GameScreen.PLAYING:
        _draw_lives(g, by)


def _draw_weapon_bar(g: Game, bar_y: int) -> None:
    """Draw the centered weapon selector in the bottom bar."""
    fonts = g.assets.fonts
    screen = g.screen
    player = g.player
    config = g.game_config

    pill_w = 92
    pill_h = 26
    spacing = 8
    total = 3 * pill_w + 2 * spacing
    start_x = SCREEN_WIDTH // 2 - total // 2
    y = bar_y + 7

    weapons = [
        ("Laser", "normal", True, Colors.EASY),
        ("Hagle", "shotgun", config["max_level_reached"] > 5, Colors.MEDIUM),
        ("Pisk", "electric whip", config["max_level_reached"] >= 10, Colors.HARD),
    ]

    for i, (name, wtype, unlocked, accent) in enumerate(weapons):
        px = start_x + i * (pill_w + spacing)
        r = pygame.Rect(px, y, pill_w, pill_h)

        if wtype == "electric whip":
            is_selected = unlocked and player.whip_charge >= player.whip_charge_threshold
        else:
            is_selected = player.current_weapon == wtype

        if not unlocked:
            pygame.draw.rect(screen, Colors.BG_DEEP, r, border_radius=pill_h // 2)
            pygame.draw.rect(screen, Colors.LOCKED, r, 1, border_radius=pill_h // 2)
            draw_text(screen, name, fonts["tiny"], Colors.LOCKED_TEXT,
                      (r.centerx, r.centery), anchor="center")
        elif is_selected:
            # Glow aura behind selected pill
            glow = pygame.Surface((pill_w + 8, pill_h + 8), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*accent[:3], 30),
                             (0, 0, pill_w + 8, pill_h + 8),
                             border_radius=pill_h // 2 + 4)
            screen.blit(glow, (px - 4, y - 4))

            pygame.draw.rect(screen, accent, r, border_radius=pill_h // 2)
            draw_text(screen, name, fonts["tiny"], Colors.BG_DEEP,
                      (r.centerx, r.centery), anchor="center")
        else:
            pygame.draw.rect(screen, (*Colors.BG_DEEP[:3], 180), r,
                             border_radius=pill_h // 2)
            pygame.draw.rect(screen, accent, r, 1, border_radius=pill_h // 2)
            draw_text(screen, name, fonts["tiny"], accent,
                      (r.centerx, r.centery), anchor="center")

        # Whip charge indicator
        if wtype == "electric whip" and unlocked:
            ratio = player.whip_charge / player.whip_charge_threshold
            if ratio < 1.0:
                charge_y = y + pill_h + 3
                charge_w = int(pill_w * min(max(ratio, 0), 1))
                pygame.draw.rect(screen, Colors.BG_DEEP,
                                 (px, charge_y, pill_w, 3), border_radius=2)
                if charge_w > 0:
                    # Gradient charge bar
                    pygame.draw.rect(screen, Colors.WHIP_CHARGING,
                                     (px, charge_y, charge_w, 3), border_radius=2)
            else:
                # Pulsing glow when fully charged
                pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1) / 2
                glow_alpha = int(30 + 50 * pulse)
                glow_surf = pygame.Surface((pill_w + 8, pill_h + 8), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*Colors.WHIP_READY, glow_alpha),
                                 (0, 0, pill_w + 8, pill_h + 8),
                                 border_radius=pill_h // 2 + 4)
                screen.blit(glow_surf, (px - 4, y - 4))


def _draw_lives(g: Game, bar_y: int) -> None:
    """Draw lives as small ship icons in the bottom-right."""
    screen = g.screen
    lives = g.player.lives

    icon_size = 20
    spacing = 5
    x = SCREEN_WIDTH - 16

    try:
        icon = pygame.transform.scale(
            g.assets.images["player"], (icon_size, icon_size),
        )
    except (pygame.error, KeyError):
        icon = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
        pygame.draw.polygon(
            icon, Colors.PRIMARY,
            [(icon_size // 2, 0), (0, icon_size), (icon_size, icon_size)],
        )

    for i in range(lives):
        ix = x - (i + 1) * (icon_size + spacing)
        screen.blit(icon, (ix, bar_y + 10))
