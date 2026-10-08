# Registro de modelos en el panel de administración.
from django.contrib import admin

from core.models import Alumno, Inscripcion, Materia


@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = ['legajo', 'apellido', 'nombre', 'email', 'activo']
    list_filter = ['activo']
    search_fields = ['legajo', 'dni', 'apellido', 'nombre', 'email']


@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'anio', 'cuatrimestre', 'cupo', 'activa']
    list_filter = ['anio', 'cuatrimestre', 'activa']
    search_fields = ['codigo', 'nombre']
    filter_horizontal = ['correlativas']


@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = ['alumno', 'materia', 'estado', 'nota', 'fecha_inscripcion']
    list_filter = ['estado', 'materia']
    search_fields = ['alumno__legajo', 'alumno__apellido', 'materia__codigo']
    autocomplete_fields = ['alumno', 'materia']
