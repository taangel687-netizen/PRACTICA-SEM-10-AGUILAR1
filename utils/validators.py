"""Validadores para las entradas del menú."""

from math import isfinite

from .exceptions import ValidationError


def sanitizar_texto(texto: str) -> str:
    """Elimina espacios sobrantes y rechaza el texto vacío."""
    valor = " ".join(texto.split())
    if not valor:
        raise ValidationError("El texto no puede estar vacío.")
    return valor


def validar_positivo_float(val: str) -> float:
    """Convierte la entrada a un número finito mayor que cero."""
    try:
        numero = float(val.strip().replace(",", "."))
    except ValueError as error:
        raise ValidationError("Ingresa un precio numérico.") from error
    if not isfinite(numero) or numero <= 0:
        raise ValidationError("El precio debe ser finito y mayor que cero.")
    return numero


def validar_entero_no_negativo(val: str) -> int:
    """Convierte la entrada a un entero mayor o igual que cero."""
    try:
        numero = int(val.strip())
    except ValueError as error:
        raise ValidationError("Ingresa un número entero.") from error
    if numero < 0:
        raise ValidationError("El número debe ser mayor o igual que cero.")
    return numero
