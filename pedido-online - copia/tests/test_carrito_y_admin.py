import os
import io
import time
import json
import requests
import mysql.connector
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@teste.com")
ADMIN_PASS  = os.getenv("ADMIN_PASS",  "123456")
CLIENT_EMAIL = os.getenv("CLIENT_EMAIL", "cliente@teste.com")
CLIENT_PASS  = os.getenv("CLIENT_PASS",  "123456")

def accept_alert_if_present(wait, driver, timeout=5):
    try:
        wait.until(EC.alert_is_present(), timeout)
        driver.switch_to.alert.accept()
    except Exception:
        pass

def wait_ready(driver, timeout=10):
    """Espera a que el documento esté completamente cargado."""
    end = time.time() + timeout
    while time.time() < end:
        state = driver.execute_script("return document.readyState")
        if state == "complete":
            return
        time.sleep(0.1)

def do_login(driver, wait, login_url, email, password):
    driver.get(login_url)
    wait_ready(driver)
    correo = EC.visibility_of_element_located((By.ID, "correo"))(driver)
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", correo)
    correo.clear(); correo.send_keys(email)
    contra = EC.visibility_of_element_located((By.ID, "contrasena"))(driver)
    contra.clear(); contra.send_keys(password)
    btn = EC.element_to_be_clickable((By.CSS_SELECTOR, "button"))(driver)
    btn.click()

def get_user_from_localstorage(driver):
    raw = driver.execute_script("return window.localStorage.getItem('usuario');")
    return json.loads(raw) if raw else None

def api_create_product(base_url, nombre, descripcion, precio, cantidad):
    png_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT\x08\x1dc`\x00\x00\x00\x02\x00\x01\xe2!\xbc3\x00\x00\x00\x00IEND\xaeB`\x82'
    files = {'imagen': ('test.png', io.BytesIO(png_bytes), 'image/png')}
    data = {'nombre': nombre, 'descripcion': descripcion, 'precio_unitario': str(precio), 'cantidad': str(cantidad)}
    r = requests.post(f"{base_url}/api/products/add", files=files, data=data, timeout=15)
    r.raise_for_status()
    return r.json()

def api_list_products(base_url):
    r = requests.get(f"{base_url}/api/products/list", timeout=10)
    r.raise_for_status()
    return r.json()

def find_product_by_name(base_url, nombre):
    for p in api_list_products(base_url):
        if p.get('nombre') == nombre:
            return p
    return None

def _screenshot(driver, name="fail_admin_ui.png"):
    try:
        driver.save_screenshot(name)
    except Exception:
        pass

def _try_open_admin_products_via_panel(driver, wait, base_login_url):
    """Si la página admin_productos.html no cargó, intenta entrar desde admin_panel.html."""
    panel_url = base_login_url.replace('login.html', 'admin_panel.html')
    driver.get(panel_url)
    wait_ready(driver)
    try:
        links = driver.find_elements(By.TAG_NAME, "a")
        for a in links:
            try:
                if "producto" in (a.text or "").lower():
                    a.click()
                    wait_ready(driver)
                    return
            except Exception:
                continue
        for a in links:
            try:
                href = a.get_attribute("href") or ""
                if "admin_productos.html" in href:
                    a.click()
                    wait_ready(driver)
                    return
            except Exception:
                continue
    except Exception:
        pass

