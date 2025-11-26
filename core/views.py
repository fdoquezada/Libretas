from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q
import pandas as pd
import csv
from io import BytesIO
from openpyxl import Workbook

from .models import Entrega, Conductor, Supervisor, Periodo
from .forms import (
    EntregaForm,
    EntregaEstadoForm,
    ConductorForm,
    SupervisorForm,
    PeriodoForm,
    CargaMasivaConductoresForm
)

def inicio(request):
    if request.user.is_authenticated:
        perfil = getattr(request.user, 'perfil', None)
        if perfil:
            return redirect('dashboard')
        else:
            return redirect('dashboard')
    return render(request, 'core/inicio.html')

    
@login_required
def dashboard(request):
    perfil = getattr(request.user, 'perfil', None)
    
    # Obtener todas las entregas filtradas por base del usuario
    entregas = Entrega.objects.select_related('conductor', 'supervisor').order_by('-fecha_entrega')
    
    if perfil:
        entregas = entregas.filter(conductor__base=perfil.base)
    
    # --- FILTROS ---
    filtro_estado = request.GET.get('estado')
    filtro_fase = request.GET.get('fase')
    filtro_periodo = request.GET.get('periodo')
    filtro_conductor = request.GET.get('conductor')
    filtro_supervisor = request.GET.get('supervisor')
    
    # Aplicar filtros si existen
    if filtro_estado:
        entregas = entregas.filter(estado=filtro_estado)
    
    if filtro_fase:
        entregas = entregas.filter(fase=filtro_fase)
    
    if filtro_periodo:
        entregas = entregas.filter(periodo__icontains=filtro_periodo)
    
    if filtro_conductor:
        entregas = entregas.filter(conductor__nombre__icontains=filtro_conductor)
    
    if filtro_supervisor:
        entregas = entregas.filter(supervisor__nombre__icontains=filtro_supervisor)
    
    # --- PAGINACIÓN ---
    paginator = Paginator(entregas, 10)  # 10 entregas por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # --- ESTADÍSTICAS ---
    total_entregas = entregas.count()
    entregas_pendientes = entregas.filter(estado='pendiente').count()
    entregas_entregadas = entregas.filter(estado='entregada').count()
    
    # Obtener opciones para los filtros
    estados = Entrega._meta.get_field('estado').choices
    fases = Entrega._meta.get_field('fase').choices
    
    # Obtener conductores y supervisores únicos para filtros
    conductores = Conductor.objects.filter(base=perfil.base).order_by('nombre') if perfil else Conductor.objects.none()
    supervisores = Supervisor.objects.filter(base=perfil.base).order_by('nombre') if perfil else Supervisor.objects.none()
    
    context = {
        'perfil': perfil,
        'total_entregas': total_entregas,
        'entregas_pendientes': entregas_pendientes,
        'entregas_entregadas': entregas_entregadas,
        'page_obj': page_obj,
        'estados': estados,
        'fases': fases,
        'conductores': conductores,
        'supervisores': supervisores,
        'filtros_aplicados': any([filtro_estado, filtro_fase, filtro_periodo, filtro_conductor, filtro_supervisor]),
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
def eliminar_entrega(request, pk):
    """
    Vista para eliminar una entrega con confirmación
    """
    # Manejar el caso GET (mostrar confirmación)
    if request.method == 'GET':
        try:
            entrega = get_object_or_404(Entrega, pk=pk)
            
            # Verificar permisos
            perfil = getattr(request.user, 'perfil', None)
            if perfil and entrega.conductor.base != perfil.base:
                messages.error(request, 'No tienes permisos para eliminar esta entrega.')
                return redirect('dashboard')
            
            return render(
                request,
                'core/confirmar_eliminacion_entrega.html',
                {'entrega': entrega},
            )
            
        except Exception as e:
            messages.error(request, f'Error al cargar la entrega: {str(e)}')
            return redirect('dashboard')
    
    # Manejar el caso POST (eliminar realmente)
    elif request.method == 'POST':
        try:
            entrega = get_object_or_404(Entrega, pk=pk)
            
            # Verificar permisos
            perfil = getattr(request.user, 'perfil', None)
            if perfil and entrega.conductor.base != perfil.base:
                messages.error(request, 'No tienes permisos para eliminar esta entrega.')
                return redirect('dashboard')
            
            # Guardar información para el mensaje
            numero_registro = entrega.numero_registro
            conductor_nombre = entrega.conductor.nombre
            
            # Eliminar la entrega
            entrega.delete()
            
            messages.success(request, f'Entrega #{numero_registro} del conductor {conductor_nombre} eliminada correctamente.')
            return redirect('dashboard')
            
        except Exception as e:
            messages.error(request, f'Error al eliminar la entrega: {str(e)}')
            return redirect('dashboard')
    
    # Para cualquier otro método HTTP, redirigir
    else:
        return redirect('dashboard')

@login_required
def crear_conductor(request):
    # Obtener el perfil del usuario logueado
    perfil = getattr(request.user, 'perfil', None)
    
    # 1. Crear la instancia del formulario, enviando el perfil si es necesario
    if request.method == 'POST':
        # Instanciar el formulario con los datos POST
        form = ConductorForm(request.POST, user_profile=perfil) 
        
        if form.is_valid():
            conductor = form.save(commit=False)
            
            # 2. ASIGNAR LA BASE DEL USUARIO
            # Esto es lo que solicitaste y es correcto.
            if perfil:
                conductor.base = perfil.base
            
            conductor.save()
            
            # Si el modelo Conductor tiene un campo OneToOneField a Perfil
            # y quieres asociarlo al perfil actual (aunque Conductor ya tiene campo 'base'):
            # conductor.perfil = perfil 
            # conductor.save()
            
            return redirect('listar_conductores')
    else:
        # Instanciar el formulario para la solicitud GET
        # Se envía el perfil aquí para que el formulario pueda filtrar opciones (ver sección 2)
        form = ConductorForm(user_profile=perfil)
        
    return render(
        request,
        'core/crear_conductor.html',
        {'form': form},
    )
@login_required
def listar_conductores(request):
    perfil = getattr(request.user, 'perfil', None)
    
    conductores = Conductor.objects.select_related('perfil').order_by('nombre')
    
    # APLICAR FILTRO POR BASE
    #if perfil:
    #conductores = conductores.filter(base=perfil.base)
    
    # FILTRO ADICIONAL POR PARÁMETRO GET
    base_filter = request.GET.get('base')
    if base_filter:
        conductores = conductores.filter(base=base_filter)
        
    # Agregar paginación si no la tienes
    from django.core.paginator import Paginator
    paginator = Paginator(conductores, 15)  # 15 items por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Obtener las opciones de base para el filtro
    from django.db.models import TextChoices
    # Asumiendo que 'base' es un Choices field en tu modelo
    base_choices = Conductor._meta.get_field('base').choices
    
    return render(
        request,
        'core/gestionar_conductores.html',
        {
            #'conductores': conductores,
            'page_obj': page_obj,
            'base_choices': base_choices,  # ← Agregar esto
        },
    )

@login_required
def editar_conductor(request, pk):
    perfil = getattr(request.user, 'perfil', None)
    
    conductor = get_object_or_404(Conductor, pk=pk)
    
    # VERIFICAR QUE EL CONDUCTOR PERTENECE A LA BASE DEL USUARIO
    if perfil and conductor.base != perfil.base:
        return redirect('listar_conductores')
    
    if request.method == 'POST':
        form = ConductorForm(request.POST, instance=conductor, user_profile=perfil)
        if form.is_valid():
            conductor_actualizado = form.save()
            # Agregar mensaje de debug
            messages.success(request, f'Conductor actualizado. Base: {conductor_actualizado.base}')
            return redirect('listar_conductores')
        else:
            # Mostrar errores del formulario
            messages.error(request, f'Errores en el formulario: {form.errors}')
    else:
        form = ConductorForm(instance=conductor, user_profile=perfil)
    
    return render(
        request,
        'core/crear_conductor.html',
        {'form': form, 'edicion': True, 'objeto': conductor},
    )
@login_required
def eliminar_conductor(request, pk):
    perfil = getattr(request.user, 'perfil', None)
    conductor = get_object_or_404(Conductor, pk=pk)
    
    # VERIFICAR QUE EL CONDUCTOR PERTENECE A LA BASE DEL USUARIO
    if perfil and conductor.base != perfil.base:
        messages.error(request, 'No tienes permisos para eliminar este conductor.')
        return redirect('listar_conductores')
    
    if request.method == 'POST':
        conductor.delete()
        messages.success(request, f'Conductor {conductor.nombre} eliminado correctamente.')
        return redirect('listar_conductores')
    
    # Si es GET, mostrar página de confirmación
    return render(
        request,
        'core/confirmar_eliminacion.html',
        {'objeto': conductor, 'entidad': 'Conductor', 'cancel_url': 'listar_conductores'},
    )
    
@login_required
def crear_supervisor(request):
    perfil = getattr(request.user, 'perfil', None)
    
    if request.method == 'POST':
        form = SupervisorForm(request.POST)
        if form.is_valid():
            supervisor = form.save(commit=False)
            if perfil:
                supervisor.base = perfil.base  # Asignar base automáticamente
            supervisor.save()
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
    perfil = getattr(request.user, 'perfil', None)
    
    supervisores = Supervisor.objects.order_by('nombre')
    
    # Paginación
    from django.core.paginator import Paginator
    paginator = Paginator(supervisores, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)  # ← page_obj correcto
        
    return render(
        request,
        'core/gestionar_supervisores.html',
        {'page_obj': page_obj},  # ← page_obj correcto
    )

@login_required
def editar_supervisor(request, pk):
    perfil = getattr(request.user, 'perfil', None)
    supervisor = get_object_or_404(Supervisor, pk=pk)
    
    # VERIFICAR QUE EL SUPERVISOR PERTENECE A LA BASE DEL USUARIO
    if perfil and supervisor.base != perfil.base:
        return redirect('listar_supervisores')
    
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
    perfil = getattr(request.user, 'perfil', None)
    supervisor = get_object_or_404(Supervisor, pk=pk)
    
    # VERIFICAR QUE EL SUPERVISOR PERTENECE A LA BASE DEL USUARIO
    if perfil and supervisor.base != perfil.base:
        return redirect('listar_supervisores')
    
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
    # Si Periodo tiene campo 'base' y debe filtrarse:
    perfil = getattr(request.user, 'perfil', None)
    periodos = Periodo.objects.order_by('-año', 'trimestre')
    
    # APLICAR FILTRO POR BASE (Si Periodo tiene una relación 'base')
     #if perfil:
        #periodos = periodos.filter(base=perfil.base)
        
    # Si Periodo es global y no necesita filtrarse por base, usa el código original:
    # periodos = Periodo.objects.order_by('-año', 'trimestre') 
    
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

@login_required
def exportar_periodos_csv(request):
    # 1. Aplicar la misma lógica de filtro por base
    perfil = getattr(request.user, 'perfil', None)
    periodos = Periodo.objects.all().order_by('-año', 'trimestre')
    
    # Si el Periodo tiene campo 'base' y quieres filtrar (Opción 1 que discutimos)
    if perfil and hasattr(Periodo, 'base'):
        periodos = periodos.filter(base=perfil.base)

    # 2. Configurar la respuesta HTTP para un archivo CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="periodos.csv"'

    writer = csv.writer(response)
    
    # 3. Escribir la cabecera (encabezados de las columnas)
    writer.writerow(['ID', 'Año', 'Trimestre', 'Nombre del Trimestre'])

    # 4. Escribir los datos
    for periodo in periodos:
        writer.writerow([
            periodo.id, 
            periodo.año, 
            periodo.trimestre, 
            periodo.get_trimestre_display()
        ])

    return response

@login_required
def exportar_periodos_xls(request):
    # 1. Aplicar la misma lógica de filtro por base
    perfil = getattr(request.user, 'perfil', None)
    periodos = Periodo.objects.all().order_by('-año', 'trimestre')
    
    # Si el Periodo tiene campo 'base' y quieres filtrar (Opción 1 que discutimos)
    if perfil and hasattr(Periodo, 'base'):
        periodos = periodos.filter(base=perfil.base)

    # 2. Crear el libro de trabajo de Excel
    wb = Workbook()
    ws = wb.active # Obtener la hoja activa (WorkSheet)
    ws.title = "Periodos"

    # 3. Escribir la cabecera (encabezados de las columnas)
    headers = ['ID', 'Año', 'Trimestre', 'Nombre del Trimestre']
    ws.append(headers)

    # 4. Escribir los datos
    for periodo in periodos:
        ws.append([
            periodo.id,
            periodo.año,
            periodo.trimestre,
            periodo.get_trimestre_display()
        ])

    # 5. Configurar la respuesta HTTP para un archivo Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="periodos.xlsx"'
    
    # 6. Guardar el libro de trabajo en la respuesta
    wb.save(response)

    return response

@login_required
def exportar_entregas_csv(request):
# Obtener el queryset inicial
    perfil = getattr(request.user, 'perfil', None)
    entregas = Entrega.objects.select_related('conductor', 'supervisor', 'periodo').all()
    
    if perfil:
        entregas = entregas.filter(base=perfil.base)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="entregas.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'Registro', 'Periodo', 'Año', 'Trimestre', 'Base', 
        'Conductor', 'Supervisor', 'Estado', 'Fase', 'Fecha de Entrega', 'Notas'
    ])

    # 4. Escribir los datos
    for entrega in entregas:
        writer.writerow([
            entrega.numero_registro,
            str(entrega.periodo), # Formato: Enero-Marzo 2024
            entrega.periodo.año,
            entrega.periodo.trimestre,
            entrega.get_base_display(), # Usa get_base_display() para el nombre legible
            entrega.conductor.nombre,
            entrega.supervisor.nombre if entrega.supervisor else 'N/A',
            entrega.get_estado_display(),
            entrega.get_fase_display(),
            entrega.fecha_entrega.strftime('%Y-%m-%d') if entrega.fecha_entrega else '',
            entrega.notas
        ])

    return response

