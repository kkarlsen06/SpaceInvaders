"""Game constants and configuration values."""

# Screen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Legacy colors (kept for entity/effect code)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 23, 68)
CYAN = (0, 255, 255)
BLUE = (0, 123, 255)
ORANGE = (255, 165, 0)
GOLD = (255, 215, 0)


# ---------------------------------------------------------------------------
# Modern UI Color Palette
# ---------------------------------------------------------------------------

class Colors:
    """Semantic color palette for the modern UI."""

    # Backgrounds
    BG_DEEP       = (8, 10, 18)
    BG_PRIMARY    = (14, 17, 30)
    BG_CARD       = (20, 24, 42)
    BG_CARD_HOVER = (28, 33, 55)
    BG_OVERLAY    = (8, 10, 18, 200)

    # Borders
    BORDER_SUBTLE = (40, 45, 70)
    BORDER_MEDIUM = (55, 62, 95)
    BORDER_BRIGHT = (80, 90, 130)

    # Primary accent: Teal/Cyan
    PRIMARY       = (0, 210, 210)
    PRIMARY_LIGHT = (80, 235, 235)
    PRIMARY_DIM   = (0, 140, 140)
    PRIMARY_GLOW  = (0, 210, 210, 60)

    # Secondary accent: Amber/Gold
    SECONDARY       = (255, 195, 50)
    SECONDARY_LIGHT = (255, 220, 100)
    SECONDARY_DIM   = (180, 140, 30)

    # Difficulty tiers
    EASY          = (100, 220, 180)
    EASY_BG       = (20, 50, 40)
    MEDIUM        = (220, 200, 100)
    MEDIUM_BG     = (50, 45, 20)
    HARD          = (230, 90, 90)
    HARD_BG       = (55, 20, 20)
    IMPOSSIBLE    = (180, 120, 255)
    IMPOSSIBLE_BG = (40, 25, 60)
    LEVEL         = (170, 130, 255)
    LEVEL_BG      = (35, 25, 55)

    # Text
    TEXT_PRIMARY   = (240, 240, 250)
    TEXT_SECONDARY = (160, 165, 190)
    TEXT_MUTED     = (100, 105, 130)
    TEXT_SHADOW    = (0, 0, 0)

    # Semantic
    SUCCESS       = (60, 210, 120)
    DANGER        = (255, 60, 80)
    LOCKED        = (80, 80, 95)
    LOCKED_TEXT   = (110, 110, 125)

    # Whip charge
    WHIP_CHARGING = (230, 70, 70)
    WHIP_READY    = (255, 100, 100)

    # Glow / accent effects
    GLOW_PRIMARY    = (0, 210, 210, 40)
    GLOW_SECONDARY  = (255, 195, 50, 40)
    GLOW_DANGER     = (255, 60, 80, 40)
    GLOW_SUCCESS    = (60, 210, 120, 40)

    # Gradient bar accents
    ACCENT_LINE_TOP    = (0, 180, 200, 120)
    ACCENT_LINE_BOTTOM = (0, 180, 200, 80)

    # Star colors (subtle tints for depth)
    STAR_WARM   = (255, 240, 220)
    STAR_COOL   = (200, 220, 255)
    STAR_BLUE   = (160, 200, 255)
    STAR_WHITE  = (240, 240, 255)

    # Explosion palette
    EXPLOSION_CORE  = (255, 255, 200)
    EXPLOSION_MID   = (255, 160, 40)
    EXPLOSION_OUTER = (255, 80, 20)
    EXPLOSION_RING  = (255, 200, 100, 100)


# Backwards-compatible pastel mapping
PASTEL_COLORS = {
    "easy": Colors.EASY,
    "medium": Colors.MEDIUM,
    "hard": Colors.HARD,
    "impossible": Colors.IMPOSSIBLE,
    "level": Colors.LEVEL,
}

# Font sizes
FONT_SIZES = {
    "tiny": 13,
    "small": 18,
    "medium": 24,
    "large": 36,
    "xlarge": 48,
    "title": 56,
}

# Player
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 40
PLAYER_SPEED = 8
PLAYER_START_LIVES = 3
SHOT_COOLDOWN_MS = 150
MOUSE_SPEED_FACTOR = 0.5

# Shots
SHOT_WIDTH = 5
SHOT_HEIGHT = 15
SHOT_SPEED_EASY = -30
SHOT_SPEED_NORMAL = -10
SHOTGUN_PELLET_ANGLES = [-45, -30, -15, 0, 15, 30, 45]
SHOTGUN_RANGE = 200
SHOTGUN_PELLET_WIDTH = 4
SHOTGUN_PELLET_HEIGHT = 10
SHOTGUN_HORIZONTAL_SPEED_FACTOR = 5
SHOTGUN_SPEED_EASY = -20
SHOTGUN_SPEED_NORMAL = -8

