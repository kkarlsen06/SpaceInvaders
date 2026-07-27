"""Centralized asset loading and management."""

from __future__ import annotations

import math
import random
from pathlib import Path

import pygame

from space_invaders.constants import SCREEN_HEIGHT, SCREEN_WIDTH


class AssetManager:
    """Loads and caches all game assets (images, sounds, fonts)."""

    def __init__(self, assets_dir: Path | str) -> None:
        self.assets_dir = Path(assets_dir)
        self.images: dict[str, pygame.Surface] = {}
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self.fonts: dict[str, pygame.font.Font] = {}

    def load_all(self) -> None:
        """Load all game assets. Must be called after pygame.init()."""
        self._load_images()
        self._load_sounds()
        self._load_fonts()

    # ------------------------------------------------------------------
    # Images
    # ------------------------------------------------------------------

    def _load_images(self) -> None:
        image_files = {
            "player": "spiller.png",
            "player2": "spiller2.png",
            "player3": "spiller3.png",
            "player4": "spiller4.png",
            "enemy": "fiende.png",
            "strong_enemy": "sterk_fiende.png",
            "life": "liv.png",
        }
        for key, filename in image_files.items():
            path = self.assets_dir / filename
            self.images[key] = pygame.image.load(str(path)).convert_alpha()

        bg_path = self.assets_dir / "background.jpg"
        try:
            bg = pygame.image.load(str(bg_path)).convert_alpha()
            # Cover-fit, not stretch: the art is 4:3 and the screen is 16:9.
            scale = max(SCREEN_WIDTH / bg.get_width(), SCREEN_HEIGHT / bg.get_height())
            scaled = pygame.transform.smoothscale(
                bg, (round(bg.get_width() * scale), round(bg.get_height() * scale)))
            cropped = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            cropped.blit(scaled, scaled.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))
            # Let the nebula backdrop and stars show through the artwork.
            cropped.set_alpha(150)
            self.images["background"] = cropped
        except (pygame.error, FileNotFoundError) as e:
            print(f"Could not load background image: {e}")

    # ------------------------------------------------------------------
    # Sounds
    # ------------------------------------------------------------------

    def _load_sounds(self) -> None:
        sound_map = {
            "shoot": "thock.wav",
            "explosion": "eksplosjon.wav",
            "theme": "theme_song.wav",
            "life": "life.wav",
        }
        for key, filename in sound_map.items():
            path = self.assets_dir / filename
            try:
                self.sounds[key] = pygame.mixer.Sound(str(path))
            except (pygame.error, FileNotFoundError) as e:
                print(f"Could not load sound {filename}: {e}")
                self.sounds[key] = self._generate_fallback(key)

        # Bonus sound is always procedural
        self.sounds["bonus"] = self._generate_bonus_sound()

    @staticmethod
    def _generate_fallback(key: str) -> pygame.mixer.Sound:
        generators = {
            "shoot": AssetManager._generate_shoot_sound,
            "explosion": AssetManager._generate_explosion_sound,
            "life": AssetManager._generate_bonus_sound,
            "theme": lambda: pygame.mixer.Sound(bytearray([127] * 4000)),
        }
        return generators.get(key, lambda: pygame.mixer.Sound(bytearray([127] * 4000)))()

    @staticmethod
    def _generate_explosion_sound() -> pygame.mixer.Sound:
        buf = bytearray()
        for i in range(12000):
            amp = max(0, 1 - i / 10000)
            buf.append(int(127 + amp * 127 * random.uniform(-1, 1)))
        return pygame.mixer.Sound(buf)

    @staticmethod
    def _generate_bonus_sound() -> pygame.mixer.Sound:
        buf = bytearray()
        for i in range(8000):
            freq = 300 + i / 20
            buf.append(int(127 + 127 * 0.8 * math.sin(freq * i / 1000)))
        return pygame.mixer.Sound(buf)

    @staticmethod
    def _generate_shoot_sound() -> pygame.mixer.Sound:
        buf = bytearray()
        for i in range(4000):
            buf.append(int(127 + 127 * max(0, 1 - i / 1000) * (0.8 if i % 8 < 4 else -0.8)))
        return pygame.mixer.Sound(buf)

    # ------------------------------------------------------------------
    # Fonts
    # ------------------------------------------------------------------

    def _load_fonts(self) -> None:
        from space_invaders.constants import FONT_SIZES

        font_path = self.assets_dir / "nasalization-rg.ttf"
        try:
            if font_path.exists():
                for name, size in FONT_SIZES.items():
                    self.fonts[name] = pygame.font.Font(str(font_path), size)
            else:
                raise FileNotFoundError(f"Font not found: {font_path}")
        except (FileNotFoundError, pygame.error):
            for name, size in FONT_SIZES.items():
                self.fonts[name] = pygame.font.SysFont("arial", size)

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def apply_volumes(self, sound_volume: float, music_volume: float) -> None:
        """Set volume levels on all loaded sounds."""
        self.sounds["shoot"].set_volume(sound_volume * 0.8)
        self.sounds["explosion"].set_volume(sound_volume * 1.2)
        self.sounds["life"].set_volume(sound_volume)
        self.sounds["bonus"].set_volume(sound_volume)
        self.sounds["theme"].set_volume(music_volume)

    @property
    def skin_images(self) -> tuple[pygame.Surface, ...]:
        """Return the player skin images as a tuple."""
        return (
            self.images["player"],
            self.images["player2"],
            self.images["player3"],
            self.images["player4"],
        )
