# Contexto del proyecto

Este repositorio es un proyecto **Python + Django + Django REST Framework** ya
inicializado y funcionando. Trabajá dentro de esta estructura y con este stack.

## Stack instalado (`requirements.txt`)

- Django
- djangorestframework
- djangorestframework-simplejwt
- django-filter
- django-cors-headers
- python-dotenv

No hay otras dependencias. La base de datos es **SQLite** (`db.sqlite3`).

## Estructura

```
config/            # Proyecto Django
  settings.py      # Configuración (lee variables desde .env)
  urls.py          # URLs raíz. Incluye un DefaultRouter de DRF vacío bajo /api/
  views.py         # Vista de /api/health/
core/              # App de Django (registrada en INSTALLED_APPS)
  models.py
  serializers.py
  views.py
  urls.py          # Incluido bajo /api/
  admin.py
  permissions.py
  services.py
  repositories.py
  tests.py
manage.py
```

## Configuración ya existente en `config/settings.py`

- `INSTALLED_APPS` incluye `rest_framework`, `rest_framework_simplejwt`,
  `django_filters`, `corsheaders` y `core`.
- `REST_FRAMEWORK`:
  - Autenticación: `JWTAuthentication`.
  - Permiso por defecto: `AllowAny` (JWT instalado pero no exigido).
  - Filtros: `DjangoFilterBackend`, `SearchFilter`, `OrderingFilter`.
  - Paginación: `PageNumberPagination`, `PAGE_SIZE = 10`.

## Endpoints existentes

- `GET  /api/health/`: chequeo de estado (público).
- `POST /api/token/` y `POST /api/token/refresh/`: tokens JWT.
- `/admin/`: admin de Django.

## Comandos

- Entorno virtual: `venv/`
- Migraciones: `python manage.py makemigrations` y `python manage.py migrate`
- Servidor: `python manage.py runserver`
