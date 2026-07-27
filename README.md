# Space Invaders Game

A classic Space Invaders game implemented in Python using Pygame.

## Running the Game

Create a virtual environment and install in development mode:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Run the game:

```bash
python -m space_invaders
# or use the installed command:
space-invaders
```

## Controls

- **Left Arrow / A**: Move left
- **Right Arrow / D**: Move right
- **Space / W / Up Arrow**: Shoot
- **1 / 2 / 3**: Switch weapons (Laser / Shotgun / Electric Whip)
- **F**: Toggle Fullscreen
- **ESC**: Pause/Quit the current game
- **Enter**: Confirm selection

## Game Modes

- **Normal Mode**: Choose from Easy, Medium, Hard, or Impossible difficulty
- **Level Mode**: Progress through increasingly difficult levels

## Features

- Varied enemies with different health points
- Score multiplier system
- Weapon upgrades (Shotgun at level 5+, Electric Whip at level 10+)
- Power-ups (extra lives)
- High score tracking per difficulty and level
- Mouse control support (toggle in Settings)
- Fullscreen mode

## Presentation

The game renders at 1280x720 into an offscreen surface, which
`systems/postfx.py` composites onto the display with a post-processing chain:

- **Bloom** — thresholded at full resolution, then blurred with a two-step
  down/up scale and added back. Thresholding *before* the downscale is what
  keeps thin bright things (lasers, star cores) glowing.
- **Vignette**, built once at 128px and scaled up.
- **Screen shake** — "trauma" that decays over time; offset scales with trauma
  squared, driven by two incommensurable sine frequencies per axis.
- **Chromatic aberration** — the red channel splits from green+blue during
  impacts, recombining losslessly at rest.
- **Impact flash** — brief additive full-screen tint.

Hits also trigger **hitstop**: a few frames where the simulation runs at
`dt == 0` while rendering continues.

Two performance notes, both load-bearing:

- `Surface.fill()` with a blend flag takes an unaccelerated path in SDL (~3ms at
  720p). Blitting a cached solid surface with the same flag is ~40x faster, so
  every full-screen blend op goes through a scratch surface.
- Additive blends ignore the alpha channel, so glows built for additive use bake
  their falloff into RGB (`make_radial_alpha(premultiplied=True)`). Without
  that, every glow renders as a flat disc.

Projectiles carry a motion tail inside their sprite image, so their `rect` is
larger than the projectile. Collision therefore runs through `hitbox_collide`,
which prefers a sprite's tight `hitbox` over its `rect`.

## Project Structure

```
src/space_invaders/
    __main__.py          # Entry point
    constants.py         # All game constants and difficulty config
    config.py            # Configuration and high-score persistence
    state.py             # GameState dataclass and GameScreen enum
    game.py              # Main Game class with game loop
    entities/            # Game entities (Player, Enemy, Shot, etc.)
    systems/             # Game systems (AssetManager, PostFX, Renderer, etc.)
    ui/                  # UI rendering (Menu, HUD, Dialogs)
```

## Testing

```bash
pip install pytest
pytest
```

`tests/test_smoke.py` boots the real game against SDL's dummy video/audio
drivers, renders every screen and plays a kill through, so the render chain and
collision wiring are covered without a display.

## Credits

This game was created as a fun project to learn Python and Pygame.
