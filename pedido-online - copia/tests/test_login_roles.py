import os
import time
import requests
import mysql.connector
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@teste.com")
ADMIN_PASS  = os.getenv("ADMIN_PASS",  "123456")
CLIENT_EMAIL = os.getenv("CLIENT_EMAIL", "cliente@teste.com")
CLIENT_PASS  = os.getenv("CLIENT_PASS",  "123456")

def seed_users(settings):
    """Ensure admin and client exist with proper roles.
    - Registers both via API (hashing handled by backend)
    - Promotes admin user to role 1 directly in DB if necessary
    """
    backend = settings["BACKEND_URL"]
    try:
        requests.post(f"{backend}/api/users/register", json={
            "nombre": "Cliente Prueba",
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASS
        }, timeout=5)
    except Exception:
        pass

    try:
        requests.post(f"{backend}/api/users/register", json={
            "nombre": "AdminTeste",
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASS
        }, timeout=5)
    except Exception:
        pass

    try:
        conn = mysql.connector.connect(
            host=settings["DB_HOST"],
            user=settings["DB_USER"],
            password=settings["DB_PASS"],
            database=settings["DB_NAME"],
        )
        cur = conn.cursor()
        cur.execute("UPDATE usuarios SET id_rol = 1 WHERE email = %s", (ADMIN_EMAIL,))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:

        print("WARNING: Could not promote admin to role 1:", e)

def do_login(driver, wait, login_url, email, password):
    driver.get(login_url)
    driver.find_element(By.ID, "correo").clear()
    driver.find_element(By.ID, "correo").send_keys(email)
    driver.find_element(By.ID, "contrasena").clear()
    driver.find_element(By.ID, "contrasena").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "button").click()

def accept_alert_if_present(wait, driver, timeout=3):
    """Si aparece un alert() de JS, lo acepta para que no bloquee la prueba."""
    try:
        wait.until(EC.alert_is_present(), timeout)
        driver.switch_to.alert.accept()
    except Exception:
        # No hubo alert en el tiempo dado
        pass

def test_login_admin_redirige_a_panel_admin(driver, wait, settings):
    seed_users(settings)
    do_login(driver, wait, settings["FRONTEND_URL"], ADMIN_EMAIL, ADMIN_PASS)
    accept_alert_if_present(wait, driver)
    wait.until(EC.url_contains("admin_panel.html"))
    assert "admin_panel.html" in driver.current_url

def test_login_cliente_redirige_a_panel_cliente(driver, wait, settings):
    seed_users(settings)
    do_login(driver, wait, settings["FRONTEND_URL"], CLIENT_EMAIL, CLIENT_PASS)
    accept_alert_if_present(wait, driver)
    wait.until(EC.url_contains("user_panel.html"))
    assert "user_panel.html" in driver.current_url

def test_login_invalido_muestra_error(driver, wait, settings):
    do_login(driver, wait, settings["FRONTEND_URL"], "noexiste@ejemplo.com", "mal")
    # Expect an error message in #error
    err = wait.until(EC.visibility_of_element_located((By.ID, "error")))
    assert "incorrecta" in err.text.lower() or "obligatorio" in err.text.lower() or "error" in err.text.lower()
