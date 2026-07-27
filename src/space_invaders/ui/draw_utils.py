"""Reusable modern UI drawing helpers."""

from __future__ import annotations

import pygame

from space_invaders.constants import Colors

# Edge-faded gradient strips are rebuilt with a per-pixel loop, so the HUD and
# separators — which redraw at identical sizes every frame — cache them.
_fade_strip_cache: dict[tuple, pygame.Surface] = {}


def _fade_strip(width: int, color: tuple[int, ...], alpha: int,
                rows: int = 1) -> pygame.Surface:
    """Horizontal line fading out towards both ends."""
    key = (width, color[:3], alpha, rows)
    strip = _fade_strip_cache.get(key)
    if strip is not None:
        return strip

    strip = pygame.Surface((width, rows), pygame.SRCALPHA)
    fade_zone = max(width // 5, 1)
    for px in range(width):
        edge = min(px, width - px, fade_zone) / fade_zone
        a = int(alpha * min(edge, 1.0))
        for row in range(rows):
            strip.set_at((px, row), (*color[:3], a >> row))
    _fade_strip_cache[key] = strip
    return strip


# ---------------------------------------------------------------------------
# Text rendering
# ---------------------------------------------------------------------------

def draw_text(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    color: tuple[int, ...],
    pos: tuple[int, int],
    anchor: str = "topleft",
    shadow: bool = False,
    shadow_color: tuple[int, ...] = Colors.TEXT_SHADOW,
    shadow_offset: tuple[int, int] = (2, 2),
) -> pygame.Rect:
    """Render text with optional drop shadow. Returns bounding rect."""
    main = font.render(text, True, color)
    rect = main.get_rect(**{anchor: pos})

    if shadow:
        sh = font.render(text, True, shadow_color)
        surface.blit(sh, rect.move(*shadow_offset))

    surface.blit(main, rect)
    return rect


def draw_spaced_text(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    color: tuple[int, ...],
    center_x: int,
    y: int,
    spacing: int = 4,
    shadow: bool = True,
    shadow_color: tuple[int, ...] = Colors.TEXT_SHADOW,
    glow_color: tuple[int, ...] | None = None,
) -> None:
    """Render text with extra letter spacing, centered horizontally.

    When *glow_color* is given, a soft bloom is drawn behind each character.
    """
    total_w = sum(font.size(c)[0] for c in text) + spacing * (len(text) - 1)
    x = center_x - total_w // 2

    # Optional glow pass
    if glow_color:
        gc = glow_color[:3]
        ga = glow_color[3] if len(glow_color) > 3 else 40
        gx = center_x - total_w // 2
        for char in text:
            glyph = font.render(char, True, gc)
            glyph.set_alpha(ga)
            for ox, oy in [(-3, 0), (3, 0), (0, -3), (0, 3), (-2, -2), (2, 2)]:
                surface.blit(glyph, (gx + ox, y + oy))
            gx += font.size(char)[0] + spacing

    for char in text:
        if shadow:
            sh = font.render(char, True, shadow_color)
            surface.blit(sh, (x + 2, y + 2))
        ch = font.render(char, True, color)
        surface.blit(ch, (x, y))
        x += ch.get_width() + spacing


def draw_glow_text(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    color: tuple[int, ...],
    pos: tuple[int, int],
    anchor: str = "midtop",
    glow_color: tuple[int, ...] | None = None,
    glow_radius: int = 6,
) -> pygame.Rect:
    """Render text with a soft glow bloom behind it."""
    main = font.render(text, True, color)
    rect = main.get_rect(**{anchor: pos})

    gc = glow_color or (*color[:3], 45)
    ga = gc[3] if len(gc) > 3 else 45
    glyph = font.render(text, True, gc[:3])

    for r_step in range(glow_radius, 0, -2):
        alpha = int(ga * (1 - r_step / glow_radius))
        g_copy = glyph.copy()
        g_copy.set_alpha(alpha)
        for ox, oy in [(-r_step, 0), (r_step, 0), (0, -r_step), (0, r_step)]:
            surface.blit(g_copy, rect.move(ox, oy))

    # Shadow then main
    sh = font.render(text, True, Colors.TEXT_SHADOW)
    surface.blit(sh, rect.move(2, 2))
    surface.blit(main, rect)
    return rect


# ---------------------------------------------------------------------------
# Panels & containers
# ---------------------------------------------------------------------------

def draw_panel(
    surface: pygame.Surface,
    rect: pygame.Rect | tuple[int, int, int, int],
    bg_color: tuple[int, ...] = Colors.BG_CARD,
    border_color: tuple[int, ...] = Colors.BORDER_SUBTLE,
    border_width: int = 1,
    radius: int = 12,
    shadow: bool = True,
    shadow_offset: int = 4,
    gradient_top: bool = False,
) -> None:
    """Draw a modern card-style panel with rounded corners and optional shadow."""
    r = pygame.Rect(rect)

    if shadow:
        sh_surf = pygame.Surface(
            (r.width + shadow_offset * 2, r.height + shadow_offset * 2),
            pygame.SRCALPHA,
        )
        pygame.draw.rect(
            sh_surf, (0, 0, 0, 50),
            (shadow_offset, shadow_offset, r.width, r.height),
            border_radius=radius,
        )
        surface.blit(sh_surf, (r.x - shadow_offset // 2, r.y))

    # draw.rect ignores alpha on an opaque target, so translucent fills (and
    # the fully transparent ones used by ghost buttons) go via a temp surface.
    if len(bg_color) > 3 and bg_color[3] < 255:
        if bg_color[3] > 0:
            fill = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
            pygame.draw.rect(fill, bg_color, (0, 0, r.width, r.height),
                             border_radius=radius)
            surface.blit(fill, r.topleft)
    else:
        pygame.draw.rect(surface, bg_color, r, border_radius=radius)

    # Subtle top-edge highlight for glass feel
    if gradient_top:
        grad_h = min(r.height // 3, 30)
        grad_surf = pygame.Surface((r.width, grad_h), pygame.SRCALPHA)
        for gy in range(grad_h):
            a = int(15 * (1 - gy / grad_h))
            pygame.draw.line(grad_surf, (255, 255, 255, a), (0, gy), (r.width, gy))
        mask = pygame.Surface((r.width, grad_h), pygame.SRCALPHA)
        pygame.draw.rect(
            mask, (255, 255, 255, 255),
            (0, 0, r.width, grad_h + radius),
            border_radius=radius,
        )
        grad_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surface.blit(grad_surf, (r.x, r.y))

    if border_width > 0:
        pygame.draw.rect(surface, border_color, r, border_width, border_radius=radius)


def draw_glass_bar(
    surface: pygame.Surface,
    rect: pygame.Rect | tuple[int, int, int, int],
    alpha: int = 140,
    accent_color: tuple[int, ...] = Colors.PRIMARY,
    accent_side: str = "bottom",
) -> None:
    """Draw a semi-transparent glass-style bar with a thin accent edge."""
    r = pygame.Rect(rect)
    bar = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
    bar.fill((*Colors.BG_DEEP[:3], alpha))

    # Inner gradient highlight
    grad_h = max(r.height // 3, 4)
    for gy in range(grad_h):
        a = int(8 * (1 - gy / grad_h))
        pygame.draw.line(bar, (255, 255, 255, a), (0, gy), (r.width, gy))

    surface.blit(bar, r.topleft)

    # Accent line with faded edges
    ac_alpha = accent_color[3] if len(accent_color) > 3 else 100
    accent_surf = _fade_strip(r.width, accent_color, ac_alpha, rows=2)

    if accent_side == "bottom":
        surface.blit(accent_surf, (r.x, r.bottom - 2))
    else:
        surface.blit(accent_surf, (r.x, r.y))


# ---------------------------------------------------------------------------
# Buttons
# ---------------------------------------------------------------------------

def draw_button(
    surface: pygame.Surface,
    rect: pygame.Rect,
    text: str,
    font: pygame.font.Font,
    *,
    bg_color: tuple[int, ...] = Colors.BG_CARD,
    bg_hover_color: tuple[int, ...] = Colors.BG_CARD_HOVER,
    text_color: tuple[int, ...] = Colors.TEXT_PRIMARY,
    text_hover_color: tuple[int, ...] | None = None,
    border_color: tuple[int, ...] = Colors.BORDER_SUBTLE,
    border_hover_color: tuple[int, ...] = Colors.PRIMARY,
    radius: int = 8,
    selected: bool = False,
    disabled: bool = False,
    mouse_pos: tuple[int, int] | None = None,
    shadow: bool = True,
) -> bool:
    """Draw a button with hover glow and return True if hovered."""
    is_hovered = (
        not disabled
        and mouse_pos is not None
        and rect.collidepoint(mouse_pos)
    )

    if disabled:
        bg = Colors.BG_DEEP
        border = Colors.LOCKED
        txt_c = Colors.LOCKED_TEXT
    elif selected:
        bg = bg_hover_color
        border = border_hover_color
        txt_c = text_hover_color or text_color
    elif is_hovered:
        bg = bg_hover_color
        border = border_hover_color
        txt_c = text_hover_color or text_color
    else:
        bg = bg_color
        border = border_color
        txt_c = text_color

    # Hover / select glow aura
    if (is_hovered or selected) and not disabled:
        glow = pygame.Surface((rect.width + 12, rect.height + 12), pygame.SRCALPHA)
        pygame.draw.rect(
            glow, (*border[:3], 22),
            (0, 0, rect.width + 12, rect.height + 12),
            border_radius=radius + 4,
        )
        surface.blit(glow, (rect.x - 6, rect.y - 6))

    draw_panel(
        surface, rect, bg, border,
        border_width=2 if (selected or is_hovered) else 1,
        radius=radius, shadow=shadow, shadow_offset=3,
        gradient_top=(is_hovered or selected) and not disabled,
    )

    rendered = font.render(text, True, txt_c)
    surface.blit(
        rendered,
        (rect.centerx - rendered.get_width() // 2,
         rect.centery - rendered.get_height() // 2),
    )
    return is_hovered


# ---------------------------------------------------------------------------
# Sliders, toggles, separators
# ---------------------------------------------------------------------------

def draw_slider(
    surface: pygame.Surface,
    rect: pygame.Rect,
    value: float,
    track_color: tuple[int, ...] = Colors.BG_DEEP,
    fill_color: tuple[int, ...] = Colors.PRIMARY,
    handle_color: tuple[int, ...] = Colors.PRIMARY_LIGHT,
    radius: int = 6,
    show_handle: bool = True,
) -> None:
    """Draw a modern slider bar (value 0.0-1.0)."""
    clamped = min(max(value, 0.0), 1.0)

    pygame.draw.rect(surface, track_color, rect, border_radius=radius)

    fill_w = max(int(rect.width * clamped), radius * 2 if clamped > 0.01 else 0)
    if fill_w > 0:
        fill_rect = pygame.Rect(rect.x, rect.y, fill_w, rect.height)
        pygame.draw.rect(surface, fill_color, fill_rect, border_radius=radius)
        # Bright top highlight
        hl = pygame.Surface((fill_w, rect.height // 2), pygame.SRCALPHA)
        hl.fill((255, 255, 255, 15))
        surface.blit(hl, (rect.x, rect.y))

    if show_handle and clamped > 0.01:
        hx = rect.x + fill_w
        hy = rect.centery
        hr = rect.height // 2 + 2
        pygame.draw.circle(surface, handle_color, (hx, hy), hr)
        pygame.draw.circle(surface, Colors.BG_DEEP, (hx, hy), hr - 3)
        pygame.draw.circle(surface, handle_color, (hx, hy), hr - 5)


def draw_toggle(
    surface: pygame.Surface,
    pos: tuple[int, int],
    active: bool,
    width: int = 50,
    height: int = 26,
    active_color: tuple[int, ...] = Colors.SUCCESS,
    inactive_color: tuple[int, ...] = Colors.LOCKED,
) -> None:
    """Draw a modern pill-shaped toggle switch."""
    r = height // 2
    track_rect = pygame.Rect(pos[0], pos[1], width, height)
    track_color = active_color if active else inactive_color

    pygame.draw.rect(surface, track_color, track_rect, border_radius=r)

    inner = pygame.Rect(pos[0] + 2, pos[1] + 2, width - 4, height - 4)
    inner_color = tuple(max(0, c - 30) for c in track_color[:3])
    pygame.draw.rect(surface, inner_color, inner, border_radius=r - 1)

    knob_r = r - 3
    knob_x = pos[0] + width - r if active else pos[0] + r
    knob_y = pos[1] + height // 2
    pygame.draw.circle(surface, Colors.TEXT_PRIMARY, (knob_x, knob_y), knob_r)


def draw_separator(
    surface: pygame.Surface,
    x: int,
    y: int,
    width: int,
    color: tuple[int, ...] = Colors.BORDER_SUBTLE,
    gradient: bool = True,
) -> None:
    """Draw a thin horizontal separator with optional edge fade."""
    if gradient and width > 20:
        surface.blit(_fade_strip(width, color, 255), (x, y))
    else:
        pygame.draw.line(surface, color, (x, y), (x + width, y), 1)


# Full-screen vignette now lives in systems/postfx.py, applied at present time.