def test_admin_puede_crear_producto_via_ui(driver, wait, settings):
    # Login admin
    do_login(driver, wait, settings["FRONTEND_URL"], ADMIN_EMAIL, ADMIN_PASS)
    accept_alert_if_present(wait, driver)

    # Ir al módulo de productos admin
    admin_prod_url = settings["FRONTEND_URL"].replace('login.html', 'admin_productos.html')
    driver.get(admin_prod_url)
    wait_ready(driver)

    btn_add = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Agregar Producto')]")))
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn_add)
    btn_add.click()

    form = wait.until(EC.visibility_of_element_located((By.ID, "formAgregarProducto")))

    def fill(locator, text):
        el = wait.until(EC.element_to_be_clickable(locator))
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        el.clear()
        el.send_keys(text)

    unico = str(int(time.time()))
    nombre = f"Producto UI {unico}"

    fill((By.ID, "nombre"), nombre)
    fill((By.ID, "descripcion"), "Creado por prueba UI")
    fill((By.ID, "precio_unitario"), "12.34")
    fill((By.ID, "cantidad"), "3")

    file_input = wait.until(EC.presence_of_element_located((By.ID, "imagen")))
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", file_input)
    png_path = os.path.abspath("test_tmp.png")
    with open(png_path, "wb") as f:
        f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT\x08\x1dc`\x00\x00\x00\x02\x00\x01\xe2!\xbc3\x00\x00\x00\x00IEND\xaeB`\x82')
    file_input.send_keys(png_path)

    # Click en "Guardar Producto"
    submit = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Guardar Producto')]")))
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", submit)
    submit.click()

    accept_alert_if_present(wait, driver)

    # Verificar que el producto aparece en la tabla
    found = False
    for _ in range(14):
        if nombre in driver.page_source:
            found = True
            break
        time.sleep(0.5)
    assert found, "No se encontró el producto creado en la tabla."

def test_cliente_no_puede_agregar_producto_sin_stock(driver, wait, settings):
    unico = str(int(time.time()))
    nombre = f"SinStock {unico}"
    api_create_product(settings["BACKEND_URL"], nombre, "Sin stock", 5.00, 0)
    prod = find_product_by_name(settings["BACKEND_URL"], nombre)
    assert prod is not None
    prod_id = prod['id_producto']
    stock = prod.get('cantidad_actual', 0) or 0

    do_login(driver, wait, settings["FRONTEND_URL"], CLIENT_EMAIL, CLIENT_PASS)
    accept_alert_if_present(wait, driver)

    productos_url = settings["FRONTEND_URL"].replace('login.html', 'productos_cliente.html')
    driver.get(productos_url); wait_ready(driver)

    driver.execute_script(f"document.getElementById('cantidad-{prod_id}').value = 1;")
    driver.execute_script(f"agregarAlCarrito({prod_id}, '{nombre}', 'Sin stock', 5.00, {stock});")
    accept_alert_if_present(wait, driver)

    usuario = get_user_from_localstorage(driver)
    carrito = driver.execute_script(f"return JSON.parse(window.localStorage.getItem('carrito_' + {usuario['id_usuario']})) || [];")
    assert all(item.get('id_producto') != prod_id for item in carrito), "Producto sin stock se añadió al carrito y no debería."

def test_cliente_agrega_con_stock_y_realiza_pedido(driver, wait, settings):
    unico = str(int(time.time()))
    nombre = f"ConStock {unico}"
    api_create_product(settings["BACKEND_URL"], nombre, "Con stock", 9.99, 5)
    prod = find_product_by_name(settings["BACKEND_URL"], nombre)
    assert prod is not None
    prod_id = prod['id_producto']
    stock = prod.get('cantidad_actual', 0) or 0

    do_login(driver, wait, settings["FRONTEND_URL"], CLIENT_EMAIL, CLIENT_PASS)
    accept_alert_if_present(wait, driver)

    productos_url = settings["FRONTEND_URL"].replace('login.html', 'productos_cliente.html')
    driver.get(productos_url); wait_ready(driver)

    driver.execute_script(f"document.getElementById('cantidad-{prod_id}').value = 2;")
    driver.execute_script(f"agregarAlCarrito({prod_id}, '{nombre}', 'Con stock', 9.99, {stock});")
    accept_alert_if_present(wait, driver)

    usuario = get_user_from_localstorage(driver)
    carrito = driver.execute_script(f"return JSON.parse(window.localStorage.getItem('carrito_' + {usuario['id_usuario']})) || [];")
    ids = [x.get('id_producto') for x in carrito]
    assert prod_id in ids, "El producto con stock no está en el carrito."

    carrito_url = settings["FRONTEND_URL"].replace('login.html', 'carrito.html')
    driver.get(carrito_url); wait_ready(driver)

    driver.execute_script("enviarPedido();")
    accept_alert_if_present(wait, driver)
    accept_alert_if_present(wait, driver)

    carrito_after = driver.execute_script(f"return JSON.parse(window.localStorage.getItem('carrito_' + {usuario['id_usuario']})) || [];")
    assert len(carrito_after) == 0, "El carrito no quedó vacío después de realizar el pedido."
