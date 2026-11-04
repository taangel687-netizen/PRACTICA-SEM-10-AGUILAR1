"""Paquete models: Contiene las entidades y jerarquías POO del dominio."""

from models.producto import DescuentoMixin, Electronico, Libro, Producto

__all__ = [
    "Producto",
    "Electronico",
    "Libro",
    "DescuentoMixin",
]

