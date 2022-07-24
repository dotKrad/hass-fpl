"""Constants for fpl."""
#
DEBUG = True


# Base component constants
NAME = "FPL Integration"
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
]
ISSUE_URL = "https://github.com/dotKrad/hass-fpl/issues"
ATTRIBUTION = "Data provided by FPL."

# Platforms
BINARY_SENSOR = "binary_sensor"
SENSOR = "sensor"
SWITCH = "switch"
PLATFORMS = [SENSOR]

# Device classes
BINARY_SENSOR_DEVICE_CLASS = "connectivity"

# Defaults
DEFAULT_NAME = DOMAIN


STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""

DEFAULT_CONF_USERNAME = ""
DEFAULT_CONF_PASSWORD = ""
