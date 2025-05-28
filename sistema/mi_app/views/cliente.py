from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from ..models import Producto, PersonalizacionOpcion
from django.contrib import messages
from ..forms import RegistroClienteForm
from django.contrib.auth.decorators import login_required
from ..forms import DireccionForm, CheckoutForm

@login_required
def catalogo_cliente(request):
    productos = Producto.objects.filter(disponible=True)
    return render(request, 'cliente/catalogo.html', {'productos': productos})

@login_required
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
        request.session.modified = True
        return redirect('ver_carrito')
    return render(request, 'cliente/detalle_producto.html', {
        'producto': producto,
        'campos_y_opciones': campos_y_opciones
    })

def registro_cliente(request):
    if request.method == 'POST':
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('catalogo_cliente')
    else:
        form = RegistroClienteForm()
    return render(request, 'login/registro.html', {'form': form})

def login_cliente(request):
    error = None
    if request.method == 'POST':
        telefono = request.POST['telefono']
        password = request.POST['password']
        user = authenticate(request, telefono=telefono, password=password)
        if user is not None:
            login(request, user)
            return redirect('catalogo_cliente')
        else:
            error = "Teléfono o contraseña incorrectos"
    return render(request, 'login/login.html', {'error': error})

def logout_cliente(request):
    logout(request)
    return redirect('login_cliente')

@login_required
def mi_cuenta(request):
    return render(request, 'cliente/mi_cuenta.html')

@login_required
def mis_direcciones(request):
    direcciones = request.user.direcciones.all()
    if request.method == 'POST':
        form = DireccionForm(request.POST)
        if form.is_valid():
            direccion = form.save(commit=False)
            direccion.cliente = request.user
            direccion.save()
            return redirect('mis_direcciones')
    else:
        form = DireccionForm()
    return render(request, 'cliente/mis_direcciones.html', {'direcciones': direcciones, 'form': form})

@login_required
def checkout(request):
    if not request.user.direcciones.exists():
        messages.info(request, "Debes agregar al menos una dirección antes de hacer un pedido.")
        return redirect('mis_direcciones')

    if request.method == 'POST':
        form = CheckoutForm(request.POST, cliente=request.user)
        if form.is_valid():
            direccion = form.cleaned_data['direccion']
            # Aquí deberías crear el pedido usando la dirección seleccionada
            # pedido = Pedido.objects.create(cliente=request.user, direccion=direccion, ...)
            messages.success(request, "¡Pedido realizado con éxito!")
            return redirect('catalogo_cliente')
    else:
        form = CheckoutForm(cliente=request.user)
    return render(request, 'cliente/checkout.html', {'form': form})