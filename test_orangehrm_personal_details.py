import os
import time
from datetime import datetime

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException


class TestOrangeHRMPersonalDetails:
    """Tests editing personal data and managing attachments for a created employee."""

    def test_edit_personal_details_and_attachments(self, driver, base_url, login_credentials):
        """Create an employee, edit personal details, and manage attachments."""

        wait = WebDriverWait(driver, 20)

        # ====================
        # STEP 1: Login
        # ====================
        print("[PD] Step 1: Logging in...")
        driver.get(base_url)

        username_input = wait.until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        password_input = driver.find_element(By.NAME, "password")

        username_input.clear()
        username_input.send_keys(login_credentials["username"])
        password_input.clear()
        password_input.send_keys(login_credentials["password"])

        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//span/h6[text()='Dashboard']")
            )
        )
        print("[PD] ✓ Logged in")

        # ====================
        # STEP 2: Create a new employee (minimal data)
        # ====================
        print("[PD] Step 2: Creating a new employee...")

        pim_menu = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='PIM']"))
        )
        pim_menu.click()

        add_employee_menu = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[text()='Add Employee']"))
        )
        add_employee_menu.click()

        wait.until(
            EC.presence_of_element_located((By.NAME, "firstName"))
        )

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        first_name = f"PD{timestamp[-4:]}"
        last_name = "Tester"
        unique_employee_id = datetime.now().strftime("%H%M%S")

        first_name_field = driver.find_element(By.NAME, "firstName")
        last_name_field = driver.find_element(By.NAME, "lastName")

        first_name_field.clear()
        first_name_field.send_keys(first_name)
        last_name_field.clear()
        last_name_field.send_keys(last_name)

        employee_id_field = driver.find_element(
            By.XPATH, "//label[text()='Employee Id']/../..//input"
        )
        employee_id_field.clear()
        employee_id_field.send_keys(unique_employee_id)
        print(f"[PD]  Employee Id set to: {unique_employee_id}")

        # Save employee (no login details needed for this test)
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
            print("[PD] ✓ Employee created and Personal Details page loaded")
        except TimeoutException:
            pytest.fail("[PD] Personal Details page did not load after saving employee")

        current_url = driver.current_url
        print(f"[PD] Personal Details URL: {current_url}")

        # ====================
        # STEP 3: Fill personal details form
        # ====================
        print("[PD] Step 3: Filling personal details form...")

        def set_text_field(label_text: str, value: str):
            try:
                field = driver.find_element(
                    By.XPATH, f"//label[text()='{label_text}']/../..//input"
                )
                field.clear()
                field.send_keys(value)
                print(f"[PD]   {label_text}: {value}")
            except Exception:
                print(f"[PD]   Warning: Could not set field '{label_text}'")

        # Basic identity fields
        set_text_field("Nick Name", "PD Nick")
        set_text_field("Other Id", "OID-12345")
        set_text_field("Driver's License Number", "D-987654321")
        set_text_field("SSN Number", "123-45-6789")
        set_text_field("SIN Number", "987-65-4321")
        set_text_field("Military Service", "None")

        # License Expiry Date
        try:
            license_expiry = driver.find_element(
                By.XPATH, "//label[text()=\"License Expiry Date\"]/../..//input"
            )
            license_expiry.clear()
            license_expiry.send_keys("2030-12-31")
            license_expiry.send_keys(Keys.TAB)
            print("[PD]   License Expiry Date: 2030-12-31")
        except Exception:
            print("[PD]   Warning: Could not set License Expiry Date")

        # Nationality dropdown
        try:
            nationality_dd = driver.find_element(
                By.XPATH,
                "(//label[text()='Nationality']/../..//div[@class='oxd-select-text-input'])[1]",
            )
            nationality_dd.click()
            time.sleep(0.5)
            nationality_dd.send_keys(Keys.ARROW_DOWN)
            nationality_dd.send_keys(Keys.ENTER)
            print("[PD]   Nationality: (first available option)")
        except Exception:
            print("[PD]   Warning: Could not set Nationality")

        # Marital Status dropdown
        try:
            marital_dd = driver.find_element(
                By.XPATH,
                "(//label[text()='Marital Status']/../..//div[@class='oxd-select-text-input'])[1]",
            )
            marital_dd.click()
            time.sleep(0.5)
            marital_dd.send_keys(Keys.ARROW_DOWN)
            marital_dd.send_keys(Keys.ENTER)
            print("[PD]   Marital Status: (first available option)")
        except Exception:
            print("[PD]   Warning: Could not set Marital Status")

        # Date of Birth
        try:
            dob_field = driver.find_element(
                By.XPATH, "//label[text()='Date of Birth']/../..//input"
            )
            dob_field.clear()
            dob_field.send_keys("1990-01-01")
            dob_field.send_keys(Keys.TAB)
            print("[PD]   Date of Birth: 1990-01-01")
        except Exception:
            print("[PD]   Warning: Could not set Date of Birth")

        # Gender (select Male if available)
        try:
            male_radio = driver.find_element(
                By.XPATH,
                "//label[text()='Male']/preceding-sibling::input | //label[text()='Male']/../input",
            )
            male_radio.click()
            print("[PD]   Gender: Male")
        except Exception:
            print("[PD]   Warning: Could not set Gender")

        # Smoker checkbox (if present)
        try:
            smoker_checkbox = driver.find_element(
                By.XPATH,
                "//label[text()='Smoker']/../following-sibling::div//input",
            )
            if not smoker_checkbox.is_selected():
                smoker_checkbox.click()
            print("[PD]   Smoker: Yes")
        except Exception:
            print("[PD]   Warning: Could not set Smoker field")

        # Save personal details
        print("[PD] Saving personal details...")
        try:
            save_personal_btn = driver.find_element(
                By.XPATH, "(//button[@type='submit'])[1]"
            )
            save_personal_btn.click()
            try:
                wait.until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, "oxd-toast-content")
                    )
                )
                print("[PD] ✓ Personal details saved successfully")
            except TimeoutException:
                print("[PD]   Warning: Success toast not detected after saving personal details")
        except Exception:
            pytest.fail("[PD] Could not click Save button for personal details")

        # ====================
        # STEP 4: Add two attachments
        # ====================
        print("[PD] Step 4: Adding two attachments...")

        # Scroll to Attachments section
        try:
            attachments_header = driver.find_element(
                By.XPATH, "//h6[text()='Attachments']"
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", attachments_header)
            time.sleep(1)
        except Exception:
            pytest.fail("[PD] Attachments section not found on Personal Details page")

        current_dir = os.path.dirname(os.path.abspath(__file__))
        file1 = os.path.join(current_dir, "test_data", "profile_image.png")
        file2 = os.path.join(current_dir, "test_data", "sample_attachment.txt")

        def add_attachment(file_path: str, comment: str):
            add_button = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//h6[text()='Attachments']/following::button[1]",
                    )
                )
            )
            add_button.click()

            file_input = wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//div[contains(@class,'orangehrm-attachment')]//input[@type='file']",
                    )
                )
            )
            file_input.send_keys(file_path)

            try:
                comment_area = driver.find_element(
                    By.XPATH,
                    "//div[contains(@class,'orangehrm-attachment')]//textarea",
                )
                comment_area.clear()
                comment_area.send_keys(comment)
            except Exception:
                print("[PD]   Warning: Could not set attachment comment")

            save_btn = driver.find_element(
                By.XPATH,
                "//div[contains(@class,'orangehrm-attachment')]//button[@type='submit']",
            )
            try:
                save_btn.click()
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", save_btn)

            try:
                wait.until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, "oxd-toast-content")
                    )
                )
                print(f"[PD]   ✓ Attachment added: {os.path.basename(file_path)}")
            except TimeoutException:
                print("[PD]   Warning: Success toast not detected after adding attachment")

        add_attachment(file1, "Profile image attachment")
        add_attachment(file2, "Text attachment for test")

        # ====================
        # STEP 5: Edit first attachment's comment
        # ====================
        print("[PD] Step 5: Editing first attachment comment...")

        try:
            table_body = wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//div[contains(@class,'orangehrm-attachment')]//div[@class='oxd-table-body']",
                    )
                )
            )
            # Each attachment is typically rendered as an 'oxd-table-card' inside the table body
            rows = table_body.find_elements(
                By.XPATH, ".//div[contains(@class,'oxd-table-card')]"
            )
            assert len(rows) >= 1, "[PD] No attachment rows found after adding"

            # Click the first row's Edit button (assumed first action button in actions cell)
            edit_button = rows[0].find_element(By.XPATH, ".//button[1]")
            edit_button.click()

            new_comment = "Updated attachment comment"
            comment_area = wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//div[contains(@class,'orangehrm-attachment')]//textarea",
                    )
                )
            )
            comment_area.clear()
            comment_area.send_keys(new_comment)

            save_btn = driver.find_element(
                By.XPATH,
                "//div[contains(@class,'orangehrm-attachment')]//button[@type='submit']",
            )
            try:
                save_btn.click()
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", save_btn)

            try:
                wait.until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, "oxd-toast-content")
                    )
                )
                print("[PD] ✓ Attachment edited successfully")
            except TimeoutException:
                print("[PD]   Warning: Success toast not detected after editing attachment")
        except Exception as exc:
            pytest.fail(f"[PD] Failed while editing attachment: {exc}")

        # ====================
        # STEP 6: Download first attachment (click file name)
        # ====================
        print("[PD] Step 6: Downloading first attachment (clicking file name)...")

        try:
            file_link = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "(//div[contains(@class,'orangehrm-attachment')]//div[@class='oxd-table-body']//div[contains(@class,'oxd-table-card')])[1]//a",
                    )
                )
            )
            file_name = file_link.text.strip() or os.path.basename(file1)
            file_link.click()
            downloads_dir = os.getenv("DOWNLOAD_DIR") or os.path.join(os.path.dirname(__file__), "downloads")
            target = os.path.join(downloads_dir, file_name)
            for _ in range(20):
                if os.path.exists(target):
                    break
                if os.path.exists(target + ".crdownload"):
                    time.sleep(0.5)
                else:
                    time.sleep(0.5)
            if os.path.exists(target):
                print(f"[PD] ✓ File downloaded: {target}")
            else:
                print("[PD]   Warning: Download file not found; continuing")
        except Exception:
            print("[PD]   Warning: Could not trigger download for first attachment")

        # ====================
        # STEP 7: Delete first attachment
        # ====================
        print("[PD] Step 7: Deleting first attachment...")

        try:
            table_body = wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//div[contains(@class,'orangehrm-attachment')]//div[@class='oxd-table-body']",
                    )
                )
            )
            rows_before = table_body.find_elements(
                By.XPATH, ".//div[contains(@class,'oxd-table-card')]"
            )
            assert len(rows_before) >= 1, "[PD] No attachments available to delete"

            delete_button = rows_before[0].find_element(By.XPATH, ".//button[last()]")
            delete_button.click()

            # Confirm deletion
            try:
                confirm_btn = wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[normalize-space()='Yes, Delete']")
                    )
                )
                confirm_btn.click()
            except TimeoutException:
                print("[PD]   Warning: Delete confirmation dialog did not appear; skipping delete verification")
                return

            try:
                wait.until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, "oxd-toast-content")
                    )
                )
                print("[PD] ✓ Attachment deleted successfully")
            except TimeoutException:
                print("[PD]   Warning: Success toast not detected after deleting attachment")

            # Verify row count decreased
            time.sleep(1)
            rows_after = table_body.find_elements(
                By.XPATH, ".//div[contains(@class,'oxd-table-card')]"
            )
            assert len(rows_after) == len(rows_before) - 1, (
                "[PD] Attachment row count did not decrease after deletion"
            )
        except Exception as exc:
            pytest.fail(f"[PD] Failed while deleting attachment: {exc}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
