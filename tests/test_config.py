"""Tests for configuration persistence."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from space_invaders.config import (
    DEFAULT_CONFIG,
    DEFAULT_HIGH_SCORES,
    load_config,
    load_high_scores,
    save_config,
    save_high_scores,
)


def test_load_config_creates_default():
    with tempfile.TemporaryDirectory() as tmp:
        cfg_path = Path(tmp) / "test_config.json"
        with patch("space_invaders.config.CONFIG_FILE", cfg_path):
            config = load_config()
            assert config["unlock_impossible"] is False
            assert config["max_level_reached"] == 1
            assert cfg_path.exists()


def test_save_and_load_config():
    with tempfile.TemporaryDirectory() as tmp:
        cfg_path = Path(tmp) / "test_config.json"
        with patch("space_invaders.config.CONFIG_FILE", cfg_path):
            config = load_config()
            config["max_level_reached"] = 5
            save_config(config)

            reloaded = load_config()
            assert reloaded["max_level_reached"] == 5


def test_load_high_scores_creates_default():
    with tempfile.TemporaryDirectory() as tmp:
        hs_path = Path(tmp) / "test_hs.json"
        with patch("space_invaders.config.HIGH_SCORE_FILE", hs_path):
            scores = load_high_scores()
            assert scores["easy"] == 0
            assert isinstance(scores["level_mode"], dict)
            assert hs_path.exists()


def test_save_and_load_high_scores():
    with tempfile.TemporaryDirectory() as tmp:
        hs_path = Path(tmp) / "test_hs.json"
        with patch("space_invaders.config.HIGH_SCORE_FILE", hs_path):
            scores = load_high_scores()
            scores["easy"] = 999
            save_high_scores(scores)

            reloaded = load_high_scores()
            assert reloaded["easy"] == 999


def test_load_config_handles_corrupt_json():
    with tempfile.TemporaryDirectory() as tmp:
        cfg_path = Path(tmp) / "test_config.json"
        cfg_path.write_text("{not valid json}")
        with patch("space_invaders.config.CONFIG_FILE", cfg_path):
            config = load_config()
            # Should fallback to defaults
            assert config["unlock_impossible"] is False
