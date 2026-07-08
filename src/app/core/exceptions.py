class BaseDomainException(Exception):
    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


class NotFoundException(BaseDomainException):
    _spanish_entity_messages = {
        "Store": "Tienda no encontrada.",
        "Store for Owner": "Tienda no encontrada.",
        "StoreOrder": "Pedido no encontrado.",
        "Order": "Pedido no encontrado.",
        "Product": "Producto no encontrado.",
        "Category": "Categoría no encontrada.",
        "User": "Usuario no encontrado.",
        "ProductVariant": "Variante no encontrada.",
        "ProductImage": "Imagen no encontrada.",
        "Notification": "Notificación no encontrada.",
        "Cart": "Carrito no encontrado.",
        "OrderItem": "Item de pedido no encontrado.",
    }

    def __init__(self, entity: str, identifier: str | None = None):
        self.entity = entity
        self.identifier = identifier
        detail = self._spanish_entity_messages.get(entity, "Recurso no encontrado.")
        super().__init__(detail)


class ConflictException(BaseDomainException):
    def __init__(self, detail: str):
        super().__init__(detail)


class ForbiddenException(BaseDomainException):
    def __init__(self, detail: str = "Operación no permitida"):
        super().__init__(detail)


class AuthenticationException(BaseDomainException):
    def __init__(self, detail: str = "No se pudo validar las credenciales."):
        super().__init__(detail)


class UnauthorizedException(AuthenticationException):
    def __init__(self, detail: str = "No se pudo validar las credenciales."):
        super().__init__(detail)


class ValidationException(BaseDomainException):
    def __init__(self, field_errors: dict[str, str]):
        self.field_errors = field_errors
        super().__init__("Error de validación")


class InvalidImageUrlError(BaseDomainException):
    def __init__(self, detail: str = "La URL de imagen no está en el host permitido"):
        super().__init__(detail)


class ServiceUnavailableException(BaseDomainException):
    def __init__(self, detail: str = "El servicio no está disponible en este momento."):
        super().__init__(detail)
