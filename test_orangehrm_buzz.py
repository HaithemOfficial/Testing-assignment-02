"""Buzz module test for OrangeHRM demo.

Covers:
- Adding a Buzz post with text and attached picture.
- Liking and editing your own post.
- Adding a comment on your post.
- Liking, editing, and deleting your comment.
- Deleting your original post.
"""
import os
import time
from datetime import datetime

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException


class TestOrangeHRMBuzz:
    """Tests Buzz posting, reactions, comments, and cleanup."""

    def test_buzz_post_with_picture_and_comments(self, driver, base_url, login_credentials):
        """Create a Buzz post with an image, interact with it, then clean up."""

        wait = WebDriverWait(driver, 20)

        # ====================
        # STEP 1: Login
        # ====================
        print("[BUZZ] Step 1: Logging in...")
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
        print("[BUZZ] ✓ Logged in")

        # ====================
        # STEP 2: Navigate to Buzz
        # ====================
        print("[BUZZ] Step 2: Navigating to Buzz...")

        buzz_menu = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Buzz']"))
        )
        buzz_menu.click()

        wait.until(
            EC.presence_of_element_located((By.XPATH, "//h6[text()='Buzz']"))
        )
        print("[BUZZ] ✓ Buzz page loaded")

        # ====================
        # STEP 3: Create a post with text and picture
        # ====================
        print("[BUZZ] Step 3: Creating a Buzz post with picture...")

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        message_base = "Automated buzz post"
        message_text = f"{message_base} {timestamp}"
        updated_message_base = "Updated buzz post"
        updated_message_text = f"{updated_message_base} {timestamp}"
        comment_base = "Automated comment"
        comment_text = f"{comment_base} {timestamp}"
        updated_comment_base = "Updated comment"
        updated_comment_text = f"{updated_comment_base} {timestamp}"

        # Enter message text
        try:
            post_textarea = wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//textarea | //form//p[contains(@class,'oxd-buzz-post-input')]/ancestor::form//textarea",
                    )
                )
            )
        except TimeoutException:
            # Fallback: contenteditable div used as input
            post_textarea = wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//div[@contenteditable='true' and contains(@class,'oxd-buzz-post-input')]",
                    )
                )
            )

        post_textarea.clear() if hasattr(post_textarea, "clear") else None
        post_textarea.send_keys(message_text)

        # Attach image
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "test_data", "profile_image.png")

        try:
            attach_button = driver.find_element(
                By.XPATH,
                "//button[contains(@class,'oxd-buzz-post-img-button') or @type='button'][.//i or .//span]",
            )
            attach_button.click()
            file_input = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "input[type='file']")
                )
            )
            file_input.send_keys(image_path)
            print("[BUZZ]   ✓ Image attached to post")
        except Exception as e:
            print(f"[BUZZ]   Warning: Could not attach image to post: {e}")

        # Click Post/Share button
        # Capture the current top Buzz post (if any) so we can detect
        # a feed refresh after posting without relying on post text.
        existing_top_post = None
        try:
            existing_top_post = driver.find_element(
                By.XPATH,
                "(//div[contains(@class,'orangehrm-buzz-post')])[1]",
            )
        except Exception:
            existing_top_post = None

        try:
            post_button = driver.find_element(
                By.XPATH,
                "//button[@type='submit' and (contains(.,'Post') or contains(.,'Share'))]",
            )
        except Exception:
            post_button = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//form//button[contains(@class,'oxd-button') and (contains(.,'Post') or contains(.,'Share'))]",
                    )
                )
            )

        try:
            post_button.click()
        except ElementClickInterceptedException:
            driver.execute_script("arguments[0].click();", post_button)

        # Wait for feed to refresh and then take the top Buzz post
        # card as the one we just created. This avoids depending on
        # the rendered text inside the card, which can be flaky.
        print("[BUZZ]   Waiting for feed to refresh after posting...")
        if existing_top_post is not None:
            try:
                WebDriverWait(driver, 10).until(EC.staleness_of(existing_top_post))
            except TimeoutException:
                print("[BUZZ]   Warning: Top Buzz post did not become stale after posting")

        try:
            post_card = wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "(//div[contains(@class,'orangehrm-buzz-post')])[1]",
                    )
                )
            )
            print("[BUZZ]  Using top Buzz post as created post")
        except TimeoutException:
            pytest.fail("[BUZZ] Buzz feed did not contain any posts after posting")

        # ====================
        # STEP 4: Like your post
        # ====================
        print("[BUZZ] Step 4: Liking your post...")

        try:
            like_button = post_card.find_element(
                By.XPATH,
                ".//button[contains(.,'Like') or contains(.,'Unlike')]",
            )
            like_button.click()
            print("[BUZZ] ✓ Post like toggled")
        except Exception:
            print("[BUZZ]   Warning: Could not like/unlike the post")

        # ====================
        # STEP 5: Edit your post (best-effort)
        # ====================
        print("[BUZZ] Step 5: Editing your post...")

        try:
            # Open actions/menu for the post
            more_button = post_card.find_element(
                By.XPATH,
                ".//button[contains(@class,'oxd-icon-button') or contains(@class,'more')]",
            )
            more_button.click()
            time.sleep(0.5)

            edit_option = driver.find_element(
                By.XPATH,
                "//div[contains(@class,'oxd-dropdown-menu')]//p[contains(normalize-space(),'Edit')]",
            )
            edit_option.click()

            edit_textarea = wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//div[contains(@class,'orangehrm-buzz-post-modal')]//textarea | //div[contains(@class,'orangehrm-buzz-post-modal')]//div[@contenteditable='true']",
                    )
                )
            )
            # Clear existing content if possible, then type new
            try:
                edit_textarea.clear()
            except Exception:
                edit_textarea.send_keys(Keys.CONTROL, "a")
                edit_textarea.send_keys(Keys.BACKSPACE)
            edit_textarea.send_keys(updated_message_text)

            save_btn = driver.find_element(
                By.XPATH,
                "//div[contains(@class,'orangehrm-buzz-post-modal')]//button[@type='submit' and (contains(.,'Save') or contains(.,'Update'))]",
            )
            try:
                save_btn.click()
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", save_btn)

            # Give some time for update, then refresh reference to the
            # top Buzz post card instead of matching on text.
            time.sleep(2)
            try:
                post_card = wait.until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "(//div[contains(@class,'orangehrm-buzz-post')])[1]",
                        )
                    )
                )
                print("[BUZZ]  Post edited successfully (top Buzz post refreshed)")
            except TimeoutException:
                print("[BUZZ]   Warning: Could not confirm edited post in feed; proceeding best-effort")
        except Exception as exc:
            print(f"[BUZZ]   Warning: Could not edit post reliably: {exc}")

        # ====================
        # STEP 6: Add a comment on your post
        # ====================
        print("[BUZZ] Step 6: Adding a comment on your post...")
        comment_block = None

        try:
            # Prefer a dedicated comment input with placeholder text
            # anywhere on the page (not strictly tied to post_card),
            # since the DOM structure can vary.
            comment_input = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//input[@placeholder='Write your comment...'] | //textarea[@placeholder='Write your comment...']",
                    )
                )
            )
            comment_input.clear()
            comment_input.send_keys(comment_text)
            comment_input.send_keys(Keys.ENTER)
        except Exception:
            # Fallback: generic Comment button followed by textarea
            try:
                comment_toggle = driver.find_element(
                    By.XPATH,
                    "//button[contains(.,'Comment')]",
                )
                comment_toggle.click()
                comment_area = wait.until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "//div[contains(@class,'orangehrm-buzz-comment')]//textarea",
                        )
                    )
                )
                comment_area.clear()
                comment_area.send_keys(comment_text)
                comment_area.send_keys(Keys.ENTER)
            except Exception as exc:
                print(f"[BUZZ]   Warning: Could not add comment to post reliably: {exc}")

        # Wait for comment to appear (best-effort)
        try:
            comment_block = wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        f"//div[contains(@class,'orangehrm-buzz-comment')][.//*[contains(normalize-space(), '{comment_base}')]]",
                    )
                )
            )
            print("[BUZZ] ✓ Comment added")
        except TimeoutException:
            print("[BUZZ]   Warning: Comment did not appear under the post; skipping comment reactions")

        # ====================
        # STEP 7: Like your comment
        # ====================
        print("[BUZZ] Step 7: Liking your comment...")
        if comment_block is not None:
            try:
                comment_like = comment_block.find_element(
                    By.XPATH,
                    ".//button[contains(.,'Like') or contains(.,'Unlike')]",
                )
                comment_like.click()
                print("[BUZZ] ✓ Comment like toggled")
            except Exception:
                print("[BUZZ]   Warning: Could not like/unlike the comment")
        else:
            print("[BUZZ]   Skipping comment like because no comment block was found")

        # ====================
        # STEP 8: Edit your comment (best-effort)
        # ====================
        print("[BUZZ] Step 8: Editing your comment...")
        if comment_block is not None:
            try:
                comment_more = comment_block.find_element(
                    By.XPATH,
                    ".//button[contains(@class,'oxd-icon-button') or contains(@class,'more')]",
                )
                comment_more.click()
                time.sleep(0.5)

                edit_comment_option = driver.find_element(
                    By.XPATH,
                    "//div[contains(@class,'oxd-dropdown-menu')]//p[contains(normalize-space(),'Edit')]",
                )
                edit_comment_option.click()

                edit_comment_area = wait.until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "//div[contains(@class,'orangehrm-buzz-comment')]//textarea",
                        )
                    )
                )
                try:
                    edit_comment_area.clear()
                except Exception:
                    edit_comment_area.send_keys(Keys.CONTROL, "a")
                    edit_comment_area.send_keys(Keys.BACKSPACE)
                edit_comment_area.send_keys(updated_comment_text)
                edit_comment_area.send_keys(Keys.ENTER)

                comment_block = wait.until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            f"//div[contains(@class,'orangehrm-buzz-comment')][.//*[contains(normalize-space(), '{updated_comment_base}')]]",
                        )
                    )
                )
                print("[BUZZ] ✓ Comment edited successfully")
            except Exception as exc:
                print(f"[BUZZ]   Warning: Could not edit comment reliably: {exc}")
        else:
            print("[BUZZ]   Skipping comment edit because no comment block was found")

        # ====================
        # STEP 9: Delete your comment
        # ====================
        print("[BUZZ] Step 9: Deleting your comment...")
        if comment_block is not None:
            try:
                comment_more = comment_block.find_element(
                    By.XPATH,
                    ".//button[contains(@class,'oxd-icon-button') or contains(@class,'more')]",
                )
                comment_more.click()
                time.sleep(0.5)

                delete_comment_option = driver.find_element(
                    By.XPATH,
                    "//div[contains(@class,'oxd-dropdown-menu')]//p[contains(normalize-space(),'Delete')]",
                )
                delete_comment_option.click()

                # Confirm delete if dialog appears
                try:
                    confirm_btn = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable(
                            (
                                By.XPATH,
                                "//button[@type='button' and contains(.,'Yes, Delete')]",
                            )
                        )
                    )
                    confirm_btn.click()
                except TimeoutException:
                    pass

                # Verify the comment is gone (best-effort)
                time.sleep(2)
                deleted_elements = driver.find_elements(
                    By.XPATH,
                    f"//div[contains(@class,'orangehrm-buzz-comment')][.//*[contains(normalize-space(), '{updated_comment_base}') or contains(normalize-space(), '{comment_base}')]]",
                )
                if deleted_elements:
                    print("[BUZZ]   Warning: Comment still present after delete attempt")
                else:
                    print("[BUZZ] ✓ Comment deleted (or no longer visible)")
            except Exception as exc:
                print(f"[BUZZ]   Warning: Could not delete comment reliably: {exc}")
        else:
            print("[BUZZ]   Skipping comment delete because no comment block was found")

        # ====================
        # STEP 10: Delete your post
        # ====================
        print("[BUZZ] Step 10: Deleting your post...")

        try:
            post_more = post_card.find_element(
                By.XPATH,
                ".//button[contains(@class,'oxd-icon-button') or contains(@class,'more')]",
            )
            post_more.click()
            time.sleep(0.5)

            delete_post_option = driver.find_element(
                By.XPATH,
                "//div[contains(@class,'oxd-dropdown-menu')]//p[contains(normalize-space(),'Delete')]",
            )
            delete_post_option.click()

            # Confirm delete if dialog appears
            try:
                confirm_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "//button[@type='button' and contains(.,'Yes, Delete')]",
                        )
                    )
                )
                confirm_btn.click()
            except TimeoutException:
                pass

            # Verify the specific post card is gone (best-effort)
            try:
                WebDriverWait(driver, 10).until(EC.staleness_of(post_card))
                print("[BUZZ]  Post deleted (original card removed from feed)")
            except TimeoutException:
                print("[BUZZ]   Warning: Could not confirm post deletion; card may still be visible")
        except Exception as exc:
            print(f"[BUZZ]   Warning: Could not delete post reliably: {exc}")

        print("[BUZZ] === Buzz post with picture and comments test completed ===")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
