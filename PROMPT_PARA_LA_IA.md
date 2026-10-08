# Prompt para la IA

Copiá el bloque de abajo, **reemplazá todo lo que está entre `<< >>`** con la
descripción de tu dominio y pegalo en tu herramienta de IA (junto con acceso al
repositorio, o pegando el contenido de los archivos que te pida).

---

```text
Tengo un proyecto Django + Django REST Framework ya armado (repositorio base de un
taller). Necesito que implementes la API completa de mi dominio DENTRO de la
estructura existente, sin cambiar el stack ni la organización de carpetas.

## Estructura existente (NO la cambies)

- Proyecto Django: `config` (settings.py, urls.py, views.py con /api/health/).
- App: `core`, con estos archivos ya creados (cada uno tiene un comentario que
  indica qué va ahí):
  - core/models.py        -> modelos
  - core/serializers.py   -> serializers
  - core/views.py         -> ViewSets
  - core/permissions.py   -> permisos personalizados
  - core/services.py      -> lógica de negocio
  - core/repositories.py  -> consultas al ORM reutilizables
  - core/exceptions.py    -> manejador de excepciones centralizado
  - core/admin.py         -> registro en el admin
  - core/urls.py          -> rutas extra que NO son ViewSets
  - core/tests.py         -> tests
- En config/urls.py ya existe `router = DefaultRouter()` incluido bajo `/api/`.
  Registrá ahí los ViewSets.
- Ya están configurados en config/settings.py: JWT (simplejwt) como autenticación
  por defecto, `IsAuthenticated` como permiso por defecto, `DjangoFilterBackend`,
  `SearchFilter` y `OrderingFilter` como filtros por defecto, y paginación
  `PageNumberPagination` con `PAGE_SIZE = 10`.
- Ya existen /api/token/ y /api/token/refresh/. Base de datos: SQLite.
- La configuración sensible se lee de `.env` con python-dotenv.

## Mi dominio

Nombre del proyecto: <<NOMBRE DE TU API, ej.: "TaskFlow">>

Descripción breve: <<QUÉ PROBLEMA RESUELVE, en 2 o 3 oraciones>>

Entidades (modelos) y sus campos:
<<Por cada modelo, listá sus campos con tipo y restricciones. Ejemplo:
- Project: name (texto, máx. 100, obligatorio), description (texto largo, opcional),
  owner (FK a User), members (M2M a User), created_at (auto).
- Task: title (texto, máx. 200), description (opcional), status (choices: todo,
  in_progress, done; default todo), priority (choices: low, medium, high),
  due_date (fecha, opcional), project (FK a Project), assigned_to (FK a User,
  opcional), tags (M2M a Tag), created_at, updated_at.
- Tag: name (texto, único).>>

Relaciones importantes: <<ej.: un Project tiene muchas Task; una Task puede tener
varios Tag; un usuario puede ser miembro de varios Project>>

Reglas de negocio / validaciones: <<ej.: due_date no puede estar en el pasado;
solo el owner puede borrar un Project; no se puede pasar una Task a "done" si
no tiene assigned_to>>

Permisos: <<ej.: solo el dueño puede editar o borrar; los miembros pueden leer;
cualquier usuario autenticado puede crear>>

Filtros, búsqueda y ordenamiento: <<ej.: Task filtrable por status, priority y
project; búsqueda por title; ordenable por due_date y created_at>>

## Qué tenés que generar (respetando estas convenciones)

1. **Modelos** en core/models.py: con `__str__`, `class Meta` (ordering,
   verbose_name), `choices` donde corresponda, `related_name` en las relaciones
   y `created_at`/`updated_at` con `auto_now_add`/`auto_now`. Usá
   `settings.AUTH_USER_MODEL` para referenciar al usuario.
2. **Serializers** en core/serializers.py: usá `serializers.ModelSerializer`,
   con `fields` explícitos (no `'__all__'`), `read_only_fields` para ids, fechas
   y owner, y validaciones con `validate_<campo>` / `validate`.
3. **ViewSets** en core/views.py: usá `viewsets.ModelViewSet`, con `queryset`
   (con `select_related`/`prefetch_related`), `serializer_class`,
   `permission_classes`, `filterset_fields`, `search_fields` y `ordering_fields`.
   Asigná el usuario autenticado en `perform_create`. Si un usuario solo debe
   ver sus datos, filtrá en `get_queryset`.
4. **Permisos personalizados** en core/permissions.py heredando de
   `permissions.BasePermission` (ej.: `IsOwnerOrReadOnly`).
5. **Lógica de negocio** que no sea trivial en core/services.py y consultas
   reutilizables en core/repositories.py. Las vistas deben quedar delgadas.
6. **Manejador de excepciones centralizado** en core/exceptions.py
   (`custom_exception_handler`, que envuelva el `exception_handler` de DRF y
   devuelva un formato de error uniforme) y activalo descomentando
   `EXCEPTION_HANDLER` en `REST_FRAMEWORK` de config/settings.py.
7. **Router**: registrá cada ViewSet en el `router` de config/urls.py con
   `router.register(...)` y un `basename`. No crees otro router.
8. **Admin**: registrá todos los modelos en core/admin.py con `@admin.register`,
   `list_display`, `list_filter` y `search_fields`.
9. **Tests** básicos en core/tests.py con `APITestCase` (crear, listar,
   permisos denegados sin token).

## Restricciones

- NO cambies settings.py salvo para activar EXCEPTION_HANDLER.
- NO agregues dependencias nuevas fuera de requirements.txt.
- NO uses Docker ni otra base de datos: SQLite.
- Nombres de clases y campos en inglés; comentarios y docstrings en español.
- Al final, indicame los comandos para generar y aplicar las migraciones
  (`python manage.py makemigrations core` y `python manage.py migrate`) y
  ejemplos de requests (con el header `Authorization: Bearer <token>`) para
  probar cada endpoint.

Mostrame el contenido completo de cada archivo que crees o modifiques.
```
