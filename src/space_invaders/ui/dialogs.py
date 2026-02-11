"""Dialog screens: game over, level complete, quit confirm, help, settings, level select."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from space_invaders.constants import (
    CYAN,
    LEVELS_PER_PAGE,
    MAX_LEVEL_PAGES,
    PASTEL_COLORS,
    RED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    WHITE,
)
from space_invaders.systems.scoring import get_current_high_score

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

    title = fonts["large"].render("VELG LEVEL", True, WHITE)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))

    level_side = 80
    margin = 20
    grid_x = int(SCREEN_WIDTH * 0.25) - ((3 * level_side + 2 * margin) // 2)
    grid_y = 150

    # Page indicator
    page_txt = fonts["medium"].render(
        f"Side {state.current_level_page + 1}/{MAX_LEVEL_PAGES}", True, WHITE)
    screen.blit(page_txt, (grid_x + (3 * level_side + 2 * margin) // 2
                           - page_txt.get_width() // 2, 110))

    # Navigation panel
    nav_x = grid_x + 3 * level_side + 2 * margin + 40
    nav_w = SCREEN_WIDTH - nav_x - 20
    nav_h = 3 * level_side + 2 * margin
    pygame.draw.rect(screen, (50, 50, 70), (nav_x, grid_y, nav_w, nav_h))
    pygame.draw.rect(screen, WHITE, (nav_x, grid_y, nav_w, nav_h), 2)

    nav_title = fonts["medium"].render("Navigasjon", True, WHITE)
    screen.blit(nav_title, (nav_x + nav_w // 2 - nav_title.get_width() // 2, grid_y + 20))

    hints = [
        "Piltaster høyre/venstre",
        "eller N/P for å bla",
        "ESC for å gå tilbake",
        "Tall 1-9 for å velge level",
    ]
    ns = (nav_h - 80) // 4
    for i, h in enumerate(hints):
        t = fonts["small"].render(h, True, WHITE)
        screen.blit(t, (nav_x + 20, grid_y + 60 + ns * i))

    # Level grid
    for row in range(3):
        for col in range(3):
            num = state.current_level_page * LEVELS_PER_PAGE + row * 3 + col + 1
            x = grid_x + col * (level_side + margin)
            y = grid_y + row * (level_side + margin)

            if num < config["max_level_reached"]:
                box_color, text_color = CYAN, WHITE
            elif num == config["max_level_reached"]:
                box_color, text_color = (100, 100, 255), WHITE
            else:
                box_color, text_color = (100, 100, 100), (200, 200, 200)

            pygame.draw.rect(screen, box_color, (x, y, level_side, level_side))
            pygame.draw.rect(screen, WHITE, (x, y, level_side, level_side), 2)
            nt = fonts["medium"].render(str(num), True, text_color)
            screen.blit(nt, (x + level_side // 2 - nt.get_width() // 2,
                             y + level_side // 2 - nt.get_height() // 2))

    # Color legend
    info_w = min(SCREEN_WIDTH - 40, (3 * level_side + 2 * margin) * 2)
    info_y = grid_y + 3 * (level_side + margin) + 10
    info_h = 100
    pygame.draw.rect(screen, (50, 50, 70), (grid_x, info_y, info_w, info_h))
    pygame.draw.rect(screen, WHITE, (grid_x, info_y, info_w, info_h), 2)

    it = fonts["medium"].render("Fargekoder:", True, WHITE)
    screen.blit(it, (grid_x + 20, info_y + 15))

    legend_w = info_w // 3
    bs = 25
    ly = info_y + 45
    for i, (color, label) in enumerate([
        (CYAN, "Fullført nivå"),
        ((100, 100, 255), "Tilgjengelig nivå"),
        ((100, 100, 100), "Låst nivå"),
    ]):
        cx = grid_x + i * legend_w + legend_w // 2
        pygame.draw.rect(screen, color, (cx - bs // 2, ly, bs, bs))
        lt = fonts["small"].render(label, True, WHITE)
        screen.blit(lt, (cx - lt.get_width() // 2, ly + bs + 5))

    # Weapon unlock info
    wy = info_y + info_h + 20
    if config["max_level_reached"] > 5:
        t = fonts["small"].render("Hagle (våpen) låst opp! Bruk tast 2", True, (255, 165, 0))
        screen.blit(t, (grid_x + 20, wy))
        wy += 30
    if config["max_level_reached"] >= 10:
        t = fonts["small"].render(
            "Elektrisk pisk (våpen) låst opp! Bruk tast 3", True, (0, 200, 255))
        screen.blit(t, (grid_x + 20, wy))


# ------------------------------------------------------------------
# Help
# ------------------------------------------------------------------

def draw_help(g: Game) -> int:
    """Draw the scrollable help screen. Returns content height for scroll limits."""
    fonts = g.assets.fonts
    screen = g.screen
    state = g.state

    screen.fill((0, 0, 0))
    g.star_group.draw(screen)

    ht = fonts["large"].render("SPILLMODUSER - HJELP", True, WHITE)
    screen.blit(ht, (SCREEN_WIDTH // 2 - ht.get_width() // 2, 50))

    box_w = int(SCREEN_WIDTH * 0.8)
    box_h = int(SCREEN_HEIGHT * 0.8)
    box_x = SCREEN_WIDTH // 2 - box_w // 2
    box_y = 100

    pygame.draw.rect(screen, (40, 40, 50, 180), (box_x, box_y, box_w, box_h))
    pygame.draw.rect(screen, WHITE, (box_x, box_y, box_w, box_h), 2)

    content_rect = pygame.Rect(box_x + 20, box_y + 20, box_w - 40, box_h - 50)
    surf = pygame.Surface((content_rect.width, 1500), pygame.SRCALPHA)

    cy = 0
    ls = 30
    ss = 50

    # Game modes
    surf.blit(fonts["medium"].render("Spillmoduser", True, (200, 200, 255)),
              (content_rect.width // 2 - fonts["medium"].render("Spillmoduser", True, WHITE).get_width() // 2, cy))
    cy += 40

    modes = [
        ("Lett [1]", "easy", "Sakte fiender, siktelinje som hjelper med sikting"),
        ("Middels [2]", "medium", "Medium hastighet på fiender, siktelinje tilgjengelig"),
        ("Vanskelig [3]", "hard", "Raske fiender, ingen siktelinje for å hjelpe med sikting"),
        ("Umulig [4]", "impossible", "Fiender skyter tilbake! Ekstrem vanskelighetsgrad"),
        ("Level Mode [L]", "level", "Spill nivåer i rekkefølge. Nye våpen låses opp ved fremgang."),
    ]
    for title, key, desc in modes:
        surf.blit(fonts["medium"].render(title, True, PASTEL_COLORS[key]), (20, cy))
        cy += 30
        surf.blit(fonts["small"].render(desc, True, WHITE), (20, cy))
        cy += ls

    cy += 20  # Extra space before controls

    # Keyboard controls
    surf.blit(fonts["medium"].render("Tastatur Kontroller", True, (220, 220, 150)), (20, cy))
    cy += 40
    for line in [
        "Bevegelse: Piltaster eller A/D",
        "Skyt: Mellomrom, W eller Pil opp",
        "Bytt våpen: 1, 2, 3 (hvis tilgjengelig)",
        "Pause/meny: ESC",
        "Fullskjerm: F",
    ]:
        surf.blit(fonts["small"].render(line, True, WHITE), (40, cy))
        cy += ls
    cy += 20

    # Mouse controls
    surf.blit(fonts["medium"].render("Musisk bevegelse", True, (150, 220, 150)), (20, cy))
    cy += 40
    for line in [
        "Bevegelse: Flytt musen horisontalt",
        "Venstre-klikk: Laser",
        "Høyre-klikk: Hagle (om tilgjengelig)",
        "Midtklikk: El-pisk (om ladet)",
    ]:
        surf.blit(fonts["small"].render(line, True, WHITE), (40, cy))
        cy += ls
    cy += 20

    # How to enable mouse
    surf.blit(fonts["medium"].render("Aktivere musisk bevegelse", True, (200, 200, 200)), (20, cy))
    cy += 40
    surf.blit(fonts["small"].render(
        "Gå til innstillinger [I] fra hovedmenyen og velg [5] Bytt", True, (200, 200, 200)), (40, cy))
    cy += ss

    # Weapon info
    surf.blit(fonts["medium"].render("Våpeninformasjon", True, (220, 180, 180)), (20, cy))
    cy += 40
    for line in [
        "Laser: Standard våpen, presist og raskt",
        "Hagle: Bred spredning, kort rekkevidde, låses opp i level 5+",
        "Elektrisk pisk: Kraftig våpen med stor rekkevidde, låses opp i level 10+",
        "Pisken lades opp når du skyter fiender. Bruk når fulladet for best effekt.",
    ]:
        surf.blit(fonts["small"].render(line, True, WHITE), (40, cy))
        cy += ls

    content_height = cy

    screen.blit(surf, content_rect, (0, state.help_scroll_y, content_rect.width, content_rect.height))

    # Scroll indicators
    if state.help_scroll_y > 0:
        mid_x = box_x + box_w // 2
        pygame.draw.polygon(screen, (200, 200, 200), [
            (mid_x, box_y + 10), (mid_x - 15, box_y + 25), (mid_x + 15, box_y + 25)])

    if state.help_scroll_y < content_height - content_rect.height:
        mid_x = box_x + box_w // 2
        by = box_y + box_h
        pygame.draw.polygon(screen, (200, 200, 200), [
            (mid_x, by - 10), (mid_x - 15, by - 25), (mid_x + 15, by - 25)])

    back = fonts["small"].render("Trykk ESC eller H for å gå tilbake", True, (200, 200, 200))
    screen.blit(back, (SCREEN_WIDTH // 2 - back.get_width() // 2, box_y + box_h + 10))

    return content_height


# ------------------------------------------------------------------
# Settings
# ------------------------------------------------------------------

def draw_settings(g: Game) -> None:
    fonts = g.assets.fonts
    screen = g.screen
    state = g.state

    screen.fill((0, 0, 0))
    g.star_group.draw(screen)

    title = fonts["large"].render("INNSTILLINGER", True, WHITE)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))

    box_w = int(SCREEN_WIDTH * 0.7)
    box_h = int(SCREEN_HEIGHT * 0.75)
    box_x = SCREEN_WIDTH // 2 - box_w // 2
    box_y = 80

    pygame.draw.rect(screen, (40, 40, 50, 200), (box_x, box_y, box_w, box_h))
    pygame.draw.rect(screen, (100, 100, 150), (box_x, box_y, box_w, box_h), 2)

    y = box_y + 30
    line_sp = 120
    bar_w = int(box_w * 0.6)
    bar_h = 20
    bar_x = box_x + 50

    # Sound
    screen.blit(fonts["medium"].render("Lydeffekter", True, (150, 220, 220)), (bar_x, y))
    by = y + 35
    pygame.draw.rect(screen, (80, 80, 80), (bar_x, by, bar_w, bar_h))
    fw = int(bar_w * state.sound_volume)
    pygame.draw.rect(screen, (100, 200, 200), (bar_x, by, fw, bar_h))
    pygame.draw.rect(screen, WHITE, (bar_x, by, bar_w, bar_h), 2)
    vt = fonts["small"].render(f"{int(state.sound_volume * 100)}%", True, WHITE)
    screen.blit(vt, (bar_x + bar_w + 20, by))
    screen.blit(fonts["small"].render("[1] Senk   [2] Øk", True, WHITE), (bar_x, by + bar_h + 10))

    # Music
    y += line_sp
    screen.blit(fonts["medium"].render("Musikk", True, (220, 150, 220)), (bar_x, y))
    by = y + 35
    pygame.draw.rect(screen, (80, 80, 80), (bar_x, by, bar_w, bar_h))
    fw = int(bar_w * (state.music_volume / 0.2))
    pygame.draw.rect(screen, (200, 100, 200), (bar_x, by, fw, bar_h))
    pygame.draw.rect(screen, WHITE, (bar_x, by, bar_w, bar_h), 2)
    vt = fonts["small"].render(f"{int((state.music_volume / 0.2) * 100)}%", True, WHITE)
    screen.blit(vt, (bar_x + bar_w + 20, by))
    screen.blit(fonts["small"].render("[3] Senk   [4] Øk", True, WHITE), (bar_x, by + bar_h + 10))

    # Mouse toggle
    y += line_sp
    screen.blit(fonts["medium"].render("Musisk bevegelse", True, (150, 220, 150)), (bar_x, y))
    ty = y + 35
    tw, th = 60, 30
    pygame.draw.rect(screen, (80, 80, 80), (bar_x, ty, tw, th))
    if state.mouse_control:
        pygame.draw.rect(screen, (150, 200, 100), (bar_x + tw // 2, ty, tw // 2, th))
    else:
        pygame.draw.rect(screen, (200, 100, 100), (bar_x, ty, tw // 2, th))
    pygame.draw.rect(screen, WHITE, (bar_x, ty, tw, th), 2)

    mc_color = (150, 200, 100) if state.mouse_control else (200, 100, 100)
    mc_txt = "PÅ" if state.mouse_control else "AV"
    screen.blit(fonts["small"].render(mc_txt, True, mc_color), (bar_x + tw + 20, ty + 5))
    screen.blit(fonts["small"].render("[5] Bytt", True, WHITE), (bar_x, ty + th + 10))

    screen.blit(fonts["small"].render(
        "Se Hjelp [H] for kontroll-informasjon", True, (200, 200, 200)),
        (box_x + 50, ty + th + 40))

    back = fonts["medium"].render("Trykk ESC eller I for å gå tilbake", True, (200, 200, 200))
    screen.blit(back, (SCREEN_WIDTH // 2 - back.get_width() // 2, box_y + box_h - 50))


# ------------------------------------------------------------------
# Level complete
# ------------------------------------------------------------------

def draw_level_complete(g: Game) -> None:
    fonts = g.assets.fonts
    screen = g.screen
    state = g.state

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    dw, dh = 400, 200
    dx = SCREEN_WIDTH // 2 - dw // 2
    dy = SCREEN_HEIGHT // 2 - dh // 2

    pygame.draw.rect(screen, (50, 90, 60), (dx, dy, dw, dh))
    pygame.draw.rect(screen, CYAN, (dx, dy, dw, dh), 2)

    lt = fonts["large"].render("LEVEL FULLFØRT!", True, CYAN)
    screen.blit(lt, (SCREEN_WIDTH // 2 - lt.get_width() // 2, dy + 30))

    if state.level > 1:
        nl = fonts["medium"].render(
            f"Level {state.level - 1} fullført! Neste: Level {state.level}", True, WHITE)
    else:
        nl = fonts["medium"].render(f"Du går nå til Level {state.level}", True, WHITE)
    screen.blit(nl, (SCREEN_WIDTH // 2 - nl.get_width() // 2, dy + 80))

    if state.show_shotgun_unlock:
        su = fonts["medium"].render("HAGLE VÅPEN LÅST OPP!", True, (255, 165, 0))
        screen.blit(su, (SCREEN_WIDTH // 2 - su.get_width() // 2, dy + 120))

    ct = fonts["small"].render("Trykk ENTER for å fortsette", True, WHITE)
    screen.blit(ct, (SCREEN_WIDTH // 2 - ct.get_width() // 2, dy + 160))


# ------------------------------------------------------------------
# Game over
# ------------------------------------------------------------------

def draw_game_over(g: Game) -> None:
    fonts = g.assets.fonts
    screen = g.screen
    state = g.state

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    dw, dh = 400, 200
    dx = SCREEN_WIDTH // 2 - dw // 2
    dy = SCREEN_HEIGHT // 2 - dh // 2

    pygame.draw.rect(screen, (90, 50, 50), (dx, dy, dw, dh))
    pygame.draw.rect(screen, RED, (dx, dy, dw, dh), 2)

    go = fonts["large"].render("GAME OVER!", True, RED)
    screen.blit(go, (SCREEN_WIDTH // 2 - go.get_width() // 2, dy + 30))

    st = fonts["medium"].render(f"Din poengsum: {state.score}", True, WHITE)
    screen.blit(st, (SCREEN_WIDTH // 2 - st.get_width() // 2, dy + 80))

    hs = get_current_high_score(state.difficulty, state.level, state.level_mode, g.high_scores)
    if state.score > hs:
        hs_msg = fonts["small"].render("Ny highscore!", True, (255, 215, 0))
        screen.blit(hs_msg, (SCREEN_WIDTH // 2 - hs_msg.get_width() // 2, dy + 120))

    ct = fonts["small"].render("Trykk ENTER for å gå til hovedmenyen", True, WHITE)
    screen.blit(ct, (SCREEN_WIDTH // 2 - ct.get_width() // 2, dy + 160))


# ------------------------------------------------------------------
# Quit confirm
# ------------------------------------------------------------------

def draw_quit_confirm(g: Game) -> None:
    fonts = g.assets.fonts
    screen = g.screen

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    dw, dh = 400, 180
    dx = SCREEN_WIDTH // 2 - dw // 2
    dy = SCREEN_HEIGHT // 2 - dh // 2

    pygame.draw.rect(screen, (60, 60, 70), (dx, dy, dw, dh))
    pygame.draw.rect(screen, (120, 120, 140), (dx, dy, dw, dh), 2)

    qt = fonts["medium"].render("Vil du avslutte spillet?", True, WHITE)
    screen.blit(qt, (SCREEN_WIDTH // 2 - qt.get_width() // 2, dy + 30))

    yt = fonts["small"].render("Ja [J/Y] - Tilbake til hovedmeny", True, WHITE)
    screen.blit(yt, (SCREEN_WIDTH // 2 - yt.get_width() // 2, dy + 80))

    nt = fonts["small"].render("Nei [N/ESC] - Fortsett spill", True, WHITE)
    screen.blit(nt, (SCREEN_WIDTH // 2 - nt.get_width() // 2, dy + 120))
