#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Background worker threads for account operations
"""

import sys
import json
import time
import logging
import requests
import asyncio
import os
from typing import Optional
from PyQt5.QtCore import QThread, pyqtSignal
from src.config.languages import _
from src.managers.database_manager import DatabaseManager


class TokenWorker(QThread):
    """Single token refresh in background"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)  # success, message
    error = pyqtSignal(str)

    def __init__(self, email, account_data, proxy_enabled=False):
        super().__init__()
        self.email = email
        self.account_data = account_data
        self.account_manager = DatabaseManager()
        self.proxy_enabled = proxy_enabled

    def run(self):
        try:
            self.progress.emit(f"Updating token: {self.email}")

            if self.refresh_token():
                self.account_manager.update_account_health(self.email, 'healthy')
                self.finished.emit(True, f"{self.email} token successfully updated")
            else:
                self.account_manager.update_account_health(self.email, 'unhealthy')
                self.finished.emit(False, f"{self.email} failed to update token")

        except Exception as e:
            self.error.emit(f"Token update error: {str(e)}")

    def refresh_token(self):
        """Refresh Firebase token"""
        try:
            refresh_token = self.account_data['stsTokenManager']['refreshToken']
            api_key = self.account_data['apiKey']

            url = f"https://securetoken.googleapis.com/v1/token?key={api_key}"
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'WarpAccountManager/1.0'
            }
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token
            }

            # Direct connection - completely bypass proxy
            response = requests.post(url, json=data, headers=headers, timeout=30, verify=False)

            if response.status_code == 200:
                token_data = response.json()
                new_token_data = {
                    'accessToken': token_data['access_token'],
                    'refreshToken': token_data['refresh_token'],
                    'expirationTime': int(time.time() * 1000) + (int(token_data['expires_in']) * 1000)
                }

                return self.account_manager.update_account_token(self.email, new_token_data)
            return False
        except Exception as e:
            logging.error(f"Token update error: {e}")
            return False


