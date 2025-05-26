from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST

# Create your views here.

from django.shortcuts import render, redirect, get_object_or_404
from .models import Pedido
from .forms import ProductoForm, PersonalizacionCampoForm, PersonalizacionOpcionFormSet
from .models import Producto
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
#PAGINA DEL LOCAL ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def pedidos_admin(request):
    estado = request.GET.get('estado')
    # Excluye los pedidos entregados
    pedidos = Pedido.objects.exclude(estado='entregado').order_by('-fecha_creacion')
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
def agregar_producto_admin(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('pedidos_admin')
    else:
        form = ProductoForm()
    return render(request, 'admin/agregar_producto_admin.html', {'form': form})

def agregar_personalizacion_admin(request):
    if request.method == 'POST':
        form = PersonalizacionCampoForm(request.POST)
        formset = PersonalizacionOpcionFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            campo = form.save()
            formset.instance = campo
            formset.save()
            return redirect('agregar_producto_admin')
    else:
        form = PersonalizacionCampoForm()
        formset = PersonalizacionOpcionFormSet()
    return render(request, 'admin/agregar_personalizacion_admin.html', {'form': form, 'formset': formset})



def productos_admin(request):
    productos = Producto.objects.all()
    return render(request, 'admin/productos_admin.html', {'productos': productos})

def editar_producto_admin(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('productos_admin')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'admin/editar_producto_admin.html', {'form': form, 'producto': producto})
#PAGINA DEL CLIENTE ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, PersonalizacionOpcion, Pedido, PedidoProducto
from django.contrib import messages

def catalogo_cliente(request):
    productos = Producto.objects.filter(disponible=True)
    return render(request, 'cliente/catalogo.html', {'productos': productos})

def agregar_al_carrito(request, producto_id):
    producto_id_str = str(producto_id)
    carrito = request.session.get('carrito', [])
    
    # Forzar que carrito sea una lista, no un dict
    if not isinstance(carrito, list):
        carrito = []

    encontrado = False
    for item in carrito:
        if isinstance(item, dict) and item.get('producto_id') == producto_id_str and not item.get('opciones'):
            item['cantidad'] += 1
            encontrado = True
            break

    if not encontrado:
        carrito.append({
            'producto_id': producto_id_str,
            'cantidad': 1,
            'opciones': [],
        })

    request.session['carrito'] = carrito
    request.session.modified = True
    return redirect('catalogo_cliente')

def ver_carrito(request):
    carrito = request.session.get('carrito', [])  # lista de dicts
    items = []
    total = 0
    nuevos_items = []

    for item in carrito:
        producto_id = item.get('producto_id')
        cantidad = item.get('cantidad', 1)
        opciones_ids = item.get('opciones', [])

        try:
            producto = Producto.objects.get(id=producto_id)
        except Producto.DoesNotExist:
            continue

        opciones_obj = []
        precio_extra_total = 0
        for opcion_id in opciones_ids:
            try:
                opcion = PersonalizacionOpcion.objects.get(id=opcion_id)
                opciones_obj.append(opcion)
                precio_extra_total += opcion.precio_extra
            except PersonalizacionOpcion.DoesNotExist:
                pass

        subtotal = (producto.precio + precio_extra_total) * cantidad
        total += subtotal

        items.append({
            'producto': producto,
            'cantidad': cantidad,
            'opciones': opciones_obj,
            'subtotal': subtotal,
        })

        nuevos_items.append(item)

    if nuevos_items != carrito:
        request.session['carrito'] = nuevos_items
        request.session.modified = True

    return render(request, 'cliente/carrito.html', {'items': items, 'total': total})

    # Limpia el carrito automáticamente si hubo productos inválidos
    if nuevos_items != carrito:
        request.session['carrito'] = nuevos_items
        request.session.modified = True

    return render(request, 'cliente/carrito.html', {'items': items, 'total': total})

def realizar_pedido(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        direccion = request.POST.get('direccion', '').strip()
        telefono = request.POST.get('telefono', '').strip()

        if not nombre or not direccion:
            messages.error(request, 'Nombre y dirección son obligatorios.')
            return redirect('ver_carrito')

        carrito = request.session.get('carrito', [])  # lista
        if not carrito:
            messages.error(request, 'Tu carrito está vacío.')
            return redirect('catalogo_cliente')

        pedido = Pedido.objects.create(
            cliente_nombre=nombre,
            cliente_direccion=direccion,
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
                cantidad=cantidad
            )

            if opciones_ids:
                pedido_item.opciones_seleccionadas.set(opciones_ids)

            total += pedido_item.subtotal()

        pedido.total = total
        pedido.save()

        # GUARDA EL TELÉFONO EN LA SESIÓN AQUÍ 👇
        request.session['telefono'] = telefono

        # Notificar a través de WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "pedidos",
            {"type": "nuevo_pedido"}
        )

        request.session['carrito'] = []
        request.session.modified = True

        messages.success(request, 'Pedido realizado con éxito.')
        return redirect('catalogo_cliente')

    
def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    
    campos_y_opciones = []
    campos = producto.campos_personalizacion.prefetch_related('opciones').all()
    for campo in campos:
        opciones = campo.opciones.all()
        campos_y_opciones.append({'campo': campo, 'opciones': opciones})
    
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))
        personalizaciones = []

        for campo in campos:
            if campo.es_multiple:
                opcion_ids = request.POST.getlist(f"campo_{campo.id}")
                personalizaciones.extend([int(op_id) for op_id in opcion_ids])
            else:
                opcion_id = request.POST.get(f"campo_{campo.id}")
                if opcion_id:
                    personalizaciones.append(int(opcion_id))

        carrito = request.session.get('carrito', [])
        carrito.append({
            'producto_id': producto.id,
            'cantidad': cantidad,
            'opciones': personalizaciones,
        })
        request.session['carrito'] = carrito
        request.session.modified = True  # asegurar guardar sesión

        return redirect('ver_carrito')

    return render(request, 'cliente/detalle_producto.html', {
        'producto': producto,
        'campos_y_opciones': campos_y_opciones
    })

