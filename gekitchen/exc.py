"""Exceptions for GE Kitchen Appliances"""


class GeException(Exception):
    """Base exception for GE Appliance errors"""


class UnknownErdCode(ValueError, GeException):
    """Invalid ERD Code"""


class GeAuthError(RuntimeError, GeException):
    """Failed to authenticate"""


class GeNotAuthedError(RuntimeError, GeException):
    """Not authenticated"""