class TokenRefreshWorker(QThread):
    """Bulk token refresh and limit information retrieval in background"""
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, accounts, proxy_enabled=False):
        super().__init__()
        self.accounts = accounts
        self.account_manager = DatabaseManager()
        self.proxy_enabled = proxy_enabled

    def run(self):
        results = []
        total_accounts = len(self.accounts)

        for i, (email, account_json, health_status) in enumerate(self.accounts):
            try:
                self.progress.emit(int((i / total_accounts) * 100), _('processing_account', email))

                # Skip banned accounts
                if health_status == _('status_banned_key'):
                    self.account_manager.update_account_limit_info(email, _('status_na'))
                    results.append((email, _('status_banned'), _('status_na')))
                    continue

                account_data = json.loads(account_json)

                # Check token expiration
                expiration_time = account_data['stsTokenManager']['expirationTime']
                # Convert to int if string
                if isinstance(expiration_time, str):
                    expiration_time = int(expiration_time)
                current_time = int(time.time() * 1000)

                if current_time >= expiration_time:
                    # Token expired, refresh it
                    self.progress.emit(int((i / total_accounts) * 100), _('refreshing_token', email))
                    if not self.refresh_token(email, account_data):
                        # Failed to refresh token - mark as unhealthy
                        self.account_manager.update_account_health(email, _('status_unhealthy'))
                        self.account_manager.update_account_limit_info(email, _('status_na'))
                        results.append((email, _('token_refresh_failed', email), _('status_na')))
                        continue

                    # Get updated account_data
                    updated_accounts = self.account_manager.get_accounts()
                    for updated_email, updated_json in updated_accounts:
                        if updated_email == email:
                            account_data = json.loads(updated_json)
                            break

                # Get limit information
                limit_info = self.get_limit_info(account_data)
                if limit_info and isinstance(limit_info, dict):
                    used = limit_info.get('requestsUsedSinceLastRefresh', 0)
                    total = limit_info.get('requestLimit', 0)
                    limit_text = f"{used}/{total}"
                    # Success - mark as healthy and save limit info
                    self.account_manager.update_account_health(email, _('status_healthy'))
                    self.account_manager.update_account_limit_info(email, limit_text)
                    results.append((email, _('success'), limit_text))
                else:
                    # Failed to get limit info - mark as unhealthy
                    self.account_manager.update_account_health(email, _('status_unhealthy'))
                    self.account_manager.update_account_limit_info(email, _('status_na'))
                    results.append((email, _('limit_info_failed'), _('status_na')))

            except Exception as e:
                self.account_manager.update_account_limit_info(email, _('status_na'))
                results.append((email, f"{_('error')}: {str(e)}", _('status_na')))

        self.finished.emit(results)

    def refresh_token(self, email, account_data):
        """Refresh Firebase token"""
        try:
            refresh_token = account_data['stsTokenManager']['refreshToken']
            api_key = account_data['apiKey']

            url = f"https://securetoken.googleapis.com/v1/token?key={api_key}"
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'WarpAccountManager/1.0'  # Mark with custom User-Agent
            }
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token
            }

            # Direct connection - completely bypass proxy
            response = requests.post(url, json=data, headers=headers, timeout=30, verify=False)

            if response.status_code == 200:
                token_data = response.json()
                new_token_data = {
                    'accessToken': token_data['access_token'],
                    'refreshToken': token_data['refresh_token'],
                    'expirationTime': int(time.time() * 1000) + (int(token_data['expires_in']) * 1000)
                }

                return self.account_manager.update_account_token(email, new_token_data)
            return False
        except Exception as e:
            logging.error(f"Token update error: {e}")
            return False

    def get_limit_info(self, account_data):
        """Get limit information from Warp API"""
        try:
            access_token = account_data['stsTokenManager']['accessToken']

            # Get dynamic OS information from proxy manager
            from src.proxy.proxy_windows import WindowsProxyManager
            from src.proxy.proxy_macos import MacOSProxyManager  
            from src.proxy.proxy_linux import LinuxProxyManager
            
            if sys.platform == "win32":
                os_info = WindowsProxyManager.get_os_info()
            elif sys.platform == "darwin":
                os_info = MacOSProxyManager.get_os_info()
            else:
                os_info = LinuxProxyManager.get_os_info()
            
            url = "https://app.warp.dev/graphql/v2?op=GetRequestLimitInfo"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
                'x-warp-client-version': 'v0.2025.08.27.08.11.stable_04',
                'x-warp-os-category': os_info['category'],
                'x-warp-os-name': os_info['name'],
                'x-warp-os-version': os_info['version'],
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'x-warp-manager-request': 'true'  # Request from our application
            }

            query = """
            query GetRequestLimitInfo($requestContext: RequestContext!) {
              user(requestContext: $requestContext) {
                __typename
                ... on UserOutput {
                  user {
                    requestLimitInfo {
                      isUnlimited
                      nextRefreshTime
                      requestLimit
                      requestsUsedSinceLastRefresh
                      requestLimitRefreshDuration
                      isUnlimitedAutosuggestions
                      acceptedAutosuggestionsLimit
                      acceptedAutosuggestionsSinceLastRefresh
                      isUnlimitedVoice
                      voiceRequestLimit
                      voiceRequestsUsedSinceLastRefresh
                      voiceTokenLimit
                      voiceTokensUsedSinceLastRefresh
                      isUnlimitedCodebaseIndices
                      maxCodebaseIndices
                      maxFilesPerRepo
                      embeddingGenerationBatchSize
                    }
                  }
                }
                ... on UserFacingError {
                  error {
                    __typename
                    ... on SharedObjectsLimitExceeded {
                      limit
                      objectType
                      message
                    }
                    ... on PersonalObjectsLimitExceeded {
                      limit
                      objectType
                      message
                    }
                    ... on AccountDelinquencyError {
                      message
                    }
                    ... on GenericStringObjectUniqueKeyConflict {
                      message
                    }
                  }
                  responseContext {
                    serverVersion
                  }
                }
              }
            }
            """

            payload = {
                "query": query,
                "variables": {
                    "requestContext": {
                        "clientContext": {
                            "version": "v0.2025.08.27.08.11.stable_04"
                        },
                        "osContext": {
                            "category": os_info['category'],
                            "linuxKernelVersion": None,
                            "name": os_info['category'],
                            "version": os_info['version']
                        }
                    }
                },
                "operationName": "GetRequestLimitInfo"
            }

            # Direct connection - completely bypass proxy
            response = requests.post(url, headers=headers, json=payload, timeout=30, verify=False)

            if response.status_code == 200:
                data = response.json()
                if 'data' in data and data['data'] and 'user' in data['data']:
                    user_data = data['data']['user']
                    if user_data and user_data.get('__typename') == 'UserOutput':
                        user_info = user_data.get('user')
                        if user_info:
                            return user_info.get('requestLimitInfo')
                        return None
            return None
        except Exception as e:
            logging.error(f"Error getting limit information: {e}")
            return None


