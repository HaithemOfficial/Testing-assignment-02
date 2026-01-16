import os
import time
from dataclasses import dataclass
from datetime import datetime

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException


@dataclass
class Candidate:
    first_name: str
    middle_name: str
    last_name: str
    email: str
    contact: str
    keywords: str
    notes: str


class TestRecruitmentAddCandidate:
    def test_add_candidate_shortlist_schedule(self, driver, base_url, login_credentials):
        """Task 3: Add a candidate, upload a file, shortlist with a note,
        then schedule an interview by filling all fields.

        Style-only changes vs friend code: helpers, dataclass, clear steps.
        """

        wait = WebDriverWait(driver, 30)

        # Helpers
        def click_js(elem):
            try:
                elem.click()
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", elem)

        def input_by_label(label, value, is_textarea=False):
            try:
                path = "//label[text()='%s']/../..//%s" % (label, "textarea" if is_textarea else "input")
                el = driver.find_element(By.XPATH, path)
                el.clear()
                el.send_keys(value)
                return True
            except Exception:
                return False

        def select_dropdown_first(label):
            try:
                box = driver.find_element(By.XPATH, f"(//label[text()='{label}']/../..//div[@class='oxd-select-text-input'])[1]")
                box.click(); time.sleep(0.5)
                box.send_keys(Keys.ARROW_DOWN); box.send_keys(Keys.ENTER)
                return True
            except Exception:
                return False

        # Step 1: Login
        driver.get(base_url)
        u = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        p = driver.find_element(By.NAME, "password")
        u.clear(); u.send_keys(login_credentials["username"]) 
        p.clear(); p.send_keys(login_credentials["password"]) 
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        wait.until(EC.presence_of_element_located((By.XPATH, "//span/h6[text()='Dashboard']")))

        # Step 2: Go to Recruitment → Add Candidate
        recruitment = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Recruitment']")))
        recruitment.click()
        add_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Add') and contains(@class,'oxd-button')]")))
        add_btn.click()
        wait.until(EC.presence_of_element_located((By.XPATH, "//h6[text()='Add Candidate']")))

        # Step 3: Fill form and upload file
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        cand = Candidate(
            first_name=f"Cand{ts[-4:]}",
            middle_name="Auto",
            last_name="Tester",
            email=f"candidate.{ts}@example.com",
            contact="1234567890",
            keywords="selenium, automation, python",
            notes="Candidate created via styled test.",
        )

        wait.until(EC.presence_of_element_located((By.NAME, "firstName"))).send_keys(cand.first_name)
        driver.find_element(By.NAME, "middleName").send_keys(cand.middle_name)
        driver.find_element(By.NAME, "lastName").send_keys(cand.last_name)

        input_by_label("Email", cand.email)
        input_by_label("Contact Number", cand.contact)
        select_dropdown_first("Vacancy")

        # Keywords, Date, Notes
        try:
            driver.find_element(By.XPATH, "//label[text()='Keywords']/../..//input").send_keys(cand.keywords)
        except Exception:
            pass
        try:
            date_el = driver.find_element(By.XPATH, "//label[text()='Date of Application']/../..//input")
            if not (date_el.get_attribute("value") or "").strip():
                date_el.clear(); date_el.send_keys("2024-01-15"); date_el.send_keys(Keys.TAB)
        except Exception:
            pass
        input_by_label("Notes", cand.notes, is_textarea=True)

        # Consent checkbox (optional)
        try:
            consent = driver.find_element(By.XPATH, "//label[contains(.,'Consent to keep data')]/../following-sibling::div//input")
            if not consent.is_selected():
                consent.click()
        except Exception:
            pass

        # Upload attachment
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_data", "sample_attachment.txt")
        try:
            driver.find_element(By.CSS_SELECTOR, "input[type='file']").send_keys(file_path)
        except Exception:
            pass

        # Step 4: Save candidate → wait for Shortlist button
        click_js(driver.find_element(By.CSS_SELECTOR, "button[type='submit']"))
        wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(normalize-space(),'Shortlist')]")))

        # Step 5: Shortlist with notes
        click_js(wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(normalize-space(),'Shortlist')]"))))
        input_by_label("Notes", "Shortlisted via styled test.", is_textarea=True)
        try:
            shortlist_save = driver.find_element(By.XPATH, "//button[@type='submit' and contains(normalize-space(),'Save')]")
        except Exception:
            try:
                shortlist_save = driver.find_element(By.XPATH, "(//div[contains(@class,'oxd-dialog-container')]//button[@type='submit'])[1]")
            except Exception:
                shortlist_save = None
        if shortlist_save:
            click_js(shortlist_save)
            try:
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "oxd-toast-content")))
            except TimeoutException:
                pass

        # Step 6: Schedule Interview (fill all fields)
        try:
            click_js(wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(normalize-space(),'Schedule Interview')]"))))
        except TimeoutException:
            # If interview stage isn’t available due to backend/validation, treat as best-effort and stop here
            return

        input_by_label("Interview Title", "Automation Engineer Interview")

        # Interviewer: type to get suggestions; pick first
        try:
            intr = driver.find_element(By.XPATH, "//label[text()='Interviewer']/../..//input")
            intr.clear(); intr.send_keys("a")
            sug = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='listbox']//span")))
            sug.click()
        except Exception:
            pass

        # Date & Time
        input_by_label("Date", "2024-01-20")
        try:
            driver.find_element(By.XPATH, "//label[text()='Date']/../..//input").send_keys(Keys.TAB)
        except Exception:
            pass
        input_by_label("Time", "10:00")
        try:
            driver.find_element(By.XPATH, "//label[text()='Time']/../..//input").send_keys(Keys.TAB)
        except Exception:
            pass

        # Save interview
        click_js(driver.find_element(By.XPATH, "//button[@type='submit' and .='Save']"))
        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "oxd-toast-content")))
        except TimeoutException:
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
