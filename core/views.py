# Vistas de la app.
from django.db.models import ProtectedError
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core import repositories, services
from core.permissions import EsStaffOSoloLectura
from core.serializers import (
    AlumnoSerializer,
    CalificacionSerializer,
    InscripcionSerializer,
    MateriaSerializer,
)


class ProtegidoContraBorradoMixin:
    """Devuelve 409 en vez de 500 si el registro tiene inscripciones asociadas."""

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {'detail': 'No se puede eliminar: tiene inscripciones asociadas. Marcalo como inactivo.'},
                status=status.HTTP_409_CONFLICT,
            )


class AlumnoViewSet(ProtegidoContraBorradoMixin, viewsets.ModelViewSet):
    serializer_class = AlumnoSerializer
    permission_classes = [EsStaffOSoloLectura]
    filterset_fields = ['activo']
    search_fields = ['legajo', 'dni', 'nombre', 'apellido', 'email']
    ordering_fields = ['legajo', 'apellido', 'nombre', 'creado']

    def get_queryset(self):
        return repositories.alumnos()

    @action(detail=True, methods=['get'])
    def inscripciones(self, request, pk=None):
        """Historial académico del alumno."""
        queryset = repositories.inscripciones_de_alumno(self.get_object())
        estado = request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        pagina = self.paginate_queryset(queryset)
        return self.get_paginated_response(InscripcionSerializer(pagina, many=True).data)


class MateriaViewSet(ProtegidoContraBorradoMixin, viewsets.ModelViewSet):
    serializer_class = MateriaSerializer
    permission_classes = [EsStaffOSoloLectura]
    filterset_fields = ['anio', 'cuatrimestre', 'activa']
    search_fields = ['codigo', 'nombre']
    ordering_fields = ['codigo', 'nombre', 'anio', 'cuatrimestre', 'cupo']

    def get_queryset(self):
        return repositories.materias()

    @action(detail=True, methods=['get'])
    def inscripciones(self, request, pk=None):
        """Alumnos inscriptos en la materia."""
        queryset = repositories.inscripciones_de_materia(self.get_object())
        estado = request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        pagina = self.paginate_queryset(queryset)
        return self.get_paginated_response(InscripcionSerializer(pagina, many=True).data)


class InscripcionViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Las inscripciones no se editan ni se borran: cambian de estado vía `calificar` y `baja`."""

    serializer_class = InscripcionSerializer
    permission_classes = [EsStaffOSoloLectura]
    filterset_fields = ['alumno', 'materia', 'estado']
    search_fields = ['alumno__legajo', 'alumno__apellido', 'materia__codigo', 'materia__nombre']
    ordering_fields = ['fecha_inscripcion', 'nota']

    def get_queryset(self):
        return repositories.inscripciones()

    def perform_create(self, serializer):
        datos = serializer.validated_data
        serializer.instance = services.inscribir(datos['alumno'], datos['materia'])

    @action(detail=True, methods=['post'])
    def calificar(self, request, pk=None):
        datos = CalificacionSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        inscripcion = services.calificar(self.get_object(), datos.validated_data['nota'])
        return Response(self.get_serializer(inscripcion).data)

    @action(detail=True, methods=['post'])
    def baja(self, request, pk=None):
        inscripcion = services.dar_de_baja(self.get_object())
        return Response(self.get_serializer(inscripcion).data)
