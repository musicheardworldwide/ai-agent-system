"""
Build script for creating a production-ready frontend bundle
"""
import os
import subprocess
import shutil
import json
import sys
from datetime import datetime

# Set up paths
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(ROOT_DIR, 'frontend')
BUILD_DIR = os.path.join(FRONTEND_DIR, 'build')
SRC_DIR = os.path.join(FRONTEND_DIR, 'src')
PUBLIC_DIR = os.path.join(FRONTEND_DIR, 'public')

def log(message):
    """Log a message with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def ensure_directory(directory):
    """Ensure a directory exists, create if it doesn't"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        log(f"Created directory: {directory}")

def copy_file(src, dst):
    """Copy a file from src to dst"""
    shutil.copy2(src, dst)
    log(f"Copied: {src} -> {dst}")

def build_frontend():
    """Build the frontend application"""
    log("Starting frontend build process...")
    
    # Ensure build directory exists and is empty
    ensure_directory(BUILD_DIR)
    for item in os.listdir(BUILD_DIR):
        item_path = os.path.join(BUILD_DIR, item)
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)
        else:
            os.remove(item_path)
    log("Cleaned build directory")
    
    # Create package.json if it doesn't exist
    package_json_path = os.path.join(FRONTEND_DIR, 'package.json')
    if not os.path.exists(package_json_path):
        log("Creating package.json...")
        package_json = {
            "name": "ai-agent-system-frontend",
            "version": "1.0.0",
            "private": true,
            "dependencies": {
                "@emotion/react": "^11.10.6",
                "@emotion/styled": "^11.10.6",
                "@mui/icons-material": "^5.11.16",
                "@mui/material": "^5.12.0",
                "axios": "^1.3.5",
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-router-dom": "^6.10.0",
                "react-scripts": "5.0.1",
                "react-syntax-highlighter": "^15.5.0"
            },
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build",
                "test": "react-scripts test",
                "eject": "react-scripts eject"
            },
            "eslintConfig": {
                "extends": [
                    "react-app"
                ]
            },
            "browserslist": {
                "production": [
                    ">0.2%",
                    "not dead",
                    "not op_mini all"
                ],
                "development": [
                    "last 1 chrome version",
                    "last 1 firefox version",
                    "last 1 safari version"
                ]
            }
        }
        with open(package_json_path, 'w') as f:
            json.dump(package_json, f, indent=2)
    
    # Create public directory if it doesn't exist
    ensure_directory(PUBLIC_DIR)
    
    # Create index.html in public directory
    index_html_path = os.path.join(PUBLIC_DIR, 'index.html')
    if not os.path.exists(index_html_path):
        log("Creating index.html...")
        with open(index_html_path, 'w') as f:
            f.write("""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta
      name="description"
      content="AI Agent System with Open Interpreter"
    />
    <link rel="apple-touch-icon" href="%PUBLIC_URL%/logo192.png" />
    <link rel="manifest" href="%PUBLIC_URL%/manifest.json" />
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap" />
    <title>AI Agent System</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>""")
    
    # Create manifest.json in public directory
    manifest_path = os.path.join(PUBLIC_DIR, 'manifest.json')
    if not os.path.exists(manifest_path):
        log("Creating manifest.json...")
        with open(manifest_path, 'w') as f:
            f.write("""{
  "short_name": "AI Agent",
  "name": "AI Agent System",
  "icons": [
    {
      "src": "favicon.ico",
      "sizes": "64x64 32x32 24x24 16x16",
      "type": "image/x-icon"
    },
    {
      "src": "logo192.png",
      "type": "image/png",
      "sizes": "192x192"
    },
    {
      "src": "logo512.png",
      "type": "image/png",
      "sizes": "512x512"
    }
  ],
  "start_url": ".",
  "display": "standalone",
  "theme_color": "#000000",
  "background_color": "#ffffff"
}""")
    
    # Create robots.txt in public directory
    robots_path = os.path.join(PUBLIC_DIR, 'robots.txt')
    if not os.path.exists(robots_path):
        log("Creating robots.txt...")
        with open(robots_path, 'w') as f:
            f.write("""# https://www.robotstxt.org/robotstxt.html
User-agent: *
Disallow:""")
    
    # Create index.js in src directory
    ensure_directory(SRC_DIR)
    index_js_path = os.path.join(SRC_DIR, 'index.js')
    if not os.path.exists(index_js_path):
        log("Creating index.js...")
        with open(index_js_path, 'w') as f:
            f.write("""import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);""")
    
    # Create index.css in src directory
    index_css_path = os.path.join(SRC_DIR, 'index.css')
    if not os.path.exists(index_css_path):
        log("Creating index.css...")
        with open(index_css_path, 'w') as f:
            f.write("""body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}""")
    
    # Create proxy configuration for development
    proxy_config_path = os.path.join(FRONTEND_DIR, 'package.json')
    with open(proxy_config_path, 'r') as f:
        package_data = json.load(f)
    
    if 'proxy' not in package_data:
        package_data['proxy'] = 'http://localhost:5000'
        with open(proxy_config_path, 'w') as f:
            json.dump(package_data, f, indent=2)
        log("Added proxy configuration to package.json")
    
    # Create .env file for production build
    env_path = os.path.join(FRONTEND_DIR, '.env')
    with open(env_path, 'w') as f:
        f.write("""REACT_APP_API_URL=
REACT_APP_VERSION=1.0.0
GENERATE_SOURCEMAP=false""")
    log("Created .env file for production build")
    
    # Create .env.production file
    env_prod_path = os.path.join(FRONTEND_DIR, '.env.production')
    with open(env_prod_path, 'w') as f:
        f.write("""REACT_APP_API_URL=https://api.lastwinnersllc.com
REACT_APP_VERSION=1.0.0
GENERATE_SOURCEMAP=false""")
    log("Created .env.production file")
    
    # Try to install dependencies and build
    try:
        log("Installing dependencies...")
        subprocess.run(['npm', 'install'], cwd=FRONTEND_DIR, check=True)
        
        log("Building production bundle...")
        subprocess.run(['npm', 'run', 'build'], cwd=FRONTEND_DIR, check=True)
        
        log("Frontend build completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        log(f"Error during build process: {e}")
        
        # If npm build fails, create a simple static version
        log("Creating static version as fallback...")
        create_static_version()
        return False

def create_static_version():
    """Create a static version of the frontend as fallback"""
    log("Creating static version of the frontend...")
    
    # Ensure build directory exists
    ensure_directory(BUILD_DIR)
    
    # Create index.html
    index_html_path = os.path.join(BUILD_DIR, 'index.html')
    with open(index_html_path, 'w') as f:
        f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Agent System</title>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap" />
    <link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons" />
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="app">
        <header class="app-header">
            <div class="toolbar">
                <button class="menu-button">
                    <span class="material-icons">menu</span>
                </button>
                <h1>AI Agent System</h1>
            </div>
        </header>
        
        <div class="app-container">
            <nav class="app-drawer">
                <div class="drawer-header">
                    <h2>AI Agent System</h2>
                    <button class="close-button">
                        <span class="material-icons">chevron_left</span>
                    </button>
                </div>
                <div class="drawer-divider"></div>
                <ul class="drawer-menu">
                    <li class="menu-item active">
                        <span class="material-icons">dashboard</span>
                        <span>Dashboard</span>
                    </li>
                    <li class="menu-item">
                        <span class="material-icons">chat</span>
                        <span>Chat</span>
                    </li>
                    <li class="menu-item">
                        <span class="material-icons">storage</span>
                        <span>Database Agent</span>
                    </li>
                    <li class="menu-item">
                        <span class="material-icons">memory</span>
                        <span>RAG Memory</span>
                    </li>
                    <li class="menu-item">
                        <span class="material-icons">build</span>
                        <span>Custom Tools</span>
                    </li>
                    <li class="menu-item">
                        <span class="material-icons">code</span>
                        <span>DevChat</span>
                    </li>
                    <li class="menu-item">
                        <span class="material-icons">cloud_upload</span>
                        <span>Deploy Website</span>
                    </li>
                    <li class="menu-item">
                        <span class="material-icons">settings</span>
                        <span>Settings</span>
                    </li>
                </ul>
            </nav>
            
            <main class="app-content">
                <div class="dashboard">
                    <h2>Welcome to the AI Agent System</h2>
                    <p>This is a sophisticated AI system with the following features:</p>
                    <div class="feature-cards">
                        <div class="card">
                            <div class="card-icon">
                                <span class="material-icons">chat</span>
                            </div>
                            <div class="card-content">
                                <h3>Open Interpreter</h3>
                                <p>Interact with the system through a natural language chat interface</p>
                            </div>
                        </div>
                        <div class="card">
                            <div class="card-icon">
                                <span class="material-icons">memory</span>
                            </div>
                            <div class="card-content">
                                <h3>Smart Memory</h3>
                                <p>RAG-based memory system for contextual understanding</p>
                            </div>
                        </div>
                        <div class="card">
                            <div class="card-icon">
                                <span class="material-icons">storage</span>
                            </div>
                            <div class="card-content">
                                <h3>Database Agent</h3>
                                <p>Intelligent database that organizes and retrieves knowledge</p>
                            </div>
                        </div>
                        <div class="card">
                            <div class="card-icon">
                                <span class="material-icons">build</span>
                            </div>
                            <div class="card-content">
                                <h3>Custom Tools</h3>
                                <p>Extensible tool system with real-time context awareness</p>
                            </div>
                        </div>
                        <div class="card">
                            <div class="card-icon">
                                <span class="material-icons">code</span>
                            </div>
                            <div class="card-content">
                                <h3>DevChat Interpreter</h3>
                                <p>Code-aware interpreter for development assistance</p>
                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    </div>
    
    <script src="script.js"></script>
</body>
</html>""")
    
    # Create styles.css
    styles_css_path = os.path.join(BUILD_DIR, 'styles.css')
    with open(styles_css_path, 'w') as f:
        f.write("""* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: 'Roboto', sans-serif;
    background-color: #121212;
    color: #fff;
}

