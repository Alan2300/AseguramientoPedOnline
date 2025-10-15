# ========== PIPELINE LOCAL ==========

# Crear entorno virtual
setup:
	python -m venv venv
	venv/Scripts/activate && pip install -r requirements.txt

# Ejecutar pruebas
test:
	venv/Scripts/activate && pytest -v

# Revisar formato del código
lint:
	venv/Scripts/activate && flake8 backend/

# Iniciar servidor local Flask
run:
	venv/Scripts/activate && set FLASK_APP=backend/app.py && set FLASK_ENV=development && flask run

# Actualizar dependencias
update:
	venv/Scripts/activate && pip freeze > requirements.txt
