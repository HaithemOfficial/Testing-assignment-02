"""Pytest configuration for OrangeHRM test automation.

Contains fixtures for WebDriver setup and teardown.
"""
import os

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture(scope="function")
def driver():
    """
    WebDriver fixture that sets up and tears down the browser for each test.
    Uses Chrome browser with automatic driver management.
    """
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--window-size=1920,1080")
    if os.getenv("HEADLESS", "0").lower() in ("1", "true", "yes"): 
        chrome_options.add_argument("--headless=new")
    
    # Initialize Chrome WebDriver
    # Work around webdriver-manager occasionally pointing to
    # a non-executable THIRD_PARTY_NOTICES.chromedriver file and
    # ensure the binary has execute permissions.
    driver_path = ChromeDriverManager().install()
    if "THIRD_PARTY_NOTICES" in driver_path:
        driver_path = os.path.join(os.path.dirname(driver_path), "chromedriver")

    if os.path.exists(driver_path):
        try:
            os.chmod(driver_path, 0o755)
        except PermissionError:
            # If we cannot change permissions, let Selenium raise a clear error.
            pass

    service = Service(driver_path)
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception:
        # Fallback to Selenium Manager-managed driver path
        driver = webdriver.Chrome(options=chrome_options)
    
    # Set implicit wait as fallback
    driver.implicitly_wait(10)
    
    yield driver
    
    # Teardown: Close browser after test
    try:
        driver.quit()
    except Exception:
        try:
            driver.service.stop()
        except Exception:
            pass


@pytest.fixture(scope="session")
def base_url():
    """
    Fixture that provides the base URL for the OrangeHRM application.
    """
    return "https://opensource-demo.orangehrmlive.com"


@pytest.fixture(scope="session")
def login_credentials():
    """
    Fixture that provides login credentials for the OrangeHRM application.
    """
    return {
        "username": "Admin",
        "password": "admin123"
    }
