from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from ..models import Pedido, Producto,PersonalizacionCampo
from ..forms import ProductoForm, PersonalizacionCampoForm,PersonalizacionOpcionFormSet
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML
from datetime import datetime

def pedidos_admin(request):
    estado_param = request.GET.get('estado', '')
    if estado_param:
        estados_seleccionados = estado_param.split(',')
    else:
        estados_seleccionados = []

    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    pedidos = Pedido.objects.all()

    # Filtrado por estados
    if estados_seleccionados:
        pedidos = pedidos.filter(estado__in=estados_seleccionados)
    # else:
    #     pedidos = pedidos.exclude(estado__in=['entregado', 'cancelado'])

    # Filtrado por fecha
    if fecha_inicio:
        try:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, "%Y-%m-%d")
            pedidos = pedidos.filter(fecha_creacion__date__gte=fecha_inicio_dt)
        except ValueError:
            pass
    if fecha_fin:
        try:
            fecha_fin_dt = datetime.strptime(fecha_fin, "%Y-%m-%d")
            pedidos = pedidos.filter(fecha_creacion__date__lte=fecha_fin_dt)
        except ValueError:
            pass

    pedidos = pedidos.order_by('-fecha_creacion')
    ultimo_pedido_id = pedidos.first().id if pedidos else None
    return render(request, 'admin/pedidos_admin.html', {
        'pedidos': pedidos,
        'estados_seleccionados': estados_seleccionados,
        'fecha_inicio': fecha_inicio or '',
        'fecha_fin': fecha_fin or '',
        'ultimo_pedido_id': ultimo_pedido_id,
    })

@require_POST
def cambiar_estado_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    nuevo_estado = request.POST.get('estado')
    estados_validos = [e[0] for e in Pedido.ESTADOS]
    if nuevo_estado in estados_validos:
        pedido.estado = nuevo_estado
        pedido.save()
    return redirect('pedidos_admin')

def imprimir_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    pedido.estado = 'proceso'
    pedido.save(update_fields=['estado'])
    return render(request, 'admin/imprimir_pedido.html', {'pedido': pedido})

def imprimir_pedido_pdf(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    html_string = render_to_string('admin/ticket_pedido_pdf.html', {'pedido': pedido})
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="pedido_{pedido.id}.pdf"'
    return response

def agregar_producto_admin(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('pedidos_admin')
    else:
        form = ProductoForm()
    return render(request, 'admin/agregar_producto_admin.html', {'form': form})

def lista_personalizaciones_admin(request):
    from ..models import PersonalizacionCampo
    personalizaciones = PersonalizacionCampo.objects.all()
    return render(request, 'admin/lista_personalizaciones_admin.html', {'personalizaciones': personalizaciones})

def agregar_personalizacion_admin(request, pk=None):
    from ..models import PersonalizacionCampo
    if pk:
        campo = get_object_or_404(PersonalizacionCampo, pk=pk)
    else:
        campo = None

    if request.method == 'POST':
        form = PersonalizacionCampoForm(request.POST, instance=campo)
        formset = PersonalizacionOpcionFormSet(request.POST, instance=campo, prefix='opciones')
        if form.is_valid() and formset.is_valid():
            campo = form.save()
            formset.instance = campo
            formset.save()
            return redirect('lista_personalizaciones_admin')
    else:
        form = PersonalizacionCampoForm(instance=campo)
        formset = PersonalizacionOpcionFormSet(instance=campo, prefix='opciones')

    return render(request, 'admin/agregar_personalizacion_admin.html', {
        'form': form,
        'formset': formset,
        'editando': pk is not None
    })

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

def pedidos_entregados_admin(request):
    pedidos = Pedido.objects.filter(estado='entregado').order_by('-fecha_creacion')
    return render(request, 'admin/pedidos_entregados_admin.html', {'pedidos': pedidos})



@require_POST
def eliminar_personalizacion_admin(request, pk):
    personalizacion = get_object_or_404(PersonalizacionCampo, pk=pk)
    personalizacion.delete()
    return redirect('lista_personalizaciones_admin')

@require_POST
def eliminar_producto_admin(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    producto.delete()
    return redirect('productos_admin')