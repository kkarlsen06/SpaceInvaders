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

## Project Structure

```
src/space_invaders/
    __main__.py          # Entry point
    constants.py         # All game constants and difficulty config
    config.py            # Configuration and high-score persistence
    state.py             # GameState dataclass and GameScreen enum
    game.py              # Main Game class with game loop
    entities/            # Game entities (Player, Enemy, Shot, etc.)
    systems/             # Game systems (AssetManager, InputHandler, Renderer, etc.)
    ui/                  # UI rendering (Menu, HUD, Dialogs)
```

## Testing

```bash
pip install pytest
pytest tests/
```

## Credits

This game was created as a fun project to learn Python and Pygame.
