"""Tests for the scoring system."""

from space_invaders.state import GameState
from space_invaders.constants import MAX_MULTIPLIER


def test_multiplier_increases():
    state = GameState()
    state.increase_multiplier()
    assert state.score_multiplier == 1.1
    assert state.consecutive_hits == 1


def test_multiplier_caps_at_max():
    state = GameState()
    for _ in range(100):
        state.increase_multiplier()
    assert state.score_multiplier == MAX_MULTIPLIER


def test_reset_multiplier():
    state = GameState()
    state.increase_multiplier()
    state.increase_multiplier()
    state.reset_multiplier()
    assert state.score_multiplier == 1.0
    assert state.consecutive_hits == 0


def test_reset_for_new_game():
    state = GameState()
    state.score = 500
    state.score_multiplier = 3.5
    state.consecutive_hits = 25
    state.reset_for_new_game()
    assert state.score == 0
    assert state.score_multiplier == 1.0
    assert state.consecutive_hits == 0
