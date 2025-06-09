from django.shortcuts import render, redirect, get_object_or_404
from ..models import Producto, Pedido, PedidoProducto, DireccionCliente
from django.contrib import messages
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth.decorators import login_required

def realizar_pedido(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        direccion_id = request.POST.get('direccion', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        if not nombre or not direccion_id:
            messages.error(request, 'Nombre y dirección son obligatorios.')
            return redirect('ver_carrito')
        carrito = request.session.get('carrito', [])
        if not carrito:
            messages.error(request, 'Tu carrito está vacío.')
            return redirect('catalogo_cliente')
        # Buscar dirección solo en DireccionCliente
        try:
            direccion_cliente = DireccionCliente.objects.get(id=direccion_id, usuario=request.user)
            direccion_str = f"{direccion_cliente.calle} {direccion_cliente.numero}"
            if direccion_cliente.piso:
                direccion_str += f", Piso: {direccion_cliente.piso}"
            if direccion_cliente.departamento:
                direccion_str += f", Dpto: {direccion_cliente.departamento}"
            if direccion_cliente.referencia:
                direccion_str += f" ({direccion_cliente.referencia})"
        except DireccionCliente.DoesNotExist:
            messages.error(request, 'La dirección seleccionada no existe.')
            return redirect('checkout')
        pedido = Pedido.objects.create(
            cliente=request.user if request.user.is_authenticated else None,
            cliente_nombre=nombre,
            cliente_direccion=direccion_str,
            cliente_telefono=telefono,
            estado='pendiente'
        )
        total = 0
        for item in carrito:
            producto_id = item.get('producto_id')
            cantidad = item.get('cantidad', 1)
            opciones_ids = item.get('opciones', [])
            producto = get_object_or_404(Producto, id=producto_id)
            pedido_item = PedidoProducto.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=cantidad,
                nombre_producto=producto.nombre,
                precio_producto=producto.precio,
            )
            if opciones_ids:
                pedido_item.opciones_seleccionadas.set(opciones_ids)
            total += pedido_item.subtotal()
        pedido.total = total
        pedido.save()
        request.session['telefono'] = telefono
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "pedidos",
            {"type": "nuevo_pedido"}
        )
        request.session['carrito'] = []
        request.session.modified = True
        messages.success(request, 'Pedido realizado con éxito.')
        return redirect('pedido_realizado')

@login_required
def checkout(request):
    carrito = request.session.get('carrito', [])
    if not carrito:
        messages.error(request, 'Tu carrito está vacío.')
        return redirect('catalogo_cliente')
    # Solo obtener direcciones de DireccionCliente
    direcciones = DireccionCliente.objects.filter(usuario=request.user)
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        direccion_id = request.POST.get('direccion')
        telefono = request.POST.get('telefono', '').strip()
        if not nombre or not direccion_id:
            messages.error(request, 'Nombre y dirección son obligatorios.')
            return redirect('checkout')
        return realizar_pedido(request)
    return render(request, 'cliente/checkout.html', {
        'user': request.user,
        'direcciones': direcciones,
    })

@login_required
def mis_pedidos(request):
    pedidos = Pedido.objects.filter(cliente=request.user).order_by('-fecha_creacion')
    return render(request, 'cliente/mis_pedidos.html', {'pedidos': pedidos})

def pedido_realizado(request):
    return render(request, 'cliente/pedido_realizado.html')