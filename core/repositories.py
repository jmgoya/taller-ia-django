# Acceso a datos (consultas al ORM).
from django.db.models import Count, Q

from core.models import NOTA_MINIMA_APROBACION, Alumno, Inscripcion, Materia

# Estados que ocupan cupo o impiden volver a inscribirse.
ESTADOS_VIGENTES = (Inscripcion.Estado.CURSANDO, Inscripcion.Estado.APROBADA)


def alumnos():
    return Alumno.objects.all()


def materias():
    vigentes = Q(inscripciones__estado=Inscripcion.Estado.CURSANDO)
    return (
        Materia.objects
        .prefetch_related('correlativas')
        .annotate(inscriptos=Count('inscripciones', filter=vigentes, distinct=True))
        .order_by(*Materia._meta.ordering)
    )


def inscripciones():
    return Inscripcion.objects.select_related('alumno', 'materia')


def inscripciones_de_alumno(alumno):
    return inscripciones().filter(alumno=alumno)


def inscripciones_de_materia(materia):
    return inscripciones().filter(materia=materia)


def materia_para_actualizar(materia_id):
    """Bloquea la fila de la materia para evitar sobrepasar el cupo en inscripciones concurrentes."""
    return Materia.objects.select_for_update().get(pk=materia_id)


def cantidad_cursando(materia):
    return Inscripcion.objects.filter(materia=materia, estado=Inscripcion.Estado.CURSANDO).count()


def tiene_inscripcion_vigente(alumno, materia):
    return Inscripcion.objects.filter(
        alumno=alumno, materia=materia, estado__in=ESTADOS_VIGENTES,
    ).exists()


def correlativas_no_aprobadas(alumno, materia):
    aprobadas = Inscripcion.objects.filter(
        alumno=alumno,
        estado=Inscripcion.Estado.APROBADA,
        nota__gte=NOTA_MINIMA_APROBACION,
    ).values('materia_id')
    return materia.correlativas.exclude(pk__in=aprobadas)


def crear_inscripcion(alumno, materia):
    return Inscripcion.objects.create(alumno=alumno, materia=materia)


def guardar(instancia, campos):
    instancia.save(update_fields=[*campos, 'actualizado'])
    return instancia
