#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
import requests
import time
import subprocess
import os
import psutil
import urllib3
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional
from src.config.languages import get_language_manager, _
from src.managers.database_manager import DatabaseManager
from src.managers.warp_registry_manager import warp_registry_manager

# OS-specific proxy managers
from src.proxy.proxy_windows import WindowsProxyManager
from src.proxy.proxy_macos import MacOSProxyManager
from src.proxy.proxy_linux import LinuxProxyManager

# Modular components
from src.managers.certificate_manager import CertificateManager, ManualCertificateDialog
from src.workers.background_workers import TokenWorker, TokenRefreshWorker, AccountCreationWorker
from src.managers.mitmproxy_manager import MitmProxyManager
from src.ui.ui_dialogs import AddAccountDialog
from src.utils.utils import load_stylesheet, get_os_info, is_port_open
from src.utils.account_processor import AccountProcessor

# Platform-specific proxy imports
if sys.platform == "win32":
    from src.proxy.proxy_windows import WindowsProxyManager
elif sys.platform == "darwin":
    from src.proxy.proxy_macos import MacOSProxyManager
else:
    from src.proxy.proxy_linux import LinuxProxyManager

# Disable SSL warnings (when using mitmproxy)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# SSL handling - keep verification enabled for security but add certificates if needed
import ssl
import urllib3
# Only disable SSL warnings for mitmproxy connections, not global SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
                             QDialog, QTextEdit, QDialogButtonBox, QStatusBar,
                             QHeaderView, QProgressDialog, QMenu, QAction,
                             QAbstractItemView, QDesktopWidget, QLabel, QLineEdit,
                             QComboBox, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt5.QtGui import QFont


# Proxy start worker thread
class ProxyStartWorker(QThread):
    """Worker thread for starting proxy to avoid UI blocking"""
    proxy_started = pyqtSignal(bool, str)  # success, message/proxy_url
    
    def __init__(self, proxy_manager, parent_window=None):
        super().__init__()
        self.proxy_manager = proxy_manager
        self.parent_window = parent_window
    
    def run(self):
        try:
            success = self.proxy_manager.start(parent_window=self.parent_window)
            if success:
                proxy_url = self.proxy_manager.get_proxy_url()
                self.proxy_started.emit(True, proxy_url)
            else:
                self.proxy_started.emit(False, "Failed to start mitmproxy")
        except (ConnectionError, TimeoutError) as e:
            print(f"Network error starting proxy: {e}")
            self.proxy_started.emit(False, f"Network error: {str(e)}")
        except Exception as e:
            print(f"Unexpected error starting proxy: {e}")
            self.proxy_started.emit(False, f"Unexpected error: {str(e)}")


# Proxy configuration worker thread
class ProxyConfigWorker(QThread):
    """Worker thread for configuring proxy settings to avoid UI blocking"""
    config_completed = pyqtSignal(bool)  # success
    
    def __init__(self, proxy_url):
        super().__init__()
        self.proxy_url = proxy_url
    
    def run(self):
        try:
            success = ProxyManager.set_proxy(self.proxy_url)
            self.config_completed.emit(success)
        except Exception as e:
            print(f"Proxy config error: {e}")
            self.config_completed.emit(False)


# Active account refresh worker thread
class ActiveAccountRefreshWorker(QThread):
    """Worker thread for refreshing active account to avoid UI blocking"""
    refresh_completed = pyqtSignal(bool, str)  # success, email
    auto_switch_to_next_account = pyqtSignal(str)  # email that needs switching
    
    def __init__(self, email, account_data, account_manager):
        super().__init__()
        self.email = email
        self.account_data = account_data
        self.account_manager = account_manager
    
    def run(self):
        try:
            # Refresh token
            success = self._renew_single_token(self.email, self.account_data)
            if success:
                # Update limit information as well
                self._update_active_account_limit(self.email)
            
            self.refresh_completed.emit(success, self.email)
        except Exception as e:
            print(f"Active account refresh error ({self.email}): {e}")
            self.refresh_completed.emit(False, self.email)
    
    def _renew_single_token(self, email, account_data):
        """Refresh token for one account"""
        try:
            import requests
            import time
            
            refresh_token = account_data['stsTokenManager']['refreshToken']
            api_key = account_data['apiKey']

            url = f"https://securetoken.googleapis.com/v1/token?key={api_key}"
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'WarpAccountManager/1.0'
            }
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token
            }

            # Skip SSL verification directly
            response = requests.post(url, json=data, headers=headers, timeout=10, verify=False)
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
            print(f"Token update error: {e}")
            return False
    
    def _update_active_account_limit(self, email):
        """Update active account limit information"""
        try:
            # Define check parameters
            check_interval = 19  # Check interval in seconds
            estimated_consumption = 15  # Estimated consumption in next interval
            
            # Get account information again with health status
            accounts_with_health = self.account_manager.get_accounts_with_health()
            health_status = 'healthy'  # Default status
            
            for acc_email, acc_json, acc_health in accounts_with_health:
                if acc_email == email:
                    account_data = json.loads(acc_json)
                    health_status = acc_health

                    # Get limit information
                    limit_info = self._get_account_limit_info(account_data)
                    if limit_info and isinstance(limit_info, dict):
                        used = limit_info.get('requestsUsedSinceLastRefresh', 0)
                        total = limit_info.get('requestLimit', 0)
                        limit_text = f"{used}/{total}"

                        self.account_manager.update_account_limit_info(email, limit_text)
                        print(f"✅ Active account limit updated: {email} - {limit_text}")
                        
                        # Check if account has reached limit and auto-switch
                        remaining = total - used if total > 0 else float('inf')
                        
                        # 根据不同情况判断是否需要切换
                        should_switch = False
                        switch_reason = ""
                        
                        # 检查是否为被封禁账号（通过健康状态判断）
                        is_banned = (health_status == 'banned')
                        
                        if remaining == 0 and total > 0:
                            should_switch = True
                            if is_banned:
                                switch_reason = "banned_and_exhausted"
                                print(f"🔴 Account {email} is banned and has 0 remaining quota ({used}/{total}) - will switch and delete")
                            else:
                                switch_reason = "exhausted_only"
                                print(f"⚪ Account {email} has 0 remaining quota ({used}/{total}) - will switch but keep account for reset")
                        elif is_banned:
                            should_switch = True
                            switch_reason = "banned_only"
                            print(f"🚫 Account {email} is banned ({used}/{total}) - will switch and delete")
                        elif remaining > 0 and remaining <= 10:
                            # 余量少于10个时提醒但不切换
                            print(f"⚠️ Account {email} has only {remaining} requests left ({used}/{total})")
                        else:
                            print(f"✅ Account {email} has {remaining} requests remaining ({used}/{total})")
                        
                        print(f"🔍 Checking limit: used={used}, total={total}, remaining={remaining}, estimated_consumption={estimated_consumption}, should_switch={should_switch}, reason={switch_reason}")
                        
                        if should_switch:
                            print(f"📢 Emitting auto-switch signal for: {email} (reason: {switch_reason})")
                            # Trigger auto-switch to next healthy account with reason
                            self.auto_switch_to_next_account.emit(f"{email}|{switch_reason}")
                        else:
                            print(f"📊 Account {email} has {remaining} requests remaining (sufficient for next {check_interval}s)")
                    else:
                        print(f"❌ Failed to get limit info: {email}")
                    break
        except Exception as e:
            print(f"Limit update error: {e}")
    
    def _get_account_limit_info(self, account_data):
        """Get account limit information from Warp API"""
        try:
            import requests
            
            # Get dynamic OS information
            os_info = get_os_info()
            
            access_token = account_data['stsTokenManager']['accessToken']

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
                'x-warp-manager-request': 'true'
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

            # Direct connection - skip SSL verification
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
            print(f"Limit information retrieval error: {e}")
            return None


def get_os_info():
    """Get operating system information for API headers"""
    return ProxyManager.get_os_info()



class ProxyManager:
    """Cross-platform proxy settings manager using OS-specific modules"""

    @staticmethod
    def set_proxy(proxy_server):
        """Enable proxy settings using OS-specific manager"""
        if sys.platform == "win32":
            return WindowsProxyManager.set_proxy(proxy_server)
        elif sys.platform == "darwin":
            return MacOSProxyManager.set_proxy(proxy_server)
        else:
            # Linux
            return LinuxProxyManager.set_proxy(proxy_server)

    @staticmethod
    def disable_proxy():
        """Disable proxy settings using OS-specific manager"""
        if sys.platform == "win32":
            return WindowsProxyManager.disable_proxy()
        elif sys.platform == "darwin":
            return MacOSProxyManager.disable_proxy()
        else:
            # Linux
            return LinuxProxyManager.disable_proxy()

    @staticmethod
    def is_proxy_enabled():
        """Check if proxy is enabled using OS-specific manager"""
        if sys.platform == "win32":
            return WindowsProxyManager.is_proxy_enabled()
        elif sys.platform == "darwin":
            return MacOSProxyManager.is_proxy_enabled()
        else:
            # Linux
            return LinuxProxyManager.is_proxy_enabled()

    @staticmethod
    def get_os_info():
        """Get OS information using OS-specific manager"""
        if sys.platform == "win32":
            return WindowsProxyManager.get_os_info()
        elif sys.platform == "darwin":
            return MacOSProxyManager.get_os_info()
        else:
            # Linux
            return LinuxProxyManager.get_os_info()


