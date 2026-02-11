"""Main renderer that dispatches to screen-specific drawing."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from space_invaders.constants import BLACK, SCREEN_HEIGHT, SCREEN_WIDTH
from space_invaders.state import GameScreen
from space_invaders.ui.menu import draw_menu
from space_invaders.ui.hud import draw_hud
from space_invaders.ui.dialogs import (
    draw_game_over,
    draw_help,
    draw_level_complete,
    draw_level_select,
    draw_quit_confirm,
    draw_settings,
)

if TYPE_CHECKING:
    from space_invaders.game import Game


class Renderer:
    """Orchestrates all drawing based on current game screen."""

    def __init__(self, game: Game) -> None:
        self.game = game
        self.help_content_height = 800  # updated by draw_help

    def draw(self) -> None:
        g = self.game
        screen = g.state.screen

        # Background
        if screen == GameScreen.MENU and "background" in g.assets.images:
            g.screen.blit(g.assets.images["background"], (0, 0))
        else:
            g.screen.fill(BLACK)

        # Stars (skip on menu which uses the background image)
        if screen != GameScreen.MENU:
            g.star_group.draw(g.screen)

        # Screen-specific drawing
        if screen == GameScreen.MENU:
            draw_menu(g)
        elif screen == GameScreen.LEVEL_SELECT:
            draw_level_select(g)
        elif screen == GameScreen.HELP:
            self.help_content_height = draw_help(g)
        elif screen == GameScreen.SETTINGS:
            draw_settings(g)
        elif screen == GameScreen.LEVEL_COMPLETE:
            self._draw_gameplay(g)
            draw_level_complete(g)
        elif screen == GameScreen.GAME_OVER:
            self._draw_gameplay(g)
            draw_game_over(g)
        elif screen == GameScreen.QUIT_CONFIRM:
            self._draw_gameplay(g)
            draw_quit_confirm(g)
        elif screen == GameScreen.PLAYING:
            self._draw_gameplay(g)

        pygame.display.flip()

    def _draw_gameplay(self, g: Game) -> None:
        """Draw the playing field: aim line, sprites, HUD."""
        from space_invaders.constants import DIFFICULTY_CONFIG

        diff_cfg = DIFFICULTY_CONFIG[g.state.difficulty]
        if diff_cfg["show_aim_line"] and g.state.screen != GameScreen.GAME_OVER:
            aim = pygame.Surface((2, SCREEN_HEIGHT), pygame.SRCALPHA)
            aim.fill((0, 0, 255, 30))
            for y in range(0, SCREEN_HEIGHT, 10):
                if y % 20 == 0:
                    pygame.draw.line(aim, (0, 0, 255, 80), (0, y), (2, y + 8), 2)
            g.screen.blit(aim, (g.player.rect.centerx - 1, 0))

        g.all_sprites.draw(g.screen)
        draw_hud(g)
