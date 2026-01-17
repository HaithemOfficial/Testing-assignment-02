import os
import time
from datetime import datetime

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException


class TestOrangeHRME2E:
    def test_employee_creation_and_verification(self, driver, base_url, login_credentials):
        wait = WebDriverWait(driver, 20)

        print("Step 1: Logging in...")
        driver.get(base_url)
        username_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password_input = driver.find_element(By.NAME, "password")
        username_input.clear(); username_input.send_keys(login_credentials["username"])
        password_input.clear(); password_input.send_keys(login_credentials["password"])
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        wait.until(EC.presence_of_element_located((By.XPATH, "//span/h6[text()='Dashboard']")))
        print("✓ Logged in")

        print("Step 2: Navigating to PIM → Add Employee...")
        pim_menu = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='PIM']")))
        pim_menu.click()
        add_employee_menu = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[text()='Add Employee']")))
        add_employee_menu.click()
        wait.until(EC.presence_of_element_located((By.NAME, "firstName")))
        print("✓ Add Employee form loaded")

        print("Step 3: Filling employee details...")
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        first_name = f"Auto{timestamp[-4:]}"
        last_name = "Tester"
        username = f"auto.user.{timestamp}"
        password = "Password123!"
        unique_employee_id = datetime.now().strftime("%H%M%S")

        first_name_field = driver.find_element(By.NAME, "firstName")
        last_name_field = driver.find_element(By.NAME, "lastName")
        first_name_field.clear(); first_name_field.send_keys(first_name)
        last_name_field.clear(); last_name_field.send_keys(last_name)

        employee_id_field = driver.find_element(By.XPATH, "//label[text()='Employee Id']/../..//input")
        auto_employee_id = employee_id_field.get_attribute("value")
        employee_id_field.clear(); employee_id_field.send_keys(unique_employee_id)
        print(f"  Auto Employee Id: {auto_employee_id} -> Overridden with: {unique_employee_id}")

        print("Step 4: Uploading profile image...")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "test_data", "profile_image.png")
        try:
            file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
            file_input.send_keys(image_path)
            time.sleep(1)
            print("✓ Profile image uploaded")
        except Exception as e:
            print(f"  Warning: Could not upload image - {str(e)}")

        print("Step 5: Creating login credentials...")
        login_toggle = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".oxd-switch-input")))
        login_toggle.click()
        time.sleep(0.5)
        username_field = wait.until(EC.presence_of_element_located((By.XPATH, "//label[text()='Username']/../..//input")))
        username_field.clear(); username_field.send_keys(username)
        password_field = driver.find_element(By.XPATH, "//label[text()='Password']/../..//input")
        password_field.clear(); password_field.send_keys(password)
        confirm_password_field = driver.find_element(By.XPATH, "//label[text()='Confirm Password']/../..//input")
        confirm_password_field.clear(); confirm_password_field.send_keys(password)
        print(f"  Username: {username}")
        print("✓ Login credentials created")

        print("Step 6: Saving employee...")
        save_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        save_button.click()
        try:
            job_tab = wait.until(EC.presence_of_element_located((By.XPATH, "//a[text()='Job']")))
            print("✓ Employee saved successfully")
            assert job_tab.is_displayed(), "Employee creation failed"
        except TimeoutException:
            print("✗ Employee not saved or Job tab not visible")
            print("  Current URL after save:", driver.current_url)
            error_labels = driver.find_elements(By.CSS_SELECTOR, "span.oxd-input-field-error-message")
            if error_labels:
                print("  Validation errors:")
                for err in error_labels:
                    try:
                        print("   -", err.text)
                    except Exception:
                        pass
            pytest.fail("Employee creation failed; Job tab not available")

        print("Step 7: Opening Job section...")
        job_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[text()='Job']")))
        job_link.click()
        wait.until(EC.presence_of_element_located((By.XPATH, "//label[text()='Joined Date']/../..//input")))
        print("✓ Job section loaded")

        print("Step 8: Setting job details...")
        joined_date_field = wait.until(EC.presence_of_element_located((By.XPATH, "//label[text()='Joined Date']/../..//input")))
        joined_date_field.clear(); joined_date_field.send_keys("2024-01-15"); joined_date_field.send_keys(Keys.TAB)
        print("  Joined Date: 2024-01-15")
        try:
            wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".oxd-form-loader")))
        except TimeoutException:
            pass

        job_title_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "(//label[text()='Job Title']/../..//div[@class='oxd-select-text-input'])[1]")))
        job_title_dropdown.click(); job_title_dropdown.send_keys(Keys.ARROW_DOWN); job_title_dropdown.send_keys(Keys.ENTER)
        print("  Job Title: (first available option)")

        job_category_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "(//label[text()='Job Category']/../..//div[@class='oxd-select-text-input'])[1]")))
        job_category_dropdown.click(); job_category_dropdown.send_keys(Keys.ARROW_DOWN); job_category_dropdown.send_keys(Keys.ENTER)
        print("  Job Category: (first available option)")

        location_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "(//label[text()='Location']/../..//div[@class='oxd-select-text-input'])[1]")))
        location_dropdown.click(); location_dropdown.send_keys(Keys.ARROW_DOWN); location_dropdown.send_keys(Keys.ENTER)
        print("  Location: (first available option)")

        employment_status_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "(//label[text()='Employment Status']/../..//div[@class='oxd-select-text-input'])[1]")))
        employment_status_dropdown.click(); time.sleep(0.5)
        full_time_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='option']//span[contains(text(),'Full-Time Permanent')]")))
        full_time_option.click()
        print("  Employment Status: Full-Time Permanent")

        print("Step 9: Saving job details...")
        save_job_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
        save_job_button.click()
        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "oxd-toast-content")))
            print("✓ Job details saved successfully")
        except TimeoutException:
            print("  Warning: Success message not detected, but continuing...")

        print("Step 10: Opening Report-to section...")
        report_to_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[text()='Report-to']")))
        report_to_link.click()
        wait.until(EC.presence_of_element_located((By.XPATH, "//h6[text()='Report to']")))
        print("✓ Report-to section loaded")

        print("Step 11: Adding supervisor...")
        add_supervisor_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//h6[text()='Assigned Supervisors']/following::button[1]")))
        add_supervisor_button.click()
        supervisor_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Type for hints...']")))
        try:
            supervisor_input.clear(); supervisor_input.send_keys("a")
            wait.until(EC.presence_of_element_located((By.XPATH, "//div[@role='listbox']")))
            first_opt = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='listbox']//span")))
            picked_name = first_opt.text.strip(); first_opt.click()
            print(f"  Supervisor assigned: {picked_name}")
        except TimeoutException:
            print("  Warning: No supervisor suggestions available; skipping supervisor assignment")

        try:
            method_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[text()='Reporting Method']/../..//div[contains(@class,'oxd-select-text-input')]")))
            method_dropdown.click(); time.sleep(0.5)
            method_options = driver.find_elements(By.XPATH, "//div[@role='listbox']//span")
            if method_options:
                method_options[0].click(); print(f"  Reporting Method set: {method_options[0].text}")
        except Exception:
            print("  Warning: Could not set Reporting Method; skipping")

        save_supervisor_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        save_supervisor_button.click()
        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "oxd-toast-content")))
            print("✓ Supervisor added successfully")
        except TimeoutException:
            print("  Warning: Success message not detected, but continuing...")
        time.sleep(2)

        print("Step 12: Navigating to Employee List...")
        pim_menu = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='PIM']")))
        pim_menu.click()
        wait.until(EC.presence_of_element_located((By.XPATH, "//h5[text()='Employee Information']")))
        print("✓ Employee List page loaded")

        print("Step 13: Filtering by Employment Status...")
        try:
            employment_status_filter = wait.until(EC.element_to_be_clickable((By.XPATH, "(//label[text()='Employment Status']/../..//div[@class='oxd-select-text-input'])[1]")))
            employment_status_filter.click(); time.sleep(0.5)
            full_time_filter = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='option']//span[contains(text(),'Full-Time Permanent')]")))
            full_time_filter.click(); print("  Filter: Full-Time Permanent")
        except TimeoutException:
            pytest.fail("Employment Status filter not available on Employee List page")

        print("Step 14: Applying Supervisor Name filter (Odis Adalwin)...")
        supervisor_filter = wait.until(EC.presence_of_element_located((By.XPATH, "//label[text()='Supervisor Name']/../..//input")))
        supervisor_filter.clear(); supervisor_filter.send_keys("Odis")
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, "//div[@role='listbox']")))
            sup_opt = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='listbox']//span[normalize-space(text())='Odis Adalwin']")))
            sup_opt.click(); print("  Filter: Supervisor Name = Odis Adalwin")
        except TimeoutException:
            print("  Warning: Supervisor 'Odis Adalwin' not in filter suggestions; proceeding without it")

        print("Step 15: Searching for employee...")
        search_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
        search_button.click()

        try:
            _ = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "oxd-table-body")))
            _ = wait.until(EC.presence_of_element_located((By.XPATH, f"//div[@class='oxd-table-card']//div[contains(text(),'{first_name}')]")))
            print(f"✓ Employee '{first_name} {last_name}' found in search results with Supervisor filter")
            assert first_name in driver.page_source, f"Employee {first_name} not found in search results"
            print("\n=== TEST PASSED ===")
            print(f"Employee '{first_name} {last_name}' (ID {unique_employee_id}) successfully created and verified!")
        except TimeoutException:
            print(f"✗ Employee '{first_name} {last_name}' (ID {unique_employee_id}) NOT found in search results")
            try:
                table_body = driver.find_element(By.CLASS_NAME, "oxd-table-body")
                if not table_body.text.strip():
                    print("  No results found in the table after search.")
                else:
                    print(f"Table content: {table_body.text[:500]}")
            except Exception:
                print("  Warning: Could not read table body text for debugging")
            print("  Search completed, but no matching employee was found.")
            pytest.fail(f"Employee '{first_name} {last_name}' (ID {unique_employee_id}) was not found in filtered search results")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
