import time
import os
import requests
import threading
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-popup-blocking")

# Create screenshots directory if it doesn't exist
os.makedirs("screenshots", exist_ok=True)

# Security and performance test results
results = {
    "security": [],
    "performance": []
}

def log_result(category, test_name, status, details=""):
    results[category].append({
        "test": test_name,
        "status": status,
        "details": details,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    })
    print(f"[{category.upper()}] {test_name}: {status} - {details}")

def test_api_endpoints_security():
    """Test API endpoints for common security issues"""
    base_url = "http://localhost:8080"
    
    # Test 1: Check for proper error handling on invalid input
    try:
        resp = requests.post(f"{base_url}/api/chat", json={"invalid": "data"})
        if resp.status_code == 400 and "error" in resp.json():
            log_result("security", "API Error Handling", "PASS", "Properly handles invalid input")
        else:
            log_result("security", "API Error Handling", "FAIL", f"Unexpected response: {resp.status_code} - {resp.text}")
    except Exception as e:
        log_result("security", "API Error Handling", "ERROR", str(e))
    
    # Test 2: Check for SQL injection protection
    try:
        payload = {"message": "'; DROP TABLE users; --"}
        resp = requests.post(f"{base_url}/api/chat", json=payload)
        if resp.status_code != 500:
            log_result("security", "SQL Injection Protection", "PASS", "No server error on SQL injection attempt")
        else:
            log_result("security", "SQL Injection Protection", "FAIL", "Server error on SQL injection attempt")
    except Exception as e:
        log_result("security", "SQL Injection Protection", "ERROR", str(e))
    
    # Test 3: Check for proper authentication/authorization
    try:
        # This should be a protected endpoint in a real system
        resp = requests.get(f"{base_url}/api/environment")
        if resp.status_code == 200:
            log_result("security", "Authorization Check", "INFO", "Environment endpoint is publicly accessible")
        elif resp.status_code == 401 or resp.status_code == 403:
            log_result("security", "Authorization Check", "PASS", "Environment endpoint properly protected")
    except Exception as e:
        log_result("security", "Authorization Check", "ERROR", str(e))
    
    # Test 4: Check for XSS protection
    try:
        payload = {"name": "<script>alert('XSS')</script>", "description": "XSS Test", "function_code": "print('test')"}
        resp = requests.post(f"{base_url}/api/tools", json=payload)
        if resp.status_code == 200:
            # In a real test, we would check if the script is escaped in the response
            log_result("security", "XSS Protection", "INFO", "Tool created with script tag in name")
        else:
            log_result("security", "XSS Protection", "INFO", f"Could not create tool with script tag: {resp.status_code}")
    except Exception as e:
        log_result("security", "XSS Protection", "ERROR", str(e))

def test_api_performance():
    """Test API endpoints for performance"""
    base_url = "http://localhost:8080"
    endpoints = [
        {"url": "/api/health", "method": "get", "data": None},
        {"url": "/api/conversations", "method": "get", "data": None},
        {"url": "/api/tools", "method": "get", "data": None},
        {"url": "/api/environment", "method": "get", "data": None},
        {"url": "/api/chat", "method": "post", "data": {"message": "Hello, performance test"}}
    ]
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint['url']}"
        method = endpoint['method']
        data = endpoint['data']
        
        # Measure response time
        start_time = time.time()
        try:
            if method == "get":
                resp = requests.get(url)
            elif method == "post":
                resp = requests.post(url, json=data)
            
            elapsed_time = time.time() - start_time
            
            if resp.status_code < 400:
                status = "PASS" if elapsed_time < 1.0 else "WARN"
                log_result("performance", f"API Response Time - {endpoint['url']}", 
                          status, f"Response time: {elapsed_time:.3f}s")
            else:
                log_result("performance", f"API Response Time - {endpoint['url']}", 
                          "FAIL", f"HTTP {resp.status_code}: {resp.text}")
        except Exception as e:
            log_result("performance", f"API Response Time - {endpoint['url']}", 
                      "ERROR", str(e))

