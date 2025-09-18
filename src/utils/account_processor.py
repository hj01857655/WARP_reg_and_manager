#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Account processing and validation functionality
"""

import json
import logging
import time
from typing import Optional, Dict, Any
from src.utils.utils import safe_json_loads, is_valid_json_structure


class AccountProcessor:
    """Account data processing and validation"""
    
    @staticmethod
    def validate_account_data(data):
        """Validate account data structure"""
        try:
            # Check if data is dict or string
            if isinstance(data, str):
                data = safe_json_loads(data)
            
            if not isinstance(data, dict):
                return False
            
            # Check required fields
            required_fields = ['email', 'stsTokenManager']
            for field in required_fields:
                if field not in data:
                    return False

            # Check stsTokenManager structure
            sts_manager = data['stsTokenManager']
            required_sts_fields = ['accessToken', 'refreshToken']
            for field in required_sts_fields:
                if field not in sts_manager:
                    return False

            return True

        except Exception as e:
            logging.error(f"Account validation error: {e}")
            return False

    @staticmethod
    def convert_to_firebase_format(account_data: Dict[str, Any], email: str = None) -> Optional[str]:
        """Convert account result to Firebase format for saving"""
        try:
            if not email:
                email = account_data.get('email')
            
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
            logging.debug(f"Used full account info: {'Yes' if user_info else 'No'}")
            
            return json.dumps(firebase_account, ensure_ascii=False)
            
        except Exception as e:
            logging.error(f"Account format conversion error: {e}")
            return None

    @staticmethod
    def process_account_limits(limit_info: Dict[str, Any]) -> str:
        """Process account limit information into readable format"""
        try:
            if not limit_info or not isinstance(limit_info, dict):
                return "N/A"
            
            used = limit_info.get('requestsUsedSinceLastRefresh', 0)
            total = limit_info.get('requestLimit', 0)
            
            if limit_info.get('isUnlimited', False):
                return f"{used}/∞"
            
            return f"{used}/{total}"
            
        except Exception as e:
            logging.error(f"Limit processing error: {e}")
            return "N/A"

    @staticmethod
    def extract_account_info(account_json: str) -> Dict[str, Any]:
        """Extract basic account information from JSON"""
        try:
            account_data = safe_json_loads(account_json)
            if not account_data:
                return {}
            
            return {
                'email': account_data.get('email', 'Unknown'),
                'uid': account_data.get('uid', 'Unknown'),
                'created_at': account_data.get('createdAt'),
                'email_verified': account_data.get('emailVerified', False),
                'last_login': account_data.get('lastLoginAt'),
                'api_key': account_data.get('apiKey', ''),
            }
        except Exception as e:
            logging.error(f"Account info extraction error: {e}")
            return {}

    @staticmethod
    def is_token_expired(account_json: str) -> bool:
        """Check if account token is expired"""
        try:
            account_data = safe_json_loads(account_json)
            if not account_data:
                return True
            
            sts_manager = account_data.get('stsTokenManager', {})
            expiration_time = sts_manager.get('expirationTime')
            
            if not expiration_time:
                return True
            
            # Convert to int if string
            if isinstance(expiration_time, str):
                expiration_time = int(expiration_time)
            
            current_time = int(time.time() * 1000)
            return current_time >= expiration_time
            
        except Exception as e:
            logging.error(f"Token expiration check error: {e}")
            return True

    @staticmethod
    def get_token_expiry_time(account_json: str) -> Optional[str]:
        """Get token expiry time in readable format"""
        try:
            account_data = safe_json_loads(account_json)
            if not account_data:
                return None
            
            sts_manager = account_data.get('stsTokenManager', {})
            expiration_time = sts_manager.get('expirationTime')
            
            if not expiration_time:
                return None
            
            # Convert to int if string
            if isinstance(expiration_time, str):
                expiration_time = int(expiration_time)
            
            # Convert to readable format
            from utils import format_timestamp
            return format_timestamp(expiration_time)
            
        except Exception as e:
            logging.error(f"Token expiry time error: {e}")
            return None

    @staticmethod
    def sanitize_account_data(account_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize account data by removing sensitive information for logging"""
        try:
            sanitized = account_data.copy()
            
            # Remove or truncate sensitive fields
            if 'stsTokenManager' in sanitized:
                sts = sanitized['stsTokenManager']
                if 'accessToken' in sts:
                    sts['accessToken'] = sts['accessToken'][:20] + "..." if sts['accessToken'] else None
                if 'refreshToken' in sts:
                    sts['refreshToken'] = sts['refreshToken'][:20] + "..." if sts['refreshToken'] else None
            
            if 'apiKey' in sanitized:
                sanitized['apiKey'] = sanitized['apiKey'][:20] + "..." if sanitized['apiKey'] else None
            
            return sanitized
            
        except Exception as e:
            logging.error(f"Data sanitization error: {e}")
            return {}

    @staticmethod
    def compare_account_versions(old_account: str, new_account: str) -> Dict[str, Any]:
        """Compare two account versions and return differences"""
        try:
            old_data = safe_json_loads(old_account)
            new_data = safe_json_loads(new_account)
            
            if not old_data or not new_data:
                return {'error': 'Invalid account data'}
            
            changes = {}
            
            # Check token changes
            old_sts = old_data.get('stsTokenManager', {})
            new_sts = new_data.get('stsTokenManager', {})
            
            if old_sts.get('accessToken') != new_sts.get('accessToken'):
                changes['access_token_changed'] = True
            
            if old_sts.get('refreshToken') != new_sts.get('refreshToken'):
                changes['refresh_token_changed'] = True
            
            if old_sts.get('expirationTime') != new_sts.get('expirationTime'):
                changes['expiration_changed'] = {
                    'old': old_sts.get('expirationTime'),
                    'new': new_sts.get('expirationTime')
                }
            
            # Check other fields
            for field in ['email', 'emailVerified', 'lastLoginAt']:
                if old_data.get(field) != new_data.get(field):
                    changes[f'{field}_changed'] = {
                        'old': old_data.get(field),
                        'new': new_data.get(field)
                    }
            
            return changes
            
        except Exception as e:
            logging.error(f"Account comparison error: {e}")
            return {'error': str(e)}

    @staticmethod
    def create_account_backup(account_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a backup copy of account data with timestamp"""
        try:
            backup = {
                'timestamp': int(time.time() * 1000),
                'backup_version': '1.0',
                'account_data': account_data.copy()
            }
            
            return backup
            
        except Exception as e:
            logging.error(f"Account backup creation error: {e}")
            return {}

    @staticmethod
    def restore_account_from_backup(backup_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Restore account data from backup"""
        try:
            if not isinstance(backup_data, dict):
                return None
            
            if 'account_data' not in backup_data:
                return None
            
            return backup_data['account_data']
            
        except Exception as e:
            logging.error(f"Account restore error: {e}")
            return None