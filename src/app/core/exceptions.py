class NotFoundException(Exception):
    def __init__(self, entity: str, identifier: str | None = None):
        self.entity = entity
        self.identifier = identifier
        detail = f"{entity} not found"
        if identifier:
            detail = f"{entity} with id '{identifier}' not found"
        super().__init__(detail)


class ConflictException(Exception):
    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


class ForbiddenException(Exception):
    def __init__(self, detail: str = "Operation not permitted"):
        self.detail = detail
        super().__init__(detail)


class AuthenticationException(Exception):
    def __init__(self, detail: str = "Could not validate credentials"):
        self.detail = detail
        super().__init__(detail)
