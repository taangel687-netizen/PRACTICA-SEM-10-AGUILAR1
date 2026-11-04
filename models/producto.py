"""Módulo de Modelos del Dominio de Productos.

Define la jerarquía de clases POO para la gestión de productos:
- Producto (Clase base abstracta con encapsulamiento estricto)
- DescuentoMixin (Mixin para herencia múltiple y control de MRO)
- Electronico (Especialización para productos tecnológicos)
- Libro (Especialización para material bibliográfico/editorial)
"""

from abc import ABC, abstractmethod
from typing import Optional

try:
    from utils.exceptions import ValidationError
except ImportError:
    # Fallback temporal si el módulo de utils aún no ha sido integrado
    class ValidationError(Exception):
        """Excepción de validación de datos de dominio."""
        pass


class DescuentoMixin:
    """Mixin que provee funcionalidad de cálculo de promociones y descuentos.
    
    Diseñado para integrarse mediante herencia múltiple sin alterar la
    jerarquía principal de Producto, demostrando linearización C3 (MRO).
    """

    def aplicar_descuento(self, precio_base: float, porcentaje: float) -> float:
        """Calcula el precio resultante tras aplicar un porcentaje de descuento.
        
        Args:
            precio_base (float): Monto original sobre el que se aplica el descuento.
            porcentaje (float): Valor porcentual entre 0.0 y 100.0.
            
        Returns:
            float: Precio con el descuento aplicado.
            
        Raises:
            ValidationError: Si el porcentaje no está en el rango [0.0, 100.0].
        """
        if not (0.0 <= porcentaje <= 100.0):
            raise ValidationError(
                f"El porcentaje de descuento debe estar entre 0 y 100. Recibido: {porcentaje}"
            )
        monto_descuento = precio_base * (porcentaje / 100.0)
        return round(precio_base - monto_descuento, 2)


