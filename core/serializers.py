# Serializers de la app.
from rest_framework import serializers

from core import repositories
from core.models import Alumno, Inscripcion, Materia


class AlumnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alumno
        fields = [
            'id', 'legajo', 'dni', 'nombre', 'apellido', 'email',
            'fecha_nacimiento', 'activo', 'creado', 'actualizado',
        ]
        read_only_fields = ['creado', 'actualizado']


class MateriaResumenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Materia
        fields = ['id', 'codigo', 'nombre']


class MateriaSerializer(serializers.ModelSerializer):
    correlativas = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Materia.objects.all(), required=False,
    )
    correlativas_detalle = MateriaResumenSerializer(source='correlativas', many=True, read_only=True)
    cuatrimestre_display = serializers.CharField(source='get_cuatrimestre_display', read_only=True)
    inscriptos = serializers.SerializerMethodField()
    cupo_disponible = serializers.SerializerMethodField()

    class Meta:
        model = Materia
        fields = [
            'id', 'codigo', 'nombre', 'descripcion', 'anio', 'cuatrimestre',
            'cuatrimestre_display', 'carga_horaria', 'cupo', 'inscriptos',
            'cupo_disponible', 'correlativas', 'correlativas_detalle', 'activa',
            'creado', 'actualizado',
        ]
        read_only_fields = ['creado', 'actualizado']

    def get_inscriptos(self, obj):
        # En los listados viene anotado; tras crear/editar se calcula.
        if not hasattr(obj, 'inscriptos'):
            obj.inscriptos = repositories.cantidad_cursando(obj)
        return obj.inscriptos

    def get_cupo_disponible(self, obj):
        return max(obj.cupo - self.get_inscriptos(obj), 0)

    def validate_correlativas(self, value):
        if self.instance and self.instance in value:
            raise serializers.ValidationError('Una materia no puede ser correlativa de sí misma.')
        return value


class InscripcionSerializer(serializers.ModelSerializer):
    alumno = serializers.PrimaryKeyRelatedField(queryset=Alumno.objects.all())
    materia = serializers.PrimaryKeyRelatedField(queryset=Materia.objects.all())
    alumno_detalle = serializers.StringRelatedField(source='alumno', read_only=True)
    materia_detalle = MateriaResumenSerializer(source='materia', read_only=True)

    class Meta:
        model = Inscripcion
        fields = [
            'id', 'alumno', 'alumno_detalle', 'materia', 'materia_detalle',
            'estado', 'nota', 'fecha_inscripcion', 'actualizado',
        ]
        read_only_fields = ['estado', 'nota', 'fecha_inscripcion', 'actualizado']


class CalificacionSerializer(serializers.Serializer):
    nota = serializers.IntegerField(min_value=1, max_value=10)