.app {
    display: flex;
    flex-direction: column;
    height: 100vh;
}

.app-header {
    background-color: #1e1e1e;
    color: white;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    z-index: 10;
}

.toolbar {
    display: flex;
    align-items: center;
    padding: 0 16px;
    height: 64px;
}

.menu-button {
    background: none;
    border: none;
    color: white;
    margin-right: 16px;
    cursor: pointer;
}

.app-container {
    display: flex;
    flex: 1;
    overflow: hidden;
}

.app-drawer {
    width: 240px;
    background-color: #1e1e1e;
    color: white;
    overflow-y: auto;
}

.drawer-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px;
    height: 64px;
}

.close-button {
    background: none;
    border: none;
    color: white;
    cursor: pointer;
}

.drawer-divider {
    height: 1px;
    background-color: rgba(255, 255, 255, 0.12);
}

.drawer-menu {
    list-style: none;
    padding: 8px 0;
}

.menu-item {
    display: flex;
    align-items: center;
    padding: 8px 16px;
    cursor: pointer;
}

.menu-item:hover {
    background-color: rgba(255, 255, 255, 0.08);
}

.menu-item.active {
    background-color: rgba(63, 81, 181, 0.16);
}

.menu-item .material-icons {
    margin-right: 16px;
}

.app-content {
    flex: 1;
    padding: 24px;
    overflow-y: auto;
    background-color: #121212;
}

