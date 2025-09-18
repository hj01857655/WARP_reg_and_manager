#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mitmproxy script for intercepting and modifying Warp API requests
"""

import json
import sqlite3
import time
import urllib3
import re
import random
import string
import logging
import os
from datetime import datetime
from mitmproxy import http
from mitmproxy.script import concurrent

# Try to import languages module - use fallback if not available
try:
    from src.config.languages import get_language_manager, _
except ImportError:
    try:
        # Fallback for when running from project root
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
        from src.config.languages import get_language_manager, _
    except ImportError:
        # Final fallback if languages module is not available
        def get_language_manager():
            return None
        def _(key):
            return key

# Configure logging for warp responses
def setup_warp_logging():
    """Setup logging for warp.dev responses"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, f"warp_responses_{datetime.now().strftime('%Y%m%d')}.log")
    
    # Create logger
    warp_logger = logging.getLogger('warp_responses')
    warp_logger.setLevel(logging.INFO)
    # 重要：防止日志消息传播到根logger，避免控制台输出
    warp_logger.propagate = False
    
    # Remove existing handlers to avoid duplicates
    for handler in warp_logger.handlers[:]:
        warp_logger.removeHandler(handler)
    
    # Create file handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)
    
    # Add handler to logger
    warp_logger.addHandler(file_handler)
    
    return warp_logger

# Initialize logger
warp_logger = setup_warp_logging()

def log_to_file(message):
    """Log message to warp responses file only"""
    warp_logger.info(message)

# Hide SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# SSL verification bypass - complete SSL verification disable
import ssl
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError:
    # Older Python versions
    pass


def randomize_uuid_string(uuid_str):
    """
    Randomly modify UUID string - letters replaced with hex symbols, digits with random numbers
    Hyphen (-) characters are preserved, upper/lower case format is preserved

    Args:
        uuid_str (str): UUID format string (e.g.: 4d22323e-1ce9-44c1-a922-112a718ea3fc)

    Returns:
        str: Randomly modified UUID string
    """
    if not uuid_str or len(uuid_str) == 0:
        # If empty, generate new UUID
        return generate_experiment_id()
        
    hex_digits_lower = '0123456789abcdef'
    hex_digits_upper = '0123456789ABCDEF'

    result = []
    for char in uuid_str:
        if char == '-':
            # Preserve hyphen character
            result.append(char)
        elif char.isdigit():
            # Replace digit with random hex character (digit or a-f)
            result.append(random.choice(hex_digits_lower))
        elif char in 'abcdef':
            # Replace lowercase hex letter with random lowercase hex letter
            result.append(random.choice(hex_digits_lower))
        elif char in 'ABCDEF':
            # Replace uppercase hex letter with random uppercase hex letter
            result.append(random.choice(hex_digits_upper))
        else:
            # Leave other characters as is (for safety)
            result.append(char)

    return ''.join(result)


def generate_experiment_id():
    """Generate UUID in Warp Experiment ID format - different each time"""
    # In format 931df166-756c-4d4c-b486-4231224bc531
    # Structure 8-4-4-4-12 hex characters
    def hex_chunk(length):
        return ''.join(random.choice('0123456789abcdef') for _ in range(length))

    return f"{hex_chunk(8)}-{hex_chunk(4)}-{hex_chunk(4)}-{hex_chunk(4)}-{hex_chunk(12)}"

