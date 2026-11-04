"""Menú del sistema de gestión de productos."""

from models.producto import Electronico, Libro, Producto
from utils.exceptions import NotFoundError, ValidationError
from utils.validators import (
    sanitizar_texto,
    validar_entero_no_negativo,
    validar_positivo_float,
)


def leer_datos_producto() -> tuple[str, float, int]:
    """Solicita y valida los campos comunes de un producto."""
    nombre = sanitizar_texto(input("Nombre: "))
    precio = validar_positivo_float(input("Precio base (S/): "))
    stock = validar_entero_no_negativo(input("Stock: "))
    return nombre, precio, stock


def buscar_producto(inventario: dict[str, Producto], id_prod: str) -> Producto:
    """Busca un producto por su identificador."""
    try:
        return inventario[id_prod]
    except KeyError as error:
        raise NotFoundError(f"No existe un producto con ID {id_prod}.") from error


def listar_productos(inventario: dict[str, Producto]) -> str:
    """Muestra los productos con el precio final de cada tipo."""
    if not inventario:
        return "El inventario está vacío."
    return "\n".join(
        f"ID {id_prod} | {producto} | Precio final: S/ "
        f"{producto.calcular_precio_final():.2f}"
        for id_prod, producto in inventario.items()
    )


def main() -> None:
    """Ejecuta el menú interactivo hasta que el usuario decida salir."""
    inventario: dict[str, Producto] = {}

    while True:
        print(
            "=== GESTIÓN DE PRODUCTOS ===\n"
            "1. Registrar electrónico\n"
            "2. Registrar libro\n"
            "3. Listar productos y precios finales\n"
            "4. Buscar producto / actualizar stock\n"
            "5. Salir"
        )
        try:
            match input("Opción: ").strip():
                case "1":
                    id_prod = str(len(inventario) + 1)
                    nombre, precio, stock = leer_datos_producto()
                    garantia = validar_entero_no_negativo(input("Garantía (meses): "))
                    inventario[id_prod] = Electronico(
                        id_prod, nombre, precio, stock, garantia
                    )
                    mensaje = f"Electrónico registrado con ID {id_prod}."
                case "2":
                    id_prod = str(len(inventario) + 1)
                    nombre, precio, stock = leer_datos_producto()
                    autor = sanitizar_texto(input("Autor: "))
                    inventario[id_prod] = Libro(id_prod, nombre, precio, stock, autor)
                    mensaje = f"Libro registrado con ID {id_prod}."
                case "3":
                    mensaje = listar_productos(inventario)
                case "4":
                    id_prod = sanitizar_texto(input("ID del producto: "))
                    producto = buscar_producto(inventario, id_prod)
                    print(producto)
                    nuevo_stock = input("Nuevo stock (Enter para solo consultar): ")
                    if nuevo_stock.strip():
                        producto.stock = validar_entero_no_negativo(nuevo_stock)
                        mensaje = f"Stock actualizado a {producto.stock}."
                    else:
                        mensaje = "Consulta completada."
                case "5":
                    print("Cerrando sistema.")
                    break
                case _:
                    raise ValidationError("Selecciona una opción del 1 al 5.")
        except (ValidationError, NotFoundError) as error:
            print(f"{type(error).__name__}: {error}")
        except (EOFError, KeyboardInterrupt):
            print("\nCerrando sistema.")
            break
        else:
            print(mensaje)
        finally:
            print()


if __name__ == "__main__":
    main()
