class DomainError(Exception):
    """Base class for expected domain failures."""


class UnsupportedCountryError(ValueError, DomainError):
    """Raised when a country is not represented by local policy data."""

