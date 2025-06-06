# sistema/urls.py
from django.contrib import admin
from django.urls import path
from mi_app import views
from mi_app.views import cliente as views_cliente
from mi_app.views.cliente import logout_cliente, mi_cuenta
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.shortcuts import redirect
from mi_app.views.admin import imprimir_pedido_pdf

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin clásico de Django

    # Panel personalizado
    path('panel/pedidos/', views.pedidos_admin, name='pedidos_admin'),
    path('panel/agregar-producto/', views.agregar_producto_admin, name='agregar_producto_admin'),
    path('panel/agregar-personalizacion/', views.agregar_personalizacion_admin, name='agregar_personalizacion_admin'),
    path('panel/pedidos/cambiar_estado/<int:pedido_id>/', views.cambiar_estado_pedido, name='cambiar_estado_pedido'),
    path('panel/pedidos/imprimir/<int:pedido_id>/', views.imprimir_pedido, name='imprimir_pedido'),
    path('panel/pedidos/imprimir_pdf/<int:pedido_id>/', imprimir_pedido_pdf, name='imprimir_pedido_pdf'),
    path('panel/productos/', views.productos_admin, name='productos_admin'),
    path('panel/productos/<int:pk>/editar/', views.editar_producto_admin, name='editar_producto_admin'),
    path('panel/productos/<int:pk>/eliminar/', views.eliminar_producto_admin, name='eliminar_producto_admin'),
    path('panel/pedidos/entregados/', views.pedidos_entregados_admin, name='pedidos_entregados_admin'),
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

    # Rutas para personalizaciones
    path('panel/personalizaciones/', views.lista_personalizaciones_admin, name='lista_personalizaciones_admin'),
    path('panel/personalizaciones/agregar/', views.agregar_personalizacion_admin, name='agregar_personalizacion_admin'),
    path('panel/personalizaciones/editar/<int:pk>/', views.agregar_personalizacion_admin, name='editar_personalizacion_admin'),
    path('panel/personalizaciones/eliminar/<int:pk>/', views.eliminar_personalizacion_admin, name='eliminar_personalizacion_admin'),

    # Rutas para registro y login de clientes
    path('registro/', views_cliente.registro_cliente, name='registro_cliente'),
    path('login/', views_cliente.login_cliente, name='login_cliente'),
    path('logout/', logout_cliente, name='logout_cliente'),

    # Redirección de login
    path('accounts/login/', RedirectView.as_view(url='/login/', permanent=False)),

    # Mi cuenta
    path('cuenta/', mi_cuenta, name='mi_cuenta'),

    # Rutas para direcciones
    path('direcciones/', views_cliente.mis_direcciones, name='mis_direcciones'),
    path('mis-direcciones/eliminar/<int:direccion_id>/', views.eliminar_direccion, name='eliminar_direccion'),

    # Nueva ruta para pedido realizado
    path('pedido-realizado/', views.pedido_realizado, name='pedido_realizado'),

    # Ruta para la pantalla de inicio (splash)
    path('', views.splash, name='splash'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

