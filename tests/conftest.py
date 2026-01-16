"""Pytest configuration for OrangeHRM test automation.

Contains fixtures for WebDriver setup/teardown and test assets.
"""
import os
import base64

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture(scope="session", autouse=True)
def ensure_test_assets():
    """Ensure required test assets exist before running tests.

    - Creates tests/test_data directory
    - Ensures profile_image.png exists (writes a tiny 1x1 PNG if missing)
    - Ensures sample_attachment.txt exists (writes placeholder if missing)
    """
    base_dir = os.path.dirname(__file__)
    data_dir = os.path.join(base_dir, "test_data")
    os.makedirs(data_dir, exist_ok=True)

    # Write a tiny transparent 1x1 PNG if missing
    png_path = os.path.join(data_dir, "profile_image.png")
    if not os.path.exists(png_path):
        tiny_png_b64 = (
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII="
        )
        with open(png_path, "wb") as f:
            f.write(base64.b64decode(tiny_png_b64))

    txt_path = os.path.join(data_dir, "sample_attachment.txt")
    if not os.path.exists(txt_path):
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("Sample attachment content for OrangeHRM personal details attachment test.\n")


@pytest.fixture(scope="function")
def driver():
    """
    WebDriver fixture that sets up and tears down the browser for each test.
    Uses Chrome browser with automatic driver management.
    """
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("--window-size=1920,1080")
    if os.getenv("HEADLESS", "0").lower() in ("1", "true", "yes"):
        chrome_options.add_argument("--headless=new")

    # Initialize Chrome WebDriver with webdriver-manager
    driver_path = ChromeDriverManager().install()
    if "THIRD_PARTY_NOTICES" in driver_path:
        driver_path = os.path.join(os.path.dirname(driver_path), "chromedriver")

    if os.path.exists(driver_path):
        try:
            os.chmod(driver_path, 0o755)
        except PermissionError:
            pass

    service = Service(driver_path)
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception:
        # Fallback to Selenium Manager-managed driver path
        driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)

    yield driver

    # Harden teardown to avoid occasional hang
    try:
        driver.quit()
    except Exception:
        try:
            driver.service.stop()
        except Exception:
            pass


@pytest.fixture(scope="session")
def base_url():
    return "https://opensource-demo.orangehrmlive.com"


@pytest.fixture(scope="session")
def login_credentials():
    return {"username": "Admin", "password": "admin123"}
