from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import PedidoProducto

@receiver(post_save, sender=PedidoProducto)
@receiver(post_delete, sender=PedidoProducto)
def actualizar_total_pedido(sender, instance, **kwargs):
    pedido = instance.pedido
    pedido.calcular_total()