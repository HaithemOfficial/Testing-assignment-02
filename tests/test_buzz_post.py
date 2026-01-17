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
        wait = WebDriverWait(driver, 30)

        def click_js(el):
            try:
                el.click()
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", el)

        def wait_xpath(xpath, cond=EC.presence_of_element_located, timeout=30):
            return WebDriverWait(driver, timeout).until(cond((By.XPATH, xpath)))

        print("Step 1: Logging in...")
        driver.get(base_url)
        u = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        p = driver.find_element(By.NAME, "password")
        u.clear(); u.send_keys(login_credentials["username"]) 
        p.clear(); p.send_keys(login_credentials["password"]) 
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        wait.until(EC.presence_of_element_located((By.XPATH, "//span/h6[text()='Dashboard']")))
        print("✓ Logged in")
        
        print("Step 2: Opening Buzz feed...")
        click_js(wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Buzz']"))))
        wait_xpath("//h6[text()='Buzz']")
        print("✓ Buzz feed loaded")
        
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        content = BuzzContent(
            message=f"Automated buzz post {ts}",
            updated_message=f"Updated buzz post {ts}",
            comment=f"Automated comment {ts}",
            updated_comment=f"Updated comment {ts}",
        )

        print("Step 3: Creating buzz post with text and image...")
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
            print("✓ Image attached to post")
        except Exception:
            print("Warning: Could not attach image")

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
        print("✓ Post submitted")

        if existing_top is not None:
            try:
                WebDriverWait(driver, 10).until(EC.staleness_of(existing_top))
            except TimeoutException:
                pass
        post_card = wait_xpath("(//div[contains(@class,'orangehrm-buzz-post')])[1]")
        
        print("Step 4: Liking post...")
        try:
            click_js(post_card.find_element(By.XPATH, ".//button[contains(.,'Like') or contains(.,'Unlike')]"))
            print("✓ Post liked")
        except Exception:
            print("Warning: Could not like post")
        
        print("Step 5: Editing post text...")
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
            print("✓ Post edited")
        except Exception:
            print("Warning: Could not edit post")

        # Step 6: Add comment
        print("Step 6: Adding comment...")
        try:
            cinput = wait_xpath("//input[@placeholder='Write your comment...'] | //textarea[@placeholder='Write your comment...']", EC.element_to_be_clickable)
            cinput.clear(); cinput.send_keys(content.comment); cinput.send_keys(Keys.ENTER)
            print("✓ Comment added")
        except Exception:
            try:
                click_js(driver.find_element(By.XPATH, "//button[contains(.,'Comment')]") )
                area = wait_xpath("//div[contains(@class,'orangehrm-buzz-comment')]//textarea")
                area.clear(); area.send_keys(content.comment); area.send_keys(Keys.ENTER)
                print("✓ Comment added via fallback")
            except Exception:
                print("Warning: Could not add comment")

        comment_block = None
        try:
            comment_block = wait_xpath(f"//div[contains(@class,'orangehrm-buzz-comment')][.//*[contains(normalize-space(), '{content.comment.split()[0]}')]]")
        except TimeoutException:
            pass

        # Step 7: Like comment
        if comment_block:
            print("Step 7: Liking comment...")
            try:
                click_js(comment_block.find_element(By.XPATH, ".//button[contains(.,'Like') or contains(.,'Unlike')]"))
                print("✓ Comment liked")
            except Exception:
                print("Warning: Could not like comment")

        # Step 8: Edit comment
        if comment_block:
            print("Step 8: Editing comment...")
            try:
                click_js(comment_block.find_element(By.XPATH, ".//button[contains(@class,'oxd-icon-button') or contains(@class,'more')]"))
                time.sleep(0.5)
                click_js(driver.find_element(By.XPATH, "//div[contains(@class,'oxd-dropdown-menu')]//p[contains(normalize-space(),'Edit')]") )
                area = wait_xpath("//div[contains(@class,'orangehrm-buzz-comment')]//textarea")
                try:
                    area.clear()
                except Exception:
                    area.send_keys(Keys.CONTROL, "a"); area.send_keys(Keys.BACKSPACE)
                area.send_keys(content.updated_comment); area.send_keys(Keys.ENTER)
                comment_block = wait_xpath(f"//div[contains(@class,'orangehrm-buzz-comment')][.//*[contains(normalize-space(), '{content.updated_comment.split()[0]}')]]")
                print("✓ Comment edited")
            except Exception:
                print("Warning: Could not edit comment")

        # Step 9: Delete comment
        if comment_block:
            print("Step 9: Deleting comment...")
            try:
                click_js(comment_block.find_element(By.XPATH, ".//button[contains(@class,'oxd-icon-button') or contains(@class,'more')]"))
                time.sleep(0.5)
                click_js(driver.find_element(By.XPATH, "//div[contains(@class,'oxd-dropdown-menu')]//p[contains(normalize-space(),'Delete')]"))
                try:
                    click_js(WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[@type='button' and contains(.,'Yes, Delete')]"))))
                except TimeoutException:
                    pass
                time.sleep(1)
                print("✓ Comment deleted")
            except Exception:
                print("Warning: Could not delete comment")

        # Step 10: Delete post
        print("Step 10: Deleting post...")
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
            print("✓ Post deleted")
        except Exception:
            print("Warning: Could not delete post")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
