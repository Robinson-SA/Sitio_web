from django.urls import path
from . import views

urlpatterns = [
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    # Empleados
    path('', views.lista_empleados, name='lista_empleados'),
    path('agregar/', views.agregar_empleado, name='agregar_empleado'),
    path('modificar/<int:pk>/', views.modificar_empleado, name='modificar_empleado'),
    path('eliminar/<int:pk>/', views.eliminar_empleado, name='eliminar_empleado'),
    path('finiquitar/<int:pk>/', views.finiquitar_empleado, name='finiquitar_empleado'),
    path('renovar/<int:pk>/', views.renovar_empleado, name='renovar_empleado'),
    path('certificado/<int:pk>/', views.agregar_certificado, name='agregar_certificado'),
]
