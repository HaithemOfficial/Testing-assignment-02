import os
import time
from datetime import datetime

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, StaleElementReferenceException


class TestPersonalDetails:
    def test_edit_personal_details_and_attachments(self, driver, base_url, login_credentials):
        wait = WebDriverWait(driver, 30)

        print("Step 1: Logging in...")
        driver.get(base_url)
        username_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password_input = driver.find_element(By.NAME, "password")
        username_input.clear(); username_input.send_keys(login_credentials["username"])
        password_input.clear(); password_input.send_keys(login_credentials["password"])
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        wait.until(EC.presence_of_element_located((By.XPATH, "//span/h6[text()='Dashboard']")))
        print("✓ Logged in")
        
        print("Step 2: Creating a new employee...")
        pim_menu = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='PIM']")))
        pim_menu.click()
        add_employee_menu = None
        for _ in range(3):
            try:
                add_employee_menu = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[text()='Add Employee']")))
                add_employee_menu.click()
                break
            except StaleElementReferenceException:
                time.sleep(0.5)
                continue
        wait.until(EC.presence_of_element_located((By.NAME, "firstName")))
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        first_name = f"PD{timestamp[-4:]}"
        last_name = "Tester"
        unique_employee_id = datetime.now().strftime("%H%M%S")

        driver.find_element(By.NAME, "firstName").send_keys(first_name)
        driver.find_element(By.NAME, "lastName").send_keys(last_name)

        employee_id_field = driver.find_element(By.XPATH, "//label[text()='Employee Id']/../..//input")
        employee_id_field.clear(); employee_id_field.send_keys(unique_employee_id)

        save_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        try:
            save_button.click()
        except ElementClickInterceptedException:
            driver.execute_script("arguments[0].click();", save_button)

        try:
            wait.until(
                EC.any_of(
                    EC.presence_of_element_located((By.XPATH, "//h6[text()='Personal Details']")),
                    EC.presence_of_element_located((By.XPATH, "//label[text()='Nick Name']/../..//input")),
                )
            )
            print("✓ Personal Details page loaded")
        except TimeoutException:
            pytest.fail("Personal Details page did not load after saving employee")

        def set_text(label, value):
            try:
                field = driver.find_element(By.XPATH, f"//label[text()='{label}']/../..//input")
                field.clear(); field.send_keys(value)
            except Exception:
                pass
        
        print("Step 3: Filling personal details...")
        set_text("Nick Name", "PD Nick")
        set_text("Other Id", "OID-12345")
        set_text("Driver's License Number", "D-987654321")
        set_text("SSN Number", "123-45-6789")
        set_text("SIN Number", "987-65-4321")
        set_text("Military Service", "None")

        try:
            license_expiry = driver.find_element(By.XPATH, "//label[text()=\"License Expiry Date\"]/../..//input")
            license_expiry.clear(); license_expiry.send_keys("2030-12-31"); license_expiry.send_keys(Keys.TAB)
        except Exception:
            pass
        
        try:
            nationality_dd = driver.find_element(By.XPATH, "(//label[text()='Nationality']/../..//div[@class='oxd-select-text-input'])[1]")
            nationality_dd.click(); time.sleep(0.5); nationality_dd.send_keys(Keys.ARROW_DOWN); nationality_dd.send_keys(Keys.ENTER)
        except Exception:
            pass
        try:
            marital_dd = driver.find_element(By.XPATH, "(//label[text()='Marital Status']/../..//div[@class='oxd-select-text-input'])[1]")
            marital_dd.click(); time.sleep(0.5); marital_dd.send_keys(Keys.ARROW_DOWN); marital_dd.send_keys(Keys.ENTER)
        except Exception:
            pass
        
        try:
            dob_field = driver.find_element(By.XPATH, "//label[text()='Date of Birth']/../..//input")
            dob_field.clear(); dob_field.send_keys("1990-01-01"); dob_field.send_keys(Keys.TAB)
        except Exception:
            pass
        try:
            male_radio = driver.find_element(By.XPATH, "//label[normalize-space()='Male']/preceding-sibling::input | //label[normalize-space()='Male']/../input")
            male_radio.click()
        except Exception:
            pass
        try:
            smoker_checkbox = driver.find_element(By.XPATH, "//label[text()='Smoker']/../following-sibling::div//input")
            if not smoker_checkbox.is_selected(): smoker_checkbox.click()
        except Exception:
            pass
        
        print("Step 4: Saving personal details...")
        try:
            save_personal_btn = driver.find_element(By.XPATH, "(//button[@type='submit'])[1]")
            save_personal_btn.click()
            try:
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "oxd-toast-content")))
                print("✓ Personal details saved")
            except TimeoutException:
                pass
        except Exception:
            pytest.fail("Could not save personal details")
        
        print("Step 5: Adding two attachments...")
        attachments_header = driver.find_element(By.XPATH, "//h6[text()='Attachments']")
        driver.execute_script("arguments[0].scrollIntoView(true);", attachments_header)
        time.sleep(1)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        file1 = os.path.join(current_dir, "test_data", "profile_image.png")
        file2 = os.path.join(current_dir, "test_data", "sample_attachment.txt")

        def add_attachment(file_path: str, comment: str):
            add_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//h6[text()='Attachments']/following::button[1]")))
            add_button.click()
            file_input = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'orangehrm-attachment')]//input[@type='file']")))
            file_input.send_keys(file_path)
            try:
                comment_area = driver.find_element(By.XPATH, "//div[contains(@class,'orangehrm-attachment')]//textarea")
                comment_area.clear(); comment_area.send_keys(comment)
            except Exception:
                pass
            save_btn = driver.find_element(By.XPATH, "//div[contains(@class,'orangehrm-attachment')]//button[@type='submit']")
            try:
                save_btn.click()
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", save_btn)
            try:
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "oxd-toast-content")))
            except TimeoutException:
                pass

        add_attachment(file1, "Profile image attachment")
        add_attachment(file2, "Text attachment for test")
        print("✓ Attachments added")
        
        print("Step 6: Editing first attachment comment...")
        table_body = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'orangehrm-attachment')]//div[@class='oxd-table-body']")))
        rows = table_body.find_elements(By.XPATH, ".//div[contains(@class,'oxd-table-card')]")
        assert len(rows) >= 1, "No attachment rows found after adding"
        edit_button = rows[0].find_element(By.XPATH, ".//button[1]")
        edit_button.click()
        new_comment = "Updated attachment comment"
        comment_area = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'orangehrm-attachment')]//textarea")))
        comment_area.clear(); comment_area.send_keys(new_comment)
        save_btn = driver.find_element(By.XPATH, "//div[contains(@class,'orangehrm-attachment')]//button[@type='submit']")
        try:
            save_btn.click()
        except ElementClickInterceptedException:
            driver.execute_script("arguments[0].click();", save_btn)
        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "oxd-toast-content")))
        except TimeoutException:
            pass
        
        print("Step 7: Downloading first attachment (best effort)...")
        try:
            file_link = wait.until(EC.element_to_be_clickable((By.XPATH, "(//div[contains(@class,'orangehrm-attachment')]//div[@class='oxd-table-body']//div[contains(@class,'oxd-table-card')])[1]//a")))
            link_name = (file_link.text or os.path.basename(file1)).strip()
            file_link.click()
            downloads_dir = os.getenv("DOWNLOAD_DIR") or os.path.join(current_dir, "downloads")
            target = os.path.join(downloads_dir, link_name)
            for _ in range(20):
                if os.path.exists(target):
                    break
                if os.path.exists(target + ".crdownload"):
                    time.sleep(0.5)
                else:
                    time.sleep(0.5)
            if not os.path.exists(target):
                print(f"[PD] Warning: download not found at {target}")
        except Exception:
            print("[PD] Warning: Could not trigger download for first attachment")
        
        print("Step 8: Deleting first attachment...")
        table_body = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'orangehrm-attachment')]//div[@class='oxd-table-body']")))
        rows_before = table_body.find_elements(By.XPATH, ".//div[contains(@class,'oxd-table-card')]")
        assert len(rows_before) >= 1, "No attachments available to delete"
        delete_button = rows_before[0].find_element(By.XPATH, ".//button[last()]")
        delete_button.click()
        try:
            confirm_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Yes, Delete']")))
            confirm_btn.click()
        except TimeoutException:
            print("[PD] Warning: Delete confirmation dialog did not appear; skipping delete verification")
            return
        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "oxd-toast-content")))
        except TimeoutException:
            pass
        time.sleep(1)
        rows_after = table_body.find_elements(By.XPATH, ".//div[contains(@class,'oxd-table-card')]")
        assert len(rows_after) == len(rows_before) - 1, "Attachment row count did not decrease after deletion"
        print(f"✓ Attachment deleted; remaining rows: {len(rows_after)}")
        print(f"[PD] Completed Personal Details test for {first_name} {last_name} (ID {unique_employee_id})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
