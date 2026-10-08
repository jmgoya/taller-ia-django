# Taller de IA — Repositorio base (Django + DRF)

Este repositorio es el **punto de partida del Taller de IA** de Programación IV.
Es un esqueleto de proyecto **Django + Django REST Framework** que ya arranca y
funciona, pero que **no tiene lógica de negocio**: no hay modelos, serializers ni
ViewSets. Esa parte la vas a generar vos con ayuda de una IA.

La estructura y las convenciones son las mismas que usamos en las clases para
construir **TaskFlow** (gestión colaborativa de proyectos y tareas), así que lo
que generes debería verse igual a lo que vimos en clase.

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
├── core/                   # App principal (acá trabaja la IA)
│   ├── models.py           # Modelos del dominio
│   ├── serializers.py      # ModelSerializer de cada modelo
│   ├── views.py            # ModelViewSet de cada modelo
│   ├── urls.py             # Rutas extra que no son ViewSets
│   ├── admin.py            # Registro en el admin
│   ├── permissions.py      # Permisos personalizados
│   ├── services.py         # Lógica de negocio
│   ├── repositories.py     # Consultas al ORM reutilizables
│   ├── exceptions.py       # Manejador de excepciones centralizado
│   └── tests.py            # Tests de la API
├── .env.example            # Variables de entorno necesarias (sin valores)
├── PROMPT_PARA_LA_IA.md    # Prompt de ejemplo para pasarle a la IA
├── manage.py
└── requirements.txt
```

Cada archivo de `core/` tiene un comentario de encabezado que indica qué va ahí.

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

# 4. Crear el archivo .env a partir del ejemplo y completarlo
cp .env.example .env
#   SECRET_KEY=<una clave larga y aleatoria>
#   DEBUG=True
#   ALLOWED_HOSTS=localhost,127.0.0.1
#   Podés generar una SECRET_KEY con:
#   python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"

# 5. Aplicar migraciones y levantar el servidor
python manage.py migrate
python manage.py runserver
```

> **Importante:** el archivo `.env` contiene secretos y **no se commitea**
> (está en `.gitignore`). Solo se versiona `.env.example`.

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
| GET    | `/api/`                | Raíz del router de DRF (vacía por ahora)  | JWT       |
| —      | `/admin/`              | Panel de administración de Django         | Sesión    |

Para obtener un token necesitás un usuario: `python manage.py createsuperuser`.
Después usás el token en el header: `Authorization: Bearer <access>`.

## ¿Qué vas a hacer en el taller?

1. Elegí un dominio de datos (puede ser TaskFlow u otro tema: biblioteca,
   turnos médicos, inventario, etc.).
2. Abrí [`PROMPT_PARA_LA_IA.md`](PROMPT_PARA_LA_IA.md), completá los
   placeholders con la descripción de tu dominio y pasáselo a tu herramienta de IA.
3. La IA debe completar **dentro de esta estructura** los modelos, serializers,
   ViewSets, permisos, el registro en el router y el admin.
4. Revisá lo generado, corré `python manage.py makemigrations` y
   `python manage.py migrate`, y probá los endpoints.
5. Compará el resultado con las convenciones vistas en clase: ¿la IA respetó la
   estructura? ¿Qué tuviste que corregir?
