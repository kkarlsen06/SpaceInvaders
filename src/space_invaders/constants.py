"""Game constants and configuration values."""

# Screen — 16:9 HD. The game renders to an offscreen surface of this size and
# PostFX presents it to the display.
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
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
    "tiny": 16,
    "small": 22,
    "medium": 29,
    "large": 44,
    "xlarge": 62,
    "title": 76,
}

# Player
PLAYER_WIDTH = 64
PLAYER_HEIGHT = 52
PLAYER_SPEED = 11
PLAYER_START_LIVES = 3
SHOT_COOLDOWN_MS = 150
MOUSE_SPEED_FACTOR = 0.5

# Shots
SHOT_WIDTH = 6
SHOT_HEIGHT = 22
SHOT_SPEED_EASY = -34
SHOT_SPEED_NORMAL = -13
SHOTGUN_PELLET_ANGLES = [-45, -30, -15, 0, 15, 30, 45]
SHOTGUN_RANGE = 280
SHOTGUN_PELLET_WIDTH = 5
SHOTGUN_PELLET_HEIGHT = 14
SHOTGUN_HORIZONTAL_SPEED_FACTOR = 5
SHOTGUN_SPEED_EASY = -20
SHOTGUN_SPEED_NORMAL = -8

# Enemies
ENEMY_BASE_SIZE = 52
ENEMY_MIN_SCALE = 0.7
ENEMY_MAX_SCALE = 1.2
STRONG_ENEMY_BASE_SIZE = 66
STRONG_ENEMY_MIN_SCALE = 0.8
STRONG_ENEMY_MAX_SCALE = 1.3
ENEMY_PROJECTILE_SPEED = 9
ENEMY_PROJECTILE_WIDTH = 7
ENEMY_PROJECTILE_HEIGHT = 20
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
BONUS_SPEED = 4
BONUS_SIZE = 38

# Particles
PARTICLE_SIZE = 6
PARTICLE_LIFETIME = 30
ELECTRICAL_PARTICLE_LIFETIME = 15

# Explosions
EXPLOSION_SIZE = 66
EXPLOSION_FRAMES = 6
EXPLOSION_FRAME_RATE_MS = 50
EXPLOSION_SHRINK_PER_FRAME = 8

# Stars
STAR_COUNT = 260
STAR_MIN_SPEED = 0.5
STAR_MAX_SPEED = 5.0
STAR_MIN_SIZE = 1
STAR_MAX_SIZE = 3

# ---------------------------------------------------------------------------
# Post-processing & game feel
# ---------------------------------------------------------------------------

# Bloom: world is downscaled by this factor, dark values subtracted, blurred
# by a second down/up pass, then added back. Lower divisor = tighter glow.
BLOOM_DOWNSCALE = 4
BLOOM_THRESHOLD = (70, 70, 70)      # subtracted at full res — keeps bloom on highlights
BLOOM_STRENGTH = 200                # 0-255 scale of the additive bloom pass

VIGNETTE_STRENGTH = 115

# Screen shake: "trauma" 0..1, offset scales with trauma squared.
TRAUMA_DECAY = 1.9                  # per second
TRAUMA_MAX_OFFSET = 22
TRAUMA_SHAKE_FREQ = 34.0
ABERRATION_MAX = 7                  # px of RGB split at full trauma

# Hitstop: brief freeze on impact, in seconds.
HITSTOP_KILL = 0.035
HITSTOP_DEATH = 0.13
HITSTOP_MAX = 0.2

# Score popups
POPUP_LIFETIME = 0.85
POPUP_RISE = 46

# HUD bar heights. The player rests above the bottom bar, so both need this.
HUD_TOP_H = 56
HUD_BOTTOM_H = 66

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
        # Counts scaled with the jump from 800px to 1280px wide so the
        # playfield keeps the same density it had at 4:3.
        "enemy_count": 5,
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
        "enemy_count": 7,
        "strong_enemy_count": 2,
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
        "enemy_count": 7,
        "strong_enemy_count": 5,
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
        "enemy_count": 8,
        "strong_enemy_count": 8,
        "show_aim_line": False,
        "shot_speed": SHOT_SPEED_NORMAL,
        "shotgun_speed": SHOTGUN_SPEED_NORMAL,
        "enemies_shoot": True,
    },
}

# Help screen
HELP_SCROLL_SPEED = 20
