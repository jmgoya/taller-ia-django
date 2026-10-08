# Modelos de la app.
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

NOTA_MINIMA_APROBACION = 4


class Alumno(models.Model):
    legajo = models.CharField(max_length=20, unique=True)
    dni = models.CharField(max_length=15, unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['apellido', 'nombre']

    def __str__(self):
        return f'{self.apellido}, {self.nombre} ({self.legajo})'


class Materia(models.Model):
    class Cuatrimestre(models.IntegerChoices):
        ANUAL = 0, 'Anual'
        PRIMERO = 1, 'Primer cuatrimestre'
        SEGUNDO = 2, 'Segundo cuatrimestre'

    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    anio = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(6)],
        help_text='Año de la carrera en que se dicta (1 a 6).',
    )
    cuatrimestre = models.PositiveSmallIntegerField(choices=Cuatrimestre.choices)
    carga_horaria = models.PositiveSmallIntegerField(help_text='Horas totales.')
    cupo = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    correlativas = models.ManyToManyField(
        'self', symmetrical=False, blank=True, related_name='habilita',
        help_text='Materias que hay que tener aprobadas para inscribirse.',
    )
    activa = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['anio', 'cuatrimestre', 'nombre']

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'


class Inscripcion(models.Model):
    class Estado(models.TextChoices):
        CURSANDO = 'CURSANDO', 'Cursando'
        APROBADA = 'APROBADA', 'Aprobada'
        DESAPROBADA = 'DESAPROBADA', 'Desaprobada'
        BAJA = 'BAJA', 'Baja'

    alumno = models.ForeignKey(Alumno, on_delete=models.PROTECT, related_name='inscripciones')
    materia = models.ForeignKey(Materia, on_delete=models.PROTECT, related_name='inscripciones')
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.CURSANDO)
    nota = models.PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_inscripcion']
        verbose_name_plural = 'inscripciones'

    def __str__(self):
        return f'{self.alumno.legajo} en {self.materia.codigo} ({self.estado})'
