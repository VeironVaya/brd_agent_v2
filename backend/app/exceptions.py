"""Domain exceptions. Services raise these; middleware/error_handler.py
turns them into the {error, message} JSON shape api_contract.md documents
per endpoint, so controllers never hand-write error responses."""


class DomainError(Exception):
    status_code: int = 400
    error: str = "error"

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotFoundError(DomainError):
    status_code = 404
    error = "not_found"


class TitleRequiredError(DomainError):
    status_code = 400
    error = "title_required"


class EmailTakenError(DomainError):
    status_code = 400
    error = "email_taken"


class InvalidRegistrationError(DomainError):
    status_code = 400
    error = "invalid_registration"


class InvalidCredentialsError(DomainError):
    status_code = 401
    error = "invalid_credentials"


class GenerationFailedError(DomainError):
    status_code = 500
    error = "generation_failed"


class ForbiddenError(DomainError):
    status_code = 403
    error = "forbidden"


class CannotShareWithSelfError(DomainError):
    status_code = 400
    error = "cannot_share_with_self"


class AlreadySharedError(DomainError):
    status_code = 400
    error = "already_shared"


class InvalidRoleError(DomainError):
    status_code = 400
    error = "invalid_role"


class InvalidChoiceDataError(DomainError):
    status_code = 400
    error = "invalid_choice_data"
