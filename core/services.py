# Lógica de negocio.
from django.db import transaction
from rest_framework.exceptions import ValidationError

from core import repositories
from core.models import NOTA_MINIMA_APROBACION, Inscripcion


@transaction.atomic
def inscribir(alumno, materia):
    """Inscribe a un alumno en una materia validando las reglas académicas."""
    materia = repositories.materia_para_actualizar(materia.pk)

    if not alumno.activo:
        raise ValidationError({'alumno': 'El alumno no está activo.'})
    if not materia.activa:
        raise ValidationError({'materia': 'La materia no está activa.'})
    if repositories.tiene_inscripcion_vigente(alumno, materia):
        raise ValidationError({'materia': 'El alumno ya cursa o ya aprobó esta materia.'})

    faltantes = repositories.correlativas_no_aprobadas(alumno, materia)
    if faltantes.exists():
        codigos = ', '.join(m.codigo for m in faltantes)
        raise ValidationError({'materia': f'Faltan aprobar las correlativas: {codigos}.'})

    if repositories.cantidad_cursando(materia) >= materia.cupo:
        raise ValidationError({'materia': 'La materia no tiene cupo disponible.'})

    return repositories.crear_inscripcion(alumno, materia)


def calificar(inscripcion, nota):
    """Registra la nota final y marca la inscripción como aprobada o desaprobada."""
    if inscripcion.estado != Inscripcion.Estado.CURSANDO:
        raise ValidationError({'estado': 'Solo se pueden calificar inscripciones en curso.'})

    inscripcion.nota = nota
    inscripcion.estado = (
        Inscripcion.Estado.APROBADA if nota >= NOTA_MINIMA_APROBACION
        else Inscripcion.Estado.DESAPROBADA
    )
    return repositories.guardar(inscripcion, ['nota', 'estado'])


def dar_de_baja(inscripcion):
    """Da de baja una inscripción en curso, liberando el cupo."""
    if inscripcion.estado != Inscripcion.Estado.CURSANDO:
        raise ValidationError({'estado': 'Solo se pueden dar de baja inscripciones en curso.'})

    inscripcion.estado = Inscripcion.Estado.BAJA
    return repositories.guardar(inscripcion, ['estado'])
