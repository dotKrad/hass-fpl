"""Constants for fpl."""
# Base component constants
DOMAIN = "fpl"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.0.1"
PLATFORMS = ["sensor"]
REQUIRED_FILES = [
    ".translations/en.json",
    "binary_sensor.py",
    "const.py",
    "config_flow.py",
    "manifest.json",
    "sensor.py",
    "switch.py",
]
ISSUE_URL = "https://github.com/dotKrad/hass-fpl/issues"
ATTRIBUTION = "Data from this is provided by FPL."

# Icons
ICON = "mdi:flash"

# Device classes
BINARY_SENSOR_DEVICE_CLASS = "connectivity"

# Configuration
CONF_BINARY_SENSOR = "binary_sensor"
CONF_SENSOR = "sensor"
CONF_SWITCH = "switch"
CONF_ENABLED = "enabled"
CONF_NAME = "name"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"

# Defaults
DEFAULT_NAME = DOMAIN
