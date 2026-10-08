# Taller de IA — Repositorio base (Django + DRF)

Este repositorio es el **punto de partida del Taller de IA** de Programación IV:
un proyecto **Django + Django REST Framework** ya inicializado y funcionando,
con la estructura de carpetas lista y sin lógica de negocio.

## Stack

- Python 3 + entorno virtual (`venv`)
- Django + Django REST Framework
- Autenticación JWT con `djangorestframework-simplejwt`
- Filtrado, búsqueda, ordenamiento y paginación con `django-filter`
- CORS con `django-cors-headers`
- Configuración por variables de entorno (`.env` + `python-dotenv`)
- Base de datos SQLite (sin configuración adicional)

## Estructura

```
.
├── config/                 # Proyecto Django
│   ├── settings.py         # Configuración (lee .env, DRF, JWT, CORS)
│   ├── urls.py             # Router de DRF + /api/health/ + /api/token/
│   ├── views.py            # Vista del health check
│   ├── asgi.py / wsgi.py
├── core/                   # App principal
│   ├── models.py           # Modelos
│   ├── serializers.py      # Serializers
│   ├── views.py            # Vistas
│   ├── urls.py             # Rutas de la app
│   ├── admin.py            # Registro en el admin
│   ├── permissions.py      # Permisos personalizados
│   ├── services.py         # Lógica de negocio
│   ├── repositories.py     # Acceso a datos
│   └── tests.py            # Tests
├── .env.example            # Variables de entorno necesarias (sin valores)
├── PROMPT_PARA_LA_IA.md    # Contexto del proyecto para la IA
├── manage.py
└── requirements.txt
```

Cada archivo de `core/` tiene un comentario de encabezado que indica qué va ahí.

`PROMPT_PARA_LA_IA.md` describe el stack y la estructura del proyecto para que
la herramienta de IA sepa en qué tipo de proyecto está trabajando.

## Cómo levantarlo

```bash
# 1. Clonar el repositorio
git clone <URL-DEL-REPO>
cd <carpeta-del-repo>

# 2. Crear y activar el entorno virtual
python -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Aplicar migraciones y levantar el servidor
python manage.py migrate
python manage.py runserver
```

> No hace falta crear un `.env`: sin él, el proyecto arranca con una clave de
> desarrollo y `DEBUG=True`. Si querés usar tus propios valores, copiá
> `.env.example` como `.env` y completalo. El `.env` **no se commitea**.

### Verificar que funciona

```bash
curl http://127.0.0.1:8000/api/health/
# {"status":"ok"}
```

### Endpoints disponibles de entrada

| Método | Ruta                   | Descripción                               | Auth      |
|--------|------------------------|-------------------------------------------|-----------|
| GET    | `/api/health/`         | Chequeo de que el entorno arrancó         | Pública   |
| POST   | `/api/token/`          | Obtener `access` y `refresh` (JWT)        | Pública   |
| POST   | `/api/token/refresh/`  | Renovar el `access` token                 | Pública   |
| GET    | `/api/`                | Raíz del router de DRF (vacía por ahora)  | Pública   |
| —      | `/admin/`              | Panel de administración de Django         | Sesión    |

Los endpoints son públicos por defecto (`AllowAny`). JWT está instalado y
disponible: para obtener un token necesitás un usuario
(`python manage.py createsuperuser`) y lo enviás en el header
`Authorization: Bearer <access>`.
