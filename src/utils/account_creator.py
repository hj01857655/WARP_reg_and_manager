#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import json
import logging
from typing import Optional, Dict, Any
from src.managers.temp_email_manager import TempEmailManager
from src.utils.warp_registration import WarpRegistrationManager


class AutoAccountCreator:
    """Automatic Warp.dev account creator with email verification"""
    
    def __init__(self):
        self.max_wait_time = 60  # Maximum wait time for email in seconds
        self.check_interval = 5   # Check email every 5 seconds
        
    def _is_proxy_error(self, error_msg: str) -> bool:
        """Check if error is related to proxy issues"""
        proxy_error_patterns = [
            "CONNECT tunnel failed",
            "response 407",
            "curl: (56)",
            "Failed to perform",
            "Proxy authentication",
            "Connection refused",
            "Timeout",
            "Network is unreachable"
        ]
        
        error_lower = str(error_msg).lower()
        return any(pattern.lower() in error_lower for pattern in proxy_error_patterns)
    
    def _get_user_friendly_error(self, error_msg: str) -> str:
        """Convert technical error to user-friendly message"""
        if self._is_proxy_error(error_msg):
            return "Network connection error. Please check your internet connection."
        return f"Registration error: {error_msg}"
    
    async def create_account(self) -> Optional[Dict[str, Any]]:
        """Create complete Warp.dev account automatically"""
        try:
            # Create temporary email
            email_result = await self._create_temp_email()
            if not email_result:
                return None
                
            email = email_result['email']
            email_token = email_result['token']
            email_url_base = email_result['url_base']
            
            # Send verification code
            verification_sent = await self._send_verification_code(email)
            if not verification_sent:
                return None
            
            # Wait for email and extract code
            oob_code = await self._wait_for_verification_email(
                email_token, email_url_base
            )
            if not oob_code:
                return None
            
            # Complete registration
            account_data = await self._complete_registration(email, oob_code)
            if not account_data:
                return None
            
            return {
                "email": email,
                "account_data": account_data,
                "temp_email_info": email_result
            }
            
        except Exception as e:
            error_msg = str(e)
            logging.error(f"Error in create_account: {error_msg}")
            
            # Check if it's a network-related error
            if self._is_proxy_error(error_msg):
                return {
                    "error": "network_error",
                    "message": "Network connection failed. Please check your internet connection.",
                    "technical_details": error_msg
                }
            else:
                return {
                    "error": "general_error",
                    "message": self._get_user_friendly_error(error_msg),
                    "technical_details": error_msg
                }
            return None
    
    async def _create_temp_email(self) -> Optional[Dict[str, Any]]:
        """Create temporary email address"""
        try:
            async with TempEmailManager() as manager:
                result = await manager.create_temp_email()
                return result
        except Exception as e:
            error_msg = str(e)
            # Check for network-related errors
            if self._is_proxy_error(error_msg):
                network_error_msg = self._get_proxy_error_message(error_msg)
                logging.error(f"Network error creating temp email: {network_error_msg}")
                raise Exception(network_error_msg)
            else:
                logging.error(f"Error creating temp email: {e}")
                return None
    
    def _get_proxy_error_message(self, error_msg: str) -> str:
        """Get user-friendly network error message"""
        if "407" in error_msg or "CONNECT tunnel failed" in error_msg:
            return "Network authentication failed. Please check your internet connection."
        elif "Network is unreachable" in error_msg or "Connection refused" in error_msg:
            return "Cannot connect to server. Please check your internet connection."
        elif "Timeout" in error_msg:
            return "Connection timeout. Please check your network connection."
        else:
            return "Network connection error. Please check your internet connection."
    
    async def _send_verification_code(self, email: str) -> bool:
        """Send verification code to email"""
        try:
            async with WarpRegistrationManager() as manager:
                result = await manager.send_email_verification(email)
                return result is not None
        except Exception as e:
            error_msg = str(e)
            # Check for network-related errors
            if self._is_proxy_error(error_msg):
                network_error_msg = self._get_proxy_error_message(error_msg)
                logging.error(f"Network error sending verification: {network_error_msg}")
                raise Exception(network_error_msg)
            else:
                logging.error(f"Error sending verification: {e}")
                return False
    
    async def _wait_for_verification_email(self, token: str, url_base: str) -> Optional[str]:
        """Wait for verification email and extract oob code"""
        try:
            async with TempEmailManager() as manager:
                wait_count = 0
                max_attempts = self.max_wait_time // self.check_interval
                
                while wait_count < max_attempts:
                    # Use new method for automatic content reading
                    messages = await manager.get_messages_with_content(token, url_base)
                    if messages:
                        # Search for message from Firebase/Warp
                        for message in messages:
                            sender = message.get('from', {}).get('address', '') or message.get('sender_email', '')
                            subject = message.get('subject', '')
                            
                            if ('firebase' in sender.lower() or 'warp' in subject.lower() or 
                                'sign in' in subject.lower()):
                                
                                # Check HTML content first
                                html_content = message.get('html_text', '') or message.get('html', '')
                                if html_content:
                                    oob_code = manager.extract_oob_code(html_content)
                                    if oob_code:
                                        return oob_code
                                
                                # Then check text content
                                text_content = message.get('text', '') or message.get('content', '')
                                if text_content:
                                    oob_code = manager.extract_oob_code(text_content)
                                    if oob_code:
                                        return oob_code
                    
                    wait_count += 1
                    if wait_count < max_attempts:
                        await asyncio.sleep(self.check_interval)
                return None
                
        except Exception as e:
            logging.error(f"Error waiting for email: {e}")
            return None
    
    async def _complete_registration(self, email: str, oob_code: str) -> Optional[Dict[str, Any]]:
        """Complete account registration with oob code"""
        try:
            from src.utils.warp_registration import complete_warp_registration
            
            # Use the complete registration function that includes account lookup
            result = await complete_warp_registration(email, oob_code)
            
            if result and result.get('status') == 'registration_complete':
                # Extract the complete account information
                auth_result = result.get('auth_result', {})
                account_info = result.get('account_info', {})
                warp_user_info = result.get('warp_user_info', {})
                
                # Combine authentication and account information
                complete_data = {
                    'auth_result': auth_result,
                    'account_info': account_info,
                    'warp_user_info': warp_user_info,
                    # Include key fields for backward compatibility
                    'localId': auth_result.get('localId'),
                    'email': auth_result.get('email', email),
                    'idToken': auth_result.get('idToken'),
                    'refreshToken': auth_result.get('refreshToken'),
                    'expiresIn': auth_result.get('expiresIn')
                }
                

                if warp_user_info and 'data' in warp_user_info:
                    warp_data = warp_user_info['data'].get('getOrCreateUser', {})
                    if warp_data and warp_data.get('__typename') == 'GetOrCreateUserOutput':
                        print(f"   Warp UID: {warp_data.get('uid', 'N/A')}")
                        print(f"   Onboarded: {warp_data.get('isOnboarded', 'N/A')}")
                
                return complete_data
            else:
                return None
                
        except Exception as e:
            logging.error(f"Error completing registration: {e}")
            return None


async def create_warp_account_automatically() -> Optional[Dict[str, Any]]:
    """Convenience function to create Warp account automatically"""
    creator = AutoAccountCreator()
    return await creator.create_account()


if __name__ == "__main__":
    import asyncio
    asyncio.run(create_warp_account_automatically())