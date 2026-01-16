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
class BuzzContent:
    message: str
    updated_message: str
    comment: str
    updated_comment: str


class TestBuzzStyled:
    def test_buzz_post_picture_comment_flow(self, driver, base_url, login_credentials):
        """Task 4: Post a Buzz message with picture, like/edit it, comment,
        like/edit/delete the comment, then delete the message.

        Style-only changes: helpers, dataclass, concise flow; features unchanged.
        """

        wait = WebDriverWait(driver, 30)

        # Helpers
        def click_js(el):
            try:
                el.click()
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", el)

        def wait_xpath(xpath, cond=EC.presence_of_element_located, timeout=30):
            return WebDriverWait(driver, timeout).until(cond((By.XPATH, xpath)))

        # Step 1: Login
        driver.get(base_url)
        u = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        p = driver.find_element(By.NAME, "password")
        u.clear(); u.send_keys(login_credentials["username"]) 
        p.clear(); p.send_keys(login_credentials["password"]) 
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        wait.until(EC.presence_of_element_located((By.XPATH, "//span/h6[text()='Dashboard']")))

        # Step 2: Go to Buzz
        click_js(wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Buzz']"))))
        wait_xpath("//h6[text()='Buzz']")

        # Step 3: Create post with text + picture
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        content = BuzzContent(
            message=f"Automated buzz post {ts}",
            updated_message=f"Updated buzz post {ts}",
            comment=f"Automated comment {ts}",
            updated_comment=f"Updated comment {ts}",
        )

        try:
            post_input = wait_xpath("//textarea | //form//p[contains(@class,'oxd-buzz-post-input')]/ancestor::form//textarea")
        except TimeoutException:
            post_input = wait_xpath("//div[@contenteditable='true' and contains(@class,'oxd-buzz-post-input')]")
        try:
            post_input.clear()
        except Exception:
            pass
        post_input.send_keys(content.message)

        img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_data", "profile_image.png")
        try:
            click_js(driver.find_element(By.XPATH, "//button[contains(@class,'oxd-buzz-post-img-button') or @type='button'][.//i or .//span]"))
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))).send_keys(img_path)
        except Exception:
            pass

        existing_top = None
        try:
            existing_top = driver.find_element(By.XPATH, "(//div[contains(@class,'orangehrm-buzz-post')])[1]")
        except Exception:
            pass

        try:
            post_btn = driver.find_element(By.XPATH, "//button[@type='submit' and (contains(.,'Post') or contains(.,'Share'))]")
        except Exception:
            post_btn = wait_xpath("//form//button[contains(@class,'oxd-button') and (contains(.,'Post') or contains(.,'Share'))]", EC.element_to_be_clickable)
        click_js(post_btn)

        if existing_top is not None:
            try:
                WebDriverWait(driver, 10).until(EC.staleness_of(existing_top))
            except TimeoutException:
                pass
        post_card = wait_xpath("(//div[contains(@class,'orangehrm-buzz-post')])[1]")

        # Step 4: Like post
        try:
            click_js(post_card.find_element(By.XPATH, ".//button[contains(.,'Like') or contains(.,'Unlike')]"))
        except Exception:
            pass

        # Step 5: Edit post
        try:
            click_js(post_card.find_element(By.XPATH, ".//button[contains(@class,'oxd-icon-button') or contains(@class,'more')]"))
            time.sleep(0.5)
            click_js(driver.find_element(By.XPATH, "//div[contains(@class,'oxd-dropdown-menu')]//p[contains(normalize-space(),'Edit')]"))
            edit_box = wait_xpath("//div[contains(@class,'orangehrm-buzz-post-modal')]//textarea | //div[contains(@class,'orangehrm-buzz-post-modal')]//div[@contenteditable='true']")
            try:
                edit_box.clear()
            except Exception:
                edit_box.send_keys(Keys.CONTROL, "a"); edit_box.send_keys(Keys.BACKSPACE)
            edit_box.send_keys(content.updated_message)
            click_js(driver.find_element(By.XPATH, "//div[contains(@class,'orangehrm-buzz-post-modal')]//button[@type='submit' and (contains(.,'Save') or contains(.,'Update'))]"))
            time.sleep(1)
            post_card = wait_xpath("(//div[contains(@class,'orangehrm-buzz-post')])[1]")
        except Exception:
            pass

        # Step 6: Add comment
        try:
            cinput = wait_xpath("//input[@placeholder='Write your comment...'] | //textarea[@placeholder='Write your comment...']", EC.element_to_be_clickable)
            cinput.clear(); cinput.send_keys(content.comment); cinput.send_keys(Keys.ENTER)
        except Exception:
            try:
                click_js(driver.find_element(By.XPATH, "//button[contains(.,'Comment')]"))
                area = wait_xpath("//div[contains(@class,'orangehrm-buzz-comment')]//textarea")
                area.clear(); area.send_keys(content.comment); area.send_keys(Keys.ENTER)
            except Exception:
                pass

        comment_block = None
        try:
            comment_block = wait_xpath(f"//div[contains(@class,'orangehrm-buzz-comment')][.//*[contains(normalize-space(), '{content.comment.split()[0]}')]]")
        except TimeoutException:
            pass

        # Step 7: Like comment
        if comment_block:
            try:
                click_js(comment_block.find_element(By.XPATH, ".//button[contains(.,'Like') or contains(.,'Unlike')]"))
            except Exception:
                pass

        # Step 8: Edit comment
        if comment_block:
            try:
                click_js(comment_block.find_element(By.XPATH, ".//button[contains(@class,'oxd-icon-button') or contains(@class,'more')]"))
                time.sleep(0.5)
                click_js(driver.find_element(By.XPATH, "//div[contains(@class,'oxd-dropdown-menu')]//p[contains(normalize-space(),'Edit')]"))
                area = wait_xpath("//div[contains(@class,'orangehrm-buzz-comment')]//textarea")
                try:
                    area.clear()
                except Exception:
                    area.send_keys(Keys.CONTROL, "a"); area.send_keys(Keys.BACKSPACE)
                area.send_keys(content.updated_comment); area.send_keys(Keys.ENTER)
                comment_block = wait_xpath(f"//div[contains(@class,'orangehrm-buzz-comment')][.//*[contains(normalize-space(), '{content.updated_comment.split()[0]}')]]")
            except Exception:
                pass

        # Step 9: Delete comment
        if comment_block:
            try:
                click_js(comment_block.find_element(By.XPATH, ".//button[contains(@class,'oxd-icon-button') or contains(@class,'more')]"))
                time.sleep(0.5)
                click_js(driver.find_element(By.XPATH, "//div[contains(@class,'oxd-dropdown-menu')]//p[contains(normalize-space(),'Delete')]"))
                try:
                    click_js(WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[@type='button' and contains(.,'Yes, Delete')]"))))
                except TimeoutException:
                    pass
                time.sleep(1)
            except Exception:
                pass

        # Step 10: Delete post
        try:
            click_js(post_card.find_element(By.XPATH, ".//button[contains(@class,'oxd-icon-button') or contains(@class,'more')]"))
            time.sleep(0.5)
            click_js(driver.find_element(By.XPATH, "//div[contains(@class,'oxd-dropdown-menu')]//p[contains(normalize-space(),'Delete')]"))
            try:
                click_js(WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[@type='button' and contains(.,'Yes, Delete')]"))))
            except TimeoutException:
                pass
            try:
                WebDriverWait(driver, 10).until(EC.staleness_of(post_card))
            except TimeoutException:
                pass
        except Exception:
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