# --- EXPORTAR ENTREGAS A EXCEL (XLSX) ---
@login_required
def exportar_entregas_xls(request):
    perfil = getattr(request.user, 'perfil', None)
    
    # Obtener el queryset inicial
    entregas = Entrega.objects.select_related('conductor', 'supervisor', 'periodo').all()
    
    # 1. Aplicar el filtro de seguridad por base
    if perfil:
        entregas = entregas.filter(base=perfil.base)

    # 2. Crear el libro de trabajo de Excel
    wb = Workbook()
    ws = wb.active 
    ws.title = "Entregas"

    # 3. Escribir la cabecera
    headers = [
        'Registro', 'Periodo', 'Año', 'Trimestre', 'Base', 
        'Conductor', 'Supervisor', 'Estado', 'Fase', 'Fecha de Entrega', 'Notas'
    ]
    ws.append(headers)

    # 4. Escribir los datos
    for entrega in entregas:
        ws.append([
            entrega.numero_registro,
            str(entrega.periodo),
            entrega.periodo.año,
            entrega.periodo.trimestre,
            entrega.get_base_display(),
            entrega.conductor.nombre,
            entrega.supervisor.nombre if entrega.supervisor else 'N/A',
            entrega.get_estado_display(),
            entrega.get_fase_display(),
            entrega.fecha_entrega.strftime('%Y-%m-%d') if entrega.fecha_entrega else '',
            entrega.notas
        ])

    # 5. Configurar la respuesta HTTP y guardar
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="entregas.xlsx"'
    wb.save(response)

    return response