class Producto(ABC):
    """Clase base abstracta que modela los atributos y comportamientos comunes de un producto.
    
    Implementa encapsulamiento riguroso mediante atributos protegidos y propiedades (@property),
    asegurando la integridad de datos en los setters.
    """

    def __init__(self, id_producto: str, nombre: str, precio: float, stock: int) -> None:
        """Inicializa una nueva instancia de Producto.
        
        Args:
            id_producto (str): Identificador único alfanumérico.
            nombre (str): Nombre descriptivo del producto.
            precio (float): Precio base unitario en moneda local (debe ser > 0).
            stock (int): Cantidad disponible en inventario (debe ser >= 0).
        """
        self._id_producto: str = ""
        self._nombre: str = ""
        self._precio: float = 0.0
        self._stock: int = 0

        # Invocar los setters para ejecutar las validaciones de negocio
        self.id_producto = id_producto
        self.nombre = nombre
        self.precio = precio
        self.stock = stock

    def __del__(self) -> None:
        """Destructor académico para demostrar el ciclo de vida del objeto y recolección de basura."""
        # En Python el cleanup determinista se prefiere con context managers,
        # pero se implementa para cumplir con la consigna de la guía técnica.
        pass

    # --- Propiedad: id_producto ---
    @property
    def id_producto(self) -> str:
        """Getter del identificador único del producto."""
        return self._id_producto

    @id_producto.setter
    def id_producto(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValidationError("El ID del producto no puede estar vacío.")
        self._id_producto = valor.strip()

    # --- Propiedad: nombre ---
    @property
    def nombre(self) -> str:
        """Getter del nombre del producto."""
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValidationError("El nombre del producto no puede estar vacío.")
        if len(valor.strip()) < 2:
            raise ValidationError("El nombre del producto debe tener al menos 2 caracteres.")
        self._nombre = valor.strip()

    # --- Propiedad: precio ---
    @property
    def precio(self) -> float:
        """Getter del precio base del producto."""
        return self._precio

    @precio.setter
    def precio(self, valor: float) -> None:
        try:
            precio_float = float(valor)
        except (ValueError, TypeError):
            raise ValidationError(f"El precio debe ser un número válido. Recibido: {valor}")

        if precio_float <= 0.0:
            raise ValidationError(
                f"El precio debe ser un número estrictamente mayor a 0. Recibido: {precio_float}"
            )
        self._precio = round(precio_float, 2)

    # --- Propiedad: stock ---
    @property
    def stock(self) -> int:
        """Getter del stock disponible en inventario."""
        return self._stock

    @stock.setter
    def stock(self, valor: int) -> None:
        try:
            stock_int = int(valor)
        except (ValueError, TypeError):
            raise ValidationError(f"El stock debe ser un número entero válido. Recibido: {valor}")

        if stock_int < 0:
            raise ValidationError(
                f"El stock no puede ser un valor negativo. Recibido: {stock_int}"
            )
        self._stock = stock_int

    # --- Métodos Polimórficos y Abstractos ---
    @abstractmethod
    def calcular_precio_final(self) -> float:
        """Calcula el precio final de venta al público aplicando reglas de negocio específicas.
        
        Debe ser sobrescrito obligatoriamente por cada subclase (Polimorfismo).
        
        Returns:
            float: Precio final calculado con recargos o beneficios aplicados.
        """
        pass

    def __str__(self) -> str:
        """Representación uniforme y legible en cadena para interfaces de usuario."""
        return (
            f"[{self.__class__.__name__}] ID: {self._id_producto} | "
            f"Nombre: {self._nombre} | Base: S/ {self._precio:.2f} | "
            f"Stock: {self._stock} unids | Precio Final: S/ {self.calcular_precio_final():.2f}"
        )


class Electronico(Producto, DescuentoMixin):
    """Especialización para productos de tecnología electrónica.
    
    Aplica herencia múltiple (Producto + DescuentoMixin) y sobrescribe
    calcular_precio_final() considerando impuesto tecnológico (18% IGV)
    y un costo adicional por meses de garantía extendida.
    """

    TASA_IMPUESTO_TECNOLOGICO: float = 0.18  # 18% IGV / Tasa arancelaria
    COSTO_POR_MES_GARANTIA: float = 5.0      # S/ 5.00 de seguro por mes de garantía

    def __init__(
        self,
        id_producto: str,
        nombre: str,
        precio: float,
        stock: int,
        marca: str,
        garantia_meses: int = 12,
        descuento_promo: float = 0.0,
    ) -> None:
        """Inicializa un producto electrónico invocando al constructor de la clase base con super().
        
        Args:
            id_producto (str): Identificador único.
            nombre (str): Nombre del dispositivo.
            precio (float): Precio base.
            stock (int): Stock en almacén.
            marca (str): Marca del fabricante.
            garantia_meses (int, opcional): Meses de garantía ofrecidos (debe ser >= 0).
            descuento_promo (float, opcional): Descuento especial de fabricante en % (0 a 100).
        """
        super().__init__(id_producto, nombre, precio, stock)
        self._marca: str = ""
        self._garantia_meses: int = 0
        self._descuento_promo: float = 0.0

        self.marca = marca
        self.garantia_meses = garantia_meses
        self.descuento_promo = descuento_promo

    @property
    def marca(self) -> str:
        """Getter de la marca del dispositivo."""
        return self._marca

    @marca.setter
    def marca(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValidationError("La marca del dispositivo no puede estar vacía.")
        self._marca = valor.strip()

    @property
    def garantia_meses(self) -> int:
        """Getter de los meses de garantía."""
        return self._garantia_meses

    @garantia_meses.setter
    def garantia_meses(self, valor: int) -> None:
        try:
            meses_int = int(valor)
        except (ValueError, TypeError):
            raise ValidationError("Los meses de garantía deben ser un entero válido.")
        if meses_int < 0:
            raise ValidationError("Los meses de garantía no pueden ser negativos.")
        self._garantia_meses = meses_int

    @property
    def descuento_promo(self) -> float:
        """Getter del descuento promocional configurado."""
        return self._descuento_promo

    @descuento_promo.setter
    def descuento_promo(self, valor: float) -> None:
        try:
            val_float = float(valor)
        except (ValueError, TypeError):
            raise ValidationError("El descuento promocional debe ser numérico.")
        if not (0.0 <= val_float <= 100.0):
            raise ValidationError("El descuento promocional debe estar entre 0% y 100%.")
        self._descuento_promo = round(val_float, 2)

    def calcular_precio_final(self) -> float:
        """Calcula el precio final del electrónico con impuesto tecnológico y garantía.
        
        Fórmula:
            Base con descuento promocional (vía DescuentoMixin)
            + Impuesto Tecnológico (18% sobre base con descuento)
            + Costo por meses de garantía extendida
            
        Returns:
            float: Precio de venta final redondeado a 2 decimales.
        """
        precio_con_descuento = self.aplicar_descuento(self._precio, self._descuento_promo)
        impuesto = precio_con_descuento * self.TASA_IMPUESTO_TECNOLOGICO
        adicional_garantia = self._garantia_meses * self.COSTO_POR_MES_GARANTIA
        return round(precio_con_descuento + impuesto + adicional_garantia, 2)

    def __str__(self) -> str:
        """Representación detallada de un producto electrónico."""
        base_str = super().__str__()
        return (
            f"{base_str} | Marca: {self._marca} | "
            f"Garantía: {self._garantia_meses} meses | Promo: {self._descuento_promo}%"
        )


class Libro(Producto, DescuentoMixin):
    """Especialización para libros físicos y digitales.
    
    Aplica herencia múltiple (Producto + DescuentoMixin).
    Sobrescribe calcular_precio_final() considerando exención tributaria (0% IGV según ley editorial)
    y un descuento adicional del 15% para ediciones digitales (ahorro en costo de imprenta).
    """

    DESCUENTO_EDICION_DIGITAL: float = 15.0  # 15% de descuento por ser digital (ahorro papel)

    def __init__(
        self,
        id_producto: str,
        nombre: str,
        precio: float,
        stock: int,
        autor: str,
        isbn: str,
        es_digital: bool = False,
        descuento_editorial: float = 0.0,
    ) -> None:
        """Inicializa un libro invocando al constructor de la clase base con super().
        
        Args:
            id_producto (str): Identificador único.
            nombre (str): Título del libro.
            precio (float): Precio de lista.
            stock (int): Ejemplares disponibles.
            autor (str): Nombre del autor o autores.
            isbn (str): Código ISBN normalizado.
            es_digital (bool, opcional): True si es eBook/digital, False si es físico.
            descuento_editorial (float, opcional): Descuento de feria/editorial en % (0 a 100).
        """
        super().__init__(id_producto, nombre, precio, stock)
        self._autor: str = ""
        self._isbn: str = ""
        self._es_digital: bool = False
        self._descuento_editorial: float = 0.0

        self.autor = autor
        self.isbn = isbn
        self.es_digital = es_digital
        self.descuento_editorial = descuento_editorial

    @property
    def autor(self) -> str:
        """Getter del autor del libro."""
        return self._autor

    @autor.setter
    def autor(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValidationError("El autor del libro no puede estar vacío.")
        self._autor = valor.strip()

    @property
    def isbn(self) -> str:
        """Getter del ISBN del libro."""
        return self._isbn

    @isbn.setter
    def isbn(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValidationError("El código ISBN no puede estar vacío.")
        self._isbn = valor.strip()

    @property
    def es_digital(self) -> bool:
        """Indica si el libro es en formato digital."""
        return self._es_digital

    @es_digital.setter
    def es_digital(self, valor: bool) -> None:
        if not isinstance(valor, bool):
            raise ValidationError("El valor de formato digital debe ser un booleano (True/False).")
        self._es_digital = valor

    @property
    def descuento_editorial(self) -> float:
        """Getter del descuento de editorial en porcentaje."""
        return self._descuento_editorial

    @descuento_editorial.setter
    def descuento_editorial(self, valor: float) -> None:
        try:
            val_float = float(valor)
        except (ValueError, TypeError):
            raise ValidationError("El descuento editorial debe ser numérico.")
        if not (0.0 <= val_float <= 100.0):
            raise ValidationError("El descuento editorial debe estar entre 0% y 100%.")
        self._descuento_editorial = round(val_float, 2)

    def calcular_precio_final(self) -> float:
        """Calcula el precio final del libro con exención tributaria y descuentos editoriales.
        
        Fórmula:
            Base con descuento editorial (vía DescuentoMixin)
            Si es_digital es True: se aplica un descuento extra del 15% por edición digital.
            Impuesto = 0.0 (Exonerado según Ley de Fomento del Libro y Lectura)
            
        Returns:
            float: Precio final neto de venta.
        """
        precio_con_desc = self.aplicar_descuento(self._precio, self._descuento_editorial)
        if self._es_digital:
            precio_con_desc = self.aplicar_descuento(precio_con_desc, self.DESCUENTO_EDICION_DIGITAL)
        return round(precio_con_desc, 2)

    def __str__(self) -> str:
        """Representación detallada de un libro."""
        tipo_formato = "Digital (eBook)" if self._es_digital else "Físico"
        base_str = super().__str__()
        return (
            f"{base_str} | Autor: {self._autor} | "
            f"ISBN: {self._isbn} | Formato: {tipo_formato} | Desc. Editorial: {self._descuento_editorial}%"
        )
