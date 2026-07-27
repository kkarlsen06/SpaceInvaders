"""Headless smoke test for the render pipeline and combat loop.

Most of the visual work (PostFX blend chain, hitbox collision, hitstop) has no
natural unit boundary — it either draws a frame or it doesn't. So this boots the
real game against SDL's dummy drivers, renders every screen, and plays a kill
through. If the render chain or collision wiring breaks, this fails.
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402
import pytest  # noqa: E402

from space_invaders.entities.enemies import Enemy  # noqa: E402
from space_invaders.entities.projectiles import Shot, hitbox_collide  # noqa: E402
from space_invaders.game import Game  # noqa: E402
from space_invaders.state import GameScreen  # noqa: E402
from space_invaders.systems.postfx import make_radial_alpha  # noqa: E402


def test_premultiplied_glow_fades_in_rgb():
    """Additive blends ignore alpha, so an additive glow must fade via RGB.

    Getting this wrong renders every glow, plume and nebula cloud as a flat
    disc — which still looks 'lit' in aggregate, so a brightness check alone
    will not catch it.
    """
    size = 64
    glow = make_radial_alpha(size, (255, 255, 255), max_alpha=255,
                             falloff=2.0, premultiplied=True)
    centre = glow.get_at((size // 2, size // 2))[0]
    mid = glow.get_at((size // 2, size // 2 + size // 4))[0]
    assert centre > mid, "premultiplied glow does not fall off in RGB"

    plain = make_radial_alpha(size, (255, 255, 255), max_alpha=255, falloff=2.0)
    assert plain.get_at((size // 2, size // 2 + size // 4))[0] == 255, \
        "plain glow should keep flat RGB and fade in alpha"


@pytest.fixture(scope="module")
def game():
    g = Game()
    yield g
    pygame.quit()


def _step(g, frames=1, dt=1 / 60):
    for _ in range(frames):
        g.fx.update(dt)
        g._update(dt)
        g.renderer.draw()


def _frame_stats(surface):
    """Mean brightness of the rendered frame, sampled on a coarse grid."""
    w, h = surface.get_size()
    px = [surface.get_at((x, y))[:3]
          for x in range(0, w, 40) for y in range(0, h, 40)]
    return sum(sum(p) / 3 for p in px) / len(px)


@pytest.mark.parametrize("screen", list(GameScreen))
def test_every_screen_renders(game, screen):
    game.state.screen = screen
    game.renderer._last_screen = None
    _step(game, 3)

    brightness = _frame_stats(game.fx.world)
    # Not a black frame (backdrop and stars are always drawn) and not blown out
    # to white by the bloom/flash passes.
    assert 1.0 < brightness < 240.0, f"{screen.name}: brightness {brightness:.1f}"


def test_hitbox_collide_ignores_the_bolt_tail():
    """Shots carry a tail in their sprite image; only the head may collide."""
    shot = Shot(100, 300)
    assert shot.rect.height > shot.hitbox.height  # tail is inside the image

    class Box(pygame.sprite.Sprite):
        def __init__(self, rect):
            super().__init__()
            self.rect = pygame.Rect(rect)

    head = Box((90, shot.hitbox.top, 20, 4))
    tail_only = Box((90, shot.rect.bottom - 4, 20, 4))

    assert hitbox_collide(shot, head)
    assert shot.rect.colliderect(tail_only.rect)      # the image overlaps...
    assert not hitbox_collide(shot, tail_only)        # ...but the bolt does not


def test_shot_destroys_enemy_and_scores(game):
    game.state.screen = GameScreen.PLAYING
    game.state.difficulty = 2
    game.state.score = 0
    game.state.reset_multiplier()

    for group in (game.enemy_group, game.shot_group, game.bonus_group):
        group.empty()

    enemy = Enemy(game.assets.images["enemy"], game.state.difficulty)
    enemy.rect.center = (400, 300)
    game.all_sprites.add(enemy)
    game.enemy_group.add(enemy)

    shot = Shot(400, 300 + Shot.bolt_size[1] // 2)
    game.all_sprites.add(shot)
    game.shot_group.add(shot)

    game._handle_shot_enemy_collisions()

    assert enemy not in game.enemy_group, "enemy survived a direct hit"
    assert game.state.score > 0
    assert len(game.enemy_group) == 1, "destroyed enemy was not replaced"
    assert game.fx.trauma > 0, "kill did not shake the camera"
    assert game.hitstop > 0, "kill did not trigger hitstop"


def test_hitstop_freezes_the_simulation(game):
    game.state.screen = GameScreen.PLAYING
    game.hitstop = 0.0
    _step(game, 2)

    enemy = next(iter(game.enemy_group))
    before = enemy.rect.y

    game.hitstop = 0.1
    # Mirrors run(): while hitstop is active the sim advances with dt == 0.
    game.hitstop = max(0.0, game.hitstop - 1 / 60)
    game._update(0.0)
    assert enemy.rect.y == before, "sprites moved during hitstop"

    game.hitstop = 0.0
    game._update(1 / 60)
    assert enemy.rect.y != before, "sprites stayed frozen after hitstop ended"
