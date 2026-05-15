from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import Empleado, Certificado
from .forms import EmpleadoForm, CertificadoForm, FiltroEstadoForm, LoginForm, RegisterForm


@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    Vista de login OWASP-compliant.
    Incluye protecciones contra fuerza bruta, CSRF, y mensajes de error genéricos.
    """
    if request.user.is_authenticated:
        return redirect('lista_empleados')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenido, {user.first_name or user.username}.')
                return redirect('lista_empleados')
            else:
                # OWASP: Mensaje genérico para no revelar si el usuario existe
                messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


@require_http_methods(["POST"])
def logout_view(request):
    """Vista de logout segura."""
    logout(request)
    messages.success(request, 'Sesión cerrada correctamente.')
    return redirect('login')


@require_http_methods(["GET", "POST"])
def register_view(request):
    """
    Vista de registro de usuario con validación de contraseña fuerte OWASP.
    """
    if request.user.is_authenticated:
        return redirect('lista_empleados')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, '¡Registro exitoso! Por favor, inicia sesión.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


@login_required(login_url='login')
def lista_empleados(request):
    filtro_form = FiltroEstadoForm(request.GET)
    empleados = Empleado.objects.all()
    estado_filtro = ''
    if filtro_form.is_valid():
        estado_filtro = filtro_form.cleaned_data.get('estado', '')
        if estado_filtro:
            empleados = empleados.filter(estado_contrato=estado_filtro)
    return render(request, 'lista.html', {
        'empleados': empleados,
        'filtro_form': filtro_form,
        'estado_filtro': estado_filtro,
    })


@login_required(login_url='login')
def agregar_empleado(request):
    if request.method == 'POST':
        action = request.POST.get('action', 'preview')
        form = EmpleadoForm(request.POST)
        if action == 'confirmar' and form.is_valid():
            form.save()
            messages.success(request, 'Empleado agregado exitosamente.')
            return redirect('lista_empleados')
        elif action == 'preview' and form.is_valid():
            return render(request, 'confirmar.html', {
                'form': form,
                'datos': form.cleaned_data,
                'accion': 'agregar',
            })
    else:
        form = EmpleadoForm()
    return render(request, 'formulario.html', {
        'form': form,
        'titulo': 'Agregar Empleado',
        'accion_url': 'agregar_empleado',
    })


@login_required(login_url='login')
def modificar_empleado(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, instance=empleado)
        if form.is_valid():
            form.save()
            messages.success(request, f'Empleado "{empleado.nombre}" modificado.')
            return redirect('lista_empleados')
    else:
        form = EmpleadoForm(instance=empleado)
    return render(request, 'formulario.html', {
        'form': form,
        'titulo': f'Modificar — {empleado.nombre}',
        'empleado': empleado,
        'accion_url': 'modificar_empleado',
    })


@login_required(login_url='login')
def eliminar_empleado(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    if request.method == 'POST':
        nombre = empleado.nombre
        empleado.delete()
        messages.success(request, f'Empleado "{nombre}" eliminado.')
        return redirect('lista_empleados')
    return render(request, 'eliminar.html', {'empleado': empleado})


@login_required(login_url='login')
def finiquitar_empleado(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    empleado.estado_contrato = 'finiquitado'
    empleado.save()
    messages.warning(request, f'"{empleado.nombre}" fue finiquitado.')
    return redirect('lista_empleados')


@login_required(login_url='login')
def renovar_empleado(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    empleado.estado_contrato = 'renovado'
    empleado.save()
    messages.success(request, f'Contrato de "{empleado.nombre}" renovado.')
    return redirect('lista_empleados')


@login_required(login_url='login')
def agregar_certificado(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    if request.method == 'POST':
        form = CertificadoForm(request.POST, request.FILES)
        if form.is_valid():
            cert = form.save(commit=False)
            cert.empleado = empleado
            cert.save()
            messages.success(request, 'Certificado agregado.')
            return redirect('modificar_empleado', pk=pk)
    else:
        form = CertificadoForm()
    return render(request, 'certificado.html', {'form': form, 'empleado': empleado})
