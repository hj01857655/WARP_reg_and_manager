#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Home Page Widget - Dashboard with system status and statistics
"""

import os
import time
import psutil
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QGridLayout, QPushButton, QProgressBar)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPalette
from src.config.languages import _


class StatCard(QFrame):
    """Modern statistics card widget with enhanced design"""
    
    def __init__(self, title, value, icon="📊", description="", color_theme="blue", parent=None):
        super().__init__(parent)
        self.color_theme = color_theme
        self.setFrameStyle(QFrame.NoFrame)
        self.setFixedHeight(140)
        self.setFixedWidth(280)
        
        # Color themes
        self.themes = {
            "blue": {"accent": "#63b3ed", "bg": "rgba(99, 179, 237, 0.1)", "border": "rgba(99, 179, 237, 0.3)"},
            "green": {"accent": "#68d391", "bg": "rgba(104, 211, 145, 0.1)", "border": "rgba(104, 211, 145, 0.3)"},
            "orange": {"accent": "#fbb86f", "bg": "rgba(251, 184, 111, 0.1)", "border": "rgba(251, 184, 111, 0.3)"},
            "purple": {"accent": "#b794f6", "bg": "rgba(183, 148, 246, 0.1)", "border": "rgba(183, 148, 246, 0.3)"},
            "red": {"accent": "#f56565", "bg": "rgba(245, 101, 101, 0.1)", "border": "rgba(245, 101, 101, 0.3)"}
        }
        
        self.theme = self.themes.get(color_theme, self.themes["blue"])
        
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)
        
        # Icon container with background
        icon_container = QWidget()
        icon_container.setFixedSize(50, 50)
        icon_container.setStyleSheet(f"""
            QWidget {{
                background: {self.theme['bg']};
                border-radius: 25px;
                border: 2px solid {self.theme['border']};
            }}
        """)
        
        icon_layout = QHBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 22))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"color: {self.theme['accent']}; background: transparent; border: none;")
        icon_layout.addWidget(icon_label)
        
        # Header layout
        header_layout = QHBoxLayout()
        header_layout.addWidget(icon_container)
        header_layout.addStretch()
        
        # Title in header
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 11, QFont.Medium))
        title_label.setStyleSheet("color: #a0aec0; background: transparent;")
        title_label.setAlignment(Qt.AlignRight)
        header_layout.addWidget(title_label)
        
        layout.addLayout(header_layout)
        
        # Value with larger, bold font
        self.value_label = QLabel(str(value))
        self.value_label.setFont(QFont("Segoe UI", 32, QFont.Bold))
        self.value_label.setStyleSheet(f"color: {self.theme['accent']}; margin: 8px 0; background: transparent;")
        self.value_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.value_label)
        
        # Description with better spacing
        if description:
            desc_label = QLabel(description)
            desc_label.setFont(QFont("Segoe UI", 10))
            desc_label.setStyleSheet("color: #718096; background: transparent; line-height: 1.4;")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # Enhanced card styling with glassmorphism effect
        self.setStyleSheet(f"""
            StatCard {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 rgba(45, 55, 72, 0.95),
                    stop: 0.5 rgba(56, 67, 84, 0.9),
                    stop: 1 rgba(37, 47, 63, 0.95)
                );
                border: 1px solid rgba(99, 179, 237, 0.2);
                border-radius: 16px;
            }}
            StatCard:hover {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 rgba(56, 67, 84, 0.95),
                    stop: 0.5 rgba(67, 78, 96, 0.9),
                    stop: 1 rgba(45, 55, 72, 0.95)
                );
                border: 1px solid {self.theme['border']};
            }}
        """)
    
    def update_value(self, value):
        """Update card value"""
        self.value_label.setText(str(value))


class SystemStatusWidget(QWidget):
    """System status monitoring widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
        # Setup timer for real-time updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_system_stats)
        self.timer.start(5000)  # Update every 5 seconds
        
        # Initial update
        self.update_system_stats()
    
    def init_ui(self):
        """Initialize system status UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Enhanced title with icon and styling
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 15)
        title_layout.setSpacing(10)
        
        title_icon = QLabel("📊")
        title_icon.setFont(QFont("Segoe UI Emoji", 16))
        title_icon.setStyleSheet("color: #63b3ed; background: transparent;")
        title_layout.addWidget(title_icon)
        
        title_label = QLabel("System Status")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setStyleSheet("color: #e2e8f0; background: transparent;")
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        # Real-time indicator
        live_indicator = QLabel("🟢 Live")
        live_indicator.setFont(QFont("Segoe UI", 10, QFont.Medium))
        live_indicator.setStyleSheet("color: #68d391; background: transparent;")
        title_layout.addWidget(live_indicator)
        
        layout.addWidget(title_container)
        
        # System info grid with better spacing
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)
        grid_layout.setContentsMargins(0, 10, 0, 0)
        
        # CPU usage with blue theme
        self.cpu_card = StatCard(
            "CPU Usage", "0%", "🖥️", 
            "Current processor utilization", "blue"
        )
        grid_layout.addWidget(self.cpu_card, 0, 0)
        
        # Memory usage with green theme
        self.memory_card = StatCard(
            "Memory", "0%", "💾", 
            "RAM usage percentage", "green"
        )
        grid_layout.addWidget(self.memory_card, 0, 1)
        
        # Disk usage with orange theme
        self.disk_card = StatCard(
            "Disk Space", "0%", "💿", 
            "Storage space utilization", "orange"
        )
        grid_layout.addWidget(self.disk_card, 1, 0)
        
        # Uptime with purple theme
        self.uptime_card = StatCard(
            "Uptime", "0h", "⏰", 
            "System running time", "purple"
        )
        grid_layout.addWidget(self.uptime_card, 1, 1)
        
        layout.addLayout(grid_layout)
        self.setLayout(layout)
    
    def update_system_stats(self):
        """Update system statistics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.cpu_card.update_value(f"{cpu_percent:.1f}%")
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.memory_card.update_value(f"{memory.percent:.1f}%")
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.disk_card.update_value(f"{disk_percent:.1f}%")
            
            # Uptime
            uptime_seconds = time.time() - psutil.boot_time()
            hours = int(uptime_seconds // 3600)
            self.uptime_card.update_value(f"{hours}h")
            
        except Exception as e:
            print(f"Error updating system stats: {e}")


class HomePage(QWidget):
    """Home page dashboard"""
    
    # Signals
    quick_action_requested = pyqtSignal(str)  # Signal for quick actions
    
    def __init__(self, account_manager=None, parent=None):
        super().__init__(parent)
        self.account_manager = account_manager
        self.init_ui()
        
        # Setup timer for periodic updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_stats)
        self.update_timer.start(10000)  # Update every 10 seconds
        
        # Initial stats update
        self.update_stats()
    
    def init_ui(self):
        """Initialize home page UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(25)
        
        # Welcome section
        welcome_section = self.create_welcome_section()
        layout.addWidget(welcome_section)
        
        # Statistics section
        stats_section = self.create_stats_section()
        layout.addWidget(stats_section)
        
        # Quick actions section
        actions_section = self.create_quick_actions_section()
        layout.addWidget(actions_section)
        
        # System status section
        system_section = SystemStatusWidget()
        layout.addWidget(system_section)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def create_welcome_section(self):
        """Create modern welcome section with enhanced design"""
        section = QWidget()
        section.setFixedHeight(140)
        
        # Create welcome card with gradient background
        section.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 rgba(99, 179, 237, 0.15),
                    stop: 0.5 rgba(139, 92, 246, 0.1),
                    stop: 1 rgba(99, 179, 237, 0.05)
                );
                border: 1px solid rgba(99, 179, 237, 0.2);
                border-radius: 16px;
                margin: 0;
            }
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(20)
        
        # Left side - Welcome content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(8)
        
        # Welcome message with emoji
        welcome_label = QLabel("🚀 Welcome to Warp Manager")
        welcome_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        welcome_label.setStyleSheet("""
            color: qlineargradient(
                x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 #63b3ed,
                stop: 1 #8b5cf6
            );
            background: transparent;
        """)
        content_layout.addWidget(welcome_label)
        
        # Subtitle with better styling
        subtitle = QLabel("Manage your Cloudflare Warp accounts efficiently and monitor system status")
        subtitle.setFont(QFont("Segoe UI", 13))
        subtitle.setStyleSheet("color: #cbd5e0; background: transparent; line-height: 1.4;")
        subtitle.setWordWrap(True)
        content_layout.addWidget(subtitle)
        
        # Current time with icon
        self.time_label = QLabel()
        self.time_label.setFont(QFont("Segoe UI", 11))
        self.time_label.setStyleSheet("color: #a0aec0; background: transparent; margin-top: 5px;")
        self.update_time()
        content_layout.addWidget(self.time_label)
        
        layout.addLayout(content_layout)
        
        # Right side - Status indicators
        status_layout = QVBoxLayout()
        status_layout.setSpacing(10)
        status_layout.setAlignment(Qt.AlignTop)
        
        # Online status indicator
        status_container = QWidget()
        status_container.setFixedSize(120, 80)
        status_container.setStyleSheet("""
            QWidget {
                background: rgba(45, 55, 72, 0.8);
                border: 1px solid rgba(104, 211, 145, 0.4);
                border-radius: 12px;
            }
        """)
        
        status_inner_layout = QVBoxLayout(status_container)
        status_inner_layout.setContentsMargins(15, 10, 15, 10)
        status_inner_layout.setSpacing(5)
        
        status_icon = QLabel("🟢")
        status_icon.setFont(QFont("Segoe UI Emoji", 20))
        status_icon.setAlignment(Qt.AlignCenter)
        status_icon.setStyleSheet("background: transparent; border: none;")
        status_inner_layout.addWidget(status_icon)
        
        status_text = QLabel("System\nOnline")
        status_text.setFont(QFont("Segoe UI", 10, QFont.Medium))
        status_text.setStyleSheet("color: #68d391; background: transparent; border: none;")
        status_text.setAlignment(Qt.AlignCenter)
        status_inner_layout.addWidget(status_text)
        
        status_layout.addWidget(status_container)
        layout.addLayout(status_layout)
        
        layout.addStretch()
        section.setLayout(layout)
        
        # Timer for time updates
        if not hasattr(self, 'time_timer'):
            self.time_timer = QTimer()
            self.time_timer.timeout.connect(self.update_time)
            self.time_timer.start(1000)  # Update every second
        
        return section
    
    def create_stats_section(self):
        """Create statistics overview section"""
        section = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Enhanced title with icon and stats counter
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 15)
        title_layout.setSpacing(10)
        
        title_icon = QLabel("📊")
        title_icon.setFont(QFont("Segoe UI Emoji", 16))
        title_icon.setStyleSheet("color: #63b3ed; background: transparent;")
        title_layout.addWidget(title_icon)
        
        title_label = QLabel("Account Statistics")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setStyleSheet("color: #e2e8f0; background: transparent;")
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        # Stats counter
        stats_count = QLabel("📈 6 Metrics")
        stats_count.setFont(QFont("Segoe UI", 10, QFont.Medium))
        stats_count.setStyleSheet("color: #68d391; background: transparent;")
        title_layout.addWidget(stats_count)
        
        layout.addWidget(title_container)
        
        # Stats grid with enhanced spacing
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)
        grid_layout.setContentsMargins(0, 10, 0, 0)
        
        # Total accounts with blue theme
        self.total_accounts_card = StatCard(
            "Total Accounts", "0", "👥", 
            "All registered accounts", "blue"
        )
        grid_layout.addWidget(self.total_accounts_card, 0, 0)
        
        # Healthy accounts with green theme
        self.active_accounts_card = StatCard(
            "Healthy Accounts", "0", "✅", 
            "Accounts ready to use", "green"
        )
        grid_layout.addWidget(self.active_accounts_card, 0, 1)
        
        # Banned accounts with red theme
        self.banned_accounts_card = StatCard(
            "Banned Accounts", "0", "❌", 
            "Accounts that are banned", "red"
        )
        grid_layout.addWidget(self.banned_accounts_card, 0, 2)
        
        # Proxy status with purple theme
        self.proxy_status_card = StatCard(
            "Proxy Status", "Stopped", "🔗", 
            "Current proxy state", "purple"
        )
        grid_layout.addWidget(self.proxy_status_card, 1, 0)
        
        # Active account with orange theme
        self.active_account_card = StatCard(
            "Active Account", "None", "🎯", 
            "Currently active account", "orange"
        )
        grid_layout.addWidget(self.active_account_card, 1, 1)
        
        # Last update with blue theme
        self.last_update_card = StatCard(
            "Last Update", "Never", "🕒", 
            "Last statistics refresh", "blue"
        )
        grid_layout.addWidget(self.last_update_card, 1, 2)
        
        layout.addLayout(grid_layout)
        section.setLayout(layout)
        return section
    
    def create_quick_actions_section(self):
        """Create quick actions section"""
        section = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Enhanced title with icon and actions counter
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 15)
        title_layout.setSpacing(10)
        
        title_icon = QLabel("⚡")
        title_icon.setFont(QFont("Segoe UI Emoji", 16))
        title_icon.setStyleSheet("color: #f6ad55; background: transparent;")
        title_layout.addWidget(title_icon)
        
        title_label = QLabel("Quick Actions")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setStyleSheet("color: #e2e8f0; background: transparent;")
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        # Actions counter
        actions_count = QLabel("3 Actions")
        actions_count.setFont(QFont("Segoe UI", 10, QFont.Medium))
        actions_count.setStyleSheet("color: #a0aec0; background: transparent;")
        title_layout.addWidget(actions_count)
        
        layout.addWidget(title_container)
        
        # Modern action buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)
        buttons_layout.setContentsMargins(0, 10, 0, 0)
        
        # Create modern button style function
        def create_modern_button(text, icon, color_theme):
            btn = QPushButton(f"{icon} {text}")
            btn.setFixedHeight(60)
            btn.setFixedWidth(200)
            
            themes = {
                "blue": {"start": "#63b3ed", "end": "#4299e1", "hover_start": "#7cc7f0", "hover_end": "#63b3ed"},
                "orange": {"start": "#fbb86f", "end": "#ed8936", "hover_start": "#fcc89b", "hover_end": "#fbb86f"},
                "green": {"start": "#68d391", "end": "#48bb78", "hover_start": "#81e6a3", "hover_end": "#68d391"}
            }
            
            theme = themes[color_theme]
            
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(
                        x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 {theme['start']},
                        stop: 1 {theme['end']}
                    );
                    color: white;
                    border: none;
                    border-radius: 12px;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 0 24px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(
                        x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 {theme['hover_start']},
                        stop: 1 {theme['hover_end']}
                    );
                }}
                QPushButton:pressed {{
                    background: qlineargradient(
                        x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 {theme['end']},
                        stop: 1 {theme['start']}
                    );
                }}
            """)
            return btn
        
        # Go to accounts
        accounts_btn = create_modern_button("Manage Accounts", "📊", "blue")
        accounts_btn.clicked.connect(lambda: self.quick_action_requested.emit("accounts"))
        buttons_layout.addWidget(accounts_btn)
        
        # Refresh all
        refresh_btn = create_modern_button("Refresh All", "🔄", "orange")
        refresh_btn.clicked.connect(lambda: self.quick_action_requested.emit("refresh"))
        buttons_layout.addWidget(refresh_btn)
        
        # Add account
        add_btn = create_modern_button("Add Account", "➕", "green")
        add_btn.clicked.connect(lambda: self.quick_action_requested.emit("add"))
        buttons_layout.addWidget(add_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        section.setLayout(layout)
        return section
    
    def update_time(self):
        """Update current time display with icon"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.setText(f"🕰️ Current time: {current_time}")
    
    def update_stats(self):
        """Update account statistics"""
        if not self.account_manager:
            return
        
        try:
            # Get account statistics
            accounts_with_health = self.account_manager.get_accounts_with_health()
            total_accounts = len(accounts_with_health)
            
            healthy_count = sum(1 for _, _, health in accounts_with_health if health == 'healthy')
            banned_count = sum(1 for _, _, health in accounts_with_health if health == 'banned')
            
            # Update cards
            self.total_accounts_card.update_value(str(total_accounts))
            self.active_accounts_card.update_value(str(healthy_count))
            self.banned_accounts_card.update_value(str(banned_count))
            
            # Active account
            active_account = self.account_manager.get_active_account()
            if active_account:
                # Truncate long email addresses
                display_email = active_account
                if len(display_email) > 20:
                    display_email = display_email[:17] + "..."
                self.active_account_card.update_value(display_email)
            else:
                self.active_account_card.update_value("None")
            
            # Last update time
            current_time = datetime.now().strftime("%H:%M:%S")
            self.last_update_card.update_value(current_time)
            
        except Exception as e:
            print(f"Error updating stats: {e}")
    
    def update_proxy_status(self, is_enabled):
        """Update proxy status"""
        if is_enabled:
            self.proxy_status_card.update_value("Running")
            self.proxy_status_card.value_label.setStyleSheet("color: #68d391; margin: 5px 0;")
        else:
            self.proxy_status_card.update_value("Stopped")
            self.proxy_status_card.value_label.setStyleSheet("color: #fc8181; margin: 5px 0;")