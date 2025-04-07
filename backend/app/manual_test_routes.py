"""
Manual testing API routes for the AI Agent System
"""
from flask import Blueprint, jsonify, request, Response, current_app
import json
import base64
import os
import time
from datetime import datetime
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
from io import BytesIO

# Create blueprint
manual_tests_api = Blueprint('manual_tests_api', __name__)

# Store test logs
manual_test_logs = []

def init_manual_tests_routes(app):
    """Initialize manual test routes"""
    app.register_blueprint(manual_tests_api, url_prefix='/api/tests/manual')

@manual_tests_api.route('/logs')
def get_test_logs():
    """Get all test logs"""
    return jsonify({'logs': manual_test_logs})

@manual_tests_api.route('/log', methods=['POST'])
def add_test_log():
    """Add a test log"""
    log_data = request.json
    
    # Add timestamp if not provided
    if 'timestamp' not in log_data:
        log_data['timestamp'] = datetime.now().isoformat()
    
    manual_test_logs.insert(0, log_data)
    
    # Keep only the last 100 logs
    if len(manual_test_logs) > 100:
        manual_test_logs.pop()
    
    return jsonify({'success': True})

@manual_tests_api.route('/logs/clear', methods=['POST'])
def clear_test_logs():
    """Clear all test logs"""
    manual_test_logs.clear()
    return jsonify({'success': True})

@manual_tests_api.route('/screenshot', methods=['POST'])
def take_screenshot():
    """Take a screenshot of the current browser state"""
    try:
        # Set up headless Chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        driver = webdriver.Chrome(options=chrome_options)
        
        # Navigate to the application
        app_url = request.json.get('url', 'http://localhost:5000')
        driver.get(app_url)
        
        # Wait for page to load
        time.sleep(2)
        
        # Take screenshot
        screenshot = driver.get_screenshot_as_png()
        
        # Close the browser
        driver.quit()
        
        # Convert to base64 for sending to frontend
        screenshot_base64 = base64.b64encode(screenshot).decode('utf-8')
        
        # Save screenshot to file
        screenshots_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'screenshots')
        os.makedirs(screenshots_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        screenshot_path = os.path.join(screenshots_dir, f'screenshot_{timestamp}.png')
        
        with open(screenshot_path, 'wb') as f:
            f.write(screenshot)
        
        # Add log
        manual_test_logs.insert(0, {
            'timestamp': datetime.now().isoformat(),
            'component': 'System',
            'action': 'Take screenshot',
            'result': f'Screenshot saved to {screenshot_path}',
            'status': 'success'
        })
        
        return jsonify({
            'success': True,
            'screenshot': screenshot_base64,
            'path': screenshot_path
        })
        
    except Exception as e:
        error_msg = f"Error taking screenshot: {str(e)}"
        
        # Add error log
        manual_test_logs.insert(0, {
            'timestamp': datetime.now().isoformat(),
            'component': 'System',
            'action': 'Take screenshot',
            'result': error_msg,
            'status': 'error'
        })
        
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500
