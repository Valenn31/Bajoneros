from django.shortcuts import render, redirect, get_object_or_404
from ..models import Producto, PersonalizacionOpcion
from django.contrib import messages

def agregar_al_carrito(request, producto_id):
    producto_id_str = str(producto_id)
    carrito = request.session.get('carrito', [])
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
    carrito = request.session.get('carrito', [])
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

def eliminar_del_carrito(request, item_index):
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