.dashboard h2 {
    margin-bottom: 16px;
    color: #fff;
}

.dashboard p {
    margin-bottom: 24px;
    color: rgba(255, 255, 255, 0.7);
}

.feature-cards {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 24px;
}

.card {
    background-color: #1e1e1e;
    border-radius: 4px;
    padding: 16px;
    display: flex;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.card-icon {
    margin-right: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background-color: rgba(63, 81, 181, 0.16);
    color: #3f51b5;
}

.card-content h3 {
    margin-bottom: 8px;
    color: #fff;
}

.card-content p {
    color: rgba(255, 255, 255, 0.7);
    margin: 0;
}

@media (max-width: 600px) {
    .app-drawer {
        position: fixed;
        top: 0;
        left: 0;
        height: 100%;
        transform: translateX(-100%);
        transition: transform 0.3s ease;
        z-index: 20;
    }
    
    .app-drawer.open {
        transform: translateX(0);
    }
    
    .feature-cards {
        grid-template-columns: 1fr;
    }
}""")
    
    # Create script.js
    script_js_path = os.path.join(BUILD_DIR, 'script.js')
    with open(script_js_path, 'w') as f:
        f.write("""document.addEventListener('DOMContentLoaded', function() {
    const menuButton = document.querySelector('.menu-button');
    const closeButton = document.querySelector('.close-button');
    const drawer = document.querySelector('.app-drawer');
    const menuItems = document.querySelectorAll('.menu-item');
    
    menuButton.addEventListener('click', function() {
        drawer.classList.toggle('open');
    });
    
    closeButton.addEventListener('click', function() {
        drawer.classList.remove('open');
    });
    
    menuItems.forEach(item => {
        item.addEventListener('click', function() {
            menuItems.forEach(i => i.classList.remove('active'));
            this.classList.add('active');
            
            if (window.innerWidth <= 600) {
                drawer.classList.remove('open');
            }
        });
    });
});""")
    
    log("Static version created successfully!")

if __name__ == "__main__":
    build_frontend()
