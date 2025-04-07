"""
Deployment API routes for the AI Agent System
"""
from flask import Blueprint, jsonify, request, Response, current_app
import json
import os
import time
import uuid
import threading
import queue
from datetime import datetime
import traceback
import subprocess
import requests

# Create blueprint
deploy_api = Blueprint('deploy_api', __name__)

# Store deployment status
deployments = {}

# Queue for streaming logs
deployment_log_queues = {}

def init_deploy_routes(app):
    """Initialize deployment routes"""
    app.register_blueprint(deploy_api, url_prefix='/api/deploy')

def add_deployment_log(deployment_id, level, message):
    """Add a log entry for a deployment"""
    log_entry = {
        'type': 'log',
        'timestamp': datetime.now().isoformat(),
        'level': level,
        'message': message
    }
    
    if deployment_id in deployment_log_queues:
        deployment_log_queues[deployment_id].put(log_entry)
    
    return log_entry

def update_deployment_status(deployment_id, status, message=None, url=None):
    """Update deployment status"""
    status_update = {
        'type': 'status',
        'timestamp': datetime.now().isoformat(),
        'status': status,
        'message': message,
        'url': url
    }
    
    if deployment_id in deployments:
        deployments[deployment_id]['status'] = status
        deployments[deployment_id]['message'] = message
        deployments[deployment_id]['url'] = url
    
    if deployment_id in deployment_log_queues:
        deployment_log_queues[deployment_id].put(status_update)
    
    return status_update

