class DomainError(Exception):
    """Base domain error."""


class ValidationError(DomainError):
    """Raised when a request violates domain invariants."""


class AlreadyClaimedError(DomainError):
    """Raised when a question claim has already been taken."""