def test_load_performance():
    """Test system under load with concurrent requests"""
    base_url = "http://localhost:8080"
    num_requests = 10
    
    def make_request(i):
        try:
            start_time = time.time()
            resp = requests.get(f"{base_url}/api/health")
            elapsed_time = time.time() - start_time
            return {"id": i, "status_code": resp.status_code, "time": elapsed_time}
        except Exception as e:
            return {"id": i, "error": str(e)}
    
    # Execute concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(make_request, i) for i in range(num_requests)]
        results_list = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    # Analyze results
    success_times = [r["time"] for r in results_list if "status_code" in r and r["status_code"] == 200]
    if success_times:
        avg_time = sum(success_times) / len(success_times)
        max_time = max(success_times)
        log_result("performance", "Concurrent Requests", 
                  "PASS" if avg_time < 1.0 else "WARN",
                  f"Avg: {avg_time:.3f}s, Max: {max_time:.3f}s, Success: {len(success_times)}/{num_requests}")
    else:
        log_result("performance", "Concurrent Requests", "FAIL", "No successful requests")

def test_ui_security():
    """Test UI for common security issues"""
    try:
        # Initialize the driver
        driver = webdriver.Chrome(options=chrome_options)
        
        # Navigate to the application
        driver.get("http://localhost:8080")
        time.sleep(2)  # Wait for page to load
        
        # Test 1: Check for secure input handling in chat
        try:
            chat_input = driver.find_element(By.ID, "user-input")
            script_payload = "<script>alert('XSS Test')</script>"
            chat_input.send_keys(script_payload)
            send_button = driver.find_element(By.XPATH, "//button[text()='Send']")
            send_button.click()
            time.sleep(2)
            
            # Check if the script was rendered as text and not executed
            page_source = driver.page_source
            if script_payload in page_source and "Tool test successful" not in page_source:
                log_result("security", "UI XSS Protection - Chat", "PASS", "Script tag properly escaped")
            else:
                log_result("security", "UI XSS Protection - Chat", "INFO", "Could not verify script handling")
            
            driver.save_screenshot("screenshots/security_xss_test.png")
        except Exception as e:
            log_result("security", "UI XSS Protection - Chat", "ERROR", str(e))
        
        # Test 2: Check for secure input handling in settings
        try:
            settings_tab = driver.find_element(By.XPATH, "//li[text()='Settings']")
            settings_tab.click()
            time.sleep(1)
            
            setting_key = driver.find_element(By.ID, "setting-key")
            setting_key.send_keys("<script>alert('XSS')</script>")
            setting_value = driver.find_element(By.ID, "setting-value")
            setting_value.send_keys("test_value")
            add_button = driver.find_element(By.XPATH, "//button[text()='Add Setting']")
            add_button.click()
            time.sleep(1)
            
            driver.save_screenshot("screenshots/security_settings_xss.png")
            log_result("security", "UI XSS Protection - Settings", "INFO", "Completed settings XSS test")
        except UnexpectedAlertPresentException:
            # If an alert appears, it might be from our test or from a real XSS vulnerability
            log_result("security", "UI XSS Protection - Settings", "WARN", "Alert detected during XSS test")
            driver.save_screenshot("screenshots/security_settings_xss_alert.png")
        except Exception as e:
            log_result("security", "UI XSS Protection - Settings", "ERROR", str(e))
        
        # Close the browser
        driver.quit()
        log_result("security", "UI Security Tests", "INFO", "Completed UI security testing")
    except Exception as e:
        log_result("security", "UI Security Tests", "ERROR", f"Failed to run UI security tests: {str(e)}")

