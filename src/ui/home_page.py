#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Home Page Widget - Dashboard with system status and statistics
"""

import os
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QGridLayout, QPushButton)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPalette
from src.config.languages import _
from src.utils.warp_user_data import WarpUserDataManager
from src.ui.theme_manager import theme_manager
from src.managers.warp_registry_manager import warp_registry_manager
import json


class StatCard(QFrame):
    """Modern statistics card widget with enhanced design"""
    
    def __init__(self, title, value, icon="📊", description="", color_theme="blue", parent=None):
        super().__init__(parent)
        self.color_theme = color_theme
        self.setFrameStyle(QFrame.NoFrame)
        self.setMinimumHeight(140)
        self.setMinimumWidth(280)
        # 移除最大尺寸限制，让卡片能够自适应
        
        # Use theme manager instead of hardcoded themes
        self.theme = theme_manager.get_card_theme(color_theme)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)
        
        # Icon container with background
        icon_container = QWidget()
        icon_container.setFixedSize(50, 50)
        icon_container.setStyleSheet(f"""
            QWidget {{
                background: {self.theme['background']};
                border-radius: 25px;
                border: 2px solid {self.theme['border']};
            }}
        """)
        
        icon_layout = QHBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 22))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"color: {self.theme['accent']}; background: transparent; border: none; outline: none; border-radius: 6px; padding: 4px;")
        icon_layout.addWidget(icon_label)
        
        # Header layout
        header_layout = QHBoxLayout()
        header_layout.addWidget(icon_container)
        header_layout.addStretch()
        
        # Title in header
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Segoe UI", 11, QFont.Medium))
        self.title_label.setStyleSheet(f"color: {theme_manager.get_color('text_muted')}; background: transparent; border: none; outline: none; border-radius: 6px; padding: 4px 8px;")
        self.title_label.setAlignment(Qt.AlignRight)
        header_layout.addWidget(self.title_label)
        
        layout.addLayout(header_layout)
        
        # Value with larger, bold font
        self.value_label = QLabel(str(value))
        self.value_label.setFont(QFont("Segoe UI", 28, QFont.Bold))
        self.value_label.setStyleSheet(f"color: {self.theme['accent']}; margin: 4px 0; background: transparent; border: none; outline: none; border-radius: 8px; padding: 6px 12px;")
        self.value_label.setAlignment(Qt.AlignLeft)
        self.value_label.setWordWrap(False)
        layout.addWidget(self.value_label)
        
        # Description with better spacing
        if description:
            self.desc_label = QLabel(description)
            self.desc_label.setFont(QFont("Segoe UI", 10))
            self.desc_label.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; background: transparent; line-height: 1.4; border: none; outline: none; border-radius: 6px; padding: 4px 8px;")
            self.desc_label.setWordWrap(True)
            layout.addWidget(self.desc_label)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # Use theme manager for card styling
        self.setStyleSheet(theme_manager.get_card_style(color_theme))
    
    def update_value(self, value):
        """Update card value"""
        self.value_label.setText(str(value))
    
    def update_title(self, title):
        """Update card title"""
        self.title_label.setText(title)
    
    def update_description(self, description):
        """Update card description"""
        if hasattr(self, 'desc_label'):
            self.desc_label.setText(description)


class HomePage(QWidget):
    """Home page dashboard"""
    
    # Signals
    quick_action_requested = pyqtSignal(str)  # Signal for quick actions
    
    def __init__(self, account_manager=None, parent=None):
        super().__init__(parent)
        self.account_manager = account_manager
        self.warp_data_reader = WarpUserDataManager()
        self.registry_manager = warp_registry_manager  # 添加注册表管理器
        self.init_ui()
        
        # Setup timer for periodic updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_stats)
        self.update_timer.start(30000)  # Update every 30 seconds for real-time data
        
        # Initial stats update
        self.update_stats()

        # 独立的页头时间定时器（每秒更新），避免依赖已删除的欢迎卡片
        self.header_time_timer = QTimer()
        self.header_time_timer.timeout.connect(self.update_header_time)
        self.header_time_timer.start(1000)
        self.update_header_time()
    
    def init_ui(self):
        """Initialize home page UI"""
        # Create main container card - 保持与其他页面一致的最外层卡片布局
        main_container = QFrame()
        main_container.setFrameStyle(QFrame.NoFrame)
        # 使用theme_manager的统一样式
        main_container.setStyleSheet(theme_manager.get_main_container_style())
        
        layout = QVBoxLayout(main_container)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(25)
        
        # Page header (title and description)
        header_section = self.create_page_header()
        layout.addWidget(header_section)
        
        # Warp client status section
        warp_status_section = self.create_warp_status_section()
        layout.addWidget(warp_status_section)
        
        # Bottom buttons section
        buttons_section = self.create_bottom_buttons_section()
        layout.addWidget(buttons_section)
        
        # Set main container as the widget's layout - 保持原来的垂直布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(main_container)
        self.setLayout(main_layout)
    
    def create_page_header(self):
        """Create unified page header with title and description"""
        header = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 10)  # 减少底部边距
        layout.setSpacing(12)
        
        # Left side - Title and description
        left_layout = QVBoxLayout()
        left_layout.setSpacing(4)  # 减少标题和描述之间的间距
        
        # Page title
        title_label = QLabel("🏠 仪表盘")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))  # 减小标题字号
        title_label.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; background: transparent; border: none; outline: none; border-radius: 8px; padding: 6px 12px;")
        left_layout.addWidget(title_label)
        
        # Page description
        desc_label = QLabel("查看系统状态和Warp账户信息")
        desc_label.setFont(QFont("Segoe UI", 11))  # 减小描述字号
        desc_label.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; background: transparent; border: none; outline: none; border-radius: 6px; padding: 4px 8px;")
        left_layout.addWidget(desc_label)
        
        layout.addLayout(left_layout)
        layout.addStretch()
        
        # Right side - Current time
        time_container = QWidget()
        # Use theme manager for time container styling
        time_container.setStyleSheet(theme_manager.get_time_container_style())
        time_layout = QHBoxLayout(time_container)
        time_layout.setContentsMargins(6, 3, 8, 3)  # 进一步减少内边距
        time_layout.setSpacing(4)  # 减少图标和文字间距
        
        clock_icon = QLabel("🕒")
        clock_icon.setObjectName("icon")  # 设置为icon类型，不受全局样式影响
        clock_icon.setFont(QFont("Segoe UI Emoji", 12))  # 减小图标大小
        clock_icon.setStyleSheet("background: transparent; border: none; padding: 0; margin: 0;")
        time_layout.addWidget(clock_icon)
        
        self.header_time_label = QLabel()
        self.header_time_label.setObjectName("time")  # 设置特殊标识，不受全局样式影响
        self.header_time_label.setFont(QFont("Segoe UI", 10, QFont.Medium))  # 减小字号
        self.header_time_label.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; background: transparent; border: none; padding: 0; margin: 0;")
        self.update_header_time()
        time_layout.addWidget(self.header_time_label)
        
        layout.addWidget(time_container)
        
        header.setLayout(layout)
        return header
    
    def update_header_time(self):
        """Update header time display"""
        if hasattr(self, 'header_time_label'):
            current_time = datetime.now().strftime("%H:%M:%S")
            self.header_time_label.setText(current_time)
    
    def create_welcome_section(self):
        """Create modern welcome section with enhanced design"""
        section = QWidget()
        section.setMinimumHeight(120)  # 使用最小高度而非固定高度
        
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
        self.welcome_label = QLabel(_('home_welcome_title'))
        self.welcome_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        self.welcome_label.setStyleSheet("""
            color: qlineargradient(
                x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 #63b3ed,
                stop: 1 #8b5cf6
            );
            background: transparent;
        """)
        content_layout.addWidget(self.welcome_label)
        
        # Subtitle with better styling
        self.subtitle = QLabel(_('home_welcome_subtitle'))
        self.subtitle.setFont(QFont("Segoe UI", 13))
        self.subtitle.setStyleSheet("color: #cbd5e0; background: transparent; line-height: 1.4;")
        self.subtitle.setWordWrap(True)
        content_layout.addWidget(self.subtitle)
        
        layout.addLayout(content_layout)
        
        # Right side - Time and Status indicators
        right_side_layout = QVBoxLayout()
        right_side_layout.setSpacing(15)
        right_side_layout.setAlignment(Qt.AlignTop)
        
        # Current time with icon (moved to right side)
        time_container = QWidget()
        time_container.setStyleSheet("""
            QWidget {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 8px;
            }
        """)
        time_layout = QHBoxLayout(time_container)
        time_layout.setContentsMargins(10, 5, 10, 5)
        
        clock_icon = QLabel("🕒")
        clock_icon.setFont(QFont("Segoe UI Emoji", 14))
        clock_icon.setStyleSheet("background: transparent; border: none; outline: none; border-radius: 6px; padding: 4px;")
        time_layout.addWidget(clock_icon)
        
        self.time_label = QLabel()
        self.time_label.setFont(QFont("Segoe UI", 11, QFont.Medium))
        self.time_label.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; background: transparent; border: none; outline: none; border-radius: 6px; padding: 4px 8px;")
        self.update_time()
        time_layout.addWidget(self.time_label)
        
        right_side_layout.addWidget(time_container)
        
        # Online status indicator
        status_container = QWidget()
        status_container.setFixedSize(130, 70)
        status_container.setStyleSheet("""
            QWidget {
                background: rgba(16, 185, 129, 0.1);
                border: 1px solid rgba(16, 185, 129, 0.3);
                border-radius: 12px;
            }
        """)
        
        status_inner_layout = QVBoxLayout(status_container)
        status_inner_layout.setContentsMargins(15, 10, 15, 10)
        status_inner_layout.setSpacing(5)
        
        status_icon = QLabel("🟢")
        status_icon.setFont(QFont("Segoe UI Emoji", 18))
        status_icon.setAlignment(Qt.AlignCenter)
        status_icon.setStyleSheet("background: transparent; border: none; outline: none; border-radius: 6px; padding: 4px;")
        status_inner_layout.addWidget(status_icon)
        
        self.status_text = QLabel(_('home_system_online'))
        self.status_text.setFont(QFont("Segoe UI", 9, QFont.Medium))
        self.status_text.setStyleSheet(f"color: {theme_manager.get_color('accent_green')}; background: transparent; border: none; outline: none; border-radius: 6px; padding: 4px 8px;")
        self.status_text.setAlignment(Qt.AlignCenter)
        status_inner_layout.addWidget(self.status_text)
        
        right_side_layout.addWidget(status_container)
        layout.addLayout(right_side_layout)
        
        layout.addStretch()
        section.setLayout(layout)
        
        # Timer for time updates
        if not hasattr(self, 'time_timer'):
            self.time_timer = QTimer()
            self.time_timer.timeout.connect(self.update_time)
            self.time_timer.start(1000)  # Update every second
        
        return section
    
    def create_bottom_buttons_section(self):
        """Create bottom buttons section"""
        section = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 15, 0, 0)
        layout.setSpacing(20)
        
        # Add stretch to center the buttons
        layout.addStretch()
        
        # Refresh button
        self.refresh_btn = QPushButton("🔄 刷新信息")
        self.refresh_btn.setFont(QFont("Segoe UI", 12, QFont.Medium))
        self.refresh_btn.setMinimumHeight(45)
        self.refresh_btn.setMinimumWidth(150)
        # Use theme manager for button styling
        self.refresh_btn.setStyleSheet(theme_manager.get_button_style('primary'))
        self.refresh_btn.clicked.connect(self.refresh_warp_status)
        layout.addWidget(self.refresh_btn)
        
        # Save account button
        self.save_btn = QPushButton("💾 保存当前账户")
        self.save_btn.setFont(QFont("Segoe UI", 12, QFont.Medium))
        self.save_btn.setMinimumHeight(45)
        self.save_btn.setMinimumWidth(150)
        # Use theme manager for button styling
        self.save_btn.setStyleSheet(theme_manager.get_button_style('success'))
        self.save_btn.clicked.connect(self.save_current_account)
        layout.addWidget(self.save_btn)
        
        # Add stretch to center the buttons
        layout.addStretch()
        
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
        title_icon.setStyleSheet(f"color: {theme_manager.get_color('accent_orange')}; background: transparent; border: none; outline: none; border-radius: 6px; padding: 4px;")
        title_layout.addWidget(title_icon)
        
        self.actions_title_label = QLabel(_('home_quick_actions'))
        self.actions_title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.actions_title_label.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; background: transparent; border: none; outline: none; border-radius: 8px; padding: 6px 12px;")
        title_layout.addWidget(self.actions_title_label)
        
        title_layout.addStretch()
        
        # Actions counter
        self.actions_count = QLabel(_('home_actions_count'))
        self.actions_count.setFont(QFont("Segoe UI", 10, QFont.Medium))
        self.actions_count.setStyleSheet(f"color: {theme_manager.get_color('text_muted')}; background: transparent; border: none; outline: none; border-radius: 6px; padding: 4px 8px;")
        title_layout.addWidget(self.actions_count)
        
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
        self.accounts_btn = create_modern_button(_('home_manage_accounts'), "📊", "blue")
        self.accounts_btn.clicked.connect(lambda: self.quick_action_requested.emit("accounts"))
        buttons_layout.addWidget(self.accounts_btn)
        
        # Refresh all
        self.refresh_btn = create_modern_button(_('home_refresh_all'), "🔄", "orange")
        self.refresh_btn.clicked.connect(lambda: self.quick_action_requested.emit("refresh"))
        buttons_layout.addWidget(self.refresh_btn)
        
        # Add account
        self.add_btn = create_modern_button(_('home_add_account_btn'), "➕", "green")
        self.add_btn.clicked.connect(lambda: self.quick_action_requested.emit("add"))
        buttons_layout.addWidget(self.add_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        section.setLayout(layout)
        return section
    
    def create_warp_status_section(self):
        """Create Warp client status section with two-row card layout"""
        section = QWidget()
        # 直接使用布局，不限制最大宽度，让卡片自适应填充
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # First row - Two cards side by side
        first_row = QHBoxLayout()
        first_row.setSpacing(20)
        
        # Left card - Account status overview
        self.account_status_card = self.create_account_overview_card()
        first_row.addWidget(self.account_status_card)
        
        # Right card - Subscription information
        self.subscription_card = self.create_subscription_card()
        first_row.addWidget(self.subscription_card)
        
        layout.addLayout(first_row)
        
        # Second row - Software information card
        second_row = QHBoxLayout()
        second_row.setSpacing(20)
        
        # Software info card
        self.software_info_card = self.create_software_info_card()
        second_row.addWidget(self.software_info_card)
        
        # Add stretch to balance the layout
        second_row.addStretch()
        
        layout.addLayout(second_row)
        
        section.setLayout(layout)
        return section
    
    def create_account_overview_card(self):
        """Create left card - Account status overview (simplified)"""
        card = QFrame()
        card.setFrameStyle(QFrame.NoFrame)
        # 移除高度限制，让卡片根据内容自适应高度
        card.setMinimumWidth(280)  # 设置最小宽度避免过窄
        # 移除最大宽度限制，让卡片自适应填充空间
        
        # Use theme manager for card styling
        card.setStyleSheet(theme_manager.get_card_style('blue'))
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)  # 进一步减少内边距
        layout.setSpacing(8)  # 进一步减少间距
        
        # Card header - 简化并减小占用空间
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 5)  # 减少底部边距
        
        account_icon = QLabel("📊")
        account_icon.setFont(QFont("Segoe UI Emoji", 14))  # 减小图标大小
        account_icon.setStyleSheet("color: #3b82f6; background: transparent;")
        header_layout.addWidget(account_icon)
        
        account_title = QLabel("账户状态")
        account_title.setFont(QFont("Segoe UI", 12, QFont.Bold))  # 减小标题字号
        account_title.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; background: transparent;")
        header_layout.addWidget(account_title)
        
        header_layout.addStretch()
        
        # Status indicator
        self.status_indicator = QLabel("● 在线")
        self.status_indicator.setFont(QFont("Segoe UI", 9, QFont.Medium))  # 减小状态字号
        self.status_indicator.setStyleSheet(f"color: {theme_manager.get_color('accent_green')}; background: transparent;")
        header_layout.addWidget(self.status_indicator)
        
        layout.addLayout(header_layout)
        
        # Account info section - 移除二级标题，直接显示信息
        info_section = QVBoxLayout()
        info_section.setSpacing(8)  # 减少信息间距
        
        # Email field - 添加圆角背景
        self.email_label = QLabel("邮箱地址: scottg2020@newbt.dpdns.org")
        self.email_label.setProperty("class", "field")  # 设置class属性以应用圆角样式
        self.email_label.setFont(QFont("Segoe UI", 11))
        self.email_label.setStyleSheet(f"color: {theme_manager.get_color('accent_blue')};")
        self.email_label.setWordWrap(True)  # 启用自动换行
        self.email_label.setTextInteractionFlags(Qt.TextSelectableByMouse)  # 允许选择文本
        info_section.addWidget(self.email_label)
        
        # User ID field - 添加圆角背景
        self.user_id_label = QLabel("用户ID: t9yuLuaoU6P45wWkie4l...")
        self.user_id_label.setProperty("class", "field")  # 设置class属性以应用圆角样式
        self.user_id_label.setFont(QFont("Segoe UI", 11))
        self.user_id_label.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')};")
        self.user_id_label.setWordWrap(True)  # 启用自动换行
        self.user_id_label.setTextInteractionFlags(Qt.TextSelectableByMouse)  # 允许选择文本
        info_section.addWidget(self.user_id_label)
        
        # Token status field - 添加圆角背景
        self.token_status_label = QLabel("令牌状态: ✅ 有效")
        self.token_status_label.setProperty("class", "field")  # 设置class属性以应用圆角样式
        self.token_status_label.setFont(QFont("Segoe UI", 11))
        self.token_status_label.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')};")
        self.token_status_label.setWordWrap(True)  # 启用自动换行
        info_section.addWidget(self.token_status_label)
        
        # Token expiry field - 添加圆角背景
        self.token_expiry_label = QLabel("令牌过期: 2025-09-22 15:39 (剩余59分钟)")
        self.token_expiry_label.setProperty("class", "field")  # 设置class属性以应用圆角样式
        self.token_expiry_label.setFont(QFont("Segoe UI", 11))
        self.token_expiry_label.setStyleSheet(f"color: {theme_manager.get_color('accent_orange')};")
        self.token_expiry_label.setWordWrap(True)  # 启用自动换行
        info_section.addWidget(self.token_expiry_label)
        
        layout.addLayout(info_section)
        
        # 移除 addStretch()，让内容自然填充
        
        return card
    
    def create_subscription_card(self):
        """创建右卡片 - 订阅信息（从注册表获取真实数据）"""
        card = QFrame()
        card.setFrameStyle(QFrame.NoFrame)
        card.setMinimumWidth(280)
        
        # Use theme manager for card styling
        card.setStyleSheet(theme_manager.get_card_style('green'))
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)
        
        # Card header
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 5)
        
        subscription_icon = QLabel("⭐")
        subscription_icon.setFont(QFont("Segoe UI Emoji", 14))
        subscription_icon.setStyleSheet("color: #10b981; background: transparent;")
        header_layout.addWidget(subscription_icon)
        
        subscription_title = QLabel("订阅信息")
        subscription_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        subscription_title.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; background: transparent;")
        header_layout.addWidget(subscription_title)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Subscription details
        details_section = QVBoxLayout()
        details_section.setSpacing(8)
        
        # 从注册表获取AIRequestLimitInfo（使用优化后的方法）
        limit_data = warp_registry_manager.get_ai_request_limit_info()
        
        # 套餐类型 (根据request_limit_refresh_duration判断)
        refresh_duration = limit_data.get("request_limit_refresh_duration", "EveryTwoWeeks")
        plan_type = "Trial Pro" if refresh_duration == "EveryTwoWeeks" else "Pro"
        self.plan_label = QLabel(f"套餐类型: {plan_type}")
        self.plan_label.setFont(QFont("Segoe UI", 11, QFont.Medium))
        self.plan_label.setStyleSheet(f"""
            QLabel {{
                color: {theme_manager.get_color('accent_blue')};
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 8px 12px;
            }}
        """)
        details_section.addWidget(self.plan_label)
        
        # 使用量
        limit = limit_data.get("limit", 2500)
        used = limit_data.get("num_requests_used_since_refresh", 0)
        self.usage_label = QLabel(f"使用量: {used} / {limit} 次")
        self.usage_label.setFont(QFont("Segoe UI", 11))
        self.usage_label.setStyleSheet(f"""
            QLabel {{
                color: {theme_manager.get_color('text_secondary')};
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 8px 12px;
            }}
        """)
        details_section.addWidget(self.usage_label)
        
        # 使用率（直接从注册表管理器获取）
        usage_percent = limit_data.get('usage_percentage', 0)
        percent_color = theme_manager.get_color('accent_green')
        if usage_percent >= 80:
            percent_color = theme_manager.get_color('accent_red')
        elif usage_percent >= 50:
            percent_color = theme_manager.get_color('accent_orange')
        
        self.percentage_label = QLabel(f"使用率: {usage_percent}%")
        self.percentage_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.percentage_label.setStyleSheet(f"""
            QLabel {{
                color: {percent_color};
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 8px 12px;
            }}
        """)
        details_section.addWidget(self.percentage_label)
        
        # 账户过期时间（直接使用格式化后的数据）
        expiry_time = limit_data.get('next_refresh_time_formatted', '未知')
        days_left = limit_data.get('days_until_refresh', -1)
        
        expiry_text = "账户过期: "
        if expiry_time != '未知':
            if days_left >= 0:
                expiry_text += f"{expiry_time} (剩余{days_left}天)"
            else:
                expiry_text += f"{expiry_time} (已过期)"
        else:
            expiry_text += "未知"
        
        self.expiry_label = QLabel(expiry_text)
        self.expiry_label.setFont(QFont("Segoe UI", 11, QFont.Medium))
        expiry_color = theme_manager.get_color('accent_orange') if days_left < 7 else theme_manager.get_color('accent_green')
        self.expiry_label.setStyleSheet(f"""
            QLabel {{
                color: {expiry_color};
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 8px 12px;
            }}
        """)
        details_section.addWidget(self.expiry_label)
        
        # 刷新周期（直接使用格式化后的数据）
        refresh_text = "刷新周期: " + limit_data.get('refresh_duration_formatted', '每两周')
        
        self.refresh_label = QLabel(refresh_text)
        self.refresh_label.setFont(QFont("Segoe UI", 11))
        self.refresh_label.setStyleSheet(f"""
            QLabel {{
                color: {theme_manager.get_color('accent_blue')};
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 8px 12px;
            }}
        """)
        details_section.addWidget(self.refresh_label)
        
        layout.addLayout(details_section)
        
        # 移除 addStretch()，让内容自然填充
        
        return card
    
    def create_software_info_card(self):
        """创建软件信息卡片（从注册表获取真实数据）"""
        card = QFrame()
        card.setFrameStyle(QFrame.NoFrame)
        card.setMinimumWidth(280)
        
        # Use theme manager for card styling
        card.setStyleSheet(theme_manager.get_card_style('orange'))
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)
        
        # Card header
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 5)
        
        software_icon = QLabel("🔒")
        software_icon.setFont(QFont("Segoe UI Emoji", 14))
        software_icon.setStyleSheet("color: #f59e0b; background: transparent;")
        header_layout.addWidget(software_icon)
        
        software_title = QLabel("软件信息")
        software_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        software_title.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; background: transparent;")
        header_layout.addWidget(software_title)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Software details
        details_layout = QVBoxLayout()
        details_layout.setSpacing(6)
        
        # 获取机器码 (ExperimentId)
        experiment_id = warp_registry_manager.get_registry_value("ExperimentId") or "未知"
        
        self.machine_label = QLabel(f"机器码: {experiment_id}")
        self.machine_label.setFont(QFont("Segoe UI", 11))
        self.machine_label.setStyleSheet(f"""
            QLabel {{
                color: {theme_manager.get_color('accent_blue')};
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 8px 12px;
            }}
        """)
        self.machine_label.setWordWrap(True)
        self.machine_label.setTextInteractionFlags(Qt.TextSelectableByMouse)  # 允许选择文本
        details_layout.addWidget(self.machine_label)
        
        # 获取软件版本（使用优化后的方法）
        version = warp_registry_manager.get_latest_version()
        
        self.version_label = QLabel(f"软件版本: {version}")
        self.version_label.setFont(QFont("Segoe UI", 11))
        self.version_label.setStyleSheet(f"""
            QLabel {{
                color: {theme_manager.get_color('accent_blue')};
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 8px 12px;
            }}
        """)
        self.version_label.setWordWrap(True)
        details_layout.addWidget(self.version_label)
        
        layout.addLayout(details_layout)
        
        # 移除 addStretch()，让内容自然填充
        
        return card
    
    
    def update_warp_status(self):
        """Update Warp client status information by decrypting and displaying user data"""
        try:
            # Check if Warp data file exists
            if not self.warp_data_reader.user_file.exists():
                self.status_indicator.setText("❌ 文件不存在")
                self.email_label.setText("邮箱地址: 文件不存在")
                self.user_id_label.setText("用户ID: 文件不存在")
                self.token_status_label.setText("令牌状态: 文件不存在")
                self.token_expiry_label.setText("令牌过期: 文件不存在")
                # self.onboarded_label.setText("入门状态: 文件不存在")
                return
                
            # Try to decrypt and read user data
            user_data = self.warp_data_reader.read_user_file()
            
            if user_data:
                # Extract data from user_data
                email = user_data.get('email', 'N/A')
                local_id = user_data.get('local_id', 'N/A')
                is_onboarded = user_data.get('is_onboarded', False)
                
                # Get token information
                id_token_info = user_data.get('id_token', {})
                expiration_time = id_token_info.get('expiration_time', 'N/A')
                
                # Update status indicator
                self.status_indicator.setText("● 在线")
                
                # Update email
                self.email_label.setText(f"邮箱地址: {email if email != 'N/A' else '无邮箱'}")
                
                # Update user ID (show first 12 characters)
                if local_id != 'N/A' and len(str(local_id)) > 12:
                    user_id_display = str(local_id)[:12] + "..."
                else:
                    user_id_display = str(local_id) if local_id != 'N/A' else '无ID'
                self.user_id_label.setText(f"用户ID: {user_id_display}")
                
                # Update token status and expiry
                if expiration_time != 'N/A' and expiration_time:
                    try:
                        from datetime import datetime
                        
                        # 简化时间解析 - 截断微秒为6位
                        time_str = expiration_time
                        if '.' in time_str and len(time_str.split('.')[1].split('+')[0]) > 6:
                            # 处理超长微秒部分
                            parts = time_str.split('.')
                            microsec_and_tz = parts[1]
                            if '+' in microsec_and_tz:
                                microsec = microsec_and_tz.split('+')[0][:6]
                                tz = '+' + microsec_and_tz.split('+')[1]
                                time_str = f"{parts[0]}.{microsec}{tz}"
                        
                        exp_time = datetime.fromisoformat(time_str)
                        now = datetime.now(exp_time.tzinfo) if exp_time.tzinfo else datetime.now()
                        
                        if exp_time > now:
                            token_status = "✅ 有效"
                            # 简化时间计算 - 只显示分钟
                            minutes_remaining = int((exp_time - now).total_seconds() // 60)
                            if minutes_remaining > 60:
                                remaining = f"(剩余{minutes_remaining//60}小时{minutes_remaining%60}分钟)"
                            else:
                                remaining = f"(剩余{minutes_remaining}分钟)"
                        else:
                            token_status = "❌ 已过期"
                            remaining = ""
                        
                        # 显示过期时间
                        expiry_display = exp_time.strftime("%H:%M:%S")
                        self.token_expiry_label.setText(f"令牌过期: {expiry_display} {remaining}")
                        
                    except Exception as parse_error:
                        token_status = "❓ 解析失败"
                        self.token_expiry_label.setText(f"令牌过期: 解析失败 ({parse_error})")
                        
                else:
                    token_status = "❌ 无令牌"
                    self.token_expiry_label.setText("令牌过期: 无令牌信息")
                    
                self.token_status_label.setText(f"令牌状态: {token_status}")
                
                # Update onboarded status (removed from simplified card layout)
                # onboard_status = "✅ 已完成" if is_onboarded else "❌ 未完成"
                # self.onboarded_label.setText(f"入门状态: {onboard_status}")
                
                # Update last refresh time (removed from simplified card layout)
                # from datetime import datetime
                # current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # self.last_update_label.setText(f"上次更新: {current_time}")
                
                # Store current user data for saving
                self.current_user_data = user_data
                
                # Print full user_data to console
                print(f"🔓 Warp user_data 解密成功:")
                for key, value in user_data.items():
                    print(f"  {key}: {value}")
                
            else:
                raise Exception("Failed to decrypt user data")
                
        except Exception as e:
            print(f"Error updating Warp status: {e}")
            # Set error values
            self.status_indicator.setText("❌ 解密失败")
            self.email_label.setText(f"邮箱地址: 错误 - {str(e)[:30]}...")
            self.user_id_label.setText("用户ID: 解密失败")
            self.token_status_label.setText("令牌状态: 解密失败")
            self.token_expiry_label.setText("令牌过期: 解密失败")
            # self.onboarded_label.setText("入门状态: 解密失败")
    
    def update_time(self):
        """Update current time display with icon"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if hasattr(self, 'time_label'):
            self.time_label.setText(_('home_current_time', current_time))
        # Also update header time
        self.update_header_time()
    
    def update_stats(self):
        """Update dashboard statistics including Warp status"""
        # Update Warp client status
        self.update_warp_status()
    
    def update_proxy_status(self, is_enabled):
        """Update proxy status - placeholder for future updates"""
        # Proxy status card has been removed, this method kept for compatibility
        pass
    
    def refresh_warp_status(self):
        """Manually refresh Warp status information"""
        print("🔄 手动刷新 Warp 账户状态...")
        self.status_indicator.setText("🔄 刷新中...")
        self.update_warp_status()
    
    def save_current_account(self):
        """Save current Warp account to account manager"""
        try:
            if not hasattr(self, 'current_user_data') or not self.current_user_data:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "警告", "没有可保存的账户数据！\n\n请先刷新账户信息。")
                return
            
            user_data = self.current_user_data
            email = user_data.get('email', '')
            
            if not email:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "警告", "无法获取账户邮箱信息！")
                return
            
            # 检查是否已经存在该账户
            if self.account_manager:
                existing_accounts = self.account_manager.get_all_accounts()
                for account in existing_accounts:
                    if account.get('email') == email:
                        from PyQt5.QtWidgets import QMessageBox
                        reply = QMessageBox.question(
                            self, 
                            "确认覆盖", 
                            f"账户 {email} 已存在！\n\n是否要更新该账户的信息？",
                            QMessageBox.Yes | QMessageBox.No
                        )
                        if reply != QMessageBox.Yes:
                            return
                        break
            
            # 准备保存的账户数据
            account_data = {
                'email': email,
                'id': user_data.get('local_id', ''),
                'token': user_data.get('id_token', {}).get('id_token', ''),
                'refresh_token': user_data.get('id_token', {}).get('refresh_token', ''),
                'display_name': user_data.get('display_name', ''),
                'is_onboarded': user_data.get('is_onboarded', False),
                'expiration_time': user_data.get('id_token', {}).get('expiration_time', ''),
                'created_at': user_data.get('linked_at', ''),
                'source': 'warp_client_import'  # 标记来源
            }
            
            # 保存到账户管理器
            if self.account_manager:
                success = self.account_manager.add_account_data(account_data)
                if success:
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.information(
                        self, 
                        "成功", 
                        f"账户 {email} 已成功保存到账户管理器！\n\n您可以在账户管理页面查看和管理此账户。"
                    )
                    print(f"💾 成功保存账户: {email}")
                else:
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.critical(self, "错误", f"保存账户 {email} 失败！")
            else:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "警告", "账户管理器不可用！")
                
        except Exception as e:
            print(f"❌ 保存账户错误: {e}")
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "错误", f"保存账户时发生错误:\n\n{str(e)}")
    
    def refresh_ui_texts(self):
        """Refresh all UI texts when language changes"""
        # 更新页头时间
        self.update_header_time()

        # 欢迎卡片已移除：仅在相关控件存在时才更新，避免属性不存在报错
        if hasattr(self, 'welcome_label'):
            self.welcome_label.setText(_('home_welcome_title'))
        if hasattr(self, 'subtitle'):
            self.subtitle.setText(_('home_welcome_subtitle'))
        if hasattr(self, 'status_text'):
            self.status_text.setText(_('home_system_online'))

        # 快速操作（若存在）
        if hasattr(self, 'actions_title_label'):
            self.actions_title_label.setText(_('home_quick_actions'))
        if hasattr(self, 'actions_count'):
            self.actions_count.setText(_('home_actions_count'))

        # 底部按钮（若存在）
        if hasattr(self, 'accounts_btn'):
            self.accounts_btn.setText(f"📊 {_('home_manage_accounts')}")
        if hasattr(self, 'refresh_btn'):
            self.refresh_btn.setText(f"🔄 {_('home_refresh_all')}")
        if hasattr(self, 'add_btn'):
            self.add_btn.setText(f"➕ {_('home_add_account_btn')}")

        # Warp 状态区（若存在）
        if hasattr(self, 'warp_title_label'):
            self.warp_title_label.setText(_('warp_status'))
        if hasattr(self, 'installation_card'):
            self.installation_card.update_title(_('warp_installation'))
        if hasattr(self, 'data_status_card'):
            self.data_status_card.update_title(_('warp_data_status'))
        if hasattr(self, 'database_size_card'):
            self.database_size_card.update_title(_('warp_database_size'))
        if hasattr(self, 'user_file_card'):
            self.user_file_card.update_title(_('warp_user_file_status'))
        