class AccountCreationWorker(QThread):
    """Temporary email and account creation in background"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)  # result dict with email data
    error = pyqtSignal(str)
    
    def __init__(self, account_manager):
        super().__init__()
        self.account_manager = account_manager
    
    def run(self):
        try:
            self.progress.emit("Initializing temporary email creation...")
            
            # Check module availability
            try:
                import asyncio
                from src.utils.account_creator import create_warp_account_automatically
                
                # Run automatic Warp.dev account creation without proxy
                self.progress.emit("Creating temporary email address...")
                
                # Create new event loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    self.progress.emit("Sending verification code...")
                    result = loop.run_until_complete(create_warp_account_automatically())
                    
                    if result:
                        # Check if result contains error information
                        if isinstance(result, dict) and 'error' in result:
                            if result['error'] == 'network_error':
                                self.error.emit(f"Network Error: {result['message']}")
                            else:
                                self.error.emit(f"Registration Error: {result['message']}")
                            return
                        
                        # Successful account creation
                        self.progress.emit(f"Account created: {result['email']}")
                        
                        # Convert result to format for database saving
                        account_json = self._convert_to_account_format(result)
                        if account_json:
                            # Save to database
                            account_manager = self.account_manager
                            success, message = account_manager.add_account(account_json)
                            
                            if success:
                                self.progress.emit(f"✅ Account added to database: {result['email']}")
                                # Return result with save information
                                result['saved_to_database'] = True
                                result['save_message'] = message
                            else:
                                self.progress.emit(f"❌ Save error: {message}")
                                result['saved_to_database'] = False
                                result['save_message'] = message
                        else:
                            self.progress.emit("❌ Account data conversion error")
                            result['saved_to_database'] = False
                            result['save_message'] = "Account data conversion error"
                        
                        self.finished.emit(result)
                    else:
                        self.error.emit("Failed to create Warp.dev account")
                finally:
                    loop.close()
                    
            except ImportError as ie:
                self.error.emit(f"Missing dependencies: {str(ie)}")
            except Exception as e:
                self.error.emit(f"Email creation error: {str(e)}")
                
        except Exception as e:
            self.error.emit(f"General error: {str(e)}")
    
    def _convert_to_account_format(self, account_result: dict) -> Optional[str]:
        """Convert result to Firebase format for saving"""
        try:
            account_data = account_result.get('account_data', {})
            email = account_result.get('email')
            
            if not account_data or not email:
                return None
            
            # Extract authentication data (from signInWithEmailLink)
            auth_result = account_data.get('auth_result', {})
            
            # Extract account information (from accounts:lookup)
            account_info = account_data.get('account_info', {})
            user_info = None
            if account_info and 'users' in account_info and account_info['users']:
                user_info = account_info['users'][0]
                logging.debug(f"user_info from lookup: {json.dumps(user_info, indent=2, ensure_ascii=False)}")
            
            # Use auth_result data if available, fallback to account_data keys
            local_id = auth_result.get('localId') or account_data.get('localId')
            id_token = auth_result.get('idToken') or account_data.get('idToken')
            refresh_token = auth_result.get('refreshToken') or account_data.get('refreshToken')
            expires_in = auth_result.get('expiresIn') or account_data.get('expiresIn', '3600')
            
            # Use user_info data if available for more accurate account details
            if user_info:
                created_at = user_info.get('createdAt', str(int(time.time() * 1000)))
                last_login_at = user_info.get('lastLoginAt', str(int(time.time() * 1000)))
                email_verified = user_info.get('emailVerified', True)
                display_name = user_info.get('displayName')  # Get displayName from user_info
            else:
                created_at = str(int(time.time() * 1000))
                last_login_at = str(int(time.time() * 1000))
                email_verified = True
                display_name = None
                    
            logging.debug(f"displayName from user_info: '{display_name}'")    
            
            # Create structure compatible with AccountManager format
            firebase_account = {
                "uid": local_id,
                "email": email,
                "emailVerified": email_verified,
                "isAnonymous": False,
                "providerData": [
                    {
                        "providerId": "password",
                        "uid": email,
                        "displayName": display_name,
                        "email": email,
                        "phoneNumber": None,
                        "photoURL": None
                    }
                ],
                "stsTokenManager": {
                    "refreshToken": refresh_token,
                    "accessToken": id_token,
                    "expirationTime": int(time.time() * 1000) + (int(expires_in) * 1000)
                },
                "createdAt": created_at,
                "lastLoginAt": last_login_at,
                "apiKey": "AIzaSyBdy3O3S9hrdayLJxJ7mriBR4qgUaUygAs",
                "appName": "[DEFAULT]"
            }
            
            logging.info(f"Successfully converted account {email} to Firebase format")
            logging.debug(f"User ID: {local_id}")
            logging.debug(f"ID Token: {id_token[:50] if id_token else 'None'}...")
            logging.debug(f"Used full account information: {'Yes' if user_info else 'No'}")
            
            return json.dumps(firebase_account, ensure_ascii=False)
            
        except Exception as e:
            logging.error(f"Account format conversion error: {e}")
            return None