def deploy_to_netlify(deployment_id, config):
    """Deploy to Netlify"""
    try:
        api_key = config.get('apiKey')
        site_name = config.get('siteName', 'ai-agent-system')
        
        if not api_key:
            update_deployment_status(deployment_id, 'failed', 'API key is required')
            return
        
        # Create build directory if it doesn't exist
        build_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'frontend/build')
        os.makedirs(build_dir, exist_ok=True)
        
        # Ensure we have an index.html file
        index_path = os.path.join(build_dir, 'index.html')
        if not os.path.exists(index_path):
            add_deployment_log(deployment_id, 'info', 'Creating index.html file...')
            with open(index_path, 'w') as f:
                f.write("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Agent System</title>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap" />
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background-color: #3f51b5;
            color: white;
            padding: 20px;
            text-align: center;
        }
        .content {
            background-color: white;
            padding: 20px;
            margin-top: 20px;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        }
        .footer {
            text-align: center;
            margin-top: 20px;
            padding: 20px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>AI Agent System</h1>
    </div>
    <div class="container">
        <div class="content">
            <h2>Welcome to the AI Agent System</h2>
            <p>This is a sophisticated AI system with the following features:</p>
            <ul>
                <li>Open-interpreter system with chat interface</li>
                <li>Smart memory system backed by RAG</li>
                <li>Database agent for knowledge management</li>
                <li>Custom tools and environment functions</li>
                <li>DevChat interpreter for code intelligence</li>
            </ul>
            <p>The system is currently being deployed. Please check back soon for the full interactive experience.</p>
        </div>
        <div class="footer">
            &copy; 2025 AI Agent System
        </div>
    </div>
</body>
</html>
                """)
        
        # Create netlify.toml file
        add_deployment_log(deployment_id, 'info', 'Creating netlify configuration...')
        netlify_config_path = os.path.join(build_dir, 'netlify.toml')
        with open(netlify_config_path, 'w') as f:
            f.write("""
[build]
  publish = "."
  command = "echo 'No build command'"

[[redirects]]
  from = "/api/*"
  to = "https://api.lastwinnersllc.com/:splat"
  status = 200
  force = true

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
            """)
        
        # Create a zip file of the build directory
        add_deployment_log(deployment_id, 'info', 'Creating deployment package...')
        zip_path = os.path.join(os.path.dirname(build_dir), 'deploy.zip')
        
        if os.path.exists(zip_path):
            os.remove(zip_path)
        
        # Create zip file
        import zipfile
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, dirs, files in os.walk(build_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, build_dir)
                    zipf.write(file_path, arcname)
        
        # Create a new site on Netlify if it doesn't exist
        add_deployment_log(deployment_id, 'info', f'Creating site {site_name} on Netlify...')
        
        # Check if site exists
        sites_response = requests.get(
            'https://api.netlify.com/api/v1/sites',
            headers={'Authorization': f'Bearer {api_key}'}
        )
        
        site_id = None
        if sites_response.status_code == 200:
            sites = sites_response.json()
            for site in sites:
                if site['name'] == site_name:
                    site_id = site['site_id']
                    add_deployment_log(deployment_id, 'info', f'Found existing site: {site_name}')
                    break
        
        # Create site if it doesn't exist
        if not site_id:
            create_site_response = requests.post(
                'https://api.netlify.com/api/v1/sites',
                json={'name': site_name},
                headers={'Authorization': f'Bearer {api_key}'}
            )
            
            if create_site_response.status_code != 201:
                update_deployment_status(
                    deployment_id, 
                    'failed', 
                    f'Failed to create site: {create_site_response.text}'
                )
                return
            
            site_data = create_site_response.json()
            site_id = site_data['site_id']
            add_deployment_log(deployment_id, 'info', f'Created new site: {site_name}')
        
        # Deploy the zip file
        add_deployment_log(deployment_id, 'info', 'Uploading deployment package to Netlify...')
        with open(zip_path, 'rb') as zip_file:
            deploy_response = requests.post(
                f'https://api.netlify.com/api/v1/sites/{site_id}/deploys',
                headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/zip'},
                data=zip_file
            )
        
        if deploy_response.status_code not in (200, 201):
            update_deployment_status(
                deployment_id, 
                'failed', 
                f'Failed to deploy: {deploy_response.text}'
            )
            return
        
        deploy_data = deploy_response.json()
        site_url = deploy_data.get('deploy_ssl_url') or deploy_data.get('deploy_url')
        
        # Wait for deployment to complete
        add_deployment_log(deployment_id, 'info', 'Waiting for deployment to complete...')
        
        # Poll for deployment status
        max_attempts = 30
        attempts = 0
        while attempts < max_attempts:
            status_response = requests.get(
                f'https://api.netlify.com/api/v1/sites/{site_id}/deploys/{deploy_data["id"]}',
                headers={'Authorization': f'Bearer {api_key}'}
            )
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                if status_data['state'] == 'ready':
                    add_deployment_log(deployment_id, 'info', 'Deployment completed successfully!')
                    update_deployment_status(
                        deployment_id, 
                        'success', 
                        'Deployment completed successfully',
                        site_url
                    )
                    return
                elif status_data['state'] == 'error':
                    update_deployment_status(
                        deployment_id, 
                        'failed', 
                        f'Deployment failed: {status_data.get("error_message", "Unknown error")}'
                    )
                    return
            
            attempts += 1
            time.sleep(2)
        
        # If we get here, deployment took too long
        update_deployment_status(
            deployment_id, 
            'failed', 
            'Deployment timed out'
        )
        
    except Exception as e:
        error_msg = f"Error deploying to Netlify: {str(e)}"
        add_deployment_log(deployment_id, 'error', error_msg)
        add_deployment_log(deployment_id, 'error', traceback.format_exc())
        update_deployment_status(deployment_id, 'failed', error_msg)

def deploy_to_vercel(deployment_id, config):
    """Deploy to Vercel"""
    try:
        api_key = config.get('apiKey')
        site_name = config.get('siteName', 'ai-agent-system')
        
        if not api_key:
            update_deployment_status(deployment_id, 'failed', 'API key is required')
            return
        
        # Create build directory if it doesn't exist
        build_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'frontend/build')
        os.makedirs(build_dir, exist_ok=True)
        
        # Ensure we have an index.html file
        index_path = os.path.join(build_dir, 'index.html')
        if not os.path.exists(index_path):
            add_deployment_log(deployment_id, 'info', 'Creating index.html file...')
            with open(index_path, 'w') as f:
                f.write("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Agent System</title>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap" />
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background-color: #3f51b5;
            color: white;
            padding: 20px;
            text-align: center;
        }
        .content {
            background-color: white;
            padding: 20px;
            margin-top: 20px;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        }
        .footer {
            text-align: center;
            margin-top: 20px;
            padding: 20px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>AI Agent System</h1>
    </div>
    <div class="container">
        <div class="content">
            <h2>Welcome to the AI Agent System</h2>
            <p>This is a sophisticated AI system with the following features:</p>
            <ul>
                <li>Open-interpreter system with chat interface</li>
                <li>Smart memory system backed by RAG</li>
                <li>Database agent for knowledge management</li>
                <li>Custom tools and environment functions</li>
                <li>DevChat interpreter for code intelligence</li>
            </ul>
            <p>The system is currently being deployed. Please check back soon for the full interactive experience.</p>
        </div>
        <div class="footer">
            &copy; 2025 AI Agent System
        </div>
    </div>
</body>
</html>
                """)
        
        # Create vercel.json file
        add_deployment_log(deployment_id, 'info', 'Creating Vercel configuration...')
        vercel_config_path = os.path.join(build_dir, 'vercel.json')
        with open(vercel_config_path, 'w') as f:
            f.write("""
{
  "version": 2,
  "builds": [
    { "src": "**/*", "use": "@vercel/static" }
  ],
  "routes": [
    { "src": "/api/(.*)", "dest": "https://api.lastwinnersllc.com/$1" },
    { "src": "/(.*)", "dest": "/index.html" }
  ]
}
            """)
        
        # Install Vercel CLI if not already installed
        try:
            subprocess.run(['vercel', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except (subprocess.SubprocessError, FileNotFoundError):
            add_deployment_log(deployment_id, 'info', 'Installing Vercel CLI...')
            subprocess.run(['npm', 'install', '-g', 'vercel'], check=True)
        
        # Create .vercel directory if it doesn't exist
        vercel_dir = os.path.join(os.path.expanduser('~'), '.vercel')
        os.makedirs(vercel_dir, exist_ok=True)
        
        # Create Vercel config file
        add_deployment_log(deployment_id, 'info', 'Setting up Vercel authentication...')
        vercel_global_config = {
            "token": api_key
        }
        
        with open(os.path.join(vercel_dir, 'config.json'), 'w') as f:
            json.dump(vercel_global_config, f)
        
        # Deploy to Vercel
        add_deployment_log(deployment_id, 'info', 'Deploying to Vercel...')
        
        # Change to build directory
        os.chdir(build_dir)
        
        # Run Vercel deploy command
        deploy_process = subprocess.Popen(
            ['vercel', '--name', site_name, '--prod', '--confirm', '--token', api_key],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Process output
        site_url = None
        for line in deploy_process.stdout:
            line = line.strip()
            add_deployment_log(deployment_id, 'info', line)
            
            # Look for deployment URL
            if 'https://' in line and '.vercel.app' in line:
                site_url = line
        
        # Wait for process to complete
        deploy_process.wait()
        
        # Check if deployment was successful
        if deploy_process.returncode != 0:
            error_output = deploy_process.stderr.read()
            update_deployment_status(
                deployment_id, 
                'failed', 
                f'Deployment failed: {error_output}'
            )
            return
        
        if site_url:
            add_deployment_log(deployment_id, 'info', f'Deployment completed successfully! URL: {site_url}')
            update_deployment_status(
                deployment_id, 
                'success', 
                'Deployment completed successfully',
                site_url
            )
        else:
            update_deployment_status(
                deployment_id, 
                'failed', 
                'Deployment completed but URL not found'
            )
        
    except Exception as e:
        error_msg = f"Error deploying to Vercel: {str(e)}"
        add_deployment_log(deployment_id, 'error', error_msg)
        add_deployment_log(deployment_id, 'error', traceback.format_exc())
        update_deployment_status(deployment_id, 'failed', error_msg)

def deploy_to_github_pages(deployment_id, config):
    """Deploy to GitHub Pages"""
    try:
        api_key = config.get('apiKey')  # GitHub token
        site_name = config.get('siteName', 'ai-agent-system')
        
        if not api_key:
            update_deployment_status(deployment_id, 'failed', 'GitHub token is required')
            return
        
        # Create build directory if it doesn't exist
        build_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'frontend/build')
        os.makedirs(build_dir, exist_ok=True)
        
        # Ensure we have an index.html file
        index_path = os.path.join(build_dir, 'index.html')
        if not os.path.exists(index_path):
            add_deployment_log(deployment_id, 'info', 'Creating index.html file...')
            with open(index_path, 'w') as f:
                f.write("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Agent System</title>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap" />
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background-color: #3f51b5;
            color: white;
            padding: 20px;
            text-align: center;
        }
        .content {
            background-color: white;
            padding: 20px;
            margin-top: 20px;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        }
        .footer {
            text-align: center;
            margin-top: 20px;
            padding: 20px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>AI Agent System</h1>
    </div>
    <div class="container">
        <div class="content">
            <h2>Welcome to the AI Agent System</h2>
            <p>This is a sophisticated AI system with the following features:</p>
            <ul>
                <li>Open-interpreter system with chat interface</li>
                <li>Smart memory system backed by RAG</li>
                <li>Database agent for knowledge management</li>
                <li>Custom tools and environment functions</li>
                <li>DevChat interpreter for code intelligence</li>
            </ul>
            <p>The system is currently being deployed. Please check back soon for the full interactive experience.</p>
        </div>
        <div class="footer">
            &copy; 2025 AI Agent System
        </div>
    </div>
</body>
</html>
                """)
        
        # Create a temporary directory for the git repository
        import tempfile
        repo_dir = tempfile.mkdtemp()
        
        add_deployment_log(deployment_id, 'info', f'Setting up Git repository in {repo_dir}...')
        
        # Initialize git repository
        os.chdir(repo_dir)
        subprocess.run(['git', 'init'], check=True)
        
        # Configure git
        subprocess.run(['git', 'config', 'user.name', 'AI Agent System'], check=True)
        subprocess.run(['git', 'config', 'user.email', 'ai-agent@example.com'], check=True)
        
        # Copy build files to repository
        add_deployment_log(deployment_id, 'info', 'Copying build files to repository...')
        import shutil
        for item in os.listdir(build_dir):
            src = os.path.join(build_dir, item)
            dst = os.path.join(repo_dir, item)
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
        
        # Create .nojekyll file to disable Jekyll processing
        with open(os.path.join(repo_dir, '.nojekyll'), 'w') as f:
            f.write('')
        
        # Add all files to git
        add_deployment_log(deployment_id, 'info', 'Adding files to Git...')
        subprocess.run(['git', 'add', '.'], check=True)
        
        # Commit changes
        add_deployment_log(deployment_id, 'info', 'Committing changes...')
        subprocess.run(['git', 'commit', '-m', 'Deploy AI Agent System'], check=True)
        
        # Create GitHub repository if it doesn't exist
        add_deployment_log(deployment_id, 'info', f'Creating GitHub repository: {site_name}...')
        
        # Check if repository exists
        repo_check = requests.get(
            f'https://api.github.com/repos/ai-agent-system/{site_name}',
            headers={'Authorization': f'token {api_key}'}
        )
        
        if repo_check.status_code != 200:
            # Create repository
            create_repo_response = requests.post(
                'https://api.github.com/user/repos',
                json={
                    'name': site_name,
                    'description': 'AI Agent System',
                    'private': False,
                    'has_issues': False,
                    'has_projects': False,
                    'has_wiki': False
                },
                headers={'Authorization': f'token {api_key}'}
            )
            
            if create_repo_response.status_code not in (201, 200):
                update_deployment_status(
                    deployment_id, 
                    'failed', 
                    f'Failed to create GitHub repository: {create_repo_response.text}'
                )
                return
            
            add_deployment_log(deployment_id, 'info', 'GitHub repository created successfully')
        else:
            add_deployment_log(deployment_id, 'info', 'GitHub repository already exists')
        
        # Add GitHub remote
        add_deployment_log(deployment_id, 'info', 'Adding GitHub remote...')
        subprocess.run(['git', 'remote', 'add', 'origin', f'https://{api_key}@github.com/ai-agent-system/{site_name}.git'], check=True)
        
        # Push to GitHub
        add_deployment_log(deployment_id, 'info', 'Pushing to GitHub...')
        subprocess.run(['git', 'push', '-f', 'origin', 'master:gh-pages'], check=True)
        
        # Enable GitHub Pages
        add_deployment_log(deployment_id, 'info', 'Enabling GitHub Pages...')
        enable_pages_response = requests.post(
            f'https://api.github.com/repos/ai-agent-system/{site_name}/pages',
            json={'source': {'branch': 'gh-pages', 'path': '/'}},
            headers={'Authorization': f'token {api_key}', 'Accept': 'application/vnd.github.switcheroo-preview+json'}
        )
        
        # Get GitHub Pages URL
        pages_response = requests.get(
            f'https://api.github.com/repos/ai-agent-system/{site_name}/pages',
            headers={'Authorization': f'token {api_key}'}
        )
        
        site_url = None
        if pages_response.status_code == 200:
            pages_data = pages_response.json()
            site_url = pages_data.get('html_url')
        
        if site_url:
            add_deployment_log(deployment_id, 'info', f'Deployment completed successfully! URL: {site_url}')
            update_deployment_status(
                deployment_id, 
                'success', 
                'Deployment completed successfully',
                site_url
            )
        else:
            site_url = f'https://ai-agent-system.github.io/{site_name}/'
            add_deployment_log(deployment_id, 'info', f'Deployment completed! URL (estimated): {site_url}')
            update_deployment_status(
                deployment_id, 
                'success', 
                'Deployment completed (URL may take a few minutes to be available)',
                site_url
            )
        
    except Exception as e:
        error_msg = f"Error deploying to GitHub Pages: {str(e)}"
        add_deployment_log(deployment_id, 'error', error_msg)
        add_deployment_log(deployment_id, 'error', traceback.format_exc())
        update_deployment_status(deployment_id, 'failed', error_msg)

@deploy_api.route('/website', methods=['POST'])
def deploy_website():
    """Deploy the website"""
    config = request.json
    
    # Generate deployment ID
    deployment_id = str(uuid.uuid4())
    
    # Initialize deployment status
    deployments[deployment_id] = {
        'id': deployment_id,
        'status': 'pending',
        'config': config,
        'timestamp': datetime.now().isoformat()
    }
    
    # Initialize log queue
    deployment_log_queues[deployment_id] = queue.Queue()
    
    # Add initial log
    add_deployment_log(deployment_id, 'info', 'Deployment initialized')
    
    # Determine deployment type
    deployment_type = config.get('deploymentType', 'static')
    
    # Start deployment in a separate thread
    if deployment_type == 'netlify':
        thread = threading.Thread(target=deploy_to_netlify, args=(deployment_id, config))
    elif deployment_type == 'vercel':
        thread = threading.Thread(target=deploy_to_vercel, args=(deployment_id, config))
    elif deployment_type == 'github':
        thread = threading.Thread(target=deploy_to_github_pages, args=(deployment_id, config))
    else:
        # Default to Netlify
        thread = threading.Thread(target=deploy_to_netlify, args=(deployment_id, config))
    
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'deploymentId': deployment_id,
        'status': 'pending'
    })

@deploy_api.route('/status/<deployment_id>')
def get_deployment_status(deployment_id):
    """Get the status of a deployment"""
    if deployment_id not in deployments:
        return jsonify({'error': 'Deployment not found'}), 404
    
    return jsonify(deployments[deployment_id])

@deploy_api.route('/logs/<deployment_id>')
def stream_deployment_logs(deployment_id):
    """Stream logs for a deployment"""
    if deployment_id not in deployment_log_queues:
        return jsonify({'error': 'Deployment not found'}), 404
    
    def generate():
        while True:
            try:
                # Get log from queue with timeout
                log = deployment_log_queues[deployment_id].get(timeout=1)
                yield f"data: {json.dumps(log)}\n\n"
                
                # If deployment is complete, send a final message and break
                if log.get('type') == 'status' and log.get('status') in ('success', 'failed'):
                    yield f"data: {json.dumps({'type': 'complete'})}\n\n"
                    break
            except queue.Empty:
                # Send a heartbeat to keep the connection alive
                yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
                
                # Check if deployment is still active
                if deployment_id not in deployments or deployments[deployment_id]['status'] in ('success', 'failed'):
                    break
    
    return Response(generate(), mimetype='text/event-stream')
