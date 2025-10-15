# Pruebas E2E con Selenium + Pytest

Estas pruebas automatizadas validan:
- **Login admin** redirige a `admin_panel.html`
- **Login cliente** redirige a `user_panel.html`
- **Login inválido** muestra error en `#error`

## Requisitos
- Python 3.10+
- Google Chrome instalado (Selenium Manager descarga el driver automáticamente)
- MySQL corriendo con la base `pedido_online_db` (usa `bdPedidos.sql` si no la tienes)
- Backend Flask corriendo en `http://127.0.0.1:5000` (ver `backend/app.py`)
- Frontend servido como estático (p. ej., `http://localhost:8000`)

## Instalar dependencias
```bash
pip install selenium pytest requests mysql-connector-python
```

## Levantar servicios locales
En una terminal, backend:
```bash
cd backend
python app.py
# Servirá en http://127.0.0.1:5000
```

En otra terminal, frontend (servidor simple):
```bash
cd frontend
python -m http.server 8000
# Abre http://localhost:8000/login.html
```

## Variables de entorno (opcional)
- `FRONTEND_URL`: URL completa del login (por defecto `http://localhost:8000/login.html`)
- `BACKEND_URL`: URL base del API (por defecto `http://127.0.0.1:5000`)
- `DB_HOST`, `DB_USER`, `DB_PASS`, `DB_NAME`: para promover el admin a rol 1
- `ADMIN_EMAIL`, `ADMIN_PASS`, `CLIENT_EMAIL`, `CLIENT_PASS`: credenciales de prueba

## Ejecutar pruebas
```bash
cd tests
pytest -v
```

## Notas
- El *seeding* registra usuarios vía API y luego **promueve** al admin a `id_rol=1` en MySQL.
- Si no puede conectar a MySQL, la prueba de admin podría fallar por falta de rol. Revisa credenciales.
- Si cambiaste los IDs de los inputs en `login.html`, ajusta los selectores en `tests/test_login_roles.py`.
