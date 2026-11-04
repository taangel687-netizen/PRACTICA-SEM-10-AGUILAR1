"""Excepciones del sistema de gestión de productos."""


class GestionProductosError(Exception):
    """Error del dominio de productos."""


class ValidationError(GestionProductosError):
    """Dato inválido."""


class NotFoundError(GestionProductosError):
    """Producto inexistente."""
