"""Constants for the CCEI BRiO WiL integration."""

DOMAIN = "brio_wil"

BRIO_PORT = 30302

# Positions in the raw TCP status string
POS_STATE = (33, 34)
POS_MODE = (64, 66)
POS_SPEED = 70
POS_BRIGHTNESS = 71
SPEED_OFFSET = 0xC

# Default polling / retry (seconds)
DEFAULT_POLL_INTERVAL = 600
DEFAULT_RETRY_INTERVAL = 60
DEFAULT_MAX_RETRY_INTERVAL = 3600

CONF_POLL_INTERVAL = "poll_interval"
CONF_RETRY_INTERVAL = "retry_interval"
CONF_MAX_RETRY_INTERVAL = "max_retry_interval"

MODES: dict[int, str] = {
    0: "Warm white", 1: "White", 2: "Blue", 3: "Lagoon", 4: "Cyan",
    5: "Purple", 6: "Magenta", 7: "Pink", 8: "Red", 9: "Orange",
    10: "Green", 16: "Gradient", 17: "Rainbow", 18: "Parade",
    19: "Techno", 20: "Horizon", 21: "Hazard", 22: "Magical",
}
MODE_BY_NAME: dict[str, int] = {v: k for k, v in MODES.items()}

SPEED_LEVELS: dict[int, str] = {0: "Slow", 1: "Medium", 2: "Fast"}
SPEED_BY_NAME: dict[str, int] = {v: k for k, v in SPEED_LEVELS.items()}
