from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Entrega, Conductor, Supervisor, Periodo
from .forms import (
    EntregaForm,
    EntregaEstadoForm,
    ConductorForm,
    SupervisorForm,
    PeriodoForm,
)

@login_required
def dashboard(request):
    perfil = getattr(request.user, 'perfil', None)
    entregas = Entrega.objects.all().select_related('conductor', 'supervisor', 'periodo')

    if perfil:
        entregas = entregas.filter(base=perfil.base)

    total_entregas = entregas.count()
    entregas_pendientes = entregas.filter(estado='pendiente').count()
    entregas_entregadas = entregas.filter(estado='entregada').count()

    context = {
        'entregas': entregas,
        'total_entregas': total_entregas,
        'entregas_pendientes': entregas_pendientes,
        'entregas_entregadas': entregas_entregadas,
        'perfil': perfil,
    }

    return render(request, 'core/dashboard.html', context)



@login_required
def crear_entrega(request):
    if request.method == 'POST':
        form = EntregaForm(request.POST)
        if form.is_valid():
            entrega = form.save(commit=False)
            perfil = getattr(request.user, 'perfil', None)
            if perfil:
                entrega.base = perfil.base
            elif entrega.conductor_id:
                entrega.base = entrega.conductor.base
            entrega.save()
            return redirect('dashboard')
    else:
        form = EntregaForm()
    return render(
        request,
        'core/crear_entrega.html',
        {'form': form},
    )


@login_required
def editar_entrega(request, pk):
    entrega = get_object_or_404(Entrega, pk=pk)
    if request.method == 'POST':
        form = EntregaEstadoForm(request.POST, instance=entrega)
        if form.is_valid():
            form.save()
            messages.success(request, 'Entrega actualizada correctamente.')
            return redirect('dashboard')
    else:
        form = EntregaEstadoForm(instance=entrega)
    return render(
        request,
        'core/editar_entrega.html',
        {'form': form, 'entrega': entrega},
    )


@login_required
def crear_conductor(request):
    if request.method == 'POST':
        form = ConductorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_conductores')
    else:
        form = ConductorForm()
    return render(
        request,
        'core/crear_conductor.html',
        {'form': form},
    )


@login_required
def listar_conductores(request):
    conductores = Conductor.objects.select_related('perfil').order_by('nombre')
    return render(
        request,
        'core/gestionar_conductores.html',
        {'conductores': conductores},
    )


@login_required
def editar_conductor(request, pk):
    conductor = get_object_or_404(Conductor, pk=pk)
    if request.method == 'POST':
        form = ConductorForm(request.POST, instance=conductor)
        if form.is_valid():
            form.save()
            return redirect('listar_conductores')
    else:
        form = ConductorForm(instance=conductor)
    return render(
        request,
        'core/crear_conductor.html',
        {'form': form, 'edicion': True, 'objeto': conductor},
    )


@login_required
def eliminar_conductor(request, pk):
    conductor = get_object_or_404(Conductor, pk=pk)
    if request.method == 'POST':
        conductor.delete()
        return redirect('listar_conductores')
    return render(
        request,
        'core/confirmar_eliminacion.html',
        {'objeto': conductor, 'entidad': 'Conductor', 'cancel_url': 'listar_conductores'},
    )


@login_required
def crear_supervisor(request):
    if request.method == 'POST':
        form = SupervisorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_supervisores')
    else:
        form = SupervisorForm()
    return render(
        request,
        'core/crear_supervisor.html',
        {'form': form},
    )


@login_required
def listar_supervisores(request):
    supervisores = Supervisor.objects.order_by('nombre')
    return render(
        request,
        'core/gestionar_supervisores.html',
        {'supervisores': supervisores},
    )


@login_required
def editar_supervisor(request, pk):
    supervisor = get_object_or_404(Supervisor, pk=pk)
    if request.method == 'POST':
        form = SupervisorForm(request.POST, instance=supervisor)
        if form.is_valid():
            form.save()
            return redirect('listar_supervisores')
    else:
        form = SupervisorForm(instance=supervisor)
    return render(
        request,
        'core/crear_supervisor.html',
        {'form': form, 'edicion': True, 'objeto': supervisor},
    )


@login_required
def eliminar_supervisor(request, pk):
    supervisor = get_object_or_404(Supervisor, pk=pk)
    if request.method == 'POST':
        supervisor.delete()
        return redirect('listar_supervisores')
    return render(
        request,
        'core/confirmar_eliminacion.html',
        {'objeto': supervisor, 'entidad': 'Supervisor', 'cancel_url': 'listar_supervisores'},
    )


@login_required
def crear_periodo(request):
    if request.method == 'POST':
        form = PeriodoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_periodos')
    else:
        form = PeriodoForm()
    return render(
        request,
        'core/crear_periodo.html',
        {'form': form},
    )


@login_required
def listar_periodos(request):
    periodos = Periodo.objects.order_by('-año', 'trimestre')
    return render(
        request,
        'core/gestionar_periodos.html',
        {'periodos': periodos},
    )


@login_required
def editar_periodo(request, pk):
    periodo = get_object_or_404(Periodo, pk=pk)
    if request.method == 'POST':
        form = PeriodoForm(request.POST, instance=periodo)
        if form.is_valid():
            form.save()
            return redirect('listar_periodos')
    else:
        form = PeriodoForm(instance=periodo)
    return render(
        request,
        'core/crear_periodo.html',
        {'form': form, 'edicion': True, 'objeto': periodo},
    )


@login_required
def eliminar_periodo(request, pk):
    periodo = get_object_or_404(Periodo, pk=pk)
    if request.method == 'POST':
        periodo.delete()
        return redirect('listar_periodos')
    return render(
        request,
        'core/confirmar_eliminacion.html',
        {'objeto': periodo, 'entidad': 'Periodo', 'cancel_url': 'listar_periodos'},
    )