class WarpProxyHandler:
    def __init__(self):
        self.db_path = "accounts.db"
        self.active_token = None
        self.active_email = None
        self.token_expiry = None
        self.last_trigger_check = 0
        self.last_token_check = 0
        self.user_settings_cache = None

    def get_active_account(self):
        """Get active account from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # First get active account
            cursor.execute('SELECT value FROM proxy_settings WHERE key = ?', ('active_account',))
            active_result = cursor.fetchone()

            if active_result:
                active_email = active_result[0]
                # Then get account data
                cursor.execute('SELECT account_data FROM accounts WHERE email = ?', (active_email,))
                account_result = cursor.fetchone()

                if account_result:
                    account_data = json.loads(account_result[0])
                    conn.close()
                    return active_email, account_data

            conn.close()
            return None, None
        except Exception as e:
            print(f"Error getting active account: {e}")
            return None, None

    def update_active_token(self):
        """Update active account token information"""
        try:
            print("🔍 Checking active account...")
            email, account_data = self.get_active_account()
            if not account_data:
                print("❌ No active account found")
                self.active_token = None
                self.active_email = None
                return False

            old_email = self.active_email

            current_time = int(time.time() * 1000)
            token_expiry = account_data['stsTokenManager']['expirationTime']
            # Convert to int if it's a string
            if isinstance(token_expiry, str):
                token_expiry = int(token_expiry)

            # If less than 1 minute left until token expires, refresh
            if current_time >= (token_expiry - 60000):  # 1 minute = 60000ms
                print(f"Refreshing token: {email}")
                if self.refresh_token(email, account_data):
                    # Get updated data
                    email, account_data = self.get_active_account()
                    if account_data:
                        self.active_token = account_data['stsTokenManager']['accessToken']
                        self.token_expiry = account_data['stsTokenManager']['expirationTime']
                        self.active_email = email
                        print(f"Token refreshed: {email}")
                        return True
                return False
            else:
                self.active_token = account_data['stsTokenManager']['accessToken']
                self.token_expiry = token_expiry
                self.active_email = email

                if old_email != email:
                    print(f"🔄 Active account changed: {old_email} → {email}")
                else:
                    print(f"✅ Token active: {email}")
                return True
        except Exception as e:
            print(f"Token update error: {e}")
            return False

    def check_account_change_trigger(self):
        """Check account change trigger file"""
        try:
            trigger_file = "account_change_trigger.tmp"
            import os

            if os.path.exists(trigger_file):
                # Check file modification time
                mtime = os.path.getmtime(trigger_file)
                if mtime > self.last_trigger_check:
                    print("🔄 Account change trigger detected!")
                    self.last_trigger_check = mtime

                    # Delete trigger file
                    try:
                        os.remove(trigger_file)
                        print("🗑️  Trigger file deleted")
                    except Exception as e:
                        print(f"Error deleting trigger file: {e}")

                    # Update token
                    print("🔄 Updating token...")
                    self.update_active_token()
                    return True
            return False
        except Exception as e:
            print(f"Trigger check error: {e}")
            return False

    def refresh_token(self, email, account_data):
        """Refresh Firebase token"""
        try:
            import requests

            refresh_token = account_data['stsTokenManager']['refreshToken']
            api_key = account_data['apiKey']

            url = f"https://securetoken.googleapis.com/v1/token?key={api_key}"
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token
            }

            # Direct connection - completely bypass proxy and SSL verification
            response = requests.post(url, json=data, timeout=30, verify=False)

            if response.status_code == 200:
                token_data = response.json()
                new_token_data = {
                    'accessToken': token_data['access_token'],
                    'refreshToken': token_data['refresh_token'],
                    'expirationTime': int(time.time() * 1000) + (int(token_data['expires_in']) * 1000)
                }

                # Update database
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('SELECT account_data FROM accounts WHERE email = ?', (email,))
                result = cursor.fetchone()

                if result:
                    account_data = json.loads(result[0])
                    account_data['stsTokenManager'].update(new_token_data)

                    cursor.execute('''
                        UPDATE accounts SET account_data = ?, last_updated = CURRENT_TIMESTAMP
                        WHERE email = ?
                    ''', (json.dumps(account_data), email))
                    conn.commit()

                conn.close()
                return True
            return False
        except Exception as e:
            print(f"Token refresh error: {e}")
            return False

    def mark_account_as_banned(self, email):
        """Mark account as banned"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Update account health_status as 'banned'
            cursor.execute('''
                UPDATE accounts SET health_status = 'banned', last_updated = CURRENT_TIMESTAMP
                WHERE email = ?
            ''', (email,))
            conn.commit()
            conn.close()

            print(f"Account marked as banned: {email}")

            # Clear active account (banned account cannot be active)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM proxy_settings WHERE key = ?', ('active_account',))
            conn.commit()
            conn.close()

            # Clear active account information in Handler
            self.active_token = None
            self.active_email = None
            self.token_expiry = None

            print("Banned account removed from active accounts list")

            # Send ban notification to GUI
            self.notify_gui_about_ban(email)
            return True

        except Exception as e:
            print(f"Error marking account as banned: {e}")
            return False

    def notify_gui_about_ban(self, email):
        """Send ban notification to GUI via file"""
        try:
            import os
            import time

            # Create ban notification file
            ban_notification_file = "ban_notification.tmp"
            with open(ban_notification_file, 'w', encoding='utf-8') as f:
                f.write(f"{email}|{int(time.time())}")

            print(f"Ban notification file created: {ban_notification_file}")
        except Exception as e:
            print(f"Error sending ban notification: {e}")

    def load_user_settings(self):
        """Load user_settings.json file"""
        try:
            import os
            if os.path.exists("user_settings.json"):
                with open("user_settings.json", 'r', encoding='utf-8') as f:
                    self.user_settings_cache = json.load(f)
                print("✅ user_settings.json file loaded successfully")
                return True
            else:
                print("⚠️ user_settings.json file not found")
                self.user_settings_cache = None
                return False
        except Exception as e:
            print(f"Error loading user_settings.json: {e}")
            self.user_settings_cache = None
            return False

    def refresh_user_settings(self):
        """Reload user_settings.json file"""
        print("🔄 Reloading user_settings.json...")
        return self.load_user_settings()

