import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# CONFIG
STRAVA_EMAIL = os.environ['STRAVA_EMAIL']
STRAVA_PASSWORD = os.environ['STRAVA_PASSWORD']

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    # Mask automation to avoid immediate detection
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    return webdriver.Chrome(options=chrome_options)

def login_and_kudos():
    driver = setup_driver()
    try:
        print("Navigating to Strava Login...")
        driver.get("https://www.strava.com/login")
        time.sleep(5) # Wait for redirects

        # DEBUG: Tell us what page we are actually on
        print(f"DEBUG: Page Title is: '{driver.title}'")
        
        # 1. Handle Cookie Banner
        try:
            accept_cookies = driver.find_element(By.CLASS_NAME, "btn-accept-cookie-banner")
            accept_cookies.click()
            print("Cookies accepted.")
        except:
            print("No cookie banner found.")

        # 2. Login
        print("Looking for email field...")
        
        # Try finding the email field by ID, Name, or Type
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='email']"))
        )
        
        print("Found email field. Entering credentials...")
        email_field.send_keys(STRAVA_EMAIL)
        driver.find_element(By.CSS_SELECTOR, "input[name='password']").send_keys(STRAVA_PASSWORD)
        driver.find_element(By.ID, "login-button").click()
        
        # 3. Wait for Dashboard
        print("Waiting for dashboard...")
        WebDriverWait(driver, 15).until(EC.url_contains("/dashboard"))
        print("Login successful!")

        # 4. Scroll and Kudos
        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        buttons = driver.find_elements(By.CSS_SELECTOR, "button[data-testid='kudos_button']")
        print(f"Found {len(buttons)} potential kudos buttons.")
        
        count = 0
        for btn in buttons:
            try:
                driver.execute_script("arguments[0].click();", btn)
                count += 1
                if count >= 20: break
            except: pass

        print(f"Run Complete. Total Kudos: {count}")

    except Exception as e:
        print(f"CRASH REPORT:")
        print(f"Error Message: {e}")
        print("-" * 20)
        print("PAGE SOURCE DUMP (First 500 chars):")
        print(driver.page_source[:500]) 
        print("-" * 20)

    finally:
        driver.quit()

if __name__ == "__main__":
    login_and_kudos()