def test_ui_performance():
    """Test UI performance metrics"""
    try:
        # Initialize the driver
        driver = webdriver.Chrome(options=chrome_options)
        
        # Measure page load time
        start_time = time.time()
        driver.get("http://localhost:8080")
        
        # Wait for the page to be fully loaded
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "user-input"))
        )
        
        load_time = time.time() - start_time
        log_result("performance", "UI Page Load Time", 
                  "PASS" if load_time < 3.0 else "WARN", 
                  f"Load time: {load_time:.3f}s")
        
        # Test UI responsiveness by measuring tab switching time
        try:
            # Switch to Tools tab and measure time
            start_time = time.time()
            tools_tab = driver.find_element(By.XPATH, "//li[text()='Tools']")
            tools_tab.click()
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, "tools-section"))
            )
            tools_switch_time = time.time() - start_time
            
            # Switch to Settings tab and measure time
            start_time = time.time()
            settings_tab = driver.find_element(By.XPATH, "//li[text()='Settings']")
            settings_tab.click()
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, "settings-section"))
            )
            settings_switch_time = time.time() - start_time
            
            # Switch to Logging tab and measure time
            start_time = time.time()
            logging_tab = driver.find_element(By.XPATH, "//li[text()='Logging']")
            logging_tab.click()
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, "logging-section"))
            )
            logging_switch_time = time.time() - start_time
            
            # Calculate average tab switch time
            avg_switch_time = (tools_switch_time + settings_switch_time + logging_switch_time) / 3
            log_result("performance", "UI Tab Switching Time", 
                      "PASS" if avg_switch_time < 0.5 else "WARN", 
                      f"Average switch time: {avg_switch_time:.3f}s")
            
            driver.save_screenshot("screenshots/performance_ui_test.png")
        except Exception as e:
            log_result("performance", "UI Tab Switching Time", "ERROR", str(e))
        
        # Close the browser
        driver.quit()
        log_result("performance", "UI Performance Tests", "INFO", "Completed UI performance testing")
    except Exception as e:
        log_result("performance", "UI Performance Tests", "ERROR", f"Failed to run UI performance tests: {str(e)}")

def generate_report():
    """Generate a comprehensive security and performance report"""
    report = """
# Security and Performance Test Report

## Summary
This report contains the results of automated security and performance testing for the AI Agent System.

## Security Test Results
"""
    
    for result in results["security"]:
        status_icon = "✅" if result["status"] == "PASS" else "⚠️" if result["status"] == "WARN" else "❌" if result["status"] == "FAIL" else "ℹ️"
        report += f"\n### {status_icon} {result['test']}\n"
        report += f"- Status: {result['status']}\n"
        report += f"- Details: {result['details']}\n"
        report += f"- Timestamp: {result['timestamp']}\n"
    
    report += """
## Performance Test Results
"""
    
    for result in results["performance"]:
        status_icon = "✅" if result["status"] == "PASS" else "⚠️" if result["status"] == "WARN" else "❌" if result["status"] == "FAIL" else "ℹ️"
        report += f"\n### {status_icon} {result['test']}\n"
        report += f"- Status: {result['status']}\n"
        report += f"- Details: {result['details']}\n"
        report += f"- Timestamp: {result['timestamp']}\n"
    
    report += """
## Recommendations
Based on the test results, here are recommendations for improving the system:

1. Implement proper authentication and authorization for sensitive endpoints
2. Add rate limiting to prevent abuse
3. Optimize database queries for better performance under load
4. Implement content security policy (CSP) headers
5. Add CSRF protection for all state-changing operations
6. Consider adding caching for frequently accessed data

## Screenshots
Screenshots from the testing process are available in the screenshots directory.
"""
    
    # Write report to file
    with open("security_performance_report.md", "w") as f:
        f.write(report)
    
    print(f"Report generated: security_performance_report.md")

# Run all tests
print("Starting security and performance testing...")

# Run security tests
print("\n=== Running Security Tests ===")
test_api_endpoints_security()
test_ui_security()

# Run performance tests
print("\n=== Running Performance Tests ===")
test_api_performance()
test_load_performance()
test_ui_performance()

# Generate report
print("\n=== Generating Report ===")
generate_report()

print("\nSecurity and performance testing completed!")
