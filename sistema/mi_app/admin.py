from django.contrib import admin
from .models import Producto, PersonalizacionCampo, PersonalizacionOpcion, Pedido, PedidoProducto
from django.shortcuts import render, redirect
from .forms import ProductoForm

# Inline para mostrar Opciones dentro de cada Campo
class PersonalizacionOpcionInline(admin.TabularInline):
    model = PersonalizacionOpcion
    extra = 1

# Admin para Producto (sin inline de PersonalizacionCampo)
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'disponible', 'personalizable')
    list_filter = ('categoria', 'disponible', 'personalizable')
    search_fields = ('nombre',)
    filter_horizontal = ('campos_personalizacion',)  # para seleccionar los campos reutilizables

# Admin para PersonalizacionCampo con sus Opciones inline
@admin.register(PersonalizacionCampo)
class PersonalizacionCampoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    inlines = [PersonalizacionOpcionInline]
    search_fields = ('nombre',)

@admin.register(PersonalizacionOpcion)
class PersonalizacionOpcionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'campo', 'precio_extra')
    list_filter = ('campo',)
    search_fields = ('nombre',)

# Inline para mostrar los productos dentro de un pedido
class PedidoProductoInline(admin.TabularInline):
    model = PedidoProducto
    extra = 0
    filter_horizontal = ('opciones_seleccionadas',)  # Para seleccionar opciones personalizadas

# Admin para Pedido con los productos inline
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente_nombre', 'estado', 'total', 'fecha_creacion')
    list_filter = ('estado', 'fecha_creacion')
    search_fields = ('cliente_nombre', 'cliente_direccion')
    inlines = [PedidoProductoInline]
    readonly_fields = ('total',)  # 👈 Esto lo hace de solo lectura

def agregar_producto_admin(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('productos_admin')
    else:
        form = ProductoForm()
    return render(request, 'admin/agregar_producto_admin.html', {'form': form})
