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

# SSL verification bypass - complete SSL verification disable
import ssl
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError:
    # Older Python versions
    pass
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QWidget, QPushButton, QTableWidget, QTableWidgetItem,
                             QDialog, QTextEdit, QLabel, QMessageBox, QHeaderView,
                             QProgressDialog, QAbstractItemView, QStatusBar, QMenu, QAction, QScrollArea, QComboBox,
                             QDesktopWidget)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QObject
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
        except Exception as e:
            self.proxy_started.emit(False, str(e))


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
            # Get account information again
            accounts = self.account_manager.get_accounts()
            for acc_email, acc_json in accounts:
                if acc_email == email:
                    account_data = json.loads(acc_json)

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
                        
                        # 只在余量为0时触发切换和删除
                        should_switch = False
                        
                        if remaining == 0 and total > 0:
                            should_switch = True
                            print(f"🔴 Account {email} has 0 remaining quota ({used}/{total}) - will switch and delete")
                        elif remaining > 0 and remaining <= 10:
                            # 余量少于10个时提醒但不切换
                            print(f"⚠️ Account {email} has only {remaining} requests left ({used}/{total})")
                        else:
                            print(f"✅ Account {email} has {remaining} requests remaining ({used}/{total})")
                        
                        print(f"🔍 Checking limit: used={used}, total={total}, remaining={remaining}, estimated_consumption={estimated_consumption}, should_switch={should_switch}")
                        
                        if should_switch:
                            print(f"📢 Emitting auto-switch signal for: {email}")
                            # Trigger auto-switch to next healthy account
                            self.auto_switch_to_next_account.emit(email)
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

        # Timer for checking ban notifications
        self.ban_timer = QTimer()
        self.ban_timer.timeout.connect(self.check_ban_notifications)
        self.ban_timer.start(1000)  # Check every 1 second

        # Timer for automatic token renewal
        self.token_renewal_timer = QTimer()
        self.token_renewal_timer.timeout.connect(self.auto_renew_tokens)
        self.token_renewal_timer.start(60000)  # Check every 1 minute (60000 ms)

        # Timer for active account refresh
        self.active_account_refresh_timer = QTimer()
        self.active_account_refresh_timer.timeout.connect(self.refresh_active_account)
        self.active_account_refresh_timer.start(30000)  # Refresh active account every 30 seconds

        # Timer for status message reset
        self.status_reset_timer = QTimer()
        self.status_reset_timer.setSingleShot(True)
        self.status_reset_timer.timeout.connect(self.reset_status_message)

        # Run token check immediately on first startup
        QTimer.singleShot(0, self.auto_renew_tokens)

        # Variables for token worker
        self.token_worker = None
        self.token_progress_dialog = None

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

    def closeEvent(self, event):
        """程序关闭时的清理工作"""
        try:
            print("🔄 程序关闭，正在清理资源...")
            
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
        self.setFixedSize(920, 680)  # Wider window for better visibility

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
        self.help_button.setToolTip("Help and User Guide")
        self.help_button.clicked.connect(self.show_help_dialog)
        button_layout.addWidget(self.help_button)

        layout.addLayout(button_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)  # Added created time column
        self.table.setHorizontalHeaderLabels([_('current'), _('email'), _('status'), _('limit'), _('created')])

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

        # Table header settings - Optimized for wider window
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # Action button column fixed width
        header.setSectionResizeMode(1, QHeaderView.Fixed)  # Email column fixed width
        header.setSectionResizeMode(2, QHeaderView.Fixed)  # Status column fixed width
        header.setSectionResizeMode(3, QHeaderView.Fixed)  # Usage column fixed width
        header.setSectionResizeMode(4, QHeaderView.Fixed)  # Created time column fixed width
        header.resizeSection(0, 90)   # Action button column width
        header.resizeSection(1, 380)  # Email column width - increased for better readability
        header.resizeSection(2, 180)  # Status column width
        header.resizeSection(3, 100)  # Usage column width
        header.resizeSection(4, 100)  # Created time column width
        header.setFixedHeight(40)  # Higher modern header

        layout.addWidget(self.table)

        central_widget.setLayout(layout)

    def load_accounts(self, preserve_limits=False):
        """Load accounts to table"""
        # 使用新方法获取包含创建时间的完整信息
        accounts = self.account_manager.get_accounts_with_all_info()

        self.table.setRowCount(len(accounts))
        active_account = self.account_manager.get_active_account()

        for row, (email, account_json, health_status, limit_info, created_at) in enumerate(accounts):
            # Activation button (Column 0) - Dark theme compatible
            activation_button = QPushButton()
            activation_button.setFixedSize(75, 28)  # Better button size for modern UI
            activation_button.setObjectName("activationButton")
            
            # Set button state
            is_active = (email == active_account)
            is_banned = (health_status == _('status_banned_key'))

            if is_banned:
                activation_button.setText(_('button_banned'))
                activation_button.setProperty("state", "banned")
                activation_button.setEnabled(False)
            elif is_active:
                activation_button.setText(_('button_stop'))
                activation_button.setProperty("state", "stop")
            else:
                activation_button.setText(_('button_start'))
                activation_button.setProperty("state", "start")

            # Connect button click handler
            activation_button.clicked.connect(lambda checked, e=email: self.toggle_account_activation(e))
            self.table.setCellWidget(row, 0, activation_button)

            # Email (Column 1)
            email_item = QTableWidgetItem(email)
            self.table.setItem(row, 1, email_item)

            # Status (Column 2)
            try:
                # Banned account check
                if health_status == _('status_banned_key'):
                    status = _('status_banned')
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
            status_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 2, status_item)

            # Limit (Column 3) - get from database (default: "Not updated")
            limit_item = QTableWidgetItem(limit_info or _('status_not_updated'))
            limit_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 3, limit_item)
            
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
            created_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.table.setItem(row, 4, created_item)

            # Set row CSS properties for dark theme compatibility
            if health_status == 'banned':
                # Banned account
                for col in range(1, 5):  # 更新为5列
                    item = self.table.item(row, col)
                    if item:
                        item.setData(Qt.UserRole, "banned")
            elif email == active_account:
                # Active account
                for col in range(1, 5):  # 更新为5列
                    item = self.table.item(row, col)
                    if item:
                        item.setData(Qt.UserRole, "active")
            elif health_status == 'unhealthy':
                # Unhealthy account
                for col in range(1, 5):  # 更新为5列
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
        batch_size = min(5, max(1, len(accounts) // 10))  # Adaptive batch size
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
        success_count = sum(1 for _, status, _ in results if status == _('success'))
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
        """Simple account activation like old version"""
        try:
            if self.account_manager.set_active_account(email):
                self.load_accounts(preserve_limits=True)
                self.status_bar.showMessage(f"Account activated: {email}", 3000)
                # Simple notification to proxy script
                self.notify_proxy_active_account_change()
            else:
                self.status_bar.showMessage("Account activation failed", 3000)
        except Exception as e:
            self.status_bar.showMessage(f"Account activation error: {str(e)}", 5000)


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

            # Get account information
            accounts_with_health = self.account_manager.get_accounts_with_health_and_limits()
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

    def _auto_switch_account(self, exhausted_email):
        """自动切换到下一个健康账号 - 按创建时间顺序"""
        try:
            print(f"🔄 Auto-switching from exhausted account: {exhausted_email}")
            
            # 先删除已用完的账号（余量为0）
            print(f"🗑️ Checking if account {exhausted_email} should be deleted...")
            
            # 确保账号确实需要删除（余量必须为0）
            should_delete = False
            accounts_to_check = self.account_manager.get_accounts_with_health_and_limits()
            for email, _, _, limit_info in accounts_to_check:
                if email == exhausted_email:
                    if limit_info and '/' in limit_info:
                        try:
                            used, total = map(int, limit_info.split('/'))
                            remaining = total - used
                            print(f"📊 Account {email}: used {used}/{total}, remaining: {remaining}")
                            
                            # 只有余量为0时才删除
                            if remaining == 0:
                                should_delete = True
                                print(f"✅ Account {email} has 0 remaining quota, will delete")
                            else:
                                print(f"⚠️ Account {email} still has {remaining} requests left, not deleting")
                        except Exception as e:
                            print(f"⚠️ Error parsing limit info: {e}, not deleting")
                    else:
                        print(f"⚠️ No limit info for {email}, not deleting")
                    break
            
            if should_delete:
                # 执行删除
                print(f"🗑️ Deleting account from database: {exhausted_email}")
                delete_success = self.account_manager.delete_account(exhausted_email)
                
                if delete_success:
                    print(f"✅ Account {exhausted_email} deleted from database successfully")
                    
                    # 立即更新UI表格，移除已删除的账号
                    removed_from_ui = False
                    for row in range(self.table.rowCount() - 1, -1, -1):
                        email_item = self.table.item(row, 1)
                        if email_item and email_item.text() == exhausted_email:
                            self.table.removeRow(row)
                            removed_from_ui = True
                            print(f"✅ Removed {exhausted_email} from UI table (row {row})")
                            break
                    
                    if not removed_from_ui:
                        print(f"⚠️ Account {exhausted_email} was not found in UI table")
                    
                    self.show_status_message(f"🗑️ Deleted exhausted account: {exhausted_email}", 5000)
                else:
                    print(f"❌ Failed to delete account {exhausted_email} from database")
                    self.show_status_message(f"❌ Failed to delete {exhausted_email}", 5000)
            
            # 导入 Warp 进程管理器
            from src.utils.warp_util import warp_manager
            
            # 获取所有账号（按创建时间顺序）
            accounts_with_health = self.account_manager.get_accounts_with_health_and_limits()
            available_accounts = []
            
            # 使用与检查时相同的智能判断逻辑
            estimated_consumption = 15  # 30秒内预计消耗15个请求
            
            for email, account_json, health_status, limit_info in accounts_with_health:
                if health_status == 'healthy' and email != exhausted_email:
                    # 检查是否还有足够的额度支撑至少一个检查周期
                    if limit_info and '/' in limit_info:
                        try:
                            used, total = map(int, limit_info.split('/'))
                            remaining = total - used
                            # 只选择有足够额度支撑下一个检查周期的账号
                            if remaining > estimated_consumption:
                                # 不排序，保持数据库中的顺序（创建时间顺序）
                                available_accounts.append((email, remaining))
                        except:
                            # 如果无法解析限制信息，仍然添加到可用列表（假设有足够额度）
                            available_accounts.append((email, 999))
                    else:
                        # 如果没有限制信息，也添加到可用列表（假设有足够额度）
                        available_accounts.append((email, 999))
            
            if available_accounts:
                # 选择第一个可用账号（最早创建的）
                next_email = available_accounts[0][0]  # 现在是元组，取第一个元素（email）
                next_remaining = available_accounts[0][1]
                
                print(f"✅ Found {len(available_accounts)} available accounts, switching to: {next_email} (remaining: {next_remaining})")
                self.show_status_message(f"🔄 Auto-switching to {next_email}", 5000)
                
                # 1. 先关闭 Warp 应用
                print("🛑 Closing Warp application before switching account...")
                if warp_manager.is_warp_running():
                    if warp_manager.stop_warp():
                        print("✅ Warp closed successfully")
                        # 验证 Warp 确实已关闭
                        import time
                        max_wait = 10  # 最多等待10秒
                        for i in range(max_wait):
                            if not warp_manager.is_warp_running():
                                print(f"✅ Warp process confirmed closed after {i+1} seconds")
                                break
                            time.sleep(1)
                        else:
                            print("⚠️ Warp process still running after 10 seconds, forcing kill...")
                            warp_manager.stop_warp(force=True)
                            time.sleep(2)
                    else:
                        print("⚠️ Failed to close Warp gracefully, trying force kill...")
                        warp_manager.stop_warp(force=True)
                        time.sleep(2)
                else:
                    print("ℹ️ Warp is not running, no need to close")
                
                # 2. 再次确认 Warp 已关闭
                import time
                if warp_manager.is_warp_running():
                    print("❌ Warp is still running, aborting account switch")
                    self.show_status_message("❌ Failed to close Warp for account switch", 5000)
                    return
                
                # 3. 切换到新账号
                print(f"🔄 Switching active account to: {next_email}")
                self._complete_account_activation(next_email)
                time.sleep(1)  # 给系统一点时间更新配置
                
                # 4. 重新打开 Warp 应用
                print("🚀 Starting Warp application with new account...")
                if not warp_manager.is_warp_running():
                    if warp_manager.start_warp(wait_for_startup=True):
                        # 再次验证 Warp 确实已启动
                        time.sleep(3)  # 额外等待确保完全启动
                        if warp_manager.is_warp_running():
                            print("✅ Warp restarted and confirmed running with new account")
                            self.show_status_message(f"✅ Switched to {next_email} and Warp is running", 5000)
                        else:
                            print("⚠️ Warp start command executed but process not detected")
                            self.show_status_message("⚠️ Warp may not have started properly, please check", 5000)
                    else:
                        print("❌ Failed to start Warp")
                        self.show_status_message("❌ Failed to start Warp, please start it manually", 5000)
                else:
                    print("⚠️ Warp is already running (unexpected)")
                    self.show_status_message(f"⚠️ Warp already running, switched to {next_email}", 5000)
            else:
                print("⚠️ No healthy accounts available for switching")
                self.show_status_message("⚠️ All accounts exhausted or unhealthy!", 8000)
                
        except Exception as e:
            print(f"Auto-switch error: {e}")
            self.show_status_message(f"❌ Auto-switch failed: {str(e)}", 5000)

    def auto_renew_tokens(self):
        """Automatic token renewal - runs once per minute"""
        try:
            print("🔄 Starting automatic token check...")

            # Get all accounts
            accounts = self.account_manager.get_accounts_with_health_and_limits()

            if not accounts:
                return

            expired_count = 0
            renewed_count = 0

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
                    current_time = int(time.time() * 1000)

                    # Check if token has expired (refresh 1 minute earlier)
                    buffer_time = 1 * 60 * 1000  # 1 dakika buffer
                    if current_time >= (expiration_time - buffer_time):
                        expired_count += 1
                        print(f"⏰ Token expiring soon: {email}")

                        # Refresh token
                        if self.renew_single_token(email, account_data):
                            renewed_count += 1
                            print(f"✅ Token updated: {email}")
                        else:
                            print(f"❌ Failed to update token: {email}")

                except Exception as e:
                    print(f"Token check error ({email}): {e}")
                    continue

            # Result message
            if expired_count > 0:
                if renewed_count > 0:
                    self.show_status_message(f"🔄 {renewed_count}/{expired_count} tokens renewed", 5000)
                    # Update table
                    self.load_accounts(preserve_limits=True)
                else:
                    self.show_status_message(f"⚠️ {expired_count} tokens could not be renewed", 5000)
            else:
                print("✅ All tokens valid")

        except Exception as e:
            print(f"Automatic token renewal error: {e}")
            self.show_status_message("❌ Token check error", 3000)

    def renew_single_token(self, email, account_data):
        """Refresh token for single account"""
        try:
            refresh_token = account_data['stsTokenManager']['refreshToken']

            # Firebase token yenileme API'si
            url = f"https://securetoken.googleapis.com/v1/token?key=AIzaSyBdy3O3S9hrdayLJxJ7mriBR4qgUaUygAs"

            payload = {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token
            }

            headers = {
                "Content-Type": "application/json"
            }

            # Direct connection - completely bypass proxy
            response = requests.post(url, json=payload, headers=headers, timeout=30, verify=False)

            if response.status_code == 200:
                token_data = response.json()

                # Update new token information
                new_access_token = token_data['access_token']
                new_refresh_token = token_data.get('refresh_token', refresh_token)
                expires_in = int(token_data['expires_in']) * 1000  # convert seconds to milliseconds

                # Yeni expiration time hesapla
                new_expiration_time = int(time.time() * 1000) + expires_in

                # Update account data
                account_data['stsTokenManager']['accessToken'] = new_access_token
                account_data['stsTokenManager']['refreshToken'] = new_refresh_token
                account_data['stsTokenManager']['expirationTime'] = new_expiration_time

                # Save to database
                updated_json = json.dumps(account_data)
                self.account_manager.update_account(email, updated_json)

                return True
            else:
                print(f"Token update error: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"Token update error ({email}): {e}")
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

    def show_help_dialog(self):
        """Open Telegram for help"""
        import webbrowser
        webbrowser.open("https://t.me/warp5215")

    def refresh_ui_texts(self):
        """Update UI texts to English"""
        # Window title
        self.setWindowTitle('Warp Account Manager')

        # Buttons
        self.proxy_start_button.setText('Start Proxy' if not self.proxy_enabled else 'Proxy Active')
        self.proxy_stop_button.setText('Stop Proxy')
        self.add_account_button.setText('Add Account')
        self.refresh_limits_button.setText('Refresh Limits')
        self.help_button.setText('Help')

        # Table headers
        self.table.setHorizontalHeaderLabels(['Current', 'Email', 'Status', 'Limit'])

        # Status bar
        debug_mode = os.path.exists("debug.txt")
        if debug_mode:
            self.status_bar.showMessage('Enable proxy and click start button on accounts to begin usage. (Debug mode active)')
        else:
            self.status_bar.showMessage('Enable proxy and click start button on accounts to begin usage.')

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
