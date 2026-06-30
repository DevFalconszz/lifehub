class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400, error_type: str = 'app_error'):
        self.message = message
        self.status_code = status_code
        self.error_type = error_type
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, message: str = 'Resource not found'):
        super().__init__(message=message, status_code=404, error_type='not_found')


class UnauthorizedError(AppError):
    def __init__(self, message: str = 'Unauthorized'):
        super().__init__(message=message, status_code=401, error_type='unauthorized')


class ForbiddenError(AppError):
    def __init__(self, message: str = 'Forbidden'):
        super().__init__(message=message, status_code=403, error_type='forbidden')
