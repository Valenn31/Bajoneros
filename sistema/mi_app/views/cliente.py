from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from ..models import Producto, PersonalizacionOpcion
from django.contrib import messages
from ..forms import RegistroClienteForm
from django.contrib.auth.decorators import login_required

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
            return redirect('catalogo_cliente')  # Cambia por la vista principal del cliente
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