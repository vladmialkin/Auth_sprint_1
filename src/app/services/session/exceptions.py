class SessionServiceError(Exception):
    pass


class NotAuthenticatedError(SessionServiceError):
    pass


class UserNotFoundError(SessionServiceError):
    pass
