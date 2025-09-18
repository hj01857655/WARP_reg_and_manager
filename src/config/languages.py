#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simplified English-only language system
"""

class LanguageManager:
    """English-only language manager"""

    def __init__(self):
        self.current_language = 'en'
        self.translations = self.load_translations()

    def detect_system_language(self):
        """Always return English"""
        return 'en'

    def load_translations(self):
        """Load English translations"""
        translations = {
            'en': {
                # General
                'app_title': 'Warp Account Manager',
                'yes': 'Yes',
                'no': 'No',
                'ok': 'OK',
                'cancel': 'Cancel',
                'close': 'Close',
                'error': 'Error',
                'success': 'Success',
                'warning': 'Warning',
                'info': 'Information',

                # Buttons
                'proxy_start': 'Start Proxy',
                'proxy_stop': 'Stop Proxy',
                'proxy_active': 'Proxy Active',
                'add_account': 'Manual Add Account',
                'auto_add_account': 'Auto Add Account',
                'refresh_limits': 'Refresh Limits',
                'help': 'Help',
                'activate': '🟢 Activate',
                'deactivate': '🔴 Deactivate',
                'delete_account': '🗑️ Delete Account',
                'create_account': '🌐 Create Account',
                'add': 'Add',
                'copy_javascript': '📋 Copy JavaScript Code',
                'copied': '✅ Copied!',
                'copy_error': '❌ Error!',
                'open_certificate': '📁 Open Certificate File',
                'installation_complete': '✅ Installation Complete',

                # Table headers
                'current': 'Current',
                'email': 'Email',
                'status': 'Status',
                'limit': 'Usage',
                'created': 'Created',

                # Activation button texts
                'button_active': 'ACTIVE',
                'button_inactive': 'INACTIVE',
                'button_banned': 'BAN',
                'button_start': 'Start',
                'button_stop': 'Stop',

                # Status messages
                'status_active': 'Active',
                'status_banned': 'BAN',
                'status_token_expired': 'Token expired',
                'status_proxy_active': ' (Proxy active)',
                'status_error': 'Error',
                'status_na': 'N/A',
                'status_not_updated': 'Not updated',
                'status_healthy': 'healthy',
                'status_unhealthy': 'unhealthy',
                'status_banned_key': 'banned',

                # Add account
                'add_account_title': 'Manual Add Account',
                'add_account_instruction': 'Paste account JSON data below:',
                'add_account_placeholder': 'Paste JSON data here...',
                'how_to_get_json': '❓ How to get JSON data?',
                'how_to_get_json_close': '❌ Close',
                'json_info_title': 'How to get JSON data?',

                # Account dialog tabs
                'tab_manual': 'Manual',
                'manual_method_title': 'Manual JSON Addition',

                # JSON steps
                'step_1': '<b>Step 1:</b> Go to Warp site and log in',
                'step_2': '<b>Step 2:</b> Open browser developer console (F12)',
                'step_3': '<b>Step 3:</b> Go to Console tab',
                'step_4': '<b>Step 4:</b> Paste the JavaScript code below into console',
                'step_5': '<b>Step 5:</b> Press Enter',
                'step_6': '<b>Step 6:</b> Click the button that appears on the page',
                'step_7': '<b>Step 7:</b> Paste the copied JSON here',

                # Certificate installation
                'cert_title': '🔒 Proxy certificate installation required',
                'cert_explanation': '''For Warp Proxy to work properly, the mitmproxy certificate needs to be added to trusted root certificate authorities.

This procedure is performed only once and does not affect system security.''',
                'cert_steps': '📋 Installation steps:',
                'cert_step_1': '<b>Step 1:</b> Click "Open Certificate File" button below',
                'cert_step_2': '<b>Step 2:</b> Double-click the opened file',
                'cert_step_3': '<b>Step 3:</b> Click "Install Certificate..." button',
                'cert_step_4': '<b>Step 4:</b> Select "Local Machine" and click "Next"',
                'cert_step_5': '<b>Step 5:</b> Select "Place all certificates in the following store"',
                'cert_step_6': '<b>Step 6:</b> Click "Browse" button',
                'cert_step_7': '<b>Step 7:</b> Select "Trusted Root Certification Authorities" folder',
                'cert_step_8': '<b>Step 8:</b> Click "OK" and "Next" buttons',
                'cert_step_9': '<b>Step 9:</b> Click "Finish" button',
                'cert_path': 'Certificate file: {}',

                # Automatic certificate installation
                'cert_creating': '🔒 Creating certificate...',
                'cert_created_success': '✅ Certificate file created successfully',
                'cert_creation_failed': '❌ Failed to create certificate',
                'cert_installing': '🔒 Checking certificate installation...',
                'cert_installed_success': '✅ Certificate installed automatically',
                'cert_install_failed': '❌ Certificate installation failed - administrator rights may be required',
                'cert_install_error': '❌ Certificate installation error: {}',

                # Manual certificate installation dialog
                'cert_manual_title': '🔒 Manual certificate installation required',
                'cert_manual_explanation': '''Automatic certificate installation failed.

You need to install the certificate manually. This procedure is performed only once and does not affect system security.''',
                'cert_manual_path': 'Certificate file location:',
                'cert_manual_steps': '''<b>Manual installation steps:</b><br><br>
<b>1.</b> Go to the file path specified above<br>
<b>2.</b> Double-click the <code>mitmproxy-ca-cert.cer</code> file<br>
<b>3.</b> Click "Install Certificate..." button<br>
<b>4.</b> Select "Local Machine" and click "Next"<br>
<b>5.</b> Select "Place all certificates in the following store"<br>
<b>6.</b> Click "Browse" → Select "Trusted Root Certification Authorities"<br>
<b>7.</b> Click "OK" → "Next" → "Finish"''',
                'cert_open_folder': '📁 Open Certificate Folder',
                'cert_manual_complete': '✅ Installation Complete',

                # Messages
                'account_added_success': 'Account added successfully',
                'no_accounts_to_update': 'No accounts found to update',
                'updating_limits': 'Updating limits...',
                'processing_account': 'Processing: {}',
                'refreshing_token': 'Refreshing token: {}',
                'accounts_updated': 'Updated {} accounts',
                'proxy_starting': 'Starting proxy...',
                'proxy_configuring': 'Configuring Windows proxy...',
                'proxy_started': 'Proxy started: {}',
                'proxy_stopped': 'Proxy stopped',
                'proxy_starting_account': 'Starting proxy and activating {}...',
                'activating_account': 'Activating account: {}...',
                'token_refreshing': 'Refreshing token: {}',
                'proxy_started_account_activated': 'Proxy started and {} activated',
                'windows_proxy_config_failed': 'Failed to configure Windows proxy',
                'mitmproxy_start_failed': 'Failed to start Mitmproxy - check port 8080',
                'proxy_start_error': 'Proxy start error: {}',
                'proxy_stop_error': 'Proxy stop error: {}',
                'account_not_found': 'Account not found',
                'account_banned_cannot_activate': 'Account {} is banned - cannot activate',
                'account_activation_error': 'Activation error: {}',
                'token_refresh_in_progress': 'Token refresh in progress, please wait...',
                'token_refresh_error': 'Token refresh error: {}',
                'account_activated': 'Account {} activated',
                'account_activation_failed': 'Failed to activate account',
                'proxy_unexpected_stop': 'Proxy stopped unexpectedly',
                'account_deactivated': 'Account {} deactivated',
                'account_deleted': 'Account {} deleted',
                'token_renewed': 'Token {} renewed',
                'account_banned_detected': '⛔ Account {} banned!',
                'token_renewal_progress': '🔄 Updated {}/{} tokens',

                # Error messages
                'invalid_json': 'Invalid JSON format',
                'email_not_found': 'Email not found',
                'certificate_not_found': 'Certificate file not found!',
                'file_open_error': 'File open error: {}',
                'proxy_start_failed': 'Failed to start proxy - check port 8080',
                'proxy_config_failed': 'Failed to configure Windows proxy',
                'token_refresh_failed': 'Failed to refresh token {}',
                'account_delete_failed': 'Failed to delete account',
                'enable_proxy_first': 'Start proxy first to activate account',
                'limit_info_failed': 'Failed to get limit information',
                'token_renewal_failed': '⚠️ Failed to renew token {}',
                'token_check_error': '❌ Token check error',
                'proxy_connection_failed': 'Proxy connection failed. Please try a different proxy.',
                'proxy_auth_failed': 'Proxy authentication failed. Check proxy credentials.',
                'proxy_timeout': 'Proxy connection timeout. Try a different proxy.',

                # Confirmation messages
                'delete_account_confirm': 'Are you sure you want to delete account \'{}\' ?\\n\\nThis action cannot be undone!',

                # Status bar messages
                'default_status': 'Enable proxy and click start button on accounts to begin usage.',
                'default_status_debug': 'Enable proxy and click start button on accounts to begin usage. (Debug mode active)',

                # Debug and console messages
                'stylesheet_load_error': 'Failed to load stylesheet: {}',
                'health_update_error': 'Health update error: {}',
                'token_update_error': 'Token update error: {}',
                'account_update_error': 'Account update error: {}',
                'active_account_set_error': 'Active account set error: {}',
                'active_account_clear_error': 'Active account clear error: {}',
                'account_delete_error': 'Account delete error: {}',
                'limit_info_update_error': 'Limit info update error: {}',
            }
        }

        return translations

    def get_text(self, key, *args):
        """Get translation text"""
        try:
            text = self.translations[self.current_language].get(key, key)
            if args:
                return text.format(*args)
            return text
        except:
            return key

    def set_language(self, language_code):
        """Set language (always English)"""
        return True

    def get_current_language(self):
        """Return current language"""
        return 'en'

    def get_available_languages(self):
        """Return available languages"""
        return ['en']

# Global language manager instance
_language_manager = None

def get_language_manager():
    """Get global language manager"""
    global _language_manager
    if _language_manager is None:
        _language_manager = LanguageManager()
    return _language_manager

def _(key, *args):
    """Short translation function"""
    return get_language_manager().get_text(key, *args)