# Enemies
ENEMY_BASE_SIZE = 40
ENEMY_MIN_SCALE = 0.7
ENEMY_MAX_SCALE = 1.2
STRONG_ENEMY_BASE_SIZE = 50
STRONG_ENEMY_MIN_SCALE = 0.8
STRONG_ENEMY_MAX_SCALE = 1.3
ENEMY_PROJECTILE_SPEED = 7
ENEMY_PROJECTILE_WIDTH = 6
ENEMY_PROJECTILE_HEIGHT = 15
ENEMY_SHOOT_PROBABILITY = 0.01
STRONG_ENEMY_SHOOT_PROBABILITY = 0.1
ENEMY_SHOT_DELAY_MIN = 3000
ENEMY_SHOT_DELAY_MAX = 8000

# Scoring
NORMAL_ENEMY_POINTS = 10
STRONG_ENEMY_POINTS = 25
MAX_MULTIPLIER = 5.0
MULTIPLIER_INCREMENT = 0.1

# Electric whip
WHIP_CHARGE_THRESHOLD = 1000
WHIP_ANGULAR_SPEED = 6
WHIP_HIT_ANGLE_TOLERANCE = 15
WHIP_PARTICLE_COUNT = 20
WHIP_LINE_THICKNESS = 5
WHIP_GLOW_THICKNESS = 8
WHIP_OUTER_GLOW_THICKNESS = 12

# Power bonus
BONUS_SPAWN_DELAY_MS = 15000
BONUS_SPEED = 3
BONUS_SIZE = 30

# Particles
PARTICLE_SIZE = 4
PARTICLE_LIFETIME = 30
ELECTRICAL_PARTICLE_LIFETIME = 15

# Explosions
EXPLOSION_SIZE = 50
EXPLOSION_FRAMES = 6
EXPLOSION_FRAME_RATE_MS = 50
EXPLOSION_SHRINK_PER_FRAME = 8

# Stars
STAR_COUNT = 150
STAR_MIN_SPEED = 0.5
STAR_MAX_SPEED = 4.0
STAR_MIN_SIZE = 1
STAR_MAX_SIZE = 3

# Skin score thresholds
SKIN_THRESHOLD_2 = 500
SKIN_THRESHOLD_3 = 1000
SKIN_THRESHOLD_4 = 1500

# Weapon unlock levels
SHOTGUN_UNLOCK_LEVEL = 5
WHIP_UNLOCK_LEVEL = 10
IMPOSSIBLE_UNLOCK_SCORE = 1000

# Level selection
LEVELS_PER_PAGE = 9
MAX_LEVEL_PAGES = 5

# Difficulty configuration
DIFFICULTY_CONFIG = {
    1: {
        "name": "Lett",
        "key": "easy",
        "enemy_speed_range": (1, 2),
        "strong_enemy_speed_range": (1, 3),
        "enemy_count": 3,
        "strong_enemy_count": 0,
        "show_aim_line": True,
        "shot_speed": SHOT_SPEED_EASY,
        "shotgun_speed": SHOTGUN_SPEED_EASY,
        "enemies_shoot": False,
    },
    2: {
        "name": "Middels",
        "key": "medium",
        "enemy_speed_range": (1, 3),
        "strong_enemy_speed_range": (1, 3),
        "enemy_count": 4,
        "strong_enemy_count": 1,
        "show_aim_line": True,
        "shot_speed": SHOT_SPEED_NORMAL,
        "shotgun_speed": SHOTGUN_SPEED_NORMAL,
        "enemies_shoot": False,
    },
    3: {
        "name": "Vanskelig",
        "key": "hard",
        "enemy_speed_range": (1, 4),
        "strong_enemy_speed_range": (2, 4),
        "enemy_count": 4,
        "strong_enemy_count": 3,
        "show_aim_line": False,
        "shot_speed": SHOT_SPEED_NORMAL,
        "shotgun_speed": SHOTGUN_SPEED_NORMAL,
        "enemies_shoot": False,
    },
    4: {
        "name": "Umulig",
        "key": "impossible",
        "enemy_speed_range": (1, 4),
        "strong_enemy_speed_range": (2, 5),
        "enemy_count": 5,
        "strong_enemy_count": 5,
        "show_aim_line": False,
        "shot_speed": SHOT_SPEED_NORMAL,
        "shotgun_speed": SHOTGUN_SPEED_NORMAL,
        "enemies_shoot": True,
    },
}

# Help screen
HELP_SCROLL_SPEED = 20