# Backward compatibility alias
ProxyManager = ProxyManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.account_manager = DatabaseManager()
        self.proxy_manager = MitmProxyManager()
        self.proxy_enabled = False
        
        # Initialize registry manager (only on Windows)
        if sys.platform == "win32":
            self.registry_manager = warp_registry_manager
            # Start registry monitoring
            self.registry_manager.start_monitoring()
        else:
            self.registry_manager = None

        # 检查程序是否被异常关闭（如果有活跃账号但代理未运行）
        self._check_and_cleanup_startup_state()

        self.init_ui()
        self.load_accounts()

        # Timer for checking proxy status
        self.proxy_timer = QTimer()
        self.proxy_timer.timeout.connect(self.check_proxy_status)
        self.proxy_timer.start(5000)  # Check every 5 seconds

        # Timer for checking ban notifications (reduced frequency)
        self.ban_timer = QTimer()
        self.ban_timer.timeout.connect(self.check_ban_notifications)
        self.ban_timer.start(5000)  # Check every 5 seconds (reduced from 1s)

        # Timer for automatic token renewal
        self.token_renewal_timer = QTimer()
        self.token_renewal_timer.timeout.connect(self.auto_renew_tokens)
        self.token_renewal_timer.start(60000)  # Check every 1 minute (60000 ms)

        # Timer for active account refresh (optimized frequency)
        self.active_account_refresh_timer = QTimer()
        self.active_account_refresh_timer.timeout.connect(self.refresh_active_account)
        self.active_account_refresh_timer.start(30000)  # Refresh active account every 30 seconds (increased from 20s)

        # Timer for status message reset
        self.status_reset_timer = QTimer()
        self.status_reset_timer.setSingleShot(True)
        self.status_reset_timer.timeout.connect(self.reset_status_message)

        # Run token check immediately on first startup
        QTimer.singleShot(0, self.auto_renew_tokens)

        # Variables for token worker
        self.token_worker = None
        self.token_progress_dialog = None
        
        # Performance optimization: cache frequently accessed data
        self._accounts_cache = None
        self._cache_timestamp = 0
        self._cache_ttl = 10  # Cache valid for 10 seconds
        
        # UI update throttling
        self._ui_update_timer = QTimer()
        self._ui_update_timer.setSingleShot(True)
        self._ui_update_timer.timeout.connect(self._perform_ui_update)
        self._pending_ui_update = False
        
        # Initialize resource monitoring
        self._init_resource_monitoring()

    def _check_and_cleanup_startup_state(self):
        """检查并清理启动时的状态不一致问题"""
        try:
            # 检查是否有活跃账号
            active_account = self.account_manager.get_active_account()
            
            if active_account:
                # 有活跃账号，检查mitmproxy和系统代理状态
                mitmproxy_running = self.proxy_manager.is_running()
                system_proxy_enabled = ProxyManager.is_proxy_enabled()
                
                # 如果活跃账号存在但代理服务都未运行，说明程序被异常关闭
                if not mitmproxy_running and not system_proxy_enabled:
                    print("⚠️ 检测到程序可能被异常关闭，清理活跃账号状态...")
                    self.account_manager.clear_active_account()
                elif not mitmproxy_running and system_proxy_enabled:
                    # 系统代理启用但mitmproxy未运行，关闭系统代理
                    print("⚠️ 检测到系统代理启用但mitmproxy未运行，关闭系统代理...")
                    ProxyManager.disable_proxy()
                    self.account_manager.clear_active_account()
                else:
                    # 状态正常或部分正常，保持原状
                    print(f"✅ 活跃账号: {active_account}, mitmproxy: {mitmproxy_running}, 系统代理: {system_proxy_enabled}")
            else:
                # 没有活跃账号，检查是否有孤儿的系统代理设置
                if ProxyManager.is_proxy_enabled():
                    print("⚠️ 没有活跃账号但系统代理启用，关闭系统代理...")
                    ProxyManager.disable_proxy()
                    
        except Exception as e:
            print(f"启动状态检查失败: {e}")
    
    def _get_cached_accounts(self, force_refresh=False):
        """Get accounts with caching to reduce database queries"""
        import time
        current_time = time.time()
        
        # Check if cache is valid
        if (not force_refresh and 
            self._accounts_cache is not None and 
            (current_time - self._cache_timestamp) < self._cache_ttl):
            return self._accounts_cache
        
        # Refresh cache
        self._accounts_cache = self.account_manager.get_accounts_with_health_and_limits()
        self._cache_timestamp = current_time
        return self._accounts_cache
    
    def _invalidate_accounts_cache(self):
        """Invalidate accounts cache when data changes"""
        self._accounts_cache = None
        self._cache_timestamp = 0
    
    def _schedule_ui_update(self, delay_ms=500):
        """Schedule a throttled UI update to avoid frequent refreshes"""
        if not self._pending_ui_update:
            self._pending_ui_update = True
            self._ui_update_timer.start(delay_ms)
    
    def _perform_ui_update(self):
        """Perform the actual UI update"""
        self._pending_ui_update = False
        self.load_accounts(preserve_limits=True)
    
    def _init_resource_monitoring(self):
        """Initialize resource monitoring with appropriate settings"""
        try:
            from src.utils.resource_monitor import start_resource_monitoring, get_resource_monitor
            # Start resource monitoring with 2-minute intervals
            start_resource_monitoring(check_interval_ms=120000)
            
            # Connect to resource monitor signals for debugging/logging
            resource_monitor = get_resource_monitor()
            resource_monitor.memory_warning.connect(self._on_memory_warning)
            resource_monitor.cleanup_completed.connect(self._on_cleanup_completed)
            
            print("✅ Resource monitoring initialized")
        except ImportError:
            print("⚠️ Resource monitoring not available (missing psutil dependency)")
        except Exception as e:
            print(f"⚠️ Failed to initialize resource monitoring: {e}")
    
    def _on_memory_warning(self, percentage):
        """Handle memory warning from resource monitor"""
        print(f"⚠️ High memory usage detected: {percentage:.1f}%")
        # Show a brief status message about high memory usage
        self.show_status_message(f"⚠️ High memory usage: {percentage:.1f}%", 3000)
    
    def _on_cleanup_completed(self, collected_objects):
        """Handle cleanup completion from resource monitor"""
        if collected_objects > 0:
            print(f"✅ Resource cleanup completed, collected {collected_objects} objects")
            # Optionally show status message for significant cleanups
            if collected_objects > 100:
                self.show_status_message(f"🔄 Memory cleanup: {collected_objects} objects freed", 2000)

    def closeEvent(self, event):
        """程序关闭时的清理工作"""
        try:
            print("🔄 程序关闭，正在清理资源...")
            
            # Stop resource monitoring and perform final cleanup
            try:
                from src.utils.resource_monitor import stop_resource_monitoring, force_resource_cleanup
                print("🔄 Stopping resource monitoring...")
                stop_resource_monitoring()
                # Force final cleanup
                collected = force_resource_cleanup()
                if collected > 0:
                    print(f"✅ Final cleanup collected {collected} objects")
            except ImportError:
                pass
            except Exception as e:
                print(f"⚠️ Error during resource cleanup: {e}")
            
            # 停止所有定时器
            if hasattr(self, 'proxy_timer'):
                self.proxy_timer.stop()
            if hasattr(self, 'ban_timer'):
                self.ban_timer.stop()
            if hasattr(self, 'token_renewal_timer'):
                self.token_renewal_timer.stop()
            if hasattr(self, 'active_account_refresh_timer'):
                self.active_account_refresh_timer.stop()
                
            # 停止注册表监控
            if hasattr(self, 'registry_manager') and self.registry_manager:
                self.registry_manager.stop_monitoring()
            
            # 如果代理启用，停止代理服务（保留活跃账号信息）
            if self.proxy_enabled:
                print("🛑 停止代理服务...")
                self.stop_proxy(clear_active_account=False)
                
            print("✅ 资源清理完成")
            
        except Exception as e:
            print(f"清理资源时发生错误: {e}")
        
        # 接受关闭事件
        event.accept()

    def init_ui(self):
        self.setWindowTitle(_('app_title'))
        self.setFixedSize(1100, 700)  # Even wider window for better visibility

        # Add status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Add GitHub link to right corner
        self.ruwis_label = QLabel('<a href="https://github.com/hj01857655/WARP_reg_and_manager" style="color: #89b4fa; text-decoration: none; font-weight: bold;">https://github.com/hj01857655/WARP_reg_and_manager</a>')
        self.ruwis_label.setOpenExternalLinks(True)
        self.ruwis_label.setStyleSheet("QLabel { padding: 2px 8px; }")
        self.status_bar.addPermanentWidget(self.ruwis_label)

        # Default status message
        debug_mode = os.path.exists("debug.txt")
        if debug_mode:
            self.status_bar.showMessage(_('default_status_debug'))
        else:
            self.status_bar.showMessage(_('default_status'))

        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout - Modern spacing with optimized margins
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 16, 20, 16)  # Wider horizontal margins
        layout.setSpacing(14)  # Better spacing between elements

        # Search and Language Bar
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 10)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(_('search_placeholder'))
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #2a2b37;
                color: #e0e0e0;
                border: 1px solid #3a3b47;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #5a6090;
            }
        """)
        self.search_input.textChanged.connect(self.load_accounts)
        search_layout.addWidget(self.search_input, 3)
        
        # 语言选择下拉框
        self.language_combo = QComboBox()
        self.language_combo.addItems(["🇺🇸 English", "🇨🇳 中文"])
        self.language_combo.setStyleSheet("""
            QComboBox {
                background-color: #2a2b37;
                color: #e0e0e0;
                border: 1px solid #3a3b47;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
                min-width: 120px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #e0e0e0;
                width: 0;
                height: 0;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #2a2b37;
                color: #e0e0e0;
                selection-background-color: #3d415a;
                border: 1px solid #3a3b47;
            }
        """)
        # 设置默认选中的语言
        from src.config.languages import get_language_manager
        lang_manager = get_language_manager()
        current_lang = lang_manager.get_current_language()
        if current_lang == 'zh':
            self.language_combo.setCurrentIndex(1)  # 中文
        else:
            self.language_combo.setCurrentIndex(0)  # English
        
        self.language_combo.currentIndexChanged.connect(self.change_language)
        search_layout.addWidget(self.language_combo, 0)  # 不伸缩，固定宽度
        
        search_layout.addStretch()
        layout.addLayout(search_layout)
        
        # Top buttons - modern spacing
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)  # Larger spacing between buttons

        # Proxy buttons - start button is now hidden (merged with account buttons)
        self.proxy_start_button = QPushButton(_('proxy_start'))
        self.proxy_start_button.setObjectName("StartButton")
        self.proxy_start_button.setMinimumHeight(36)  # Taller modern buttons
        self.proxy_start_button.clicked.connect(self.start_proxy)
        self.proxy_start_button.setVisible(False)  # Now hidden

        self.proxy_stop_button = QPushButton(_('proxy_stop'))
        self.proxy_stop_button.setObjectName("StopButton")
        self.proxy_stop_button.setMinimumHeight(36)  # Taller modern buttons
        self.proxy_stop_button.clicked.connect(self.stop_proxy)
        self.proxy_stop_button.setVisible(False)  # Initially hidden

        # Other buttons
        self.add_account_button = QPushButton(_('add_account'))
        self.add_account_button.setObjectName("AddButton")
        self.add_account_button.setMinimumHeight(36)  # Taller modern buttons
        self.add_account_button.clicked.connect(self.add_account)

        self.refresh_limits_button = QPushButton(_('refresh_limits'))
        self.refresh_limits_button.setObjectName("RefreshButton")
        self.refresh_limits_button.setMinimumHeight(36)  # Taller modern buttons
        self.refresh_limits_button.clicked.connect(self.refresh_limits)

        # Account creation button
        self.create_account_button = QPushButton(_('auto_add_account'))
        self.create_account_button.setObjectName("CreateAccountButton")
        self.create_account_button.setMinimumHeight(36)  # Taller modern buttons
        self.create_account_button.clicked.connect(self.create_new_account)

        button_layout.addWidget(self.proxy_stop_button)
        button_layout.addWidget(self.add_account_button)
        button_layout.addWidget(self.create_account_button)
        button_layout.addWidget(self.refresh_limits_button)
        button_layout.addStretch()

        # Help button on the right
        self.help_button = QPushButton('Help')
        self.help_button.setFixedHeight(36)  # Compatible with modern button height
        self.help_button.setToolTip(_('help_tooltip'))
        self.help_button.clicked.connect(self.show_help_dialog)
        button_layout.addWidget(self.help_button)

        layout.addLayout(button_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)  # ID, Email, Status, Usage, Created, Action
        self.table.setHorizontalHeaderLabels(['ID', 'Email', 'Status', 'Usage', 'Created', 'Action'])

        # Table settings for dark theme compatibility
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(45)  # Taller rows for better readability
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setFocusPolicy(Qt.NoFocus)
        
        # Set font size for better readability
        font = QFont()
        font.setPointSize(10)  # Slightly larger font
        self.table.setFont(font)

        # Add right-click context menu
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        # Table header settings - Optimized for 1100px wide window
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # ID column fixed width
        header.setSectionResizeMode(1, QHeaderView.Fixed)  # Email column fixed width
        header.setSectionResizeMode(2, QHeaderView.Fixed)  # Status column fixed width
        header.setSectionResizeMode(3, QHeaderView.Fixed)  # Usage column fixed width
        header.setSectionResizeMode(4, QHeaderView.Fixed)  # Created time column fixed width
        header.setSectionResizeMode(5, QHeaderView.Fixed)  # Action button column fixed width
        header.resizeSection(0, 50)   # ID column width
        header.resizeSection(1, 380)  # Email column width
        header.resizeSection(2, 180)  # Status column width
        header.resizeSection(3, 100)  # Usage column width
        header.resizeSection(4, 120)  # Created time column width
        header.resizeSection(5, 100)  # Action button column width
        header.setFixedHeight(40)  # Higher modern header

        layout.addWidget(self.table)

        central_widget.setLayout(layout)

    def load_accounts(self, preserve_limits=False):
        """Load accounts to table with search functionality"""
        # 使用新方法获取包含创建时间的完整信息
        all_accounts = self.account_manager.get_accounts_with_all_info()
        
        # 获取搜索文字
        search_text = self.search_input.text().lower().strip() if hasattr(self, 'search_input') else ''
        
        # 过滤账号
        if search_text:
            accounts = []
            for account in all_accounts:
                account_id, email, account_json, health_status, created_at, limit_info = account
                
                # 搜索匹配条件：邮箱、ID、状态、使用量
                search_fields = [
                    str(account_id).lower(),
                    email.lower(),
                    health_status.lower() if health_status else '',
                    limit_info.lower() if limit_info else ''
                ]
                
                # 尝试解析状态信息进行搜索
                try:
                    if health_status == 'banned':
                        search_fields.append('banned')
                    else:
                        account_data = json.loads(account_json)
                        expiration_time = account_data['stsTokenManager']['expirationTime']
                        if isinstance(expiration_time, str):
                            expiration_time = int(expiration_time)
                        current_time = int(time.time() * 1000)
                        
                        if current_time >= expiration_time:
                            search_fields.append('expired')
                            search_fields.append('token expired')
                        else:
                            search_fields.append('active')
                except:
                    search_fields.append('error')
                
                # 检查是否匹配搜索文字
                if any(search_text in field for field in search_fields):
                    accounts.append(account)
        else:
            accounts = all_accounts

        self.table.setRowCount(len(accounts))
        active_account = self.account_manager.get_active_account()

        # 数据顺序现在是: (id, email, account_data, health_status, created_at, limit_info)
        for row, (account_id, email, account_json, health_status, created_at, limit_info) in enumerate(accounts):
            # ID (Column 0)
            id_item = QTableWidgetItem(str(account_id))
            id_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table.setItem(row, 0, id_item)
            
            # Email (Column 1)
            email_item = QTableWidgetItem(email)
            self.table.setItem(row, 1, email_item)
            

            # Status (Column 2)
            try:
                # Banned account check - show banned status instead of token status
                if health_status == 'banned':
                    status = 'Banned'
                else:
                    account_data = json.loads(account_json)
                    expiration_time = account_data['stsTokenManager']['expirationTime']
                    # Convert to int if it's a string
                    if isinstance(expiration_time, str):
                        expiration_time = int(expiration_time)
                    current_time = int(time.time() * 1000)

                    if current_time >= expiration_time:
                        status = _('status_token_expired')
                    else:
                        status = _('status_active')

                    # If active account, indicate it
                    if email == active_account:
                        status += _('status_proxy_active')

            except:
                status = _('status_error')

            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table.setItem(row, 2, status_item)

            # Usage (Column 3) - get from database (default: "Not updated")
            usage_item = QTableWidgetItem(limit_info or 'Not updated')
            usage_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table.setItem(row, 3, usage_item)
            
            # Created time (Column 4)
            if created_at:
                # 格式化创建时间（显示为易读格式）
                try:
                    from datetime import datetime
                    # 解析SQLite时间格式
                    dt = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                    # 格式化为更紧凑的显示
                    created_str = dt.strftime('%m-%d %H:%M')
                except:
                    created_str = created_at[:16] if created_at else 'Unknown'
            else:
                created_str = 'Unknown'
            
            created_item = QTableWidgetItem(created_str)
            created_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table.setItem(row, 4, created_item)
            
            # Action button (Column 5) - Dark theme compatible
            activation_button = QPushButton()
            activation_button.setFixedSize(75, 28)  # Better button size for modern UI
            activation_button.setObjectName("activationButton")
            
            # Set button state
            is_active = (email == active_account)
            is_banned = (health_status == 'banned')  # Use direct health status

            if is_banned:
                activation_button.setText('Banned')  # Show banned text
                activation_button.setProperty("state", "banned")
                activation_button.setEnabled(False)  # Disable button for banned accounts
            elif is_active:
                activation_button.setText('Stop')
                activation_button.setProperty("state", "stop")
                activation_button.setEnabled(True)
            else:
                activation_button.setText('Start')
                activation_button.setProperty("state", "start")
                activation_button.setEnabled(True)

            # Connect button click handler
            activation_button.clicked.connect(lambda checked, e=email: self.toggle_account_activation(e))
            self.table.setCellWidget(row, 5, activation_button)

            # Set row CSS properties for dark theme compatibility
            if health_status == 'banned':
                # Banned account
                for col in range(0, 5):  # Columns 0-4 (ID to Created)
                    item = self.table.item(row, col)
                    if item:
                        item.setData(Qt.UserRole, "banned")
            elif email == active_account:
                # Active account
                for col in range(0, 5):  # Columns 0-4
                    item = self.table.item(row, col)
                    if item:
                        item.setData(Qt.UserRole, "active")
            elif health_status == 'unhealthy':
                # Unhealthy account
                for col in range(0, 5):  # Columns 0-4
                    item = self.table.item(row, col)
                    if item:
                        item.setData(Qt.UserRole, "unhealthy")

    def toggle_account_activation(self, email):
        """Change account activation state - start proxy if necessary"""

        # Banned account check
        accounts_with_health = self.account_manager.get_accounts_with_health()
        for acc_email, _, acc_health in accounts_with_health:
            if acc_email == email and acc_health == 'banned':
                self.show_status_message(f"{email} account is banned - cannot activate", 5000)
                return

        # Check active account
        active_account = self.account_manager.get_active_account()

        if email == active_account and self.proxy_enabled:
            # Account already active - deactivate (also stop proxy)
            self.stop_proxy()
        else:
            # Account not active or proxy disabled - start proxy and activate account
            if not self.proxy_enabled:
                # First start proxy
                self.show_status_message(f"Starting proxy and activating {email}...", 2000)
                if self.start_proxy_and_activate_account(email):
                    return  # Successful - operation completed
                else:
                    return  # Failed - error message already shown
            else:
                # Proxy already active, just activate account
                # 但在切换账号时，先停止代理再重新启动，确保控制台窗口正确关闭
                self.show_status_message(f"Switching to {email}...", 2000)
                # 停止代理但不清除活跃账号（之后会设置新的）
                self.stop_proxy(clear_active_account=False)
                # 重新启动代理并激活新账号
                if self.start_proxy_and_activate_account(email):
                    return  # Successful - operation completed
                else:
                    return  # Failed - error message already shown

    def show_context_menu(self, position):
        """Show right-click context menu"""
        item = self.table.itemAt(position)
        if item is None:
            return

        row = item.row()
        email_item = self.table.item(row, 1)  # Email is now in column 1
        if not email_item:
            return

        email = email_item.text()

        # Check account status
        accounts_with_health = self.account_manager.get_accounts_with_health()
        health_status = None
        for acc_email, _, acc_health in accounts_with_health:
            if acc_email == email:
                health_status = acc_health
                break

        # Create menu
        menu = QMenu(self)

        # Activate/Deactivate
        if self.proxy_enabled:
            active_account = self.account_manager.get_active_account()
            if email == active_account:
                deactivate_action = QAction("🔴 Deactivate", self)
                deactivate_action.triggered.connect(lambda: self.deactivate_account(email))
                menu.addAction(deactivate_action)
            else:
                if health_status != 'banned':
                    activate_action = QAction("🟢 Activate", self)
                    activate_action.triggered.connect(lambda: self.activate_account(email))
                    menu.addAction(activate_action)

        menu.addSeparator()

        # Delete account
        delete_action = QAction("🗑️ Delete Account", self)
        delete_action.triggered.connect(lambda: self.delete_account_with_confirmation(email))
        menu.addAction(delete_action)

        # Show menu
        menu.exec_(self.table.mapToGlobal(position))

    def deactivate_account(self, email):
        """Deactivate account"""
        try:
            if self.account_manager.clear_active_account():
                self.load_accounts(preserve_limits=True)
                self.show_status_message(f"{email} account deactivated", 3000)
            else:
                self.show_status_message("Failed to deactivate account", 3000)
        except Exception as e:
            self.show_status_message(f"Error: {str(e)}", 5000)

    def delete_account_with_confirmation(self, email):
        """Delete account with confirmation"""
        try:
            reply = QMessageBox.question(self, "Delete Account",
                                       f"Are you sure you want to delete account '{email}'?\n\n"
                                       f"This action cannot be undone!",
                                       QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.No)

            if reply == QMessageBox.Yes:
                if self.account_manager.delete_account(email):
                    self.load_accounts(preserve_limits=True)
                    self.show_status_message(f"{email} account deleted", 3000)
                else:
                    self.show_status_message("Account could not be deleted", 3000)
        except Exception as e:
            self.show_status_message(f"Deletion error: {str(e)}", 5000)

    def add_account(self):
        """Open add account dialog"""
        dialog = AddAccountDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            json_data = dialog.get_json_data()
            if json_data:
                success, message = self.account_manager.add_account(json_data)
                if success:
                    self.load_accounts()
                    self.status_bar.showMessage(_('account_added_success'), 3000)
                else:
                    self.status_bar.showMessage(f"{_('error')}: {message}", 5000)

    def create_new_account(self):
        """Create new account"""
        try:
            print("🔧 Starting new account creation procedure...")
            
            # Check availability of required dependencies
            try:
                import curl_cffi
                import bs4
                from src.managers.temp_email_manager import create_temporary_email
                # Start creation process in separate thread
                self._start_account_creation()
            except ImportError as ie:
                print(f"Import error: {ie}")
                self._show_dependency_error(str(ie))
                return
            
        except Exception as e:
            print(f"Account creation error: {e}")
            self.status_bar.showMessage(f"Error: {str(e)}", 5000)
    
    def _start_account_creation(self):
        """Start account creation process"""
        # Show progress dialog
        self.create_progress_dialog = QProgressDialog(
            "Creating temporary email...", 
            "Cancel", 
            0, 0, self
        )
        self.create_progress_dialog.setWindowModality(Qt.WindowModal)
        self.create_progress_dialog.show()
        
        # Start worker in separate thread
        self.account_creation_worker = AccountCreationWorker(self.account_manager)
        self.account_creation_worker.progress.connect(self._update_creation_progress)
        self.account_creation_worker.finished.connect(self._creation_finished)
        self.account_creation_worker.error.connect(self._creation_error)
        self.account_creation_worker.start()
        
        # Disable buttons
        self.create_account_button.setEnabled(False)
        self.add_account_button.setEnabled(False)
    
    def _show_dependency_error(self, error_details: str = ""):
        """Show missing dependencies error"""
        error_message = "Required dependencies are missing for auto account creation."
        if "curl_cffi" in error_details:
            error_message += "\n\nMissing: curl_cffi"
        if "bs4" in error_details or "beautifulsoup" in error_details.lower():
            error_message += "\n\nMissing: beautifulsoup4"
            
        QMessageBox.warning(
            self,
            "Missing Dependencies",
            error_message + "\n\nPlease install dependencies:\n\n"
            "pip install -r requirements.txt\n\n"
            "Then restart the application."
        )
        self.status_bar.showMessage("❌ Missing dependencies for auto creation", 5000)
    
    def _update_creation_progress(self, message):
        """Update account creation progress"""
        if hasattr(self, 'create_progress_dialog'):
            self.create_progress_dialog.setLabelText(message)
    
    def _creation_finished(self, result):
        """Account creation completion"""
        if hasattr(self, 'create_progress_dialog'):
            self.create_progress_dialog.close()
        
        # Enable buttons
        self.create_account_button.setEnabled(True)
        self.add_account_button.setEnabled(True)
        
        if result and 'email' in result:
            email = result['email']
            
            # Check if account was saved to database 
            if result.get('saved_to_database', False):
                self.status_bar.showMessage(f"✅ Account created and saved: {email}", 5000)
                # Reload accounts table to show new account immediately
                self.load_accounts()
                
                # Show result to user
                QMessageBox.information(
                    self,
                    "Account Created Successfully",
                    f"✅ Warp.dev account created and added to database:\n\n{email}\n\nThe account is now available in your accounts list."
                )
            else:
                # Account created but check if there's database save error or if it's old implementation
                if result.get('save_message'):
                    self.status_bar.showMessage(f"⚠️ Account created but not saved: {email}", 5000)
                    QMessageBox.warning(
                        self,
                        "Account Created",
                        f"Account created: {email}\n\n⚠️ However, it was not saved to the database.\n\nError: {result.get('save_message', 'Unknown error')}"
                    )
                else:
                    # Old implementation - just temporary email created
                    self.status_bar.showMessage(f"✅ Temporary email created: {email}", 5000)
                    
                    # Show result to user
                    QMessageBox.information(
                        self,
                        "Account Created",
                        f"Account successfully created\n✅ {email}\n"
                    )
            
        else:
            self.status_bar.showMessage("❌ Failed to create account", 5000)
        
        # Clear worker
        self.account_creation_worker = None
    
    def _creation_error(self, error_message):
        """Account creation error"""
        if hasattr(self, 'create_progress_dialog'):
            self.create_progress_dialog.close()
        
        # Enable buttons
        self.create_account_button.setEnabled(True)
        self.add_account_button.setEnabled(True)
        
        # General error handling
        QMessageBox.critical(
            self,
            "Account Creation Error", 
            f"Failed to create account:\n\n{error_message}"
        )
        self.status_bar.showMessage(f"❌ Error: {error_message}", 5000)
        
        self.account_creation_worker = None

    def refresh_limits(self):
        """Update limits with enhanced background processing"""
        accounts = self.account_manager.get_accounts_with_health()
        if not accounts:
            self.status_bar.showMessage(_('no_accounts_to_update'), 3000)
            return

        # Progress dialog with cancel support
        self.progress_dialog = QProgressDialog(
            f"Preparing to refresh {len(accounts)} accounts...",
            "Cancel", 0, 100, self
        )
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setMinimumDuration(0)  # Show immediately
        self.progress_dialog.canceled.connect(self.cancel_refresh)
        self.progress_dialog.show()

        # Start worker thread with batch processing
        batch_size = min(10, max(3, len(accounts) // 5))  # Adaptive batch size: 3-10 concurrent
        self.worker = TokenRefreshWorker(accounts, self.proxy_enabled, batch_size)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.refresh_finished)
        self.worker.error.connect(self.refresh_error)
        self.worker.account_updated.connect(self.on_account_refreshed)  # Real-time updates
        self.worker.start()

        # Track refresh state
        self.refresh_count = 0
        self.refresh_total = len(accounts)
        self.refresh_start_time = time.time()

        # Disable buttons during refresh
        self.refresh_limits_button.setEnabled(False)
        self.add_account_button.setEnabled(False)
        self.create_account_button.setEnabled(False)

    def cancel_refresh(self):
        """Cancel the refresh operation"""
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.cancel()
            self.status_bar.showMessage("Cancelling refresh operation...", 2000)
    
    def on_account_refreshed(self, email, status, limit_info):
        """Handle real-time account refresh update"""
        self.refresh_count += 1
        
        # Update the specific row in the table immediately
        for row in range(self.table.rowCount()):
            email_item = self.table.item(row, 1)
            if email_item and email_item.text() == email:
                # Update limit column (column 3)
                limit_item = self.table.item(row, 3)
                if limit_item:
                    limit_item.setText(limit_info)
                else:
                    self.table.setItem(row, 3, QTableWidgetItem(limit_info))
                break
        
        # Calculate speed
        elapsed = time.time() - self.refresh_start_time
        speed = self.refresh_count / elapsed if elapsed > 0 else 0
        remaining = (self.refresh_total - self.refresh_count) / speed if speed > 0 else 0
        
        # Update progress with ETA
        if remaining > 0:
            eta_text = f" (ETA: {int(remaining)}s)"
        else:
            eta_text = ""
        
        self.update_progress(
            int((self.refresh_count / self.refresh_total) * 100),
            f"Updated {email} ({self.refresh_count}/{self.refresh_total}){eta_text}"
        )
    
    def update_progress(self, value, text):
        """Update progress"""
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.setValue(value)
            self.progress_dialog.setLabelText(text)

    def refresh_finished(self, results):
        """Update completed with statistics"""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()

        # Calculate statistics
        total_time = time.time() - self.refresh_start_time if hasattr(self, 'refresh_start_time') else 0
        # Status is already translated in TokenRefreshWorker, compare with the translated value
        success_status = _('success')  # Get the translated success string
        success_count = sum(1 for _, status, _ in results if status == success_status)
        failed_count = len(results) - success_count
        
        # Reload table (limit information will come automatically from database)
        self.load_accounts()

        # Activate buttons
        self.refresh_limits_button.setEnabled(True)
        self.add_account_button.setEnabled(True)
        self.create_account_button.setEnabled(True)

        # Show detailed status message
        if total_time > 0:
            status_msg = f"✅ Refreshed {len(results)} accounts in {total_time:.1f}s "
            status_msg += f"(Success: {success_count}, Failed: {failed_count})"
        else:
            status_msg = f"✅ Refreshed {len(results)} accounts"
        
        self.status_bar.showMessage(status_msg, 5000)

    def refresh_error(self, error_message):
        """Update error"""
        self.progress_dialog.close()
        self.refresh_limits_button.setEnabled(True)
        self.add_account_button.setEnabled(True)
        self.create_account_button.setEnabled(True)
        self.status_bar.showMessage(f"{_('error')}: {error_message}", 5000)

    def start_proxy_and_activate_account(self, email):
        """Start proxy and activate account using background thread"""
        try:
            # Start Mitmproxy
            print(f"Starting proxy and activating {email}...")

            # Show progress dialog
            self.proxy_progress = QProgressDialog(_('proxy_starting_account').format(email), _('cancel'), 0, 0, self)
            self.proxy_progress.setWindowModality(Qt.WindowModal)
            self.proxy_progress.show()
            QApplication.processEvents()

            # Store email for later use
            self.activating_email = email
            
            # Start proxy in background thread
            self.proxy_worker = ProxyStartWorker(self.proxy_manager, parent_window=self)
            self.proxy_worker.proxy_started.connect(self._on_proxy_started_with_account)
            self.proxy_worker.start()
            
        except Exception as e:
            if hasattr(self, 'proxy_progress'):
                self.proxy_progress.close()
            print(f"Proxy start error: {e}")
            self.status_bar.showMessage(_('proxy_start_error').format(str(e)), 5000)
            return False
    
    def _on_proxy_started_with_account(self, success, message):
        """Handle proxy start completion with account activation"""
        try:
            if hasattr(self, 'proxy_progress'):
                self.proxy_progress.close()
                
            if success:
                proxy_url = message  # message contains proxy_url on success
                self.proxy_progress = QProgressDialog(_('proxy_configuring'), None, 0, 0, self)
                self.proxy_progress.setWindowModality(Qt.WindowModal)
                self.proxy_progress.show()
                QApplication.processEvents()
                
                # Configure proxy in background thread
                self.proxy_config_worker = ProxyConfigWorker(proxy_url)
                self.proxy_config_worker.config_completed.connect(
                    lambda success: self._on_proxy_configured_with_account(success, proxy_url)
                )
                self.proxy_config_worker.start()
                
            else:
                print("Failed to start Mitmproxy")
                self.status_bar.showMessage(_('mitmproxy_start_failed'), 5000)
                return False
        except Exception as e:
            if hasattr(self, 'proxy_progress'):
                self.proxy_progress.close()
            print(f"Proxy start error: {e}")
            self.status_bar.showMessage(_('proxy_start_error').format(str(e)), 5000)
            return False
    
    def _on_proxy_configured_with_account(self, success, proxy_url):
        """Handle proxy configuration completion with account activation"""
        try:
            if hasattr(self, 'proxy_progress'):
                self.proxy_progress.close()
                
            if success:
                self.proxy_progress = QProgressDialog(_('activating_account').format(self.activating_email), None, 0, 0, self)
                self.proxy_progress.setWindowModality(Qt.WindowModal)
                self.proxy_progress.show()
                QApplication.processEvents()

                self.proxy_enabled = True
                self.proxy_start_button.setEnabled(False)
                self.proxy_start_button.setText(_('proxy_active'))
                self.proxy_stop_button.setVisible(True)
                self.proxy_stop_button.setEnabled(True)

                # Start active account refresh timer
                if hasattr(self, 'active_account_refresh_timer') and not self.active_account_refresh_timer.isActive():
                    self.active_account_refresh_timer.start(60000)

                # Activate account
                self.activate_account(self.activating_email)

                self.proxy_progress.close()

                self.status_bar.showMessage(_('proxy_started_account_activated').format(self.activating_email), 5000)
                print(f"Proxy successfully started and {self.activating_email} activated!")
                return True
            else:
                print("Failed to configure Windows proxy")
                self.proxy_manager.stop()
                self.status_bar.showMessage(_('windows_proxy_config_failed'), 5000)
                return False
        except Exception as e:
            if hasattr(self, 'proxy_progress'):
                self.proxy_progress.close()
            print(f"Proxy config error: {e}")
            self.status_bar.showMessage(_('proxy_start_error').format(str(e)), 5000)
            return False

    def start_proxy(self):
        """Start proxy using background thread"""
        try:
            print("Starting proxy...")

            # Show progress dialog
            self.proxy_progress = QProgressDialog(_('proxy_starting'), _('cancel'), 0, 0, self)
            self.proxy_progress.setWindowModality(Qt.WindowModal)
            self.proxy_progress.show()
            QApplication.processEvents()

            # Start proxy in background thread
            self.proxy_worker = ProxyStartWorker(self.proxy_manager, parent_window=self)
            self.proxy_worker.proxy_started.connect(self._on_proxy_started)
            self.proxy_worker.start()
            
        except Exception as e:
            if hasattr(self, 'proxy_progress'):
                self.proxy_progress.close()
            print(f"Proxy start error: {e}")
            self.status_bar.showMessage(_('proxy_start_error').format(str(e)), 5000)
    
    def _on_proxy_started(self, success, message):
        """Handle proxy start completion (without account activation)"""
        try:
            if hasattr(self, 'proxy_progress'):
                self.proxy_progress.close()
                
            if success:
                proxy_url = message  # message contains proxy_url on success
                self.proxy_progress = QProgressDialog(_('proxy_configuring'), None, 0, 0, self)
                self.proxy_progress.setWindowModality(Qt.WindowModal)
                self.proxy_progress.show()
                QApplication.processEvents()
                
                # Configure proxy in background thread
                self.proxy_config_worker = ProxyConfigWorker(proxy_url)
                self.proxy_config_worker.config_completed.connect(
                    lambda success: self._on_proxy_configured(success, proxy_url)
                )
                self.proxy_config_worker.start()
                
            else:
                print("Failed to start Mitmproxy")
                self.status_bar.showMessage(_('mitmproxy_start_failed'), 5000)
        except Exception as e:
            if hasattr(self, 'proxy_progress'):
                self.proxy_progress.close()
            print(f"Proxy start error: {e}")
            self.status_bar.showMessage(_('proxy_start_error').format(str(e)), 5000)
    
    def _on_proxy_configured(self, success, proxy_url):
        """Handle proxy configuration completion (without account activation)"""
        try:
            if hasattr(self, 'proxy_progress'):
                self.proxy_progress.close()
                
            if success:
                self.proxy_enabled = True
                self.proxy_start_button.setEnabled(False)
                self.proxy_start_button.setText(_('proxy_active'))
                self.proxy_stop_button.setVisible(True)
                self.proxy_stop_button.setEnabled(True)

                # Start active account refresh timer
                if hasattr(self, 'active_account_refresh_timer') and not self.active_account_refresh_timer.isActive():
                    self.active_account_refresh_timer.start(60000)

                # Update table in background to avoid blocking
                QTimer.singleShot(100, lambda: self.load_accounts())

                self.status_bar.showMessage(f"Proxy started: {proxy_url}", 5000)
                print("Proxy successfully started!")
            else:
                print("Failed to configure Windows proxy")
                self.proxy_manager.stop()
                self.status_bar.showMessage(_('windows_proxy_config_failed'), 5000)
        except Exception as e:
            if hasattr(self, 'proxy_progress'):
                self.proxy_progress.close()
            print(f"Proxy config error: {e}")
            self.status_bar.showMessage(_('proxy_start_error').format(str(e)), 5000)

    def stop_proxy(self, clear_active_account=True):
        """停止代理
        
        Args:
            clear_active_account (bool): 是否清除活跃账号，默认True
        """
        try:
            # Disable Windows proxy settings
            ProxyManager.disable_proxy()

            # Stop Mitmproxy
            self.proxy_manager.stop()

            # 根据参数决定是否清除活跃账号
            if clear_active_account:
                self.account_manager.clear_active_account()

            # Stop active account refresh timer
            if hasattr(self, 'active_account_refresh_timer') and self.active_account_refresh_timer.isActive():
                self.active_account_refresh_timer.stop()
                print("🔄 Active account refresh timer stopped")

            self.proxy_enabled = False
            self.proxy_start_button.setEnabled(True)
            self.proxy_start_button.setText(_('proxy_start'))
            self.proxy_stop_button.setVisible(False)  # Hide
            self.proxy_stop_button.setEnabled(False)

            # Update table
            self.load_accounts(preserve_limits=True)

            self.status_bar.showMessage(_('proxy_stopped'), 3000)
        except Exception as e:
            self.status_bar.showMessage(_('proxy_stop_error').format(str(e)), 5000)

    def activate_account(self, email):
        """Activate account"""
        try:
            # First check account status
            accounts_with_health = self.account_manager.get_accounts_with_health()
            account_data = None
            health_status = None

            for acc_email, acc_json, acc_health in accounts_with_health:
                if acc_email == email:
                    account_data = json.loads(acc_json)
                    health_status = acc_health
                    break

            if not account_data:
                self.status_bar.showMessage(_('account_not_found'), 3000)
                return

            # Banned account cannot be activated
            if health_status == 'banned':
                self.status_bar.showMessage(_('account_banned_cannot_activate').format(email), 5000)
                return

            # Token expiry check
            current_time = int(time.time() * 1000)
            expiration_time = account_data['stsTokenManager']['expirationTime']
            # Convert to int if it's a string
            if isinstance(expiration_time, str):
                expiration_time = int(expiration_time)

            if current_time >= expiration_time:
                # Token refresh - move to thread
                self.start_token_refresh(email, account_data)
                return

            # Check token validity, activate account directly
            self._complete_account_activation(email)

        except Exception as e:
            self.status_bar.showMessage(_('account_activation_error').format(str(e)), 5000)

    def start_token_refresh(self, email, account_data):
        """Start token refresh process in thread"""
        # If another token worker is running, wait
        if self.token_worker and self.token_worker.isRunning():
            self.status_bar.showMessage(_('token_refresh_in_progress'), 3000)
            return

        # Show progress dialog
        self.token_progress_dialog = QProgressDialog(_('token_refreshing').format(email), _('cancel'), 0, 0, self)
        self.token_progress_dialog.setWindowModality(Qt.WindowModal)
        self.token_progress_dialog.show()

        # Start token worker
        self.token_worker = TokenWorker(email, account_data, self.proxy_enabled)
        self.token_worker.progress.connect(self.update_token_progress)
        self.token_worker.finished.connect(self.token_refresh_finished)
        self.token_worker.error.connect(self.token_refresh_error)
        self.token_worker.start()

    def update_token_progress(self, message):
        """Update token refresh progress"""
        if self.token_progress_dialog:
            self.token_progress_dialog.setLabelText(message)

    def token_refresh_finished(self, success, message):
        """Token refresh completed"""
        if self.token_progress_dialog:
            self.token_progress_dialog.close()
            self.token_progress_dialog = None

        self.status_bar.showMessage(message, 3000)

        if success:
            # Token successfully refreshed, activate account
            email = self.token_worker.email
            self._complete_account_activation(email)

        # Clean up worker
        self.token_worker = None

    def token_refresh_error(self, error_message):
        """Token refresh error"""
        if self.token_progress_dialog:
            self.token_progress_dialog.close()
            self.token_progress_dialog = None

        self.status_bar.showMessage(_('token_refresh_error').format(error_message), 5000)
        self.token_worker = None

    def _complete_account_activation(self, email):
        """账号激活并检查Warp进程"""
        try:
            if self.account_manager.set_active_account(email):
                self.load_accounts(preserve_limits=True)
                self.status_bar.showMessage(f"Account activated: {email}", 3000)
                # Simple notification to proxy script
                self.notify_proxy_active_account_change()
                
                # 激活成功后检查Warp进程状态
                self._check_and_start_warp_if_needed(email)
            else:
                self.status_bar.showMessage("Account activation failed", 3000)
        except Exception as e:
            self.status_bar.showMessage(f"Account activation error: {str(e)}", 5000)
    
    def _check_and_start_warp_if_needed(self, email):
        """检查Warp进程状态，如果没有运行则启动"""
        try:
            # 导入warp_manager
            from src.utils.warp_util import warp_manager
            
            # 检查Warp是否运行
            if not warp_manager.is_warp_running():
                print(f"🔎 Warp is not running after account activation, starting Warp for {email}...")
                self.show_status_message(f"🚀 Starting Warp for {email}...", 3000)
                
                # 尝试启动Warp
                if warp_manager.start_warp(wait_for_startup=True):
                    # 等待一下确保完全启动
                    import time
                    time.sleep(2)
                    
                    # 再次检查确认
                    if warp_manager.is_warp_running():
                        print(f"✅ Warp started successfully for account {email}")
                        self.show_status_message(f"✅ Warp started with {email}", 4000)
                    else:
                        print(f"⚠️ Warp start command executed but process not confirmed for {email}")
                        self.show_status_message(f"⚠️ Warp may not have started properly", 4000)
                else:
                    print(f"❌ Failed to start Warp for account {email}")
                    self.show_status_message(f"❌ Failed to start Warp, please start manually", 4000)
            else:
                print(f"ℹ️ Warp is already running with account {email}")
                # 不显示状态消息，因为这是正常情况
                
        except ImportError:
            print("⚠️ warp_util module not available, skipping Warp process check")
        except Exception as e:
            print(f"⚠️ Error checking/starting Warp process: {e}")


    def fetch_and_save_user_settings(self, email):
        """Make GetUpdatedCloudObjects API request and save as user_settings.json"""
        try:
            # Get dynamic OS information
            os_info = get_os_info()
            
            # Get active account token
            accounts = self.account_manager.get_accounts()
            account_data = None

            for acc_email, acc_json in accounts:
                if acc_email == email:
                    account_data = json.loads(acc_json)
                    break

            if not account_data:
                print(f"❌ Account not found: {email}")
                return False

            access_token = account_data['stsTokenManager']['accessToken']

            # Prepare API request
            url = "https://app.warp.dev/graphql/v2?op=GetUpdatedCloudObjects"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
                'x-warp-client-version': 'v0.2025.09.01.20.54.stable_04',
                'x-warp-os-category': os_info['category'],
                'x-warp-os-name': os_info['name'],
                'x-warp-os-version': os_info['version'],
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            }

            # GraphQL query ve variables
            payload = {
                "query": """query GetUpdatedCloudObjects($input: UpdatedCloudObjectsInput!, $requestContext: RequestContext!) {
  updatedCloudObjects(input: $input, requestContext: $requestContext) {
    __typename
    ... on UpdatedCloudObjectsOutput {
      actionHistories {
        actions {
          __typename
          ... on BundledActions {
            actionType
            count
            latestProcessedAtTimestamp
            latestTimestamp
            oldestTimestamp
          }
          ... on SingleAction {
            actionType
            processedAtTimestamp
            timestamp
          }
        }
        latestProcessedAtTimestamp
        latestTimestamp
        objectType
        uid
      }
      deletedObjectUids {
        folderUids
        genericStringObjectUids
        notebookUids
        workflowUids
      }
      folders {
        name
        metadata {
          creatorUid
          currentEditorUid
          isWelcomeObject
          lastEditorUid
          metadataLastUpdatedTs
          parent {
            __typename
            ... on FolderContainer {
              folderUid
            }
            ... on Space {
              uid
              type
            }
          }
          revisionTs
          trashedTs
          uid
        }
        permissions {
          guests {
            accessLevel
            source {
              __typename
              ... on FolderContainer {
                folderUid
              }
              ... on Space {
                uid
                type
              }
            }
            subject {
              __typename
              ... on UserGuest {
                firebaseUid
              }
              ... on PendingUserGuest {
                email
              }
            }
          }
          lastUpdatedTs
          anyoneLinkSharing {
            accessLevel
            source {
              __typename
              ... on FolderContainer {
                folderUid
              }
              ... on Space {
                uid
                type
              }
            }
          }
          space {
            uid
            type
          }
        }
        isWarpPack
      }
      genericStringObjects {
        format
        metadata {
          creatorUid
          currentEditorUid
          isWelcomeObject
          lastEditorUid
          metadataLastUpdatedTs
          parent {
            __typename
            ... on FolderContainer {
              folderUid
            }
            ... on Space {
              uid
              type
            }
          }
          revisionTs
          trashedTs
          uid
        }
        permissions {
          guests {
            accessLevel
            source {
              __typename
              ... on FolderContainer {
                folderUid
              }
              ... on Space {
                uid
                type
              }
            }
            subject {
              __typename
              ... on UserGuest {
                firebaseUid
              }
              ... on PendingUserGuest {
                email
              }
            }
          }
          lastUpdatedTs
          anyoneLinkSharing {
            accessLevel
            source {
              __typename
              ... on FolderContainer {
                folderUid
              }
              ... on Space {
                uid
                type
              }
            }
          }
          space {
            uid
            type
          }
        }
        serializedModel
      }
      notebooks {
        data
        title
        metadata {
          creatorUid
          currentEditorUid
          isWelcomeObject
          lastEditorUid
          metadataLastUpdatedTs
          parent {
            __typename
            ... on FolderContainer {
              folderUid
            }
            ... on Space {
              uid
              type
            }
          }
          revisionTs
          trashedTs
          uid
        }
        permissions {
          guests {
            accessLevel
            source {
              __typename
              ... on FolderContainer {
                folderUid
              }
              ... on Space {
                uid
                type
              }
            }
            subject {
              __typename
              ... on UserGuest {
                firebaseUid
              }
              ... on PendingUserGuest {
                email
              }
            }
          }
          lastUpdatedTs
          anyoneLinkSharing {
            accessLevel
            source {
              __typename
              ... on FolderContainer {
                folderUid
              }
              ... on Space {
                uid
                type
              }
            }
          }
          space {
            uid
            type
          }
        }
      }
      responseContext {
        serverVersion
      }
      userProfiles {
        displayName
        email
        photoUrl
        uid
      }
      workflows {
        data
        metadata {
          creatorUid
          currentEditorUid
          isWelcomeObject
          lastEditorUid
          metadataLastUpdatedTs
          parent {
            __typename
            ... on FolderContainer {
              folderUid
            }
            ... on Space {
              uid
              type
            }
          }
          revisionTs
          trashedTs
          uid
        }
        permissions {
          guests {
            accessLevel
            source {
              __typename
              ... on FolderContainer {
                folderUid
              }
              ... on Space {
                uid
                type
              }
            }
            subject {
              __typename
              ... on UserGuest {
                firebaseUid
              }
              ... on PendingUserGuest {
                email
              }
            }
          }
          lastUpdatedTs
          anyoneLinkSharing {
            accessLevel
            source {
              __typename
              ... on FolderContainer {
                folderUid
              }
              ... on Space {
                uid
                type
              }
            }
          }
          space {
            uid
            type
          }
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
}""",
                "variables": {
                    "input": {
                        "folders": [
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:14:09.132139Z", "permissionsTs": "2025-09-04T15:14:09.132139Z", "revisionTs": "2025-09-04T15:14:09.132139Z", "uid": "EDD5BxHhckNftq2AqF16y0"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:15:51.073272Z", "permissionsTs": "2025-09-04T15:15:51.073272Z", "revisionTs": "2025-09-04T15:15:51.073272Z", "uid": "VtF6FwDkPcgMKjkEW0i011"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:17:17.397772Z", "permissionsTs": "2025-09-04T15:17:17.397772Z", "revisionTs": "2025-09-04T15:17:17.397772Z", "uid": "J13I26jNGbrV2OV8HUn7WJ"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:15:50.956728Z", "permissionsTs": "2025-09-04T15:15:50.956728Z", "revisionTs": "2025-09-04T15:15:50.956728Z", "uid": "8apsBUk0x5243ZYdCVu9lB"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:17:17.496422Z", "permissionsTs": "2025-09-04T15:17:17.496422Z", "revisionTs": "2025-09-04T15:17:17.496422Z", "uid": "m6ufDjY2pqQFk5Mz65BCNx"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:14:09.023623Z", "permissionsTs": "2025-09-04T15:14:09.023623Z", "revisionTs": "2025-09-04T15:14:09.023623Z", "uid": "kVsPIbczwIva4hLbHZMouT"}
                        ],
                        "forceRefresh": False,
                        "genericStringObjects": [
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:16:07.403093Z", "permissionsTs": None, "revisionTs": "2025-09-04T15:16:07.403093Z", "uid": "rYPkTIutkV8CjPI7T7oORM"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:17:53.983781Z", "permissionsTs": None, "revisionTs": "2025-09-04T15:17:53.983781Z", "uid": "P6to7VPbCHk0JwB3gqRGX6"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:15:03.045160Z", "permissionsTs": None, "revisionTs": "2025-09-04T15:15:03.045160Z", "uid": "pbwvZnbU8bJvmEIsKjXfBw"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:16:07.403093Z", "permissionsTs": None, "revisionTs": "2025-09-04T15:16:07.403093Z", "uid": "xrpRwHBwAI4nj21YHaVl7i"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:14:28.273803Z", "permissionsTs": "2025-09-04T15:14:28.273803Z", "revisionTs": "2025-09-04T15:14:28.273803Z", "uid": "5NqwjuMw606Zjk9d4bNbAo"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:15:02.982064Z", "permissionsTs": "2025-09-04T15:15:02.982064Z", "revisionTs": "2025-09-04T15:15:02.982064Z", "uid": "BCzdHbP76LQphANlQfUmVP"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:16:08.136555Z", "permissionsTs": None, "revisionTs": "2025-09-04T15:16:08.136555Z", "uid": "SGbrqUIVT2WfOUwLhj4yp0"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:14:27.597151Z", "permissionsTs": "2025-09-04T15:14:27.597151Z", "revisionTs": "2025-09-04T15:14:27.597151Z", "uid": "0IIBDzTfGNfA2GEkgF2QjN"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:14:28.273803Z", "permissionsTs": "2025-09-04T15:14:28.273803Z", "revisionTs": "2025-09-04T15:14:28.273803Z", "uid": "GcalSGa8Aprrcmvx5G2NLL"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:15:03.045160Z", "permissionsTs": None, "revisionTs": "2025-09-04T15:15:03.045160Z", "uid": "LDJfBBCEErAZSzg6hpCY4A"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:16:07.403093Z", "permissionsTs": None, "revisionTs": "2025-09-04T15:16:07.403093Z", "uid": "AHrIt6mfJi7NdsIBiSA0tz"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:14:27.597151Z", "permissionsTs": "2025-09-04T15:14:27.597151Z", "revisionTs": "2025-09-04T15:14:27.597151Z", "uid": "fkI3MiLCjKhHrGf9n6O0Yo"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:17:53.983781Z", "permissionsTs": None, "revisionTs": "2025-09-04T15:17:53.983781Z", "uid": "DZKY9uei132xJ5Mq5MBw6T"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:17:53.983781Z", "permissionsTs": None, "revisionTs": "2025-09-04T15:17:53.983781Z", "uid": "CkjKbSV08kRoYGUEY9LvfY"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:17:54.625539Z", "permissionsTs": None, "revisionTs": "2025-09-04T15:17:54.625539Z", "uid": "7oQYxEq7ZpEXDcE9t4EAYC"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:16:08.136555Z", "permissionsTs": None, "revisionTs": "2025-09-04T15:16:08.136555Z", "uid": "am8aJIQHuondndQFyfHa4i"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:14:27.597151Z", "permissionsTs": "2025-09-04T15:14:27.597151Z", "revisionTs": "2025-09-04T15:14:27.597151Z", "uid": "HGht23AnvjqHuT8UwCYNAO"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:17:54.625539Z", "permissionsTs": None, "revisionTs": "2025-09-04T15:17:54.625539Z", "uid": "V8mjwCcOVAvHOFXfy93rwI"}
                        ],
                        "notebooks": [
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:15:51.211785Z", "permissionsTs": "2025-09-04T15:15:51.211785Z", "revisionTs": "2025-09-04T15:15:51.211785Z", "uid": "UdtjGuGcUYIGpZjZlgC764"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:14:09.253619Z", "permissionsTs": "2025-09-04T15:14:09.253619Z", "revisionTs": "2025-09-04T15:14:09.253619Z", "uid": "bDbGHWpn4uca3EFGTH1U2Q"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:17:17.603173Z", "permissionsTs": "2025-09-04T15:17:17.603173Z", "revisionTs": "2025-09-04T15:17:17.603173Z", "uid": "jauSUuyNTBgbBuWiE8TUHY"}
                        ],
                        "workflows": [
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:17:17.552627Z", "permissionsTs": "2025-09-04T15:17:17.552627Z", "revisionTs": "2025-09-04T15:17:17.552627Z", "uid": "iwMafgTRhaYK0Iw3cse39R"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:17:17.552627Z", "permissionsTs": "2025-09-04T15:17:17.552627Z", "revisionTs": "2025-09-04T15:17:17.552627Z", "uid": "NWGQamxykgd5ypAdqqFKsM"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:14:09.192955Z", "permissionsTs": "2025-09-04T15:14:09.192955Z", "revisionTs": "2025-09-04T15:14:09.192955Z", "uid": "RqUpAjdKD6kRvIyVaDo1uB"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:17:17.552627Z", "permissionsTs": "2025-09-04T15:17:17.552627Z", "revisionTs": "2025-09-04T15:17:17.552627Z", "uid": "VVnHPmOGnL158geO9QjMzH"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:14:09.192955Z", "permissionsTs": "2025-09-04T15:14:09.192955Z", "revisionTs": "2025-09-04T15:14:09.192955Z", "uid": "D2H43FGrjjUj87Xtz4faGH"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:17:17.552627Z", "permissionsTs": "2025-09-04T15:17:17.552627Z", "revisionTs": "2025-09-04T15:17:17.552627Z", "uid": "MFyXwtpP1Yw6pcinj03n2n"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:17:17.552627Z", "permissionsTs": "2025-09-04T15:17:17.552627Z", "revisionTs": "2025-09-04T15:17:17.552627Z", "uid": "VXuPYgyHagWEFmRs3Nw7bs"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:14:09.192955Z", "permissionsTs": "2025-09-04T15:14:09.192955Z", "revisionTs": "2025-09-04T15:14:09.192955Z", "uid": "CfO2BNrKtpxosE7BarOhzF"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:15:51.140134Z", "permissionsTs": "2025-09-04T15:15:51.140134Z", "revisionTs": "2025-09-04T15:15:51.140134Z", "uid": "2qvtn32aHqe1h0tgjTXJLH"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:14:09.192955Z", "permissionsTs": "2025-09-04T15:14:09.192955Z", "revisionTs": "2025-09-04T15:14:09.192955Z", "uid": "JIzhs7KX6R7q1469U0OkAx"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:14:09.192955Z", "permissionsTs": "2025-09-04T15:14:09.192955Z", "revisionTs": "2025-09-04T15:14:09.192955Z", "uid": "EgE7149EOK5HZlg33UG55A"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:15:51.019199Z", "permissionsTs": "2025-09-04T15:15:51.019199Z", "revisionTs": "2025-09-04T15:15:51.019199Z", "uid": "v7gvOPIm5MDbfTiZfY1PrZ"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:15:51.140134Z", "permissionsTs": "2025-09-04T15:15:51.140134Z", "revisionTs": "2025-09-04T15:15:51.140134Z", "uid": "ZgbNP7xZFDMI2mlfufMpoH"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:17:17.454688Z", "permissionsTs": "2025-09-04T15:17:17.454688Z", "revisionTs": "2025-09-04T15:17:17.454688Z", "uid": "GKk36aCOvwgUnas8YGrm5t"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:15:51.140134Z", "permissionsTs": "2025-09-04T15:15:51.140134Z", "revisionTs": "2025-09-04T15:15:51.140134Z", "uid": "HZeCcSc8pdwBJCLVtBfcyO"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:17:17.552627Z", "permissionsTs": "2025-09-04T15:17:17.552627Z", "revisionTs": "2025-09-04T15:17:17.552627Z", "uid": "wkIO1y9MBx6qBtJm8hSX5H"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:15:51.019199Z", "permissionsTs": "2025-09-04T15:15:51.019199Z", "revisionTs": "2025-09-04T15:15:51.019199Z", "uid": "vQwM7UBNFCm08dYwvs1yBA"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:17:17.552627Z", "permissionsTs": "2025-09-04T15:17:17.552627Z", "revisionTs": "2025-09-04T15:17:17.552627Z", "uid": "EWkCGy5fVCn6LzKZ3aap7n"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:15:51.019199Z", "permissionsTs": "2025-09-04T15:15:51.019199Z", "revisionTs": "2025-09-04T15:15:51.019199Z", "uid": "1cYEBtjukUIbF4vhTGEL3C"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:15:51.140134Z", "permissionsTs": "2025-09-04T15:15:51.140134Z", "revisionTs": "2025-09-04T15:15:51.140134Z", "uid": "Hp7Rd4X9Cz1E1EuvwLSDRf"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:14:09.192955Z", "permissionsTs": "2025-09-04T15:14:09.192955Z", "revisionTs": "2025-09-04T15:14:09.192955Z", "uid": "gnT8FcrxNhqFBzuGr3Rpmr"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:14:09.083649Z", "permissionsTs": "2025-09-04T15:14:09.083649Z", "revisionTs": "2025-09-04T15:14:09.083649Z", "uid": "kDomyveR7d4nLXSmGGh5sm"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:15:51.140134Z", "permissionsTs": "2025-09-04T15:15:51.140134Z", "revisionTs": "2025-09-04T15:15:51.140134Z", "uid": "UpAfUQYo4UfUj0hay0REri"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:17:17.454688Z", "permissionsTs": "2025-09-04T15:17:17.454688Z", "revisionTs": "2025-09-04T15:17:17.454688Z", "uid": "PRy3g6EKx6HlA0CF4tBfFd"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:15:51.140134Z", "permissionsTs": "2025-09-04T15:15:51.140134Z", "revisionTs": "2025-09-04T15:15:51.140134Z", "uid": "Fm9NQzwF6U3lLIWMWAvtEY"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:17:17.454688Z", "permissionsTs": "2025-09-04T15:17:17.454688Z", "revisionTs": "2025-09-04T15:17:17.454688Z", "uid": "dWtnvCRrHazYVFBb9QMo1B"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:14:09.083649Z", "permissionsTs": "2025-09-04T15:14:09.083649Z", "revisionTs": "2025-09-04T15:14:09.083649Z", "uid": "mCl51EOXLpiExaHl1knxUB"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:14:09.192955Z", "permissionsTs": "2025-09-04T15:14:09.192955Z", "revisionTs": "2025-09-04T15:14:09.192955Z", "uid": "PVZgftdFpFR4BN2k9AmCBw"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:15:51.140134Z", "permissionsTs": "2025-09-04T15:15:51.140134Z", "revisionTs": "2025-09-04T15:15:51.140134Z", "uid": "wKSGpwXdQJgs4Bbl5ZGeEc"},
                            {"actionsTs": None, "metadataTs": "2025-09-04T15:14:09.083649Z", "permissionsTs": "2025-09-04T15:14:09.083649Z", "revisionTs": "2025-09-04T15:14:09.083649Z", "uid": "mJg9qgqMkWSYytyq8Z7yym"}
                        ]
                    },
                    "requestContext": {
                        "clientContext": {"version": "v0.2025.09.01.20.54.stable_04"},
                        "osContext": {"category": os_info['category'], "linuxKernelVersion": None, "name": os_info['category'], "version": "10 (19045)"}
                    }
                },
                "operationName": "GetUpdatedCloudObjects"
            }

            # Direct connection - completely bypass proxy
            response = requests.post(url, headers=headers, json=payload, timeout=60, verify=False)

            if response.status_code == 200:
                user_settings_data = response.json()

                # Save to user_settings.json file
                with open("user_settings.json", 'w', encoding='utf-8') as f:
                    json.dump(user_settings_data, f, indent=2, ensure_ascii=False)

                print(f"✅ user_settings.json file successfully created ({email})")
                self.status_bar.showMessage(f"🔄 User settings downloaded for {email}", 3000)
                return True
            else:
                print(f"❌ API request failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"user_settings retrieval error: {e}")
            return False

    def notify_proxy_active_account_change(self):
        """Notify proxy script about active account change"""
        try:
            # Check if proxy is running
            if hasattr(self, 'proxy_manager') and self.proxy_manager.is_running():
                print("📢 Notifying proxy about active account change...")

                # File system triggers - safer approach
                import time
                trigger_file = "account_change_trigger.tmp"
                try:
                    with open(trigger_file, 'w') as f:
                        f.write(str(int(time.time())))
                    print("✅ Created proxy trigger file")
                except Exception as e:
                    print(f"Error creating trigger file: {e}")

                print("✅ Proxy notified about account change")
            else:
                print("ℹ️  Proxy not running, cannot notify about account change")
        except Exception as e:
            print(f"Proxy notification error: {e}")

    def refresh_account_token(self, email, account_data):
        """Refresh token for one account"""
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

            # Direct connection - skip SSL verification
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
            print(f"Token update error: {e}")
            return False

    def check_proxy_status(self):
        """Check proxy status"""
        if self.proxy_enabled:
            if not self.proxy_manager.is_running():
                # Proxy stopped unexpectedly
                self.proxy_enabled = False
                self.proxy_start_button.setEnabled(True)
                self.proxy_start_button.setText(_('proxy_start'))
                self.proxy_stop_button.setVisible(False)  # Hide
                self.proxy_stop_button.setEnabled(False)
                ProxyManager.disable_proxy()
                self.account_manager.clear_active_account()
                self.load_accounts(preserve_limits=True)

                self.status_bar.showMessage(_('proxy_unexpected_stop'), 5000)

    def check_ban_notifications(self):
        """Check ban notifications"""
        try:
            import os

            ban_notification_file = "ban_notification.tmp"
            if os.path.exists(ban_notification_file):
                # Read file
                with open(ban_notification_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()

                if content:
                    # Separate email and timestamp
                    parts = content.split('|')
                    if len(parts) >= 2:
                        banned_email = parts[0]
                        timestamp = parts[1]

                        print(f"Ban notification received: {banned_email} (time: {timestamp})")

                        # Refresh table
                        self.load_accounts(preserve_limits=True)

                        # Inform user
                        self.show_status_message(f"⛔ {banned_email} account banned!", 8000)

                # Delete file
                os.remove(ban_notification_file)
                print("Ban notification file deleted")

        except Exception as e:
            # Continue silently on error (normal if file doesn't exist)
            pass

    def refresh_active_account(self):
        """Refresh token and limit of active account - every 30 seconds"""
        try:
            # Stop timer if proxy is not active
            if not self.proxy_enabled:
                if self.active_account_refresh_timer.isActive():
                    self.active_account_refresh_timer.stop()
                    print("🔄 Active account refresh timer stopped (proxy disabled)")
                return

            # Get active account
            active_email = self.account_manager.get_active_account()
            if not active_email:
                return

            print(f"🔄 Refreshing active account: {active_email}")

            # Get account information (use cache for better performance)
            accounts_with_health = self._get_cached_accounts()
            active_account_data = None
            health_status = None

            for email, account_json, acc_health, limit_info in accounts_with_health:
                if email == active_email:
                    active_account_data = json.loads(account_json)
                    health_status = acc_health
                    break

            if not active_account_data:
                print(f"❌ Active account not found: {active_email}")
                return

            # Skip banned account
            if health_status == 'banned':
                print(f"⛔ Active account banned, skipping: {active_email}")
                return

            # Start refresh in background thread
            if hasattr(self, 'active_refresh_worker') and self.active_refresh_worker.isRunning():
                print("🔄 Active account refresh already in progress")
                return
            
            self.active_refresh_worker = ActiveAccountRefreshWorker(
                active_email, active_account_data, self.account_manager
            )
            self.active_refresh_worker.refresh_completed.connect(self._on_active_account_refreshed)
            self.active_refresh_worker.auto_switch_to_next_account.connect(self._auto_switch_account)
            self.active_refresh_worker.start()

        except Exception as e:
            print(f"Active account refresh error: {e}")
    
    def _on_active_account_refreshed(self, success, email):
        """Handle active account refresh completion"""
        try:
            if success:
                print(f"✅ Active account refreshed: {email}")
                # Update table in background to avoid blocking
                QTimer.singleShot(100, lambda: self.load_accounts(preserve_limits=False))
            else:
                print(f"❌ Failed to refresh active account: {email}")
                self.account_manager.update_account_health(email, 'unhealthy')
                # Update table to show unhealthy status
                QTimer.singleShot(100, lambda: self.load_accounts(preserve_limits=True))
        except Exception as e:
            print(f"Active account refresh completion error: {e}")

    def _auto_switch_account(self, email_with_reason):
        """自动切换到下一个健康账号 - 按创建时间顺序"""
        try:
            # 解析邮箱和切换原因
            if '|' in email_with_reason:
                exhausted_email, switch_reason = email_with_reason.split('|', 1)
            else:
                exhausted_email = email_with_reason
                switch_reason = "unknown"
            
            print(f"🔄 Auto-switching from account: {exhausted_email} (reason: {switch_reason})")
            
            # 根据切换原因决定是否删除账号
            should_delete = switch_reason in ['banned_only', 'banned_and_exhausted']
            
            if should_delete:
                print(f"🗑️ Deleting banned account: {exhausted_email}")
                delete_success = self.account_manager.delete_account(exhausted_email)
                
                if delete_success:
                    print(f"✅ Banned account {exhausted_email} deleted from database")
                    self.show_status_message(f"🗑️ Deleted banned: {exhausted_email}", 3000)
                else:
                    print(f"❌ Failed to delete banned account {exhausted_email}")
            else:
                print(f"🔄 Keeping exhausted account {exhausted_email} for quota reset (reason: {switch_reason})")
                self.show_status_message(f"🔄 Switching from {exhausted_email} (keeping for reset)", 3000)
            
            # 获取下一个可用账号
            available_accounts = self._find_available_accounts(exhausted_email)
            
            if available_accounts:
                # 选择第一个可用账号（最早创建的）
                next_email = available_accounts[0][0]  # 现在是元组，取第一个元素（email）
                next_remaining = available_accounts[0][1]
                
                print(f"✅ Found {len(available_accounts)} available accounts, switching to: {next_email} (remaining: {next_remaining})")
                
                # 直接切换到新账号（不重启Warp进程）
                self._complete_account_activation(next_email)
                
                # 给系统一点时间更新配置
                time.sleep(1)
                
                print(f"✅ Account switched to {next_email} (no Warp restart)")
                self.show_status_message(f"✅ Switched to {next_email}", 4000)
            else:
                print("⚠️ No healthy accounts available for switching")
                self.show_status_message("⚠️ All accounts exhausted or unhealthy!", 8000)
                
        except Exception as e:
            print(f"Auto-switch error: {e}")
            self.show_status_message(f"❌ Auto-switch failed: {str(e)}", 5000)
    
    def _find_available_accounts(self, excluded_email):
        """查找可用账号（按创建时间顺序）"""
        accounts_with_health = self.account_manager.get_accounts_with_health_and_limits()
        available_accounts = []
        estimated_consumption = 15  # 15秒内预计消老15个请求
        
        for email, account_json, health_status, limit_info in accounts_with_health:
            if health_status == 'healthy' and email != excluded_email:
                # 检查是否还有足够的额度支撑至少一个检查周期
                if limit_info and '/' in limit_info:
                    try:
                        used, total = map(int, limit_info.split('/'))
                        remaining = total - used
                        # 只选择有足够额度支撑下一个检查周期的账号
                        if remaining > estimated_consumption:
                            available_accounts.append((email, remaining))
                    except:
                        # 如果无法解析限制信息，仍然添加到可用列表
                        available_accounts.append((email, 999))
                else:
                    # 如果没有限制信息，也添加到可用列表
                    available_accounts.append((email, 999))
        
        return available_accounts

    def cleanup_exhausted_accounts(self):
        """清理被封禁的账号（保留只是用完额度的账号等待重置）"""
        try:
            # Use cached data to avoid repeated database queries
            accounts = self._get_cached_accounts()
            deleted_count = 0
            deleted_emails = []
            active_account = self.account_manager.get_active_account()
            
            for email, _, health_status, limit_info in accounts:
                # 跳过活动账号（让auto_switch处理）
                if email == active_account:
                    continue
                
                # 只删除被封禁的账号，保留用完额度的账号等待重置
                if health_status == 'banned':
                    print(f"🗑️ Auto-deleting banned account: {email}")
                    if self.account_manager.delete_account(email):
                        deleted_count += 1
                        deleted_emails.append(f"{email}(banned)")
            
            if deleted_count > 0:
                print(f"✅ Auto-cleaned {deleted_count} banned accounts: {', '.join(deleted_emails)}")
                self.show_status_message(f"🗑️ Deleted {deleted_count} banned accounts", 5000)
                # Invalidate cache since data changed
                self._invalidate_accounts_cache()
                # 刷新表格
                self.load_accounts(preserve_limits=True)
            
            return deleted_count
                
        except Exception as e:
            print(f"Cleanup exhausted accounts error: {e}")
            return 0

    def auto_renew_tokens(self):
        """Automatic token renewal - runs once per minute using background worker"""
        try:
            # 清理被封禁的账号（保留用完额度的账号等待重置）
            self.cleanup_exhausted_accounts()
            
            # Check if a renewal is already in progress
            if hasattr(self, 'token_renewal_worker') and self.token_renewal_worker and self.token_renewal_worker.isRunning():
                print("⚠️ Token renewal already in progress, skipping...")
                return
                
            print("🔄 Starting automatic token check...")

            # Get all accounts
            accounts = self.account_manager.get_accounts_with_health_and_limits()

            if not accounts:
                return

            # Filter accounts that need token renewal
            accounts_to_renew = []
            current_time = int(time.time() * 1000)
            buffer_time = 1 * 60 * 1000  # 1 minute buffer
            
            for email, account_json, health_status, limit_info in accounts:
                # Skip banned accounts
                if health_status == 'banned':
                    continue

                try:
                    account_data = json.loads(account_json)
                    expiration_time = account_data['stsTokenManager']['expirationTime']
                    # Convert to int if it's a string
                    if isinstance(expiration_time, str):
                        expiration_time = int(expiration_time)

                    # Check if token has expired or will expire soon
                    if current_time >= (expiration_time - buffer_time):
                        accounts_to_renew.append((email, account_json, health_status))
                        print(f"⏰ Token expiring soon: {email}")

                except Exception as e:
                    print(f"Token check error ({email}): {e}")
                    continue

            # If there are accounts to renew, start background worker
            if accounts_to_renew:
                print(f"📋 Found {len(accounts_to_renew)} tokens to renew")
                
                # Create and start token renewal worker with small batch size to avoid blocking
                self.token_renewal_worker = TokenRefreshWorker(accounts_to_renew, self.proxy_enabled, batch_size=2)
                self.token_renewal_worker.finished.connect(self._on_auto_renew_finished)
                self.token_renewal_worker.error.connect(self._on_auto_renew_error)
                self.token_renewal_worker.start()
                
                self.show_status_message(f"🔄 Renewing {len(accounts_to_renew)} expiring tokens...", 3000)
            else:
                print("✅ All tokens valid")

        except Exception as e:
            print(f"Automatic token renewal error: {e}")
            self.show_status_message("❌ Token check error", 3000)
    
    def _on_auto_renew_finished(self, results):
        """Handle automatic token renewal completion"""
        try:
            # Calculate statistics
            success_status = _('success')  # Get the translated success string
            success_count = sum(1 for _, status, _ in results if status == success_status)
            failed_count = len(results) - success_count
            
            # Update UI if successful
            if success_count > 0:
                self.show_status_message(f"🔄 {success_count}/{len(results)} tokens renewed", 5000)
                # Update table to reflect new token status
                self.load_accounts(preserve_limits=True)
            elif failed_count > 0:
                self.show_status_message(f"⚠️ {failed_count} tokens could not be renewed", 5000)
                
            # Clear the worker reference
            self.token_renewal_worker = None
            
        except Exception as e:
            print(f"Auto renew finished error: {e}")
    
    def _on_auto_renew_error(self, error_message):
        """Handle automatic token renewal error"""
        print(f"Auto renewal error: {error_message}")
        self.show_status_message(f"❌ Token renewal error: {error_message}", 5000)
        # Clear the worker reference
        self.token_renewal_worker = None

    def renew_single_token(self, email, account_data, callback=None):
        """Refresh token for single account using background worker
        
        Args:
            email: Account email
            account_data: Account data dictionary
            callback: Optional callback function(success, message) to call when done
        """
        try:
            # Create a single token worker
            token_worker = TokenWorker(email, account_data, self.proxy_enabled)
            
            # Connect signals if callback provided
            if callback:
                token_worker.finished.connect(lambda success, msg: callback(success, msg))
            
            # Handle completion
            def on_token_renewed(success, message):
                if success:
                    print(f"✅ {message}")
                    # Reload accounts to update UI if this is the active account
                    active_email = self.account_manager.get_active_account()
                    if active_email == email:
                        self.load_accounts(preserve_limits=True)
                else:
                    print(f"❌ {message}")
            
            token_worker.finished.connect(on_token_renewed)
            
            # Start the worker
            token_worker.start()
            
            # Return True to indicate the process started (not the result)
            return True
            
        except Exception as e:
            print(f"Token renewal start error ({email}): {e}")
            if callback:
                callback(False, str(e))
            return False

    def reset_status_message(self):
        """Reset status message to default"""
        debug_mode = os.path.exists("debug.txt")
        if debug_mode:
            default_message = _('default_status_debug')
        else:
            default_message = _('default_status')

        self.status_bar.showMessage(default_message)

    def show_status_message(self, message, timeout=5000):
        """Show status message and return to default after specified time"""
        self.status_bar.showMessage(message)

        # Start reset timer
        if timeout > 0:
            self.status_reset_timer.start(timeout)
    
    def change_language(self, index):
        """切换语言"""
        from src.config.languages import get_language_manager
        lang_manager = get_language_manager()
        
        if index == 0:  # English
            lang_manager.set_language('en')
        elif index == 1:  # 中文
            lang_manager.set_language('zh')
        
        # 刷新UI文字
        self.refresh_ui_texts()
        
        # 显示切换成功消息
        if index == 0:
            self.show_status_message("Language switched to English", 2000)
        else:
            self.show_status_message("语言切换为中文", 2000)

    def show_help_dialog(self):
        """显示联系我们的对话框"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QTextEdit
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont, QDesktopServices
        from PyQt5.QtCore import QUrl
        
        dialog = QDialog(self)
        dialog.setWindowTitle(_('contact_us_title'))
        dialog.setFixedSize(580, 420)
        dialog.setModal(True)
        
        # 设置对话框样式
        dialog.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #2d3748, stop: 1 #1a202c);
                border-radius: 12px;
            }
            QLabel {
                color: #e2e8f0;
                font-size: 14px;
                line-height: 1.4;
            }
            QLabel#title {
                color: #63b3ed;
                font-size: 20px;
                font-weight: bold;
                margin: 10px 0;
            }
            QLabel#description {
                color: #a0aec0;
                font-size: 13px;
                padding: 10px;
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                border-left: 4px solid #63b3ed;
            }
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #4299e1, stop: 1 #3182ce);
                color: #ffffff;
                border: none;
                padding: 12px 20px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 500;
                margin: 3px 0;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #63b3ed, stop: 1 #4299e1);
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #3182ce, stop: 1 #2c5282);
            }
            QPushButton#closeBtn {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #718096, stop: 1 #4a5568);
                margin-top: 15px;
            }
            QPushButton#closeBtn:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #a0aec0, stop: 1 #718096);
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 25, 30, 25)
        
        # 标题
        title_label = QLabel(_('contact_us_header'))
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 描述信息
        description = QLabel(_('contact_description'))
        description.setObjectName("description")
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignLeft)
        layout.addWidget(description)
        
        # 联系方式列表
        contact_info = QLabel(
            _('contact_channel_desc') + "<br><br>" +
            _('contact_chat_desc') + "<br><br>" +
            _('contact_github_desc')
        )
        contact_info.setWordWrap(True)
        contact_info.setAlignment(Qt.AlignLeft)
        layout.addWidget(contact_info)
        
        # 按钮区域
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(10)
        
        # Telegram Channel 按钮
        channel_btn = QPushButton(_('contact_telegram_channel'))
        channel_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://t.me/warp5215")))
        channel_btn.setCursor(Qt.PointingHandCursor)
        buttons_layout.addWidget(channel_btn)
        
        # Telegram Chat 按钮
        chat_btn = QPushButton(_('contact_telegram_chat'))
        chat_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://t.me/warp1215")))
        chat_btn.setCursor(Qt.PointingHandCursor)
        buttons_layout.addWidget(chat_btn)
        
        # GitHub 按钮
        github_btn = QPushButton(_('contact_github_repo'))
        github_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/hj01857655/WARP_reg_and_manager")))
        github_btn.setCursor(Qt.PointingHandCursor)
        buttons_layout.addWidget(github_btn)
        
        layout.addLayout(buttons_layout)
        
        # 分隔线
        separator = QLabel()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: rgba(255, 255, 255, 0.1); margin: 10px 0;")
        layout.addWidget(separator)
        
        # 关闭按钮
        close_btn = QPushButton(_('contact_close'))
        close_btn.setObjectName("closeBtn")
        close_btn.clicked.connect(dialog.accept)
        close_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec_()

    def refresh_ui_texts(self):
        """更新UI文字"""
        # Window title
        self.setWindowTitle(_('app_title'))

        # Buttons
        self.proxy_start_button.setText(_('proxy_start') if not self.proxy_enabled else _('proxy_active'))
        self.proxy_stop_button.setText(_('proxy_stop'))
        self.add_account_button.setText(_('add_account'))
        self.create_account_button.setText(_('auto_add_account'))
        self.refresh_limits_button.setText(_('refresh_limits'))
        self.help_button.setText(_('help'))
        self.help_button.setToolTip(_('help_tooltip'))

        # Search placeholder
        self.search_input.setPlaceholderText(_('search_placeholder'))
        
        # Table headers
        self.table.setHorizontalHeaderLabels(['ID', _('email'), _('status'), _('limit'), _('created'), 'Action'])

        # Status bar
        debug_mode = os.path.exists("debug.txt")
        if debug_mode:
            self.status_bar.showMessage(_('default_status_debug'))
        else:
            self.status_bar.showMessage(_('default_status'))

        # Reload table
        self.load_accounts(preserve_limits=True)

    def closeEvent(self, event):
        """Clean up when application closes"""
        if self.proxy_enabled:
            self.stop_proxy()

        event.accept()


def main():
    app = QApplication(sys.argv)
    # Application style: modern and compact
    load_stylesheet(app)

    window = MainWindow()
    
    # Center window on screen for better visibility
    desktop = QDesktopWidget()
    screen = desktop.availableGeometry()
    window_size = window.geometry()
    
    # Position window slightly to the right to avoid blocking main work area
    x = int((screen.width() - window_size.width()) * 0.7)  # 70% from left edge
    y = int((screen.height() - window_size.height()) * 0.3)  # 30% from top
    
    window.move(x, y)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
