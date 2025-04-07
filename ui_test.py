import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Create screenshots directory if it doesn't exist
os.makedirs("screenshots", exist_ok=True)

# Initialize the driver
driver = webdriver.Chrome(options=chrome_options)

# Test function to capture screenshots of different UI sections
def test_ui_sections():
    print("Starting UI testing...")
    
    # Navigate to the application
    driver.get("http://localhost:8080")
    time.sleep(2)  # Wait for page to load
    
    # Take screenshot of main page
    driver.save_screenshot("screenshots/main_page.png")
    print("Captured main page screenshot")
    
    # Test Chat section (default view)
    print("Testing Chat section...")
    chat_input = driver.find_element(By.ID, "user-input")
    chat_input.send_keys("Hello, this is a test message")
    send_button = driver.find_element(By.XPATH, "//button[text()='Send']")
    send_button.click()
    time.sleep(2)  # Wait for response
    driver.save_screenshot("screenshots/chat_test.png")
    print("Tested Chat functionality")
    
    # Test Tools section
    print("Testing Tools section...")
    tools_tab = driver.find_element(By.XPATH, "//li[text()='Tools']")
    tools_tab.click()
    time.sleep(1)
    driver.save_screenshot("screenshots/tools_section.png")
    
    # Test tool functionality
    test_button = driver.find_element(By.XPATH, "//button[text()='Test']")
    test_button.click()
    time.sleep(1)
    driver.save_screenshot("screenshots/tool_test.png")
    print("Tested Tools functionality")
    
    # Test Settings section
    print("Testing Settings section...")
    settings_tab = driver.find_element(By.XPATH, "//li[text()='Settings']")
    settings_tab.click()
    time.sleep(1)
    driver.save_screenshot("screenshots/settings_section.png")
    
    # Test adding a new setting
    setting_key = driver.find_element(By.ID, "setting-key")
    setting_key.send_keys("TEST_SETTING")
    setting_value = driver.find_element(By.ID, "setting-value")
    setting_value.send_keys("test_value")
    setting_desc = driver.find_element(By.ID, "setting-description")
    setting_desc.send_keys("Test setting description")
    add_button = driver.find_element(By.XPATH, "//button[text()='Add Setting']")
    add_button.click()
    time.sleep(1)
    driver.save_screenshot("screenshots/setting_added.png")
    print("Tested Settings functionality")
    
    # Test Logging section
    print("Testing Logging section...")
    logging_tab = driver.find_element(By.XPATH, "//li[text()='Logging']")
    logging_tab.click()
    time.sleep(1)
    driver.save_screenshot("screenshots/logging_section.png")
    print("Verified Logging section")
    
    # Test DevChat section
    print("Testing DevChat section...")
    devchat_tab = driver.find_element(By.XPATH, "//li[text()='DevChat']")
    devchat_tab.click()
    time.sleep(1)
    
    # Test DevChat functionality
    dev_input = driver.find_element(By.ID, "dev-input")
    dev_input.send_keys("Tell me about the database models")
    dev_send_button = driver.find_element(By.XPATH, "//div[@id='dev-chat-section']//button[text()='Send']")
    dev_send_button.click()
    time.sleep(2)  # Wait for response
    driver.save_screenshot("screenshots/devchat_test.png")
    print("Tested DevChat functionality")
    
    print("UI testing completed successfully!")

# Run the tests
try:
    test_ui_sections()
except Exception as e:
    print(f"Error during UI testing: {str(e)}")
finally:
    # Close the browser
    driver.quit()
    print("Browser closed")
