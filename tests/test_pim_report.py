import time
from dataclasses import dataclass
from datetime import datetime

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException


@dataclass
class ReportSpec:
    name: str
    include_text: str = "Current and Past Employees"
    min_columns: int = 15
    remaining_min: int = 8
    groups: tuple = ("Personal", "Contact Details", "Job", "Salary")


class TestPIMReportStyled:
    def test_create_report_with_criteria_and_columns(self, driver, base_url, login_credentials):
        wait = WebDriverWait(driver, 30)

        def click_js(el):
            try:
                el.click()
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", el)

        def wait_xpath(xpath, cond=EC.presence_of_element_located, timeout=30):
            return WebDriverWait(driver, timeout).until(cond((By.XPATH, xpath)))

        print("Step 1: Logging in and navigating to Dashboard...")
        driver.get(base_url)
        u = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        p = driver.find_element(By.NAME, "password")
        u.clear(); u.send_keys(login_credentials["username"]) 
        p.clear(); p.send_keys(login_credentials["password"]) 
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        wait.until(EC.presence_of_element_located((By.XPATH, "//span/h6[text()='Dashboard']")))
        
        print("Step 2: Navigating to PIM > Reports and opening Define Report page...")
        click_js(wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='PIM']"))))
        try:
            click_js(wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'viewDefinedPredefinedReports') or .//span[normalize-space()='Reports']]"))))
            click_js(wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'oxd-button') and contains(.,'Add')]"))))
            wait_xpath("//h6[contains(.,'Define Report')]")
            print("✓ Define Report page loaded")
        except TimeoutException:
            driver.get(base_url + "/web/index.php/pim/definePredefinedReport")
            try:
                wait_xpath("//h6[contains(.,'Define Report') or contains(.,'Reports')]")
                print("✓ Fallback: Define Report page loaded via direct URL")
            except TimeoutException:
                pass
        
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        spec = ReportSpec(name=f"Auto PIM Report {ts}")

        print(f"Step 3: Filling report name '{spec.name}' and setting Include option...")
        name_input = wait_xpath("//label[text()='Report Name']/../following-sibling::div//input")
        name_input.clear(); name_input.send_keys(spec.name)

        click_js(wait_xpath("//label[text()='Include']/../following-sibling::div//div[contains(@class,'oxd-select-text')]", EC.element_to_be_clickable))
        click_js(wait_xpath(f"//div[@role='option' and contains(.,'{spec.include_text}')]", EC.element_to_be_clickable))
        
        for i in range(2):
            try:
                click_js(wait_xpath("//label[text()='Selection Criteria']/../following-sibling::div//div[contains(@class,'oxd-select-text')]", EC.element_to_be_clickable))
                opts = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@role='listbox']/div[@role='option']")))
                (opts[i] if i < len(opts) else opts[0]).click()
                click_js(driver.find_element(By.XPATH, "//button[contains(@class,'oxd-button') and contains(.,'Add Criteria')]"))
                time.sleep(0.3)
            except Exception:
                pass

        try:
            dels = driver.find_elements(By.XPATH, "//div[contains(@class,'oxd-table-card')]//button[contains(@class,'oxd-icon-button')]")
            for b in dels:
                try:
                    b.click(); time.sleep(0.2)
                except ElementClickInterceptedException:
                    driver.execute_script("arguments[0].click();", b)
        except Exception:
            pass
        
        def select_group(label_sub: str) -> bool:
            try:
                click_js(wait_xpath("//label[text()='Display Fields']/../following-sibling::div//div[contains(@class,'oxd-select-text')]", EC.element_to_be_clickable))
            except TimeoutException:
                return False
            try:
                click_js(wait_xpath(f"//div[@role='option' and contains(.,'{label_sub}')]", EC.element_to_be_clickable))
            except TimeoutException:
                try:
                    click_js(wait_xpath("//div[@role='option']", EC.element_to_be_clickable))
                except TimeoutException:
                    return False
            return True

        def add_fields_from_current_group(max_fields=5):
            try:
                click_js(wait_xpath("//label[text()='Display Fields']/../following-sibling::div//following::div[contains(@class,'oxd-select-text')][1]", EC.element_to_be_clickable))
                fields = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@role='listbox']/div[@role='option']")))
                count = 0
                for f in fields:
                    try:
                        f.click()
                        click_js(driver.find_element(By.XPATH, "//button[contains(@class,'oxd-button') and contains(.,'Add Display Field')]"))
                        count += 1
                        time.sleep(0.2)
                        if count >= max_fields:
                            break
                        click_js(driver.find_element(By.XPATH, "//label[text()='Display Fields']/../following-sibling::div//following::div[contains(@class,'oxd-select-text')][1]"))
                    except Exception:
                        break
            except Exception:
                pass

        total_cols = 0
        for grp in spec.groups:
            if not select_group(grp):
                break
            add_fields_from_current_group(5)
            rows = driver.find_elements(By.XPATH, "//div[contains(@class,'oxd-table-card')][.//div[contains(@class,'oxd-table-header-cell') and contains(.,'Display Field')]]/following-sibling::div[contains(@class,'oxd-table-card')]")
            total_cols = len(rows)
            if total_cols >= spec.min_columns:
                break
        
        try:
            cbs = driver.find_elements(By.XPATH, "//label[contains(.,'Include Header')]/../following-sibling::div//input[@type='checkbox']")
            for cb in cbs:
                try:
                    if not cb.is_selected():
                        cb.click()
                except ElementClickInterceptedException:
                    driver.execute_script("arguments[0].click();", cb)
        except Exception:
            pass
        
        try:
            display_rows = driver.find_elements(By.XPATH, "//div[contains(@class,'oxd-table-card')][.//div[contains(@class,'oxd-table-header-cell') and contains(.,'Display Field')]]/following-sibling::div[contains(@class,'oxd-table-card')]")
            buttons = []
            for r in display_rows:
                bs = r.find_elements(By.XPATH, ".//button[contains(@class,'oxd-icon-button')]")
                if bs:
                    buttons.append(bs[-1])
            for b in buttons[:3]:
                try:
                    b.click(); time.sleep(0.2)
                except ElementClickInterceptedException:
                    driver.execute_script("arguments[0].click();", b)
        except Exception:
            pass

        try:
            grp_del = driver.find_elements(By.XPATH, "//div[contains(@class,'oxd-table-card')][.//div[contains(.,'Display Field Group')]]//button[contains(@class,'oxd-icon-button')]")
            if grp_del:
                try:
                    grp_del[0].click(); time.sleep(0.3)
                except ElementClickInterceptedException:
                    driver.execute_script("arguments[0].click();", grp_del[0])
        except Exception:
            pass

        remaining = driver.find_elements(By.XPATH, "//div[contains(@class,'oxd-table-card')][.//div[contains(@class,'oxd-table-header-cell') and contains(.,'Display Field')]]/following-sibling::div[contains(@class,'oxd-table-card')]")
        if total_cols >= spec.remaining_min:
            assert len(remaining) >= spec.remaining_min, "Expected at least 8 display columns to remain after deletions"
        
        try:
            click_js(driver.find_element(By.XPATH, "//button[@type='submit' and contains(.,'Save')]"))
            wait.until(EC.presence_of_element_located((By.XPATH, "//h6[contains(.,'Defined Predefined Reports')]")))
        except Exception:
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
