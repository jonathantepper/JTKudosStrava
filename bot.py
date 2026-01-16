import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# CONFIG
STRAVA_EMAIL = os.environ['STRAVA_EMAIL']
STRAVA_PASSWORD = os.environ['STRAVA_PASSWORD']

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run invisible
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    # Mask automation to avoid immediate detection
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
    
    return webdriver.Chrome(options=chrome_options)

def login_and_kudos():
    driver = setup_driver()
    try:
        print("Navigating to Strava Login...")
        driver.get("https://www.strava.com/login")
        
        # 1. Handle Cookie Banner (if it pops up)
        try:
            accept_cookies = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "btn-accept-cookie-banner"))
            )
            accept_cookies.click()
            print("Cookies accepted.")
        except:
            print("No cookie banner found (or already accepted).")

        # 2. Login
        print("Entering credentials...")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email")))
        
        driver.find_element(By.ID, "email").send_keys(STRAVA_EMAIL)
        driver.find_element(By.ID, "password").send_keys(STRAVA_PASSWORD)
        driver.find_element(By.ID, "login-button").click()
        
        # 3. Wait for Dashboard
        print("Waiting for dashboard...")
        WebDriverWait(driver, 15).until(EC.url_contains("/dashboard"))
        print("Login successful!")

        # 4. Scroll and Kudos
        # We scroll down a few times to load the feed
        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        # Find empty kudos buttons (unfilled hearts/thumbs)
        # Note: Strava changes these IDs often. We look for the specific 'kudos' testid or class.
        # Current common selector for un-clicked kudos:
        buttons = driver.find_elements(By.CSS_SELECTOR, "button[data-testid='kudos_button']")
        
        count = 0
        print(f"Found {len(buttons)} potential kudos buttons.")
        
        for btn in buttons:
            try:
                # Check if it's already filled (Strava usually changes the icon, but clicking again usually toggles or does nothing. 
                # Strava 'unfilled' kudos buttons usually have a specific SVG inside.)
                
                # We click using JS to avoid 'element intercepted' errors
                driver.execute_script("arguments[0].click();", btn)
                print("Kudos given!")
                count += 1
                time.sleep(1) # Human pause
                
                if count >= 20: # Sip limit
                    break
            except Exception as e:
                print(f"Skipped a button: {e}")

        print(f"Run Complete. Total Kudos: {count}")

    except Exception as e:
        print(f"Crash: {e}")
        # Debug: Print page source if we fail
        # print(driver.page_source)
    finally:
        driver.quit()

if __name__ == "__main__":
    login_and_kudos()