@login_required
def carga_masiva_conductores(request):
    perfil = getattr(request.user, 'perfil', None)
    
    if not perfil:
        messages.error(request, 'No tienes un perfil asignado.')
        return redirect('listar_conductores')
    
    if request.method == 'POST':
        form = CargaMasivaConductoresForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                archivo = request.FILES['archivo_excel']
                
                # Leer el archivo Excel
                df = pd.read_excel(archivo)
                
                # Validar columnas requeridas
                columnas_requeridas = ['nombre']
                for columna in columnas_requeridas:
                    if columna not in df.columns:
                        messages.error(request, f'La columna "{columna}" es requerida en el archivo Excel.')
                        return render(request, 'core/carga_masiva_conductores.html', {'form': form})
                
                conductores_creados = 0
                conductores_actualizados = 0
                errores = []
                
                # Obtener las bases válidas del modelo
                bases_validas = dict(Perfil.BASE_CHOICES).keys()
                
                for index, fila in df.iterrows():
                    try:
                        nombre = str(fila['nombre']).strip()
                        
                        if not nombre:
                            errores.append(f"Fila {index + 2}: El nombre no puede estar vacío")
                            continue
                        
                        # Obtener la base del Excel o usar la del usuario por defecto
                        if 'base' in df.columns:
                            base_excel = str(fila['base']).strip().lower()
                            # Validar que la base sea válida
                            if base_excel in bases_validas:
                                base_a_usar = base_excel
                            else:
                                base_a_usar = perfil.base  # Usar base del usuario si no es válida
                                if base_excel:  # Solo mostrar advertencia si hay valor
                                    errores.append(f"Fila {index + 2}: Base '{fila['base']}' no válida. Se usó '{perfil.base}'")
                        else:
                            base_a_usar = perfil.base  # Usar base del usuario si no hay columna base
                        
                        # Verificar si el conductor ya existe (mismo nombre)
                        conductor_existente = Conductor.objects.filter(
                            nombre__iexact=nombre
                        ).first()
                        
                        if conductor_existente:
                            # Actualizar conductor existente (incluyendo base si se especificó)
                            conductor_existente.nombre = nombre
                            if 'base' in df.columns and str(fila['base']).strip() in bases_validas:
                                conductor_existente.base = str(fila['base']).strip().lower()
                            conductor_existente.save()
                            conductores_actualizados += 1
                        else:
                            # Crear nuevo conductor
                            Conductor.objects.create(
                                nombre=nombre,
                                base=base_a_usar
                            )
                            conductores_creados += 1
                            
                    except Exception as e:
                        errores.append(f"Fila {index + 2}: Error - {str(e)}")
                        continue
                
                # Mostrar resultados
                if conductores_creados > 0 or conductores_actualizados > 0:
                    mensaje = f"Carga completada: {conductores_creados} nuevos, {conductores_actualizados} actualizados"
                    if errores:
                        mensaje += f". Errores: {len(errores)}"
                    messages.success(request, mensaje)
                
                if errores:
                    request.session['errores_carga'] = errores[:10]
                
                return redirect('listar_conductores')
                
            except Exception as e:
                messages.error(request, f'Error al procesar el archivo: {str(e)}')
    
    else:
        form = CargaMasivaConductoresForm()
    
    errores = request.session.pop('errores_carga', [])
    
    return render(request, 'core/carga_masiva_conductores.html', {
        'form': form,
        'errores': errores
    }) 

@login_required
def descargar_plantilla_conductores(request):
    # Crear un DataFrame de ejemplo con columna base
    data = {
        'nombre': [
            'JUAN PEREZ GARCIA',
            'MARIA LOPEZ MARTINEZ', 
            'CARLOS RAMIREZ SUAREZ',
            'ANA GOMEZ HERNANDEZ'
        ],
        'base': [
            'lampa',
            'calle larga', 
            'lampa',
            'calle larga'
        ]
    }
    
    df = pd.DataFrame(data)
    
    # Crear el archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Conductores', index=False)
        
        # Obtener la hoja y ajustar anchos
        worksheet = writer.sheets['Conductores']
        worksheet.column_dimensions['A'].width = 30  # nombre
        worksheet.column_dimensions['B'].width = 15  # base
        
        # Agregar nota sobre bases válidas
        worksheet['D1'] = 'Bases válidas:'
        worksheet['D2'] = 'lampa'
        worksheet['D3'] = 'calle larga'
    
    output.seek(0)
    
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="plantilla_conductores.xlsx"'
    
    return response