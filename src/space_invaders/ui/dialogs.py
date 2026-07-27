"""Dialog screens: game over, level complete, quit confirm, help, settings, level select."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from space_invaders.constants import (
    Colors,
    LEVELS_PER_PAGE,
    MAX_LEVEL_PAGES,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from space_invaders.systems.scoring import get_current_high_score
from space_invaders.ui.draw_utils import (
    draw_button,
    draw_glow_text,
    draw_panel,
    draw_separator,
    draw_slider,
    draw_text,
    draw_toggle,
)

if TYPE_CHECKING:
    from space_invaders.game import Game


# ------------------------------------------------------------------
# Level select
# ------------------------------------------------------------------

def draw_level_select(g: Game) -> None:
    fonts = g.assets.fonts
    screen = g.screen
    state = g.state
    config = g.game_config
    mouse = state.mouse_pos

    draw_glow_text(screen, "VELG LEVEL", fonts["large"], Colors.PRIMARY,
                   (SCREEN_WIDTH // 2, 40), glow_color=(*Colors.PRIMARY[:3], 30),
                   glow_radius=6)

    level_side = 104
    margin = 24
    grid_total_w = 3 * level_side + 2 * margin
    grid_x = int(SCREEN_WIDTH * 0.25) - grid_total_w // 2
    grid_y = 165

    # Page indicator
    draw_text(screen, f"Side {state.current_level_page + 1}/{MAX_LEVEL_PAGES}",
              fonts["medium"], Colors.TEXT_SECONDARY,
              (grid_x + grid_total_w // 2, 118), anchor="midtop")

    # Navigation panel
    nav_x = grid_x + grid_total_w + 44
    nav_w = SCREEN_WIDTH - nav_x - 40
    nav_h = 3 * level_side + 2 * margin
    draw_panel(screen, (nav_x, grid_y, nav_w, nav_h),
               Colors.BG_CARD, Colors.BORDER_MEDIUM, radius=14, gradient_top=True)

    draw_glow_text(screen, "Navigasjon", fonts["medium"], Colors.PRIMARY,
                   (nav_x + nav_w // 2, grid_y + 20),
                   glow_color=(*Colors.PRIMARY[:3], 15), glow_radius=3)

    draw_separator(screen, nav_x + 20, grid_y + 52, nav_w - 40, Colors.BORDER_SUBTLE)

    hints = [
        "Piltaster h\u00f8yre/venstre",
        "eller N/P for \u00e5 bla",
        "ESC for \u00e5 g\u00e5 tilbake",
        "Tall 1-9 for \u00e5 velge level",
    ]
    ns = (nav_h - 90) // 4
    for i, h in enumerate(hints):
        draw_text(screen, h, fonts["small"], Colors.TEXT_SECONDARY,
                  (nav_x + 20, grid_y + 65 + ns * i))

    # Level grid
    for row in range(3):
        for col in range(3):
            num = state.current_level_page * LEVELS_PER_PAGE + row * 3 + col + 1
            x = grid_x + col * (level_side + margin)
            y = grid_y + row * (level_side + margin)
            r = pygame.Rect(x, y, level_side, level_side)

            if num < config["max_level_reached"]:
                draw_button(screen, r, str(num), fonts["large"],
                            bg_color=Colors.BG_CARD, border_color=Colors.SUCCESS,
                            text_color=Colors.TEXT_PRIMARY, radius=16,
                            mouse_pos=mouse, shadow=True)
            elif num == config["max_level_reached"]:
                draw_button(screen, r, str(num), fonts["large"],
                            bg_color=Colors.BG_CARD, border_color=Colors.PRIMARY,
                            border_hover_color=Colors.PRIMARY_LIGHT,
                            text_color=Colors.TEXT_PRIMARY, radius=16,
                            selected=True, mouse_pos=mouse, shadow=True)
            else:
                draw_button(screen, r, str(num), fonts["large"],
                            disabled=True, radius=16, mouse_pos=mouse, shadow=False)

    # Color legend
    info_w = min(SCREEN_WIDTH - grid_x * 2, grid_total_w * 2)
    info_y = grid_y + 3 * (level_side + margin) + 4
    info_h = 100
    draw_panel(screen, (grid_x, info_y, info_w, info_h),
               Colors.BG_CARD, Colors.BORDER_SUBTLE, radius=12, gradient_top=True)

    draw_text(screen, "Fargekoder:", fonts["small"], Colors.TEXT_SECONDARY,
              (grid_x + 20, info_y + 12))

    legend_w = info_w // 3
    ly = info_y + 44
    for i, (color, label) in enumerate([
        (Colors.SUCCESS, "Fullf\u00f8rt niv\u00e5"),
        (Colors.PRIMARY, "Tilgjengelig niv\u00e5"),
        (Colors.LOCKED, "L\u00e5st niv\u00e5"),
    ]):
        cx = grid_x + i * legend_w + legend_w // 2
        pill = pygame.Rect(cx - 16, ly, 32, 16)
        pygame.draw.rect(screen, color, pill, border_radius=8)
        draw_text(screen, label, fonts["tiny"], Colors.TEXT_SECONDARY,
                  (cx, ly + 24), anchor="midtop")

    # Weapon unlock info
    wy = info_y + info_h + 12
    if config["max_level_reached"] > 5:
        draw_text(screen, "Hagle (v\u00e5pen) l\u00e5st opp! Bruk tast 2",
                  fonts["small"], Colors.SECONDARY, (grid_x + 20, wy))
        wy += 28
    if config["max_level_reached"] >= 10:
        draw_text(screen, "Elektrisk pisk (v\u00e5pen) l\u00e5st opp! Bruk tast 3",
                  fonts["small"], Colors.PRIMARY, (grid_x + 20, wy))


# ------------------------------------------------------------------
# Help
# ------------------------------------------------------------------

def draw_help(g: Game) -> int:
    """Draw the scrollable help screen. Returns content height for scroll limits."""
    fonts = g.assets.fonts
    screen = g.screen
    state = g.state

    draw_glow_text(screen, "SPILLMODUSER - HJELP", fonts["large"], Colors.PRIMARY,
                   (SCREEN_WIDTH // 2, 45),
                   glow_color=(*Colors.PRIMARY[:3], 30), glow_radius=5)

    box_w = int(SCREEN_WIDTH * 0.82)
    box_h = int(SCREEN_HEIGHT * 0.78)
    box_x = SCREEN_WIDTH // 2 - box_w // 2
    box_y = 100

    draw_panel(screen, (box_x, box_y, box_w, box_h),
               Colors.BG_CARD, Colors.BORDER_MEDIUM, radius=16,
               shadow=True, gradient_top=True)

    content_rect = pygame.Rect(box_x + 32, box_y + 24, box_w - 64, box_h - 56)
    surf = pygame.Surface((content_rect.width, 1800), pygame.SRCALPHA)
    # The input handler needs the real viewport height to clamp scrolling.
    g.renderer.help_view_height = content_rect.height

    cy = 0
    ls = 36
    section_gap = 30
    indent = 28

    # --- Game modes ---
    draw_text(surf, "Spillmoduser", fonts["medium"], Colors.PRIMARY_LIGHT,
              (content_rect.width // 2, cy), anchor="midtop")
    cy += 38
    draw_separator(surf, 20, cy, content_rect.width - 40, Colors.BORDER_SUBTLE)
    cy += 12

    tier_colors = {
        "easy": Colors.EASY,
        "medium": Colors.MEDIUM,
        "hard": Colors.HARD,
        "impossible": Colors.IMPOSSIBLE,
        "level": Colors.LEVEL,
    }
    modes = [
        ("Lett [1]", "easy", "Sakte fiender, siktelinje som hjelper med sikting"),
        ("Middels [2]", "medium", "Medium hastighet p\u00e5 fiender, siktelinje tilgjengelig"),
        ("Vanskelig [3]", "hard", "Raske fiender, ingen siktelinje for \u00e5 hjelpe med sikting"),
        ("Umulig [4]", "impossible", "Fiender skyter tilbake! Ekstrem vanskelighetsgrad"),
        ("Level Mode [L]", "level", "Spill niv\u00e5er i rekkef\u00f8lge. Nye v\u00e5pen l\u00e5ses opp ved fremgang."),
    ]
    for title, key, desc in modes:
        draw_text(surf, title, fonts["medium"], tier_colors[key], (indent, cy))
        cy += 38
        draw_text(surf, desc, fonts["small"], Colors.TEXT_SECONDARY, (indent + 14, cy))
        cy += ls

    cy += section_gap

    # --- Keyboard controls ---
    draw_text(surf, "Tastatur Kontroller", fonts["medium"], Colors.SECONDARY,
              (indent, cy))
    cy += 44
    draw_separator(surf, indent, cy, content_rect.width - indent * 2, Colors.BORDER_SUBTLE)
    cy += 10
    for line in [
        "Bevegelse: Piltaster eller A/D",
        "Skyt: Mellomrom, W eller Pil opp",
        "Bytt v\u00e5pen: 1, 2, 3 (hvis tilgjengelig)",
        "Pause/meny: ESC",
        "Fullskjerm: F",
    ]:
        draw_text(surf, line, fonts["small"], Colors.TEXT_SECONDARY, (indent + 20, cy))
        cy += ls
    cy += section_gap

    # --- Mouse controls ---
    draw_text(surf, "Musisk bevegelse", fonts["medium"], Colors.SUCCESS,
              (indent, cy))
    cy += 44
    draw_separator(surf, indent, cy, content_rect.width - indent * 2, Colors.BORDER_SUBTLE)
    cy += 10
    for line in [
        "Bevegelse: Flytt musen horisontalt",
        "Venstre-klikk: Laser",
        "H\u00f8yre-klikk: Hagle (om tilgjengelig)",
        "Midtklikk: El-pisk (om ladet)",
    ]:
        draw_text(surf, line, fonts["small"], Colors.TEXT_SECONDARY, (indent + 20, cy))
        cy += ls
    cy += section_gap

    # --- How to enable mouse ---
    draw_text(surf, "Aktivere musisk bevegelse", fonts["medium"],
              Colors.TEXT_SECONDARY, (indent, cy))
    cy += 35
    draw_text(surf, "G\u00e5 til innstillinger [I] fra hovedmenyen og velg [5] Bytt",
              fonts["small"], Colors.TEXT_MUTED, (indent + 20, cy))
    cy += ls + section_gap

    # --- Weapon info ---
    draw_text(surf, "V\u00e5peninformasjon", fonts["medium"], Colors.HARD,
              (indent, cy))
    cy += 44
    draw_separator(surf, indent, cy, content_rect.width - indent * 2, Colors.BORDER_SUBTLE)
    cy += 10
    for line in [
        "Laser: Standard v\u00e5pen, presist og raskt",
        "Hagle: Bred spredning, kort rekkevidde, l\u00e5ses opp i level 5+",
        "Elektrisk pisk: Kraftig v\u00e5pen med stor rekkevidde, l\u00e5ses opp i level 10+",
        "Pisken lades opp n\u00e5r du skyter fiender. Bruk n\u00e5r fulladet for best effekt.",
    ]:
        draw_text(surf, line, fonts["small"], Colors.TEXT_SECONDARY, (indent + 20, cy))
        cy += ls

    content_height = cy

    screen.blit(surf, content_rect,
                (0, state.help_scroll_y, content_rect.width, content_rect.height))

    # Scroll indicators with glow
    if state.help_scroll_y > 0:
        mid_x = box_x + box_w // 2
        # Fade gradient at top
        fade = pygame.Surface((box_w - 4, 20), pygame.SRCALPHA)
        for fy in range(20):
            a = int(80 * (1 - fy / 20))
            pygame.draw.line(fade, (*Colors.BG_CARD[:3], a), (0, fy), (box_w - 4, fy))
        screen.blit(fade, (box_x + 2, box_y + 2))
        pygame.draw.polygon(screen, Colors.PRIMARY_DIM, [
            (mid_x, box_y + 8), (mid_x - 10, box_y + 20), (mid_x + 10, box_y + 20)])

    if state.help_scroll_y < content_height - content_rect.height:
        mid_x = box_x + box_w // 2
        by = box_y + box_h
        # Fade gradient at bottom
        fade = pygame.Surface((box_w - 4, 20), pygame.SRCALPHA)
        for fy in range(20):
            a = int(80 * fy / 20)
            pygame.draw.line(fade, (*Colors.BG_CARD[:3], a), (0, fy), (box_w - 4, fy))
        screen.blit(fade, (box_x + 2, by - 22))
        pygame.draw.polygon(screen, Colors.PRIMARY_DIM, [
            (mid_x, by - 8), (mid_x - 10, by - 20), (mid_x + 10, by - 20)])

    draw_text(screen, "Trykk ESC eller H for \u00e5 g\u00e5 tilbake", fonts["small"],
              Colors.TEXT_MUTED, (SCREEN_WIDTH // 2, box_y + box_h + 10), anchor="midtop")

    return content_height


# ------------------------------------------------------------------
# Settings
# ------------------------------------------------------------------

def draw_settings(g: Game) -> None:
    fonts = g.assets.fonts
    screen = g.screen
    state = g.state

    draw_glow_text(screen, "INNSTILLINGER", fonts["large"], Colors.PRIMARY,
                   (SCREEN_WIDTH // 2, 28),
                   glow_color=(*Colors.PRIMARY[:3], 30), glow_radius=5)

    box_w = int(SCREEN_WIDTH * 0.7)
    box_h = int(SCREEN_HEIGHT * 0.72)
    box_x = SCREEN_WIDTH // 2 - box_w // 2
    box_y = 82

    draw_panel(screen, (box_x, box_y, box_w, box_h),
               Colors.BG_CARD, Colors.BORDER_MEDIUM, radius=16,
               shadow=True, gradient_top=True)

    y = box_y + 30
    line_sp = 115
    bar_w = int(box_w * 0.55)
    bar_h = 14
    bar_x = box_x + 55

    # --- Sound effects ---
    draw_text(screen, "Lydeffekter", fonts["medium"], Colors.PRIMARY, (bar_x, y))
    by = y + 38
    draw_slider(screen, pygame.Rect(bar_x, by, bar_w, bar_h),
                state.sound_volume, fill_color=Colors.PRIMARY)
    draw_text(screen, f"{int(state.sound_volume * 100)}%", fonts["small"],
              Colors.TEXT_PRIMARY, (bar_x + bar_w + 20, by - 2))
    draw_text(screen, "[1] Senk   [2] \u00d8k", fonts["tiny"],
              Colors.TEXT_MUTED, (bar_x, by + bar_h + 10))

    # --- Music ---
    y += line_sp
    draw_text(screen, "Musikk", fonts["medium"], Colors.IMPOSSIBLE, (bar_x, y))
    by = y + 38
    draw_slider(screen, pygame.Rect(bar_x, by, bar_w, bar_h),
                state.music_volume / 0.2, fill_color=Colors.IMPOSSIBLE)
    draw_text(screen, f"{int((state.music_volume / 0.2) * 100)}%", fonts["small"],
              Colors.TEXT_PRIMARY, (bar_x + bar_w + 20, by - 2))
    draw_text(screen, "[3] Senk   [4] \u00d8k", fonts["tiny"],
              Colors.TEXT_MUTED, (bar_x, by + bar_h + 10))

    # --- Mouse toggle ---
    y += line_sp
    draw_text(screen, "Musisk bevegelse", fonts["medium"], Colors.SUCCESS, (bar_x, y))
    ty = y + 38
    draw_toggle(screen, (bar_x, ty), state.mouse_control)

    label = "P\u00c5" if state.mouse_control else "AV"
    label_color = Colors.SUCCESS if state.mouse_control else Colors.HARD
    draw_text(screen, label, fonts["small"], label_color, (bar_x + 65, ty + 4))
    draw_text(screen, "[5] Bytt", fonts["tiny"],
              Colors.TEXT_MUTED, (bar_x, ty + 34))

    draw_separator(screen, bar_x, ty + 60, bar_w, Colors.BORDER_SUBTLE)

    draw_text(screen, "Se Hjelp [H] for kontroll-informasjon", fonts["small"],
              Colors.TEXT_MUTED, (bar_x, ty + 72))

    draw_text(screen, "Trykk ESC eller I for \u00e5 g\u00e5 tilbake", fonts["medium"],
              Colors.TEXT_MUTED, (SCREEN_WIDTH // 2, box_y + box_h - 45), anchor="midtop")


# ------------------------------------------------------------------
# Level complete
# ------------------------------------------------------------------

def draw_level_complete(g: Game) -> None:
    fonts = g.assets.fonts
    screen = g.screen
    state = g.state
    transitions = g.renderer.transitions

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill(Colors.BG_OVERLAY)
    screen.blit(overlay, (0, 0))

    dw, dh = 640, 310
    dx = SCREEN_WIDTH // 2 - dw // 2

    slide_key = "level_complete_slide"
    offset = 0 if transitions.is_done(slide_key) else transitions.get(slide_key, 0)
    dy = SCREEN_HEIGHT // 2 - dh // 2 + int(offset)

    draw_panel(screen, (dx, dy, dw, dh),
               Colors.BG_CARD, Colors.SUCCESS, border_width=2, radius=18,
               shadow=True, shadow_offset=10, gradient_top=True)

    draw_glow_text(screen, "LEVEL FULLF\u00d8RT!", fonts["large"], Colors.SUCCESS,
                   (SCREEN_WIDTH // 2, dy + 38),
                   glow_color=(*Colors.SUCCESS[:3], 35), glow_radius=5)

    if state.level > 1:
        msg = f"Level {state.level - 1} fullf\u00f8rt! Neste: Level {state.level}"
    else:
        msg = f"Du g\u00e5r n\u00e5 til Level {state.level}"
    draw_text(screen, msg, fonts["medium"], Colors.TEXT_PRIMARY,
              (SCREEN_WIDTH // 2, dy + 118), anchor="midtop")

    if state.show_shotgun_unlock:
        draw_text(screen, "HAGLE V\u00c5PEN L\u00c5ST OPP!", fonts["medium"],
                  Colors.SECONDARY, (SCREEN_WIDTH // 2, dy + 168), anchor="midtop")

    draw_separator(screen, dx + 50, dy + 222, dw - 100, Colors.BORDER_SUBTLE)

    draw_text(screen, "Trykk ENTER for \u00e5 fortsette", fonts["small"],
              Colors.TEXT_MUTED, (SCREEN_WIDTH // 2, dy + 246), anchor="midtop")


# ------------------------------------------------------------------
# Game over
# ------------------------------------------------------------------

def draw_game_over(g: Game) -> None:
    fonts = g.assets.fonts
    screen = g.screen
    state = g.state
    transitions = g.renderer.transitions

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill(Colors.BG_OVERLAY)
    screen.blit(overlay, (0, 0))

    dw, dh = 640, 310
    dx = SCREEN_WIDTH // 2 - dw // 2

    slide_key = "game_over_slide"
    offset = 0 if transitions.is_done(slide_key) else transitions.get(slide_key, 0)
    dy = SCREEN_HEIGHT // 2 - dh // 2 + int(offset)

    draw_panel(screen, (dx, dy, dw, dh),
               Colors.BG_CARD, Colors.DANGER, border_width=2, radius=18,
               shadow=True, shadow_offset=10, gradient_top=True)

    draw_glow_text(screen, "GAME OVER", fonts["large"], Colors.DANGER,
                   (SCREEN_WIDTH // 2, dy + 38),
                   glow_color=(*Colors.DANGER[:3], 40), glow_radius=6)

    draw_text(screen, f"Din poengsum: {state.score}", fonts["medium"],
              Colors.TEXT_PRIMARY, (SCREEN_WIDTH // 2, dy + 118), anchor="midtop")

    hs = get_current_high_score(state.difficulty, state.level, state.level_mode, g.high_scores)
    if state.score > hs:
        draw_text(screen, "Ny highscore!", fonts["small"], Colors.SECONDARY,
                  (SCREEN_WIDTH // 2, dy + 168), anchor="midtop")

    draw_separator(screen, dx + 50, dy + 222, dw - 100, Colors.BORDER_SUBTLE)

    draw_text(screen, "Trykk ENTER for \u00e5 g\u00e5 til hovedmenyen", fonts["small"],
              Colors.TEXT_MUTED, (SCREEN_WIDTH // 2, dy + 246), anchor="midtop")


# ------------------------------------------------------------------
# Quit confirm
# ------------------------------------------------------------------

def draw_quit_confirm(g: Game) -> None:
    fonts = g.assets.fonts
    screen = g.screen
    transitions = g.renderer.transitions

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill(Colors.BG_OVERLAY)
    screen.blit(overlay, (0, 0))

    dw, dh = 640, 280
    dx = SCREEN_WIDTH // 2 - dw // 2

    slide_key = "quit_confirm_slide"
    offset = 0 if transitions.is_done(slide_key) else transitions.get(slide_key, 0)
    dy = SCREEN_HEIGHT // 2 - dh // 2 + int(offset)

    draw_panel(screen, (dx, dy, dw, dh),
               Colors.BG_CARD, Colors.BORDER_BRIGHT, border_width=2, radius=18,
               shadow=True, shadow_offset=10, gradient_top=True)

    draw_text(screen, "Vil du avslutte spillet?", fonts["medium"],
              Colors.TEXT_PRIMARY, (SCREEN_WIDTH // 2, dy + 44), anchor="midtop")

    draw_separator(screen, dx + 50, dy + 104, dw - 100, Colors.BORDER_SUBTLE)

    draw_text(screen, "Ja [J/Y] - Tilbake til hovedmeny", fonts["small"],
              Colors.TEXT_SECONDARY, (SCREEN_WIDTH // 2, dy + 132), anchor="midtop")

    draw_text(screen, "Nei [N/ESC] - Fortsett spill", fonts["small"],
              Colors.TEXT_SECONDARY, (SCREEN_WIDTH // 2, dy + 186), anchor="midtop")
