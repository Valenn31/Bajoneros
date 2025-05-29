from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import date
from django.contrib.auth.models import User  # Nueva importación

# Producto del menú
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    categoria = models.CharField(max_length=50)
    disponible = models.BooleanField(default=True)
    personalizable = models.BooleanField(default=False)
    campos_personalizacion = models.ManyToManyField('PersonalizacionCampo', blank=True, related_name='productos')

    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)  # 👈 campo nuevo

    def __str__(self):
        return self.nombre


# Campo de personalización (ej: "Aderezo", "Tipo de pan")
class PersonalizacionCampo(models.Model):
    nombre = models.CharField(max_length=100)
    es_multiple = models.BooleanField(default=False)  # NUEVO CAMPO

    def __str__(self):
        return self.nombre


# Opciones dentro de un campo (ej: "Ketchup", "Mayonesa")
class PersonalizacionOpcion(models.Model):
    campo = models.ForeignKey(PersonalizacionCampo, on_delete=models.CASCADE, related_name='opciones')
    nombre = models.CharField(max_length=100)
    precio_extra = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.nombre} +${self.precio_extra}"


# Pedido
class Pedido(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('proceso', 'En proceso'),
        ('listo', 'Listo para entregar'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]

    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pedidos',
        null=True, blank=True
    )
    cliente_nombre = models.CharField(max_length=100)
    cliente_direccion = models.CharField(max_length=200)
    cliente_telefono = models.CharField(max_length=20, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente_nombre}"
    
    def calcular_total(self):
        total = sum([item.subtotal() for item in self.items.all()])
        self.total = total
        self.save(update_fields=['total'])

# Item dentro de un pedido
class PedidoProducto(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    opciones_seleccionadas = models.ManyToManyField(PersonalizacionOpcion, blank=True)
        # Nuevos campos para mantener datos históricos
    nombre_producto = models.CharField(max_length=200)
    precio_producto = models.DecimalField(max_digits=10, decimal_places=2)
    
    def subtotal(self):
        subtotal_base = self.producto.precio * self.cantidad
        extras = sum([op.precio_extra for op in self.opciones_seleccionadas.all()])
        return subtotal_base + (extras * self.cantidad)

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre} para Pedido #{self.pedido.id}"


class ClienteManager(BaseUserManager):
    def create_user(self, telefono, password=None):
        if not telefono:
            raise ValueError('El teléfono es obligatorio')
        user = self.model(telefono=telefono)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, telefono, password):
        user = self.create_user(telefono, password)
        user.is_admin = True
        user.save(using=self._db)
        return user

class Cliente(AbstractBaseUser, PermissionsMixin):  # <--- AGREGÁ PermissionsMixin
    telefono = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)  # <-- NUEVO CAMPO
    fecha_nacimiento = models.DateField(null=True, blank=True)  # NUEVO CAMPO
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'telefono'
    REQUIRED_FIELDS = []

    objects = ClienteManager()

    def __str__(self):
        return self.telefono

    @property
    def is_staff(self):
        return self.is_admin

    def edad(self):
        if self.fecha_nacimiento:
            today = date.today()
            return today.year - self.fecha_nacimiento.year - (
                (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
            )
        return None

class Direccion(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='direcciones')
    nombre = models.CharField(max_length=100, help_text="Ej: Casa, Trabajo, etc.")
    direccion = models.CharField(max_length=200)
    referencia = models.CharField(max_length=200, blank=True)
    # Puedes agregar más campos si necesitas (ej: ciudad, provincia)
    def __str__(self):
        return f"{self.nombre}: {self.direccion}"

class DireccionCliente(models.Model):
    # Usuario usando el modelo personalizado configurado
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='direcciones_cliente')
    nombre = models.CharField(max_length=100)  # Ej: "Casa", "Trabajo"
    direccion = models.TextField()
    referencia = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.nombre} - {self.usuario.telefono}"  # Usando telefono en lugar de username