def eliminar_del_carrito(request, item_index):
    """
    Elimina un producto del carrito por su índice en la lista de la sesión.
    """
    try:
        item_index = int(item_index)
        carrito = request.session.get('carrito', [])
        if 0 <= item_index < len(carrito):
            del carrito[item_index]
            request.session['carrito'] = carrito
            request.session.modified = True
    except (ValueError, TypeError):
        pass
    return redirect('ver_carrito')

def checkout(request):
    carrito = request.session.get('carrito', [])
    if not carrito:
        messages.error(request, 'Tu carrito está vacío.')
        return redirect('catalogo_cliente')

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        direccion = request.POST.get('direccion', '').strip()
        telefono = request.POST.get('telefono', '').strip()

        if not nombre or not direccion:
            messages.error(request, 'Nombre y dirección son obligatorios.')
            return redirect('checkout')

        # Aquí puedes reutilizar la lógica de realizar_pedido
        return realizar_pedido(request)

    return render(request, 'cliente/checkout.html')

def mis_pedidos(request):
    # Aquí puedes usar el nombre, teléfono o una cookie/sesión para filtrar los pedidos del cliente.
    # Ejemplo simple: por teléfono guardado en sesión (ajusta según tu lógica de autenticación).
    telefono = request.session.get('telefono')
    pedidos = []
    if telefono:
        pedidos = Pedido.objects.filter(cliente_telefono=telefono).order_by('-fecha_creacion')
    request.session['telefono'] = telefono  # Así el cliente puede ver sus pedidos
    return render(request, 'cliente/mis_pedidos.html', {'pedidos': pedidos})

def pedidos_entregados_admin(request):
    pedidos = Pedido.objects.filter(estado='entregado').order_by('-fecha_creacion')
    return render(request, 'admin/pedidos_entregados_admin.html', {'pedidos': pedidos})


