import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8000/login.html")


BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:5000")

@pytest.fixture(scope="session")
def settings():
    return {
        "FRONTEND_URL": FRONTEND_URL,
        "BACKEND_URL": BACKEND_URL,
        "DB_HOST": os.getenv("DB_HOST", "localhost"),
        "DB_USER": os.getenv("DB_USER", "root"),
        "DB_PASS": os.getenv("DB_PASS", ""),
        "DB_NAME": os.getenv("DB_NAME", "pedido_online_db"),
    }

@pytest.fixture
def driver():
    opts = Options()
    d = webdriver.Chrome(options=opts)
    d.set_window_size(1280, 900)
    yield d
    d.quit()

@pytest.fixture
def wait(driver):
    return WebDriverWait(driver, 10)
