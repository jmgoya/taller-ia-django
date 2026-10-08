# Rutas de la app.
from rest_framework.routers import DefaultRouter

from core.views import AlumnoViewSet, InscripcionViewSet, MateriaViewSet

router = DefaultRouter()
router.register('alumnos', AlumnoViewSet, basename='alumno')
router.register('materias', MateriaViewSet, basename='materia')
router.register('inscripciones', InscripcionViewSet, basename='inscripcion')

urlpatterns = router.urls