# Global handler instance
handler = WarpProxyHandler()

def is_relevant_request(flow: http.HTTPFlow) -> bool:
    """Check if this request is relevant to us"""

    # Check and exclude requests from WarpAccountManager
    if flow.request.headers.get("x-warp-manager-request") == "true":
        return False

    # Check Firebase token refresh requests by User-Agent and exclude them from processing
    if ("securetoken.googleapis.com" in flow.request.pretty_host and
        flow.request.headers.get("User-Agent") == "WarpAccountManager/1.0"):
        return False

    # Process only specific domains
    relevant_domains = [
        "app.warp.dev",
        "dataplane.rudderstack.com",  # For blocking
        "sentry.io"  # For blocking
    ]

    # Silently pass requests not related to Warp (don't block internet access)
    if not any(domain in flow.request.pretty_host for domain in relevant_domains):
        return False

    return True

def request(flow: http.HTTPFlow) -> None:
    """Executed when request is intercepted"""

    # Immediately filter unimportant requests - pass silently (don't interfere with internet access)
    if not is_relevant_request(flow):
        # Directly pass all traffic not related to Warp
        return

    request_url = flow.request.pretty_url

    # Block requests to *.dataplane.rudderstack.com
    if "dataplane.rudderstack.com" in flow.request.pretty_host:
        print(f"🚫 Blocked Rudderstack request: {request_url}")
        flow.response = http.Response.make(
            204,  # No Content
            b"",
            {"Content-Type": "text/plain"}
        )
        return
    
    # Block requests to *.sentry.io (error reporting service)
    if "sentry.io" in flow.request.pretty_host:
        print(f"🚫 Blocked Sentry request: {request_url}")
        flow.response = http.Response.make(
            204,  # No Content
            b"",
            {"Content-Type": "text/plain"}
        )
        return
    
    # Block requests to app.warp.dev/analytics/block (analytics collection)
    if "app.warp.dev" in flow.request.pretty_host and "/analytics/block" in flow.request.path:
        print(f"🚫 Blocked Warp analytics request: {request_url}")
        flow.response = http.Response.make(
            204,  # No Content
            b"",
            {"Content-Type": "text/plain"}
        )
        return

    # Log detailed request information to file only (no console output)
    if "app.warp.dev" in flow.request.pretty_host:
        log_to_file("=== REQUEST DETAILS ===")
        log_to_file(f"URL: {flow.request.pretty_url}")
        log_to_file(f"Method: {flow.request.method}")
        log_to_file(f"Path: {flow.request.path}")
        log_to_file(f"Host: {flow.request.pretty_host}")
        log_to_file("Request Headers:")
        for header_name, header_value in flow.request.headers.items():
            if ('experiment' in header_name.lower() or 'authorization' in header_name.lower() or 
                'warp' in header_name.lower() or header_name.lower() in ['content-type', 'user-agent']):
                
                log_to_file(f"  {header_name}: {header_value}")
        
        # Log request body for POST requests
        if flow.request.method == "POST":
            try:
                # 检查请求内容是否为空
                if flow.request.content is None:
                    log_to_file("Request Body: [Empty request]")
                else:
                    content_type = flow.request.headers.get("content-type", "")
                    if "application/json" in content_type.lower():
                        request_text = flow.request.content.decode('utf-8', errors='replace')
                        log_to_file(f"Request Body: {request_text}")
                    else:
                        log_to_file(f"Request Body: [Binary data - {len(flow.request.content)} bytes]")
            except Exception as e:
                log_to_file(f"Error reading request content: {e}")
        
        log_to_file("=== END REQUEST ===\n")

    # Detect CreateGenericStringObject request - trigger user_settings.json update
    if ("/graphql/v2?op=CreateGenericStringObject" in request_url and
        flow.request.method == "POST"):
        print("🔄 CreateGenericStringObject request detected - updating user_settings.json...")
        handler.refresh_user_settings()

    # Check account change trigger (on every request)
    if handler.check_account_change_trigger():
        print("🔄 Trigger detected and token updated!")

    # Show active account information
    print(f"📧 Current active account: {handler.active_email}")

    # Check token every 30 seconds
    current_time = time.time()
    if current_time - handler.last_token_check > 30:  # 30 seconds
        print("⏰ Time for token check, updating...")
        handler.update_active_token()
        handler.last_token_check = current_time

    # Check active account
    if not handler.active_email:
        print("❓ No active account found, checking token...")
        handler.update_active_token()

    # Modify Authorization header
    if handler.active_token:
        old_auth = flow.request.headers.get("Authorization", "None")
        new_auth = f"Bearer {handler.active_token}"
        flow.request.headers["Authorization"] = new_auth

        print(f"🔑 Authorization header updated: {handler.active_email}")

        # Check if tokens are actually different
        if old_auth == new_auth:
            print("   ⚠️  WARNING: Old and new tokens are IDENTICAL!")
        else:
            print("   ✅ Token successfully changed")

        # Also show token ending
        if len(handler.active_token) > 100:
            print(f"   Token : {handler.active_token}")

    else:
        print("❌ ACTIVE TOKEN NOT FOUND - HEADER NOT MODIFIED!")
        print(f"   Active email: {handler.active_email}")
        print(f"   Token status: {handler.active_token is not None}")

    # For all app.warp.dev requests check and randomize x-warp-experiment-id header
    if "app.warp.dev" in flow.request.pretty_host:
        # Always generate new experiment ID and add/modify header
        new_experiment_id = generate_experiment_id()
        old_experiment_id = flow.request.headers.get("x-warp-experiment-id", "None")
        flow.request.headers["x-warp-experiment-id"] = new_experiment_id
        
        print(f"🧪 Experiment ID changed ({flow.request.path}):")
        if old_experiment_id != '' or old_experiment_id == None:
            print(f"   Old: {old_experiment_id}")
        print(f"   New: {new_experiment_id}")

