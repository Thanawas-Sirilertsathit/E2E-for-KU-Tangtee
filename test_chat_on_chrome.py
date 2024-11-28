"""Test chat E2E"""
from decouple import Config
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import uuid
import time

config = Config()

URL = config('URL')
EMAIL = config('EMAIL')
PASSWORD = config('PASSWORD')
SEARCH_KEYWORD = config('SEARCH_KEYWORD')
HEADLESS = config('HEADLESS', default='True') == 'True'

def get_driver(headless=True):
    """Construct driver"""
    options = Options()
    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
    else:
        options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    return driver

driver = get_driver(HEADLESS)

try:
    # Open the url
    url = URL
    driver.get(url)
    expected_title = "ku-tangtee"
    time.sleep(2)

    # Confirm title
    if driver.title == expected_title:
        print(f"Page title verified: {driver.title}")
    else:
        print(f"Unexpected title: {driver.title}")

    # Search bar test
    try:
        search_box = driver.find_element(By.CSS_SELECTOR, "input[placeholder='Search']")
        search_box.send_keys(SEARCH_KEYWORD + Keys.RETURN)
        time.sleep(2)
        print("Search box interacted successfully!")

    except Exception as e:
        print("Search box not found:", e)

    # Click view button on the first activity that we found
    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "button"))
        )
        view_button = driver.find_element(By.XPATH, "//button[contains(text(), 'View')]")
        view_button.click()
        print("View button clicked successfully!")
        time.sleep(2)

    except Exception as e:
        print("View button not found or could not be clicked:", e)

    # Click login button to initiate Google OAuth
    try:
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Login')]"))
        )
        login_button.click()
        print("Login button clicked successfully!")
        time.sleep(2)

        main_window = driver.current_window_handle
        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
        for handle in driver.window_handles:
            if handle != main_window:
                driver.switch_to.window(handle)
                break

        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "identifierId"))
        )
        email_field.send_keys(EMAIL)
        driver.find_element(By.ID, "identifierNext").click()
        print("Input email successfully")
        password_field = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type=password]"))
        )
        password_field.send_keys(PASSWORD)
        driver.find_element(By.ID, "passwordNext").click()
        print("Input password successfully")

        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(1))
        driver.switch_to.window(main_window)
        print("Logged in successfully via Google OAuth!")
        time.sleep(2)

    except Exception as e:
        print("Login failed:", e)

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    print("Scrolled down the page!")

    # Click the Chat button
    try:
        chat_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Chat')]"))
        )
        chat_button.click()
        print("Chat button clicked successfully!")
        time.sleep(3)

    except Exception as e:
        print("Chat button not found or could not be clicked:", e)

    # Generate test message using uuid
    test_message = f"Test message: {uuid.uuid4()}"
    print(f"Generated test message: {test_message}")

    # Input in the chat textarea
    try:
        chat_input_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[placeholder='Start your chat']"))
        )
        chat_input_field.send_keys(test_message + Keys.RETURN)
        print("Message inputted into the chat textarea!")
        time.sleep(2)

    except Exception as e:
        print("Chat input field not found:", e)

    # Check the existence chat bubble we sent
    try:
        chat_bubbles = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".chat-bubble"))
        )
        for bubble in chat_bubbles:
            if test_message in bubble.text:
                print(f"Found chat bubble contains the message: {test_message}")
                break
        else:
            print("Chat bubble with the expected message not found.")
    except Exception as e:
        print("Chat bubble not found or message not sent:", e)

    # Save screenshot
    screenshot_path = "screenshot.png"
    driver.save_screenshot(screenshot_path)
    print(f"Screenshot saved at: {screenshot_path}")

finally:
    driver.quit()
