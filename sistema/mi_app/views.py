from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST

# Create your views here.

from django.shortcuts import render, redirect, get_object_or_404
from .models import Pedido


def pedidos_admin(request):
    estado = request.GET.get('estado')
    pedidos = Pedido.objects.all()
    if estado:
        pedidos = pedidos.filter(estado=estado)
    return render(request, 'admin/pedidos_admin.html', {'pedidos': pedidos})

def cambiar_estado_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    nuevo_estado = request.POST.get('estado')
    if nuevo_estado:
        pedido.estado = nuevo_estado
        pedido.save()
    return redirect('pedidos_admin')


# ESTO ES PARA IMPRIMIR UN PEDIDO CON LA TICKETERA (NO FUNCIONANDO)
def imprimir_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    pedido.estado = 'proceso'
    pedido.save(update_fields=['estado'])  # Actualizar estado al imprimir
    return render(request, 'admin/imprimir_pedido.html', {'pedido': pedido})


# ESTO ACTUALIZA EL ESTADO DEL PEDIDO DESDE EL PANEL ADMIN
@require_POST
def cambiar_estado_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    nuevo_estado = request.POST.get('estado')

    estados_validos = [e[0] for e in Pedido.ESTADOS]
    if nuevo_estado in estados_validos:
        pedido.estado = nuevo_estado
        pedido.save()
    return redirect('pedidos_admin')