def responseheaders(flow: http.HTTPFlow) -> None:
    """Executed when response headers are received - controls streaming"""
    # Immediately filter unimportant requests - pass silently
    if not is_relevant_request(flow):
        return

    # Enable streaming for /ai/multi-agent endpoint
    if "/ai/multi-agent" in flow.request.path:
        flow.response.stream = True
        print(f"[{time.strftime('%H:%M:%S')}] Streaming enabled: {flow.request.pretty_url}")
    else:
        flow.response.stream = False

def response(flow: http.HTTPFlow) -> None:
    """Executed when response is received"""

    # Check Firebase token refresh requests by User-Agent and exclude them from processing
    if ("securetoken.googleapis.com" in flow.request.pretty_host and
        flow.request.headers.get("User-Agent") == "WarpAccountManager/1.0"):
        return

    # Immediately filter unimportant requests - pass silently (don't interfere with internet access)
    if not is_relevant_request(flow):
        return

    # Exclude requests from WarpAccountManager
    if flow.request.headers.get("x-warp-manager-request") == "true":
        return

    # Log detailed response information to file only (no console output)
    if "app.warp.dev" in flow.request.pretty_host:
        log_to_file("=== RESPONSE DETAILS ===")
        log_to_file(f"URL: {flow.request.pretty_url}")
        log_to_file(f"Method: {flow.request.method}")
        log_to_file(f"Status: {flow.response.status_code}")
        log_to_file(f"Host: {flow.request.pretty_host}")
        log_to_file("Response Headers:")
        for header_name, header_value in flow.response.headers.items():
            log_to_file(f"  {header_name}: {header_value}")
        
        # Log request headers for context
        log_to_file("Request Headers (context):")
        for header_name, header_value in flow.request.headers.items():
            if ('experiment' in header_name.lower() or 'authorization' in header_name.lower() or 
                'warp' in header_name.lower() or header_name.lower() in ['content-type', 'user-agent']):
                # 记录完整值，不截断
                log_to_file(f"  {header_name}: {header_value}")
        
        # Log response content (完整记录，不截断)
        try:
            # 检查响应内容是否为空
            if flow.response.content is None:
                log_to_file("Response Content: [Empty response]")
            else:
                content_type = flow.response.headers.get("content-type", "")
                if "application/json" in content_type.lower():
                    response_text = flow.response.content.decode('utf-8', errors='replace')
                    # 完整记录响应内容
                    log_to_file(f"Response Content: {response_text}")
                elif "text/" in content_type.lower():
                    response_text = flow.response.content.decode('utf-8', errors='replace')
                    # 完整记录响应内容
                    log_to_file(f"Response Content: {response_text}")
                else:
                    log_to_file(f"Response Content: [Binary data - {len(flow.response.content)} bytes]")
        except Exception as e:
            log_to_file(f"Error reading response content: {e}")
        
        log_to_file("=== END RESPONSE ===")

    # app.warp.dev specific processing only
    if "app.warp.dev" in flow.request.pretty_host:
        # Use cached response for GetUpdatedCloudObjects request
        if ("/graphql/v2?op=GetUpdatedCloudObjects" in flow.request.pretty_url and
            flow.request.method == "POST" and
            flow.response.status_code == 200 and
            handler.user_settings_cache is not None):
            print("🔄 GetUpdatedCloudObjects response being replaced with cached data...")
            try:
                # Convert cached data to JSON string
                cached_response = json.dumps(handler.user_settings_cache, ensure_ascii=False)

                # Modify Response
                flow.response.content = cached_response.encode('utf-8')
                flow.response.headers["Content-Length"] = str(len(flow.response.content))
                flow.response.headers["Content-Type"] = "application/json"

                print("✅ GetUpdatedCloudObjects response successfully modified")
            except Exception as e:
                print(f"❌ Error modifying response: {e}")

        # 403 error in /ai/multi-agent endpoint - immediate account ban
        if "/ai/multi-agent" in flow.request.path and flow.response.status_code == 403:
            print("⛔ 403 FORBIDDEN - Account ban detected!")
            if handler.active_email:
                print(f"Banned account: {handler.active_email}")
                handler.mark_account_as_banned(handler.active_email)
            else:
                print("Active account not found, ban not marked")

        # If 401 error received, try to refresh token
        if flow.response.status_code == 401:
            print("401 error received, refreshing token...")
            if handler.update_active_token():
                print("Token refreshed, retry request")

# Load active account on startup
def load(loader):
    """Executed when script starts"""
    print("Warp Proxy Script started")
    print(f"📝 app.warp.dev requests/responses will be logged to: logs/warp_responses_{datetime.now().strftime('%Y%m%d')}.log")
    print("Checking database connection...")
    handler.update_active_token()
    if handler.active_email:
        print(f"Active account loaded: {handler.active_email}")
        print(f"Token exists: {handler.active_token is not None}")
    else:
        print("No active account found - Don't forget to activate an account!")

    # Load user_settings.json file
    print("Loading user_settings.json file...")
    handler.load_user_settings()

def done():
    """Executed when script stops"""
    print("Warp Proxy Script stopped")
