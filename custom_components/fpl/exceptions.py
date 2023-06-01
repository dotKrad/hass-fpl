"""exceptions file"""


class WarrantException(Exception):
    """Base class for all Warrant exceptions"""


class ForceChangePasswordException(WarrantException):
    """Raised when the user is forced to change their password"""


class TokenVerificationException(WarrantException):
    """Raised when token verification fails."""


class NoTerrytoryAvailableException(Exception):
    """Thrown when not possible to determine user territory"""
