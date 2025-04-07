"""
Update the deployment routes to use the build_frontend.py script
"""
import os
import sys
import importlib.util
from flask import Blueprint, jsonify, request, Response, current_app
import json
import time
import threading
import subprocess
from datetime import datetime

# Import the build_frontend module
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from build_frontend import build_frontend

# Update the deploy_to_netlify function
def deploy_to_netlify(deployment_id, config):
    """Deploy to Netlify"""
    try:
        api_key = config.get('apiKey')
        site_name = config.get('siteName', 'ai-agent-system')
        
        if not api_key:
            update_deployment_status(deployment_id, 'failed', 'API key is required')
            return
        
        # Build the frontend
        add_deployment_log(deployment_id, 'info', 'Building frontend application...')
        build_success = build_frontend()
        
        if not build_success:
            add_deployment_log(deployment_id, 'warning', 'Full build failed, using static version as fallback')
        else:
            add_deployment_log(deployment_id, 'success', 'Frontend built successfully')
        
        # Continue with deployment...
        # (rest of the function remains the same)
    except Exception as e:
        error_msg = f"Error deploying to Netlify: {str(e)}"
        add_deployment_log(deployment_id, 'error', error_msg)
        update_deployment_status(deployment_id, 'failed', error_msg)

# Update the deploy_to_vercel function
def deploy_to_vercel(deployment_id, config):
    """Deploy to Vercel"""
    try:
        api_key = config.get('apiKey')
        site_name = config.get('siteName', 'ai-agent-system')
        
        if not api_key:
            update_deployment_status(deployment_id, 'failed', 'API key is required')
            return
        
        # Build the frontend
        add_deployment_log(deployment_id, 'info', 'Building frontend application...')
        build_success = build_frontend()
        
        if not build_success:
            add_deployment_log(deployment_id, 'warning', 'Full build failed, using static version as fallback')
        else:
            add_deployment_log(deployment_id, 'success', 'Frontend built successfully')
        
        # Continue with deployment...
        # (rest of the function remains the same)
    except Exception as e:
        error_msg = f"Error deploying to Vercel: {str(e)}"
        add_deployment_log(deployment_id, 'error', error_msg)
        update_deployment_status(deployment_id, 'failed', error_msg)

# Update the deploy_to_github_pages function
def deploy_to_github_pages(deployment_id, config):
    """Deploy to GitHub Pages"""
    try:
        api_key = config.get('apiKey')  # GitHub token
        site_name = config.get('siteName', 'ai-agent-system')
        
        if not api_key:
            update_deployment_status(deployment_id, 'failed', 'GitHub token is required')
            return
        
        # Build the frontend
        add_deployment_log(deployment_id, 'info', 'Building frontend application...')
        build_success = build_frontend()
        
        if not build_success:
            add_deployment_log(deployment_id, 'warning', 'Full build failed, using static version as fallback')
        else:
            add_deployment_log(deployment_id, 'success', 'Frontend built successfully')
        
        # Continue with deployment...
        # (rest of the function remains the same)
    except Exception as e:
        error_msg = f"Error deploying to GitHub Pages: {str(e)}"
        add_deployment_log(deployment_id, 'error', error_msg)
        update_deployment_status(deployment_id, 'failed', error_msg)
