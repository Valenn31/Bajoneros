# sistema/urls.py
from django.contrib import admin
from django.urls import path
from mi_app import views  # asegurate de que esto esté bien

urlpatterns = [
    path('admin/', admin.site.urls),  # esto es el panel automático de Django
    path('panel/pedidos/', views.pedidos_admin, name='pedidos_admin'),
    path('panel/pedidos/cambiar_estado/<int:pedido_id>/', views.cambiar_estado_pedido, name='cambiar_estado_pedido'),
    path('panel/pedidos/imprimir/<int:pedido_id>/', views.imprimir_pedido, name='imprimir_pedido'),
    
    path('catalogo/', views.catalogo_cliente, name='catalogo_cliente'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('agregar-al-carrito/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('realizar-pedido/', views.realizar_pedido, name='realizar_pedido'),
    
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
]

