#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import asyncio
import time
import sys
from typing import Optional, Dict, Any

# Import registry manager only on Windows
if sys.platform == "win32":
    from src.managers.warp_registry_manager import warp_registry_manager
else:
    warp_registry_manager = None

# Attempt to import curl_cffi
try:
    from curl_cffi.requests import AsyncSession
    CURL_CFFI_AVAILABLE = True
except ImportError:
    CURL_CFFI_AVAILABLE = False


class WarpRegistrationManager:
    """Manager for Warp.dev account registration"""
    
    def __init__(self):
        self.session: Optional[object] = None
        
        # Warp.dev API endpoints
        self.firebase_api_key = "AIzaSyBdy3O3S9hrdayLJxJ7mriBR4qgUaUygAs"
        self.send_oob_url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={self.firebase_api_key}"
        self.verify_oob_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithEmailLink?key={self.firebase_api_key}"
        self.lookup_url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={self.firebase_api_key}"
        self.warp_graphql_url = "https://app.warp.dev/graphql/v2?op=GetOrCreateUser"
        
    async def __aenter__(self):
        """Async context manager entry"""
        if CURL_CFFI_AVAILABLE:
            # Configuration for curl_cffi without proxy
            session_config = {
                'verify': False,  # 禁用SSL验证
                'timeout': 30,    # 设置超时
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Content-Type': 'application/json',
                    'Origin': 'https://app.warp.dev',
                    'Referer': 'https://app.warp.dev/',
                }
            }
            
            logging.info("Registration using direct connection (no proxy)")
            self.session = AsyncSession(**session_config)
        else:
            self.session = None
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session and CURL_CFFI_AVAILABLE:
            await self.session.close()
    
    async def send_email_verification(self, email: str) -> Optional[Dict[str, Any]]:
        """Send email verification code to the email address"""
        if not CURL_CFFI_AVAILABLE:
            # Заглушка для тестирования
            await asyncio.sleep(1)
            return {
                "email": email,
                "kind": "identitytoolkit#GetOobConfirmationCodeResponse"
            }
            
        try:
            payload = {
                "requestType": "EMAIL_SIGNIN",
                "email": email,
                "clientType": "CLIENT_TYPE_WEB", 
                "continueUrl": "https://app.warp.dev/login?redirect_to=/teams_discovery",
                "canHandleCodeInApp": True
            }
            
            print(f"📧 Sending verification code to {email}...")
            
            response = await self.session.post(self.send_oob_url, json=payload)
            
            if response.status_code == 200:
                result = json.loads(response.content)
                logging.info(f"Verification code sent to {email}")
                return result
            else:
                logging.error(f"Code sending error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"Error sending email verification: {e}")
            return None
    
    async def verify_email_code(self, email: str, oob_code: str) -> Optional[Dict[str, Any]]:
        """Verify email verification code"""
        if not CURL_CFFI_AVAILABLE:
            # Заглушка для тестирования
            await asyncio.sleep(1)
            return {
                "localId": f"test_user_{int(time.time())}",
                "email": email,
                "idToken": f"test_token_{int(time.time())}",
                "refreshToken": f"test_refresh_{int(time.time())}",
                "expiresIn": "3600"
            }
            
        try:
            payload = {
                "email": email,
                "oobCode": oob_code
            }
            
            print(f"🔐 Confirming code for {email}...")
            
            response = await self.session.post(self.verify_oob_url, json=payload)
            
            if response.status_code == 200:
                result = json.loads(response.content)
                logging.info(f"Email confirmed for {email}")
                return result
            else:
                logging.error(f"Code confirmation error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"Error verifying email code: {e}")
            return None

    async def lookup_account_info(self, id_token: str) -> Optional[Dict[str, Any]]:
        """Get complete account information using idToken"""
        try:
            payload = {
                "idToken": id_token
            }
            
            print(f"🔍 Getting full account information...")
            
            response = await self.session.post(self.lookup_url, json=payload)
            
            if response.status_code == 200:
                result = json.loads(response.content)
                logging.info("Full account information retrieved")
                logging.debug(f"Raw lookup response: {json.dumps(result, indent=2, ensure_ascii=False)}")
                return result
            else:
                logging.error(f"Information retrieval error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"Error looking up account info: {e}")
            return None

    async def get_or_create_warp_user(self, id_token: str) -> Optional[Dict[str, Any]]:
        """Create or get Warp user profile using idToken"""
        try:
            payload = {
                "operationName": "GetOrCreateUser",
                "variables": {
                    "input": {},
                    "requestContext": {
                        "osContext": {},
                        "clientContext": {}
                    }
                },
                "query": "mutation GetOrCreateUser($input: GetOrCreateUserInput!, $requestContext: RequestContext!) {\n  getOrCreateUser(requestContext: $requestContext, input: $input) {\n    __typename\n    ... on GetOrCreateUserOutput {\n      uid\n      isOnboarded\n      anonymousUserInfo {\n        anonymousUserType\n        linkedAt\n        __typename\n      }\n      workspaces {\n        joinableTeams {\n          teamUid\n          numMembers\n          name\n          teamAcceptingInvites\n          __typename\n        }\n        __typename\n      }\n      onboardingSurveyStatus\n      firstLoginAt\n      adminOf\n      deletedAnonymousUser\n      __typename\n    }\n    ... on UserFacingError {\n      error {\n        message\n        __typename\n      }\n      __typename\n    }\n  }\n}\n"
            }
            
            headers = {
                "Authorization": f"Bearer {id_token}",
                "Content-Type": "application/json"
            }
            
            print(f"👤 Creating/getting Warp user...")
            
            response = await self.session.post(self.warp_graphql_url, json=payload, headers=headers)
            
            if response.status_code == 200:
                result = json.loads(response.content)
                logging.info("Warp user created/retrieved")
                return result
            else:
                logging.error(f"Warp user creation error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"Error creating Warp user: {e}")
            return None


async def register_warp_account(email: str) -> Optional[Dict[str, Any]]:
    """Register new Warp.dev account with given email"""
    # Prepare registry environment on Windows
    if warp_registry_manager:
        logging.info("Preparing Warp registry environment for registration...")
        warp_registry_manager.prepare_for_registration()
    
    async with WarpRegistrationManager() as manager:
        # Отправляем код подтверждения
        verification_result = await manager.send_email_verification(email)
        
        if verification_result:
            logging.info(f"Confirmation code sent to {email}")
            return {
                "status": "verification_sent",
                "email": email,
                "verification_result": verification_result
            }
        else:
            logging.error(f"Failed to send confirmation code to {email}")
            return None


async def complete_warp_registration(email: str, oob_code: str) -> Optional[Dict[str, Any]]:
    """Complete Warp.dev account registration with verification code"""
    # Prepare registry environment on Windows
    if warp_registry_manager:
        logging.info("Preparing Warp registry environment for registration completion...")
        warp_registry_manager.prepare_for_registration()
    
    async with WarpRegistrationManager() as manager:
        # Confirm code
        auth_result = await manager.verify_email_code(email, oob_code)
        
        if auth_result and 'idToken' in auth_result:
            id_token = auth_result['idToken']
            logging.info(f"Received idToken: {id_token[:50]}...")
            
            # Get full account information
            account_info = await manager.lookup_account_info(id_token)
            
            # Create/get Warp user
            warp_user_info = await manager.get_or_create_warp_user(id_token)
            
            if account_info:
                logging.info(f"Account {email} successfully registered and full information retrieved")
                return {
                    "status": "registration_complete",
                    "email": email,
                    "auth_result": auth_result,
                    "account_info": account_info,
                    "warp_user_info": warp_user_info
                }
            else:
                logging.warning(f"Account {email} registered but failed to get full information")
                return {
                    "status": "registration_complete",
                    "email": email,
                    "auth_result": auth_result,
                    "account_info": None,
                    "warp_user_info": warp_user_info
                }
        else:
            logging.error(f"Failed to complete registration for {email}")
            return None


if __name__ == "__main__":
    import asyncio
    asyncio.run(register_warp_account("test@example.com"))