#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Utility functions for the application
"""

import os
import socket
from src.config.languages import _


def load_stylesheet(app):
    """Apply modern light theme style"""
    try:
        # Import light theme from styles module
        from src.ui.styles.light_theme import get_light_theme_stylesheet
        
        # Apply light theme stylesheet
        app.setStyleSheet(get_light_theme_stylesheet())
        print("Light theme loaded successfully")
        
    except Exception as e:
        print(f"Light theme load error: {e}")
        # Fallback to basic light theme
        app.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
                color: #1a1a1a;
            }
            QWidget {
                background-color: #ffffff;
                color: #1a1a1a;
            }
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #0051D5;
            }
            QTableWidget {
                background-color: #ffffff;
                color: #1a1a1a;
                border: 1px solid #e0e0e0;
            }
        """)
        print("Fallback light theme loaded")


def is_port_open(host, port):
    """Check if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False


def get_os_info():
    """Get operating system information for API headers"""
    # Use the modular proxy manager approach
    import sys
    from src.proxy.proxy_windows import WindowsProxyManager
    from src.proxy.proxy_macos import MacOSProxyManager
    from src.proxy.proxy_linux import LinuxProxyManager
    
    if sys.platform == "win32":
        return WindowsProxyManager.get_os_info()
    elif sys.platform == "darwin":
        return MacOSProxyManager.get_os_info()
    else:
        return LinuxProxyManager.get_os_info()


def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    return f"{size_bytes:.1f}{size_names[i]}"


def validate_email(email):
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def safe_json_loads(json_string):
    """Safely load JSON string with error handling"""
    import json
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError) as e:
        print(f"JSON decode error: {e}")
        return None


def truncate_string(text, max_length=50):
    """Truncate string to maximum length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def get_unique_filename(base_path, extension=""):
    """Get unique filename by appending counter if file exists"""
    if not extension.startswith('.') and extension:
        extension = '.' + extension
    
    counter = 1
    original_path = base_path + extension
    new_path = original_path
    
    while os.path.exists(new_path):
        name_part = base_path
        new_path = f"{name_part}_{counter}{extension}"
        counter += 1
    
    return new_path


def ensure_directory_exists(directory_path):
    """Ensure directory exists, create if it doesn't"""
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception as e:
        print(f"Failed to create directory {directory_path}: {e}")
        return False


def is_valid_json_structure(data, required_fields=None):
    """Validate JSON structure against required fields"""
    if not isinstance(data, dict):
        return False
    
    if required_fields:
        for field in required_fields:
            if field not in data:
                return False
    
    return True


def format_timestamp(timestamp_ms):
    """Format timestamp in milliseconds to readable date"""
    try:
        import datetime
        timestamp_s = int(timestamp_ms) / 1000
        dt = datetime.datetime.fromtimestamp(timestamp_s)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return "Invalid date"


def get_app_version():
    """Get application version"""
    try:
        # Try to read from version file or package info
        version_file = os.path.join(os.path.dirname(__file__), "VERSION")
        if os.path.exists(version_file):
            with open(version_file, 'r') as f:
                return f.read().strip()
        else:
            return "1.0.0"  # Default version
    except:
        return "1.0.0"


def cleanup_temp_files(temp_dir, max_age_hours=24):
    """Clean up temporary files older than specified age"""
    try:
        import time
        import glob
        
        if not os.path.exists(temp_dir):
            return
        
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for file_path in glob.glob(os.path.join(temp_dir, "*")):
            try:
                file_age = current_time - os.path.getmtime(file_path)
                if file_age > max_age_seconds:
                    os.remove(file_path)
                    print(f"Cleaned up temp file: {file_path}")
            except Exception as e:
                print(f"Failed to clean up {file_path}: {e}")
                
    except Exception as e:
        print(f"Temp file cleanup error: {e}")


def check_internet_connectivity(host="8.8.8.8", port=53, timeout=3):
    """Check if internet connectivity is available"""
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False


def get_system_info():
    """Get basic system information"""
    import platform
    import sys
    
    return {
        'platform': platform.platform(),
        'python_version': sys.version,
        'architecture': platform.architecture()[0],
        'processor': platform.processor(),
        'hostname': platform.node()
    }