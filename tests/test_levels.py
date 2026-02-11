"""Tests for level requirements."""

from space_invaders.systems.levels import set_level_requirements


def test_level_1():
    reqs = set_level_requirements(1)
    assert reqs["target_score"] == 100
    assert reqs["enemy_count"] == 3
    assert reqs["strong_enemy_count"] == 0


def test_level_5():
    reqs = set_level_requirements(5)
    assert reqs["target_score"] == 300
    assert reqs["enemy_count"] == 5
    assert reqs["strong_enemy_count"] == 1


def test_level_scaling():
    reqs_10 = set_level_requirements(10)
    reqs_20 = set_level_requirements(20)
    assert reqs_20["target_score"] > reqs_10["target_score"]


def test_high_levels_cap_enemies():
    reqs = set_level_requirements(100)
    assert reqs["enemy_count"] <= 8
