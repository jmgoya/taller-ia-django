# Tests de la app.
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Alumno, Inscripcion, Materia


class BaseTestCase(APITestCase):
    def setUp(self):
        self.staff = get_user_model().objects.create_user('admin', password='x', is_staff=True)
        self.client.force_authenticate(self.staff)
        self.alumno = Alumno.objects.create(
            legajo='1001', dni='30111222', nombre='Ana', apellido='García', email='ana@uni.edu',
        )
        self.prog1 = Materia.objects.create(
            codigo='PRG1', nombre='Programación I', anio=1, cuatrimestre=1, carga_horaria=96, cupo=2,
        )
        self.prog2 = Materia.objects.create(
            codigo='PRG2', nombre='Programación II', anio=1, cuatrimestre=2, carga_horaria=96, cupo=30,
        )
        self.prog2.correlativas.add(self.prog1)

    def inscribir(self, alumno, materia):
        return self.client.post('/api/inscripciones/', {'alumno': alumno.pk, 'materia': materia.pk})


class PermisosTests(BaseTestCase):
    def test_lectura_publica(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get('/api/alumnos/').status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get('/api/materias/').status_code, status.HTTP_200_OK)

    def test_escritura_requiere_staff(self):
        self.client.force_authenticate(None)
        respuesta = self.client.post('/api/alumnos/', {})
        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)

        comun = get_user_model().objects.create_user('comun', password='x')
        self.client.force_authenticate(comun)
        respuesta = self.client.post('/api/alumnos/', {})
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)


class AlumnoTests(BaseTestCase):
    def test_crear_alumno(self):
        respuesta = self.client.post('/api/alumnos/', {
            'legajo': '1002', 'dni': '30999888', 'nombre': 'Luis',
            'apellido': 'Pérez', 'email': 'luis@uni.edu',
        })
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Alumno.objects.count(), 2)

    def test_legajo_duplicado(self):
        respuesta = self.client.post('/api/alumnos/', {
            'legajo': '1001', 'dni': '1', 'nombre': 'X', 'apellido': 'Y', 'email': 'x@uni.edu',
        })
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('legajo', respuesta.data)

    def test_buscar_por_apellido(self):
        respuesta = self.client.get('/api/alumnos/?search=garc')
        self.assertEqual(respuesta.data['count'], 1)

    def test_no_borra_alumno_con_inscripciones(self):
        self.inscribir(self.alumno, self.prog1)
        respuesta = self.client.delete(f'/api/alumnos/{self.alumno.pk}/')
        self.assertEqual(respuesta.status_code, status.HTTP_409_CONFLICT)


class MateriaTests(BaseTestCase):
    def test_cupo_disponible(self):
        self.inscribir(self.alumno, self.prog1)
        respuesta = self.client.get(f'/api/materias/{self.prog1.pk}/')
        self.assertEqual(respuesta.data['inscriptos'], 1)
        self.assertEqual(respuesta.data['cupo_disponible'], 1)

    def test_no_es_correlativa_de_si_misma(self):
        respuesta = self.client.patch(
            f'/api/materias/{self.prog1.pk}/', {'correlativas': [self.prog1.pk]}, format='json',
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filtrar_por_anio(self):
        respuesta = self.client.get('/api/materias/?cuatrimestre=2')
        self.assertEqual([m['codigo'] for m in respuesta.data['results']], ['PRG2'])


class InscripcionTests(BaseTestCase):
    def test_inscripcion_exitosa(self):
        respuesta = self.inscribir(self.alumno, self.prog1)
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(respuesta.data['estado'], Inscripcion.Estado.CURSANDO)

    def test_no_permite_inscripcion_duplicada(self):
        self.inscribir(self.alumno, self.prog1)
        respuesta = self.inscribir(self.alumno, self.prog1)
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_exige_correlativas(self):
        respuesta = self.inscribir(self.alumno, self.prog2)
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('PRG1', str(respuesta.data))

    def test_con_correlativa_aprobada_puede_inscribirse(self):
        inscripcion = self.inscribir(self.alumno, self.prog1).data
        self.client.post(f'/api/inscripciones/{inscripcion["id"]}/calificar/', {'nota': 8})
        respuesta = self.inscribir(self.alumno, self.prog2)
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)

    def test_respeta_cupo(self):
        otros = [
            Alumno.objects.create(legajo=f'2{i}', dni=f'4{i}', nombre='N', apellido='A', email=f'{i}@u.edu')
            for i in range(2)
        ]
        for otro in otros:
            self.assertEqual(self.inscribir(otro, self.prog1).status_code, status.HTTP_201_CREATED)
        respuesta = self.inscribir(self.alumno, self.prog1)
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cupo', str(respuesta.data))

    def test_baja_libera_cupo_y_permite_reinscribirse(self):
        inscripcion = self.inscribir(self.alumno, self.prog1).data
        respuesta = self.client.post(f'/api/inscripciones/{inscripcion["id"]}/baja/')
        self.assertEqual(respuesta.data['estado'], Inscripcion.Estado.BAJA)
        self.assertEqual(self.inscribir(self.alumno, self.prog1).status_code, status.HTTP_201_CREATED)

    def test_alumno_inactivo_no_puede_inscribirse(self):
        self.alumno.activo = False
        self.alumno.save()
        respuesta = self.inscribir(self.alumno, self.prog1)
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_calificar(self):
        inscripcion = self.inscribir(self.alumno, self.prog1).data
        url = f'/api/inscripciones/{inscripcion["id"]}/calificar/'
        respuesta = self.client.post(url, {'nota': 2})
        self.assertEqual(respuesta.data['estado'], Inscripcion.Estado.DESAPROBADA)
        # Ya no está en curso: no se puede volver a calificar.
        self.assertEqual(self.client.post(url, {'nota': 9}).status_code, status.HTTP_400_BAD_REQUEST)

    def test_nota_fuera_de_rango(self):
        inscripcion = self.inscribir(self.alumno, self.prog1).data
        respuesta = self.client.post(f'/api/inscripciones/{inscripcion["id"]}/calificar/', {'nota': 11})
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_historial_del_alumno(self):
        self.inscribir(self.alumno, self.prog1)
        respuesta = self.client.get(f'/api/alumnos/{self.alumno.pk}/inscripciones/')
        self.assertEqual(respuesta.data['count'], 1)
        respuesta = self.client.get(f'/api/materias/{self.prog1.pk}/inscripciones/?estado=CURSANDO')
        self.assertEqual(respuesta.data['count'], 1)
