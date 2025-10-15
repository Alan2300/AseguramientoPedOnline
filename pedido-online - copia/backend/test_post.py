# test_post.py
import requests

url = 'http://127.0.0.1:5000/api/products/'
payload = {
    "nombre": "Anillo de oro",
    "descripcion": "18K",
    "precio_unitario": 150.00,
    "cantidad_actual": 20,
    "ubicacion": "Estantería B2"
}

resp = requests.post(url, json=payload)
print("Status:", resp.status_code)
try:
    print("Respuesta JSON:", resp.json())
except Exception:
    print("Respuesta no es JSON:", resp.text)
