#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simplified English-only language system
"""

class LanguageManager:
    """Multi-language manager with Chinese and English support"""

    def __init__(self):
        self.current_language = self.detect_system_language()
        self.translations = self.load_translations()

    def detect_system_language(self):
        """Detect system language, default to Chinese"""
        try:
            import locale
            system_lang = locale.getdefaultlocale()[0]
            if system_lang and 'zh' in system_lang.lower():
                return 'zh'
            return 'en'
        except:
            return 'zh'  # Default to Chinese

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
                'help_tooltip': 'Contact Us - Get help and support',
                
                # Contact Us dialog
                'contact_us_title': 'Contact Us',
                'contact_us_header': '📢 Connect with Us',
                'contact_description': 'Welcome to our community! Use the links below to get the latest updates, community support, and technical help.',
                'contact_channel_desc': '📢 <b>Channel:</b> Latest updates and releases',
                'contact_chat_desc': '💬 <b>Chat:</b> Community support and discussions',
                'contact_github_desc': '📁 <b>GitHub:</b> Source code and development',
                'contact_telegram_channel': '📢 Telegram Channel',
                'contact_telegram_chat': '💬 Telegram Chat',
                'contact_github_repo': '📁 GitHub Repository',
                'contact_close': '✖️ Close',
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
                'search_placeholder': '🔍 Search by email, ID, status (active/banned/expired)...',

                # Debug and console messages
                'stylesheet_load_error': 'Failed to load stylesheet: {}',
                'health_update_error': 'Health update error: {}',
                'token_update_error': 'Token update error: {}',
                'account_update_error': 'Account update error: {}',
                'active_account_set_error': 'Active account set error: {}',
                'active_account_clear_error': 'Active account clear error: {}',
                'account_delete_error': 'Account delete error: {}',
                'limit_info_update_error': 'Limit info update error: {}',
                
                # Batch operation buttons
                'delete_banned': '🗑️ Delete Banned',
                'refresh_tokens': '🔄 Refresh Tokens',
                
                # Action column
                'action': 'Action',
                'button_start': 'Start',
                'button_stop': 'Stop',
                
                # Error messages
                'no_healthy_accounts': '⚠️ No healthy accounts available for switching',
                'account_switching_failed': 'Account switching failed',
                
                # Confirmation dialogs
                'delete_banned_confirm': 'Are you sure you want to delete all banned accounts?\n\nThis action cannot be undone!',
                'refresh_tokens_confirm': 'Are you sure you want to refresh all expired tokens?',
                
                # Operation results
                'deleted_banned_accounts': 'Deleted {} banned accounts',
                'refreshed_tokens': 'Refreshed {} tokens',
                'no_banned_accounts': 'No banned accounts found',
                'no_expired_tokens': 'No expired tokens found',
                
                # Column headers
                'expires': 'Expires',
                
                # Sidebar translations
                'sidebar_subtitle': 'Account Management',
                'sidebar_navigation': 'NAVIGATION',
                'sidebar_dashboard': 'Dashboard',
                'sidebar_accounts': 'Account Management',
                'sidebar_cleanup': 'Cleanup Tools',
                'sidebar_about': 'About',
                'sidebar_status': '🟢 System Ready',
                'sidebar_version': 'Version 2.0.0',
                
                # About page translations
                'about_app_title': 'Warp Account Manager',
                'about_version': 'Version 2.0.0',
                'about_description': 'A powerful tool for managing Warp Terminal accounts with advanced features\nand modern user interface',
                'about_app_info_title': '📋 Application Information',
                'about_version_changelog_title': '📌 Version & Changelog',
                'about_version_changelog_content': '🔖 Current Version: v2.0.0\n📅 Release Date: 2025-01-19\n\n📋 Latest Changes:\n• Enhanced modern UI with glassmorphism effects\n• Improved sidebar navigation with animations\n• Added comprehensive error handling system\n• Implemented registry monitoring for auto-switching\n• Added multi-language support framework\n• Enhanced security with data encryption\n• Optimized performance and memory usage\n• Added automated testing framework\n\n🔗 Full changelog: https://github.com/hj01857655/WARP_reg_and_manager/releases',
                'about_features_title': '✨ Key Features',
                'about_features_content': '• Multi-account management with health monitoring\n• Automatic token refresh and account switching\n• Modern responsive user interface with animations\n• Real-time system status monitoring\n• Batch operations for account management\n• Multi-language support (English/中文)\n• Advanced mitmproxy integration\n• Registry monitoring and auto-switching\n• Secure local data encryption',
                'about_tech_title': '🛠️ Technology Stack',
                'about_core_tech_title': '🖥️ Core Technologies',
                'about_core_tech_content': '• Python {} - Main development language\n• PyQt5 5.15+ - Cross-platform GUI framework\n• SQLite 3.x - Embedded database system\n• asyncio - Asynchronous programming support',
                'about_github_btn': '📂 GitHub Repository',
                'about_telegram_channel_btn': '📱 Telegram Channel',
                'about_telegram_chat_btn': '💬 Telegram Chat',
                
                # About page - Additional sections
                'about_network_security_title': '🌐 Network & Security',
                'about_network_security_content': '• requests 2.25+ - HTTP library for API calls\n• urllib3 - HTTP client for Python\n• mitmproxy 8.0+ - HTTP/HTTPS proxy server\n• cryptography - Cryptographic recipes and primitives\n• SSL/TLS - Secure communication protocols',
                'about_system_integration_title': '⚙️ System Integration',
                'about_system_integration_content': '• psutil - System and process utilities\n• winreg - Windows registry access (Windows only)\n• pathlib - Object-oriented filesystem paths\n• threading - Thread-based parallelism\n• json - JSON encoder and decoder',
                'about_author_contact_title': '👤 Author & Contact',
                'about_dev_team_title': '🧑‍💻 Development Team',
                'about_dev_team_content': '• Lead Developer: Community Contributors\n• UI/UX Designer: Modern Interface Team\n• Security Consultant: Privacy Protection Team\n• Quality Assurance: Testing & Validation Team\n\n📧 Contact: github.com/hj01857655\n🌐 Project: WARP_reg_and_manager\n📚 Documentation: Integrated Help System',
                'about_system_info_title': '💻 System Information',
                'about_os_info_title': '🖥️ Operating System',
                'about_python_env_title': '🐍 Python Environment',
                'about_app_runtime_title': '🚀 Application Runtime',
                'about_credits_title': '👥 Credits & Acknowledgments',
                'about_dev_team_credits_title': 'Development Team',
                'about_dev_team_credits_content': '• Lead Developer: Community Contributors\n• UI/UX Design: Modern Dark Theme\n• Testing: Community Feedback\n• Documentation: Integrated Help System',
                'about_special_thanks_title': 'Special Thanks',
                'about_special_thanks_content': '• Cloudflare for the Warp service\n• PyQt5 community for the GUI framework\n• All users who provided feedback\n• Open source contributors',
                'about_links_contact_title': '🔗 Links & Contact',
                'about_license_title': '📏 License & Legal Information',
                'about_mit_license_title': '📜 Open Source License (MIT)',
                'about_mit_license_content': 'MIT License\n\nCopyright (c) 2025 Warp Account Manager Contributors\n\nPermission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.',
                'about_terms_disclaimer_title': '⚠️ Usage Terms & Disclaimer',
                'about_terms_disclaimer_content': '⚠️ Important Notice:\n\nThis software is provided "AS IS" without warranty of any kind.\n\n📝 Terms of Use:\n• Educational and personal use only\n• Users must comply with Warp Terminal\'s terms of service\n• Use responsibly and ethically\n• Comply with all applicable laws and regulations\n• Do not use for malicious purposes\n• Respect third-party service terms\n\n🚫 Disclaimer:\nThe developers are not responsible for any misuse, damage, or legal issues arising from the use of this software. Users assume full responsibility.',
                'about_third_party_title': '🙏 Third-party Acknowledgments',
                'about_third_party_content': '• Warp - For the Warp Terminal service and API\n• Qt Company - PyQt5 GUI framework\n• Python Software Foundation - Python language\n• mitmproxy contributors - Proxy server technology\n• Open source community - Various libraries and tools\n• All users and contributors - Feedback and improvements\n\nThis project is not affiliated with Warp or its parent company.',
                
                # HomePage Dashboard translations
                'home_welcome_title': '🚀 Welcome to Warp Manager',
                'home_welcome_subtitle': 'Manage your Warp Terminal accounts efficiently and monitor system status',
                'home_current_time': '🕰️ Current time: {}',
                'home_system_online': 'System\nOnline',
                'home_system_status': 'System Status',
                'home_live_indicator': '🟢 Live',
                
                # HomePage Statistics
                'home_account_statistics': 'Account Statistics',
                'home_metrics_count': '📈 6 Metrics',
                'home_total_accounts': 'Total Accounts',
                'home_total_accounts_desc': 'All registered accounts',
                'home_healthy_accounts': 'Healthy Accounts',
                'home_healthy_accounts_desc': 'Accounts ready to use',
                'home_banned_accounts': 'Banned Accounts',
                'home_banned_accounts_desc': 'Accounts that are banned',
                'home_proxy_status': 'Proxy Status',
                'home_proxy_status_desc': 'Current proxy state',
                'home_proxy_running': 'Running',
                'home_proxy_stopped': 'Stopped',
                'home_active_account': 'Active Account',
                'home_active_account_desc': 'Currently active account',
                'home_last_update': 'Last Update',
                'home_last_update_desc': 'Last statistics refresh',
                'home_none': 'None',
                'home_never': 'Never',
                
                # HomePage Quick Actions
                'home_quick_actions': 'Quick Actions',
                'home_actions_count': '3 Actions',
                'home_manage_accounts': 'Manage Accounts',
                'home_refresh_all': 'Refresh All',
                'home_add_account_btn': 'Add Account',
                
                # HomePage System Info
                'home_cpu_usage': 'CPU Usage',
                'home_cpu_usage_desc': 'Current processor utilization',
                'home_memory': 'Memory',
                'home_memory_desc': 'RAM usage percentage',
                'home_disk_space': 'Disk Space',
                'home_disk_space_desc': 'Storage space utilization',
                'home_uptime': 'Uptime',
                'home_uptime_desc': 'System running time',
                
                # Warp Client Status
                'warp_status': 'Warp Client Status',
                'warp_installation': 'Installation',
                'warp_data_status': 'Data Status', 
                'warp_database_size': 'Database Size',
                'warp_database_tables': 'DB Tables',
                'warp_user_file_size': 'User File Size',
                'warp_user_file_status': 'User File',
                'warp_last_modified': 'Last Modified',
                'warp_installed': 'Installed',
                'warp_not_installed': 'Not Installed',
                'warp_data_available': 'Available',
                'warp_data_unavailable': 'Unavailable',
                'warp_encrypted': 'Encrypted',
                'warp_readable': 'Readable',
                
                # Import/Export translations
                'import_export': '📤 Import/Export',
                'import_export_tooltip': 'Import or export accounts',
                'import_export_title': 'Import/Export Accounts',
                'export_tab': 'Export',
                'import_tab': 'Import',
                'export_options': 'Export Options',
                'export_all_accounts': 'Export all accounts',
                'export_healthy_only': 'Export healthy accounts only',
                'accounts_preview': 'Accounts Preview',
                'total_accounts_count': 'Total accounts: {}',
                'export_to_file': '📥 Export to File',
                'select_import_file': 'Select Import File',
                'no_file_selected': 'No file selected',
                'browse': 'Browse...',
                'import_options': 'Import Options',
                'skip_duplicate_accounts': 'Skip duplicate accounts',
                'validate_before_import': 'Validate file before import',
                'file_preview': 'File Preview',
                'import_accounts': '📤 Import Accounts',
                'exporting_account': 'Exporting',
                'importing_account': 'Importing',
                'export_success': 'Successfully exported {} accounts',
                'export_failed': 'Export failed',
                'import_complete': 'Import completed',
                'import_failed': 'Import failed',
                'import_results': 'Success: {}, Failed: {}',
                'skipping_duplicate': 'Skipping duplicate',
                'save_export_file': 'Save Export File',
                'select_json_file': 'Select JSON File',
                'warning': 'Warning',
                'error': 'Error',
                'success': 'Success',
                'no_accounts_to_export': 'No accounts to export',
                'please_select_file': 'Please select a file',
                'invalid_file_format': 'Invalid file format',
                'invalid_accounts_format': 'Invalid accounts format',
                'missing_required_fields': 'Missing required fields',
                'invalid_json_file': 'Invalid JSON file',
                'validation_error': 'Validation error',
                'export_date': 'Export date',
                'total_accounts': 'Total accounts',
                'accounts_list': 'Accounts list',
                'and_more': 'and {} more',
                'error_reading_file': 'Error reading file',
                'close': 'Close',
                'yes': 'Yes',
                'no': 'No',
                'ok': 'OK',
                'cancel': 'Cancel',
                'info': 'Information',
                'status_healthy': 'healthy',
                'status_unknown': 'unknown',
                
                # Cleanup Page
                'cleanup_title': 'System Cleanup Tools',
                'cleanup_description': 'Clean and optimize your system by resetting machine IDs and removing temporary files',
                'cleanup_tools_section': 'Maintenance Tools',
                'cleanup_reset_machine_id_button': 'Reset Machine ID',
                'cleanup_reset_machine_id_info': 'Reset the system machine identifier to resolve registration conflicts or hardware changes',
                'cleanup_one_click_button': 'One-Click Cleanup',
                'cleanup_one_click_info': 'Automatically clean cache, temporary files, and optimize database performance',
                'cleanup_log_section': 'Operation History',
                'cleanup_ready': 'System ready',
                'cleanup_confirm_title': 'Confirm Operation',
                'cleanup_confirm_reset_machine_id': 'Are you sure you want to reset the machine ID?\n\nThis will clear all system identifiers and may require re-registration.',
                'cleanup_confirm_one_click': 'Proceed with system cleanup?\n\nThis will remove temporary files and optimize the database.',
                'cleanup_already_running': 'A cleanup operation is already in progress',
                'cleanup_started': 'Started cleanup operation',
                'cleanup_resetting_machine_id': 'Resetting machine ID...',
                'cleanup_clearing_registry': 'Clearing registry entries...',
                'cleanup_finalizing': 'Finalizing changes...',
                'cleanup_machine_id_reset_success': 'Machine ID has been successfully reset',
                'cleanup_scanning_system': 'Scanning system...',
                'cleanup_clearing_cache': 'Clearing cache files...',
                'cleanup_removing_temp_files': 'Removing temporary files...',
                'cleanup_optimizing_database': 'Optimizing database...',
                'cleanup_one_click_success': 'System cleanup completed successfully',
            },
            'zh': {
                # Contact Us dialog (Chinese)
                'contact_us_title': '联系我们',
                'contact_us_header': '📢 与我们联系',
                'contact_description': '欢迎加入我们的社区！下面的链接可以帮助您获取最新更新、社区支持和技术帮助。',
                'contact_channel_desc': '📢 <b>频道:</b> 最新更新和发布',
                'contact_chat_desc': '💬 <b>聊天:</b> 社区支持和讨论',
                'contact_github_desc': '📁 <b>GitHub:</b> 源代码和开发',
                'contact_telegram_channel': '📢 Telegram 频道',
                'contact_telegram_chat': '💬 Telegram 聊天',
                'contact_github_repo': '📁 GitHub 仓库',
                'contact_close': '✖️ 关闭',
                
                # Basic UI translations
                'help': '帮助',
                'help_tooltip': '联系我们 - 获取帮助和支持',
                'app_title': 'Warp 账号管理器',
                'proxy_start': '启动代理',
                'proxy_stop': '停止代理',
                'proxy_active': '代理活跃',
                'add_account': '手动添加账号',
                'auto_add_account': '自动添加账号',
                'refresh_limits': '刷新限制',
                'email': '邮箱',
                'status': '状态',
                'limit': '用量',
                'created': '创建时间',
                'default_status': '启用代理并点击账号的开始按钮来开始使用。',
                'default_status_debug': '启用代理并点击账号的开始按钮来开始使用。（调试模式已激活）',
                'search_placeholder': '🔍 按邮箱、ID、状态（活跃/封禁/过期）搜索...',
                
                # 批量操作按钮
                'delete_banned': '🗑️ 删除封禁账号',
                'refresh_tokens': '🔄 刷新令牌',
                
                # 操作按钮
                'action': '操作',
                'button_start': '开始',
                'button_stop': '停止',
                
                # 状态翻译
                'status_active': '活跃',
                'status_banned': '封禁',
                'status_token_expired': '令牌过期',
                'status_na': '无',
                
                # 错误信息
                'no_healthy_accounts': '⚠️ 没有可用的健康账户可以切换',
                'account_switching_failed': '账户切换失败',
                
                # 确认对话框
                'delete_banned_confirm': '确定要删除所有封禁的账号吗？\n\n此操作无法撤销！',
                'refresh_tokens_confirm': '确定要刷新所有过期的令牌吗？',
                
                # 操作结果
                'deleted_banned_accounts': '已删除 {} 个封禁账号',
                'refreshed_tokens': '已刷新 {} 个令牌',
                'no_banned_accounts': '没有找到封禁的账号',
                'no_expired_tokens': '没有找到过期的令牌',
                
                # 列标题
                'expires': '账号过期',
                
                # 侧边栏翻译
                'sidebar_subtitle': '账号管理',
                'sidebar_navigation': '导航',
                'sidebar_dashboard': '仪表板',
                'sidebar_accounts': '账号管理',
                'sidebar_cleanup': '清理工具',
                'sidebar_about': '关于',
                'sidebar_status': '🟢 系统就绪',
                'sidebar_version': '版本 2.0.0',
                
                # 关于页面翻译
                'about_app_title': 'Warp 账号管理器',
                'about_version': '版本 2.0.0',
                'about_description': '一个用于管理 Warp Terminal 账户的强大工具\n具有先进功能和现代用户界面',
                'about_app_info_title': '📋 应用程序信息',
                'about_version_changelog_title': '📌 版本及更新日志',
                'about_version_changelog_content': '🔖 当前版本: v2.0.0\n📅 发布日期: 2025-01-19\n\n📋 最新更改:\n• 增强的现代 UI 和毛玻璃效果\n• 改进的侧边栏导航和动画\n• 添加综合错误处理系统\n• 实现注册表监控和自动切换\n• 添加多语言支持框架\n• 增强数据加密安全性\n• 优化性能和内存使用\n• 添加自动化测试框架\n\n🔗 完整更新日志: https://github.com/hj01857655/WARP_reg_and_manager/releases',
                'about_features_title': '✨ 主要功能',
                'about_features_content': '• 带有健康监控的多账户管理\n• 自动令牌刷新和账户切换\n• 现代响应式用户界面和动画\n• 实时系统状态监控\n• 账户管理批量操作\n• 多语言支持（英文/中文）\n• 高级 mitmproxy 集成\n• 注册表监控和自动切换\n• 安全的本地数据加密',
                'about_tech_title': '🛠️ 技术栈',
                'about_core_tech_title': '🖥️ 核心技术',
                'about_core_tech_content': '• Python {} - 主要开发语言\n• PyQt5 5.15+ - 跨平台 GUI 框架\n• SQLite 3.x - 嵌入式数据库系统\n• asyncio - 异步编程支持',
                'about_github_btn': '📂 GitHub 仓库',
                'about_telegram_channel_btn': '📱 Telegram 频道',
                'about_telegram_chat_btn': '💬 Telegram 聊天',
                
                # 关于页面 - 额外部分
                'about_network_security_title': '🌐 网络与安全',
                'about_network_security_content': '• requests 2.25+ - API 调用 HTTP 库\n• urllib3 - Python HTTP 客户端\n• mitmproxy 8.0+ - HTTP/HTTPS 代理服务器\n• cryptography - 加密算法和原语\n• SSL/TLS - 安全通信协议',
                'about_system_integration_title': '⚙️ 系统集成',
                'about_system_integration_content': '• psutil - 系统和进程工具\n• winreg - Windows 注册表访问（仅 Windows）\n• pathlib - 面向对象的文件系统路径\n• threading - 基于线程的并行\n• json - JSON 编解码器',
                'about_author_contact_title': '👤 作者与联系方式',
                'about_dev_team_title': '🧑‍💻 开发团队',
                'about_dev_team_content': '• 主开发者：社区贡献者\n• UI/UX 设计：现代界面团队\n• 安全顾问：隐私保护团队\n• 质量保证：测试验证团队\n\n📧 联系：github.com/hj01857655\n🌐 项目：WARP_reg_and_manager\n📚 文档：集成帮助系统',
                'about_system_info_title': '💻 系统信息',
                'about_os_info_title': '🖥️ 操作系统',
                'about_python_env_title': '🐍 Python 环境',
                'about_app_runtime_title': '🚀 应用运行时',
                'about_credits_title': '👥 致谢与鸣谢',
                'about_dev_team_credits_title': '开发团队',
                'about_dev_team_credits_content': '• 主开发者：社区贡献者\n• UI/UX 设计：现代暗黑主题\n• 测试：社区反馈\n• 文档：集成帮助系统',
                'about_special_thanks_title': '特别感谢',
                'about_special_thanks_content': '• Warp 提供 Warp Terminal 服务\n• PyQt5 社区提供 GUI 框架\n• 所有提供反馈的用户\n• 开源贡献者',
                'about_links_contact_title': '🔗 链接与联系',
                'about_license_title': '📏 许可证与法律信息',
                'about_mit_license_title': '📜 开源许可证 (MIT)',
                'about_mit_license_content': 'MIT 许可证\n\n版权所有 (c) 2025 Warp 账号管理器贡献者\n\n特此允许任何人免费获取本软件及相关文档文件（"软件"）的副本，并无限制地处理本软件，包括但不限于使用、复制、修改、合并、发布、分发、再许可和/或出售本软件的权利，以及允许提供本软件的人员这样做，但需满足以下条件：\n\n上述版权声明和本许可声明应包含在本软件的所有副本或重要部分中。',
                'about_terms_disclaimer_title': '⚠️ 使用条款与免责声明',
                'about_terms_disclaimer_content': '⚠️ 重要通知：\n\n本软件按"原样"提供，不提供任何形式的担保。\n\n📝 使用条款：\n• 仅供教育和个人使用\n• 用户必须遵守 Warp Terminal 的服务条款\n• 负责任地、道德地使用\n• 遵守所有适用的法律法规\n• 不得用于恶意目的\n• 尊重第三方服务条款\n\n🚫 免责声明：\n开发者对因使用本软件而产生的任何误用、损害或法律问题不承担责任。用户承担全部责任。',
                'about_third_party_title': '🙏 第三方致谢',
                'about_third_party_content': '• Warp - 提供 Warp Terminal 服务和 API\n• Qt 公司 - PyQt5 GUI 框架\n• Python 软件基金会 - Python 语言\n• mitmproxy 贡献者 - 代理服务器技术\n• 开源社区 - 各种库和工具\n• 所有用户和贡献者 - 反馈和改进\n\n本项目与 Warp 及其母公司无关。',
                
                # HomePage 仪表盘翻译
                'home_welcome_title': '🚀 欢迎使用 Warp 管理器',
                'home_welcome_subtitle': '高效管理您的 Warp Terminal 账户并监控系统状态',
                'home_current_time': '🕰️ 当前时间：{}',
                'home_system_online': '系统\n在线',
                'home_system_status': '系统状态',
                'home_live_indicator': '🟢 实时',
                
                # HomePage 统计信息
                'home_account_statistics': '账户统计',
                'home_metrics_count': '📈 6 项指标',
                'home_total_accounts': '账户总数',
                'home_total_accounts_desc': '所有已注册的账户',
                'home_healthy_accounts': '健康账户',
                'home_healthy_accounts_desc': '可以使用的账户',
                'home_banned_accounts': '封禁账户',
                'home_banned_accounts_desc': '已被封禁的账户',
                'home_proxy_status': '代理状态',
                'home_proxy_status_desc': '当前代理服务状态',
                'home_proxy_running': '运行中',
                'home_proxy_stopped': '已停止',
                'home_active_account': '活跃账户',
                'home_active_account_desc': '当前激活的账户',
                'home_last_update': '最后更新',
                'home_last_update_desc': '统计信息最后刷新时间',
                'home_none': '无',
                'home_never': '从未',
                
                # HomePage 快捷操作
                'home_quick_actions': '快捷操作',
                'home_actions_count': '3 项操作',
                'home_manage_accounts': '管理账户',
                'home_refresh_all': '全部刷新',
                'home_add_account_btn': '添加账户',
                
                # HomePage 系统信息
                'home_cpu_usage': 'CPU 使用率',
                'home_cpu_usage_desc': '当前处理器利用率',
                'home_memory': '内存',
                'home_memory_desc': '内存使用百分比',
                'home_disk_space': '磁盘空间',
                'home_disk_space_desc': '存储空间利用率',
                'home_uptime': '运行时间',
                'home_uptime_desc': '系统运行时间',
                
                # Warp 客户端状态
                'warp_status': 'Warp 客户端状态',
                'warp_installation': '安装状态',
                'warp_data_status': '数据状态', 
                'warp_database_size': '数据库大小',
                'warp_database_tables': '数据表数',
                'warp_user_file_size': '用户文件大小',
                'warp_user_file_status': '用户文件状态',
                'warp_last_modified': '最后修改',
                'warp_installed': '已安装',
                'warp_not_installed': '未安装',
                'warp_data_available': '数据可用',
                'warp_data_unavailable': '数据不可用',
                'warp_encrypted': '已加密',
                'warp_readable': '可读取',
                
                # 导入/导出翻译
                'import_export': '📤 导入/导出',
                'import_export_tooltip': '导入或导出账号',
                'import_export_title': '导入/导出账号',
                'export_tab': '导出',
                'import_tab': '导入',
                'export_options': '导出选项',
                'export_all_accounts': '导出所有账号',
                'export_healthy_only': '仅导出健康账号',
                'accounts_preview': '账号预览',
                'total_accounts_count': '账号总数：{}',
                'export_to_file': '📥 导出到文件',
                'select_import_file': '选择导入文件',
                'no_file_selected': '未选择文件',
                'browse': '浏览...',
                'import_options': '导入选项',
                'skip_duplicate_accounts': '跳过重复账号',
                'validate_before_import': '导入前验证文件',
                'file_preview': '文件预览',
                'import_accounts': '📤 导入账号',
                'exporting_account': '正在导出',
                'importing_account': '正在导入',
                'export_success': '成功导出 {} 个账号',
                'export_failed': '导出失败',
                'import_complete': '导入完成',
                'import_failed': '导入失败',
                'import_results': '成功：{}，失败：{}',
                'skipping_duplicate': '跳过重复',
                'save_export_file': '保存导出文件',
                'select_json_file': '选择JSON文件',
                'warning': '警告',
                'error': '错误',
                'success': '成功',
                'no_accounts_to_export': '没有可导出的账号',
                'please_select_file': '请选择一个文件',
                'invalid_file_format': '无效的文件格式',
                'invalid_accounts_format': '无效的账号格式',
                'missing_required_fields': '缺少必填字段',
                'invalid_json_file': '无效的 JSON 文件',
                'validation_error': '验证错误',
                'export_date': '导出日期',
                'total_accounts': '账号总数',
                'accounts_list': '账号列表',
                'and_more': '及 {} 更多',
                'error_reading_file': '读取文件错误',
                'close': '关闭',
                'yes': '是',
                'no': '否',
                'ok': '确定',
                'cancel': '取消',
                'info': '信息',
                'status_healthy': '健康',
                'status_unknown': '未知',
                
                # 清理工具页面
                'cleanup_title': '系统清理工具',
                'cleanup_description': '通过重置机器码和清除临时文件来清理和优化您的系统',
                'cleanup_tools_section': '维护工具',
                'cleanup_reset_machine_id_button': '重置机器码',
                'cleanup_reset_machine_id_info': '重置系统机器标识符以解决注册冲突或硬件更改问题',
                'cleanup_one_click_button': '一键清理',
                'cleanup_one_click_info': '自动清理缓存、临时文件并优化数据库性能',
                'cleanup_log_section': '操作历史',
                'cleanup_ready': '系统就绪',
                'cleanup_confirm_title': '确认操作',
                'cleanup_confirm_reset_machine_id': '您确定要重置机器码吗？\n\n这将清除所有系统标识符，可能需要重新注册。',
                'cleanup_confirm_one_click': '是否继续系统清理？\n\n这将删除临时文件并优化数据库。',
                'cleanup_already_running': '清理操作正在进行中',
                'cleanup_started': '开始清理操作',
                'cleanup_resetting_machine_id': '正在重置机器码...',
                'cleanup_clearing_registry': '正在清除注册表项...',
                'cleanup_finalizing': '正在完成更改...',
                'cleanup_machine_id_reset_success': '机器码已成功重置',
                'cleanup_scanning_system': '正在扫描系统...',
                'cleanup_clearing_cache': '正在清理缓存文件...',
                'cleanup_removing_temp_files': '正在删除临时文件...',
                'cleanup_optimizing_database': '正在优化数据库...',
                'cleanup_one_click_success': '系统清理已成功完成',
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
        """Set language"""
        if language_code in self.translations:
            self.current_language = language_code
            return True
        return False

    def get_current_language(self):
        """Return current language"""
        return self.current_language

    def get_available_languages(self):
        """Return available languages"""
        return ['en', 'zh']

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
