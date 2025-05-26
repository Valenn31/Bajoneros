# sistema/urls.py
from django.contrib import admin
from django.urls import path
from mi_app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin clásico de Django

    # Panel personalizado
    path('panel/pedidos/', views.pedidos_admin, name='pedidos_admin'),
    path('panel/agregar-producto/', views.agregar_producto_admin, name='agregar_producto_admin'),
    path('panel/pedidos/cambiar_estado/<int:pedido_id>/', views.cambiar_estado_pedido, name='cambiar_estado_pedido'),
    path('panel/pedidos/imprimir/<int:pedido_id>/', views.imprimir_pedido, name='imprimir_pedido'),

    # Catalogo y carrito
    path('catalogo/', views.catalogo_cliente, name='catalogo_cliente'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('agregar-al-carrito/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('realizar-pedido/', views.realizar_pedido, name='realizar_pedido'),

    # Otras rutas
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('eliminar-del-carrito/<int:item_index>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('checkout/', views.checkout, name='checkout'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

