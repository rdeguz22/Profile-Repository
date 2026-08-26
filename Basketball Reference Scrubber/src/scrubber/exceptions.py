class ScrubberError(Exception):
    """Base class for all foundation errors."""


class PlayerNotFoundError(ScrubberError):
    pass


class TeamNotFoundError(ScrubberError):
    pass


class NBAApiError(ScrubberError):
    pass


class QueryError(ScrubberError):
    pass
