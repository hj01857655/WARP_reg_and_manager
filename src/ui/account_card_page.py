#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Account Card Page - Modern card-based account management interface
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QScrollArea, QGridLayout, QGroupBox, QLineEdit,
    QMessageBox, QProgressBar, QTableWidget, QTableWidgetItem,
    QHeaderView, QStackedWidget, QButtonGroup, QCheckBox,
    QComboBox, QMenu, QAction, QFileDialog, QDialog,
    QDialogButtonBox, QFormLayout, QSpinBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QPalette, QColor
from src.config.languages import _
from src.ui.theme_manager import theme_manager
import json
from datetime import datetime


class AccountCard(QFrame):
    """Individual account card widget"""
    
    action_requested = pyqtSignal(str, dict)  # action_type, account_data
    
    def __init__(self, account_data, parent=None):
        super().__init__(parent)
        self.account_data = account_data
        self.init_ui()
    
    def init_ui(self):
        """Initialize card UI"""
        self.setObjectName("accountCard")
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet("""
            QFrame#accountCard {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                padding: 20px;
            }
            QFrame#accountCard:hover {
                border: 1px solid #007AFF;
                box-shadow: 0 4px 12px rgba(0, 122, 255, 0.15);
            }
        """)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(16)
        
        # Header section with status indicator
        header_layout = QHBoxLayout()
        
        # Status icon
        status_icon = self.get_status_icon()
        status_label = QLabel(status_icon)
        status_label.setFont(QFont("Segoe UI Emoji", 24))
        status_label.setStyleSheet("background: transparent; border: none; outline: none; border-radius: 8px; padding: 6px;")
        header_layout.addWidget(status_label)
        
        # Account type badge
        type_badge = QLabel(self.account_data.get('type', 'Trial Pro'))
        type_badge.setStyleSheet("""
            QLabel {
                background-color: #007AFF;
                color: white;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: bold;
                border: none;
                outline: none;
            }
        """)
        header_layout.addWidget(type_badge)
        
        header_layout.addStretch()
        
        # Status text
        status_text = QLabel(self.get_status_text())
        status_text.setStyleSheet(f"color: {self.get_status_color()}; font-weight: bold; background: transparent; border: none; outline: none; border-radius: 6px; padding: 4px 8px;")
        header_layout.addWidget(status_text)
        
        layout.addLayout(header_layout)
        
        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("background-color: #f0f0f0;")
        layout.addWidget(divider)
        
        # Account info section
        info_group = QGroupBox("📧 账户信息")
        info_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #1a1a1a;
                border: none;
                margin-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 0px;
            }
        """)
        info_layout = QVBoxLayout()
        
        # Email
        email_layout = QHBoxLayout()
        email_label = QLabel("邮箱地址:")
        email_label.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; background: transparent; border: none; outline: none; border-radius: 6px; padding: 4px 8px;")
        email_value = QLabel(self.account_data.get('email', 'unknown@email.com'))
        email_value.setStyleSheet(f"color: {theme_manager.get_color('accent_blue')}; font-family: monospace; background: transparent; border: none; outline: none; border-radius: 6px; padding: 4px 8px;")
        email_value.setTextInteractionFlags(Qt.TextSelectableByMouse)
        email_layout.addWidget(email_label)
        email_layout.addWidget(email_value)
        email_layout.addStretch()
        info_layout.addLayout(email_layout)
        
        # User ID
        id_layout = QHBoxLayout()
        id_label = QLabel("用户ID:")
        id_label.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; background: transparent; border: none; outline: none; border-radius: 6px; padding: 4px 8px;")
        id_value = QLabel(self.account_data.get('user_id', 'N/A')[:20] + "...")
        id_value.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-family: monospace; background: transparent; border: none; outline: none; border-radius: 6px; padding: 4px 8px;")
        id_value.setToolTip(self.account_data.get('user_id', 'N/A'))
        id_layout.addWidget(id_label)
        id_layout.addWidget(id_value)
        id_layout.addStretch()
        info_layout.addLayout(id_layout)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Usage info section
        usage_group = QGroupBox("📊 使用情况")
        usage_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #1a1a1a;
                border: none;
                margin-top: 8px;
            }
        """)
        usage_layout = QVBoxLayout()
        
        # Usage bar
        usage_bar = QProgressBar()
        usage_value = self.get_usage_percentage()
        usage_bar.setValue(usage_value)
        usage_bar.setStyleSheet("""
            QProgressBar {
                background-color: #f0f0f0;
                border: none;
                border-radius: 8px;
                height: 20px;
                text-align: center;
                color: #1a1a1a;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: """ + self.get_usage_color(usage_value) + """;
                border-radius: 8px;
            }
        """)
        usage_bar.setFormat(f"{self.account_data.get('usage', '0')} / 2500 GB")
        usage_layout.addWidget(usage_bar)
        
        # Expiry date
        expiry_layout = QHBoxLayout()
        expiry_label = QLabel("过期时间:")
        expiry_label.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; background: transparent; border: none; outline: none; border-radius: 6px; padding: 4px 8px;")
        expiry_value = QLabel(self.format_expiry_date())
        expiry_value.setStyleSheet(f"color: {self.get_expiry_color()}; font-weight: bold; background: transparent; border: none; outline: none; border-radius: 6px; padding: 4px 8px;")
        expiry_layout.addWidget(expiry_label)
        expiry_layout.addWidget(expiry_value)
        expiry_layout.addStretch()
        usage_layout.addLayout(expiry_layout)
        
        usage_group.setLayout(usage_layout)
        layout.addWidget(usage_group)
        
        # Software info section
        software_group = QGroupBox("🔧 软件信息")
        software_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #1a1a1a;
                border: none;
                margin-top: 8px;
            }
        """)
        software_layout = QVBoxLayout()
        
        # Machine ID
        machine_layout = QHBoxLayout()
        machine_label = QLabel("机器码:")
        machine_label.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; background: transparent; border: none; outline: none; border-radius: 6px; padding: 4px 8px;")
        machine_value = QLabel(self.account_data.get('machine_id', 'N/A')[:30] + "...")
        machine_value.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-family: monospace; font-size: 11px; background: transparent; border: none; outline: none; border-radius: 6px; padding: 4px 8px;")
        machine_value.setToolTip(self.account_data.get('machine_id', 'N/A'))
        machine_layout.addWidget(machine_label)
        machine_layout.addWidget(machine_value)
        machine_layout.addStretch()
        software_layout.addLayout(machine_layout)
        
        software_group.setLayout(software_layout)
        layout.addWidget(software_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 刷新信息")
        refresh_btn.setObjectName("secondaryButton")
        refresh_btn.setStyleSheet("""
            QPushButton#secondaryButton {
                background-color: #ffffff;
                color: #007AFF;
                border: 1px solid #007AFF;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton#secondaryButton:hover {
                background-color: rgba(0, 122, 255, 0.1);
            }
        """)
        refresh_btn.clicked.connect(lambda: self.action_requested.emit("refresh", self.account_data))
        button_layout.addWidget(refresh_btn)
        
        # Primary action button
        if self.is_active():
            action_btn = QPushButton("⏸️ 停止")
            action_btn.setObjectName("dangerButton")
            action_btn.setStyleSheet("""
                QPushButton#dangerButton {
                    background-color: #FF3B30;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-weight: 500;
                }
                QPushButton#dangerButton:hover {
                    background-color: #D70015;
                }
            """)
            action_btn.clicked.connect(lambda: self.action_requested.emit("stop", self.account_data))
        else:
            action_btn = QPushButton("▶️ 启动")
            action_btn.setObjectName("primaryButton")
            action_btn.setStyleSheet("""
                QPushButton#primaryButton {
                    background-color: #34C759;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-weight: 500;
                }
                QPushButton#primaryButton:hover {
                    background-color: #28A745;
                }
            """)
            action_btn.clicked.connect(lambda: self.action_requested.emit("start", self.account_data))
        
        button_layout.addWidget(action_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def get_status_icon(self):
        """Get status icon based on account status"""
        status = self.account_data.get('status', 'unknown')
        if status == 'active':
            return "✅"
        elif status == 'banned':
            return "🚫"
        elif status == 'expired':
            return "⏰"
        else:
            return "❓"
    
    def get_status_text(self):
        """Get status text"""
        status = self.account_data.get('status', 'unknown')
        if status == 'active':
            return "在线"
        elif status == 'banned':
            return "已封禁"
        elif status == 'expired':
            return "已过期"
        else:
            return "未知"
    
    def get_status_color(self):
        """Get status color"""
        status = self.account_data.get('status', 'unknown')
        if status == 'active':
            return "#34C759"
        elif status == 'banned':
            return "#FF3B30"
        elif status == 'expired':
            return "#FF9500"
        else:
            return "#666666"
    
    def get_usage_percentage(self):
        """Calculate usage percentage"""
        try:
            usage_str = str(self.account_data.get('usage', '0'))
            # Extract numeric value from string like "250 GB" or "250"
            usage_str = usage_str.replace('GB', '').replace('gb', '').strip()
            usage = float(usage_str) if usage_str else 0
            # Assuming 2500 GB is the limit
            percentage = min(100, int((usage / 2500) * 100))
            return percentage
        except:
            return 0
    
    def get_usage_color(self, percentage):
        """Get color based on usage percentage"""
        if percentage < 50:
            return "#34C759"
        elif percentage < 80:
            return "#FF9500"
        else:
            return "#FF3B30"
    
    def format_expiry_date(self):
        """Format expiry date"""
        expiry = self.account_data.get('expiry', '')
        if expiry and expiry != 'N/A':
            expiry_str = str(expiry)
            # If it looks like a date, try to format it
            if '-' in expiry_str or '/' in expiry_str:
                # Just return the date part if it has time
                return expiry_str.split(' ')[0] if ' ' in expiry_str else expiry_str
            return expiry_str
        return "永久"  # Permanent
    
    def get_expiry_color(self):
        """Get color based on expiry status"""
        expiry = str(self.account_data.get('expiry', ''))
        
        # Check if already expired
        if self.account_data.get('status') == 'expired':
            return "#FF3B30"  # Red
        
        # Check for days remaining in Chinese format
        if '剩余' in expiry:  # "remaining" in Chinese
            try:
                if '天' in expiry:  # days
                    days = int(expiry.split('剩余')[1].split('天')[0])
                    if days < 7:
                        return "#FF3B30"  # Red
                    elif days < 30:
                        return "#FF9500"  # Orange
                elif '分钟' in expiry or '小时' in expiry:  # minutes or hours
                    return "#FF3B30"  # Red for expiring soon
            except:
                pass
        
        return "#666666"  # Default gray
    
    def is_active(self):
        """Check if account is currently active"""
        return self.account_data.get('is_active', False)


class AccountCardPage(QWidget):
    """Main account management page with card layout"""
    
    def __init__(self, account_manager=None, parent=None):
        super().__init__(parent)
        self.account_manager = account_manager
        self.cards = []  # 保留cards属性以支持卡片视图（如果需要）
        self.search_text = ""  # 搜索文本
        self.selected_accounts = set()  # 选中的账户ID
        self.sort_column = 4  # 默认按账户过期列（第4列）排序
        self.sort_order = Qt.AscendingOrder  # 默认升序
        self.init_ui()
        self.load_accounts()
    
    def init_ui(self):
        """Initialize the page UI"""
        # Create main container card
        main_container = QFrame()
        main_container.setFrameStyle(QFrame.NoFrame)
        main_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 rgba(255, 255, 255, 0.98),
                    stop: 0.5 rgba(248, 250, 252, 0.95),
                    stop: 1 rgba(241, 245, 249, 0.98)
                );
                border: 1px solid rgba(226, 232, 240, 0.8);
                border-radius: 20px;
                margin: 10px;
            }
        """)
        
        # Container layout
        container_layout = QVBoxLayout(main_container)
        container_layout.setContentsMargins(30, 25, 30, 25)
        container_layout.setSpacing(25)
        
        # Page header (title and description)
        page_header = self.create_page_header()
        container_layout.addWidget(page_header)
        
        # Action buttons header
        action_header = self.create_action_header()
        container_layout.addWidget(action_header)
        
        # Table view - 直接使用表格视图
        self.create_table_view()
        container_layout.addWidget(self.table_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(main_container)
        self.setLayout(main_layout)
    
    def create_page_header(self):
        """Create unified page header with title and description"""
        header = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 10)  # 与home_page一致
        layout.setSpacing(12)  # 与home_page一致
        
        # Left side - Title and description
        left_layout = QVBoxLayout()
        left_layout.setSpacing(4)  # 与home_page一致
        
        # Page title - 与home_page和cleanup_page相同的样式
        title_label = QLabel("👥 账户管理")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))  # 统一字号
        title_label.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; background: transparent; border: none; outline: none; border-radius: 8px; padding: 6px 12px;")
        title_label.setObjectName("title")  # 设置objectName以排除全局样式
        left_layout.addWidget(title_label)
        
        # Page description - 与home_page和cleanup_page相同的样式
        desc_label = QLabel("查看和管理当前Warp Terminal账户信息")
        desc_label.setFont(QFont("Segoe UI", 11))  # 统一字号
        desc_label.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; background: transparent; border: none; outline: none; border-radius: 6px; padding: 4px 8px;")
        desc_label.setObjectName("title")  # 设置objectName以排除全局样式
        left_layout.addWidget(desc_label)
        
        layout.addLayout(left_layout)
        layout.addStretch()
        
        header.setLayout(layout)
        return header
    
    def create_action_header(self):
        """Create action buttons header"""
        header = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 15)
        layout.setSpacing(15)
        
        # 左边按钮组
        # 添加账户按钮
        add_btn = QPushButton("➕ 添加账户")
        add_btn.setStyleSheet(theme_manager.get_button_style('primary'))
        add_btn.clicked.connect(self.add_account)
        layout.addWidget(add_btn)
        
        # 刷新全部按钮
        refresh_btn = QPushButton("🔄 刷新全部")
        refresh_btn.setStyleSheet(theme_manager.get_button_style('primary'))
        refresh_btn.clicked.connect(self.refresh_all)
        layout.addWidget(refresh_btn)
        
        # 批量删除按钮
        batch_delete_btn = QPushButton("🗑️ 批量删除")
        batch_delete_btn.setStyleSheet(theme_manager.get_button_style('danger_outline'))
        batch_delete_btn.clicked.connect(self.batch_delete)
        layout.addWidget(batch_delete_btn)
        
        # 导入导出按钮
        import_btn = QPushButton("📥 导入")
        import_btn.setStyleSheet(theme_manager.get_button_style('secondary'))
        import_btn.clicked.connect(self.import_accounts)
        layout.addWidget(import_btn)
        
        export_btn = QPushButton("📤 导出")
        export_btn.setStyleSheet(theme_manager.get_button_style('secondary'))
        export_btn.clicked.connect(self.export_accounts)
        layout.addWidget(export_btn)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setStyleSheet("background-color: #dee2e6; margin: 0 10px;")
        layout.addWidget(separator)
        
        # 批量操作菜单
        batch_menu_btn = QPushButton("⚡ 批量操作")
        batch_menu_btn.setStyleSheet(theme_manager.get_button_style('warning'))
        batch_menu = QMenu()
        batch_menu.addAction("✅ 激活选中", self.batch_activate)
        batch_menu.addAction("⏸️ 暂停选中", self.batch_pause)
        batch_menu.addAction("🔄 刷新选中", self.batch_refresh_selected)
        batch_menu.addAction("📋 复制选中邮箱", self.copy_selected_emails)
        batch_menu_btn.setMenu(batch_menu)
        layout.addWidget(batch_menu_btn)
        
        layout.addStretch()
        
        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 搜索账号...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #ced4da;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                min-width: 250px;
            }
            QLineEdit:focus {
                border-color: #007AFF;
                outline: none;
            }
        """)
        self.search_input.textChanged.connect(self.on_search_text_changed)
        layout.addWidget(self.search_input)
        
        # 高级筛选按钮
        filter_btn = QPushButton("⚙️")
        filter_btn.setToolTip("高级筛选")
        filter_btn.setStyleSheet(theme_manager.get_button_style('primary'))
        filter_btn.clicked.connect(self.show_advanced_filter)
        layout.addWidget(filter_btn)
        
        header.setLayout(layout)
        return header
    
    def create_table_view(self):
        """创建表格视图"""
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(6)  # 选择, 邮箱, 状态, 限制, 账户过期, 操作
        self.table_widget.setHorizontalHeaderLabels([
            '',  # 选择列不需要文字，只有复选框
            _('table_email') if hasattr(_, 'table_email') else '邮箱',
            _('table_status') if hasattr(_, 'table_status') else '状态', 
            _('table_limit') if hasattr(_, 'table_limit') else '限制',
            _('table_expiry') if hasattr(_, 'table_expiry') else '账户过期',
            _('table_actions') if hasattr(_, 'table_actions') else '操作'
        ])
        
        # 创建全选复选框
        self.select_all_checkbox = QCheckBox()
        self.select_all_checkbox.setToolTip('全选/取消全选')
        self.select_all_checkbox.stateChanged.connect(self.toggle_select_all)
        
        # 表格样式 - 移除可能导致表头被截断的固定高度
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                gridline-color: #f0f0f0;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
                min-height: 40px;
            }
            QTableWidget::item:selected {
                background-color: rgba(0, 122, 255, 0.1);
                color: #1a1a1a;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                color: #495057;
                padding: 12px 8px;
                border: none;
                border-bottom: 2px solid #dee2e6;
                font-weight: bold;
                min-height: 45px;
            }
        """)
        
        # 设置表头
        header = self.table_widget.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Fixed)    # 选择
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # 邮箱
        header.setSectionResizeMode(2, QHeaderView.Fixed)    # 状态
        header.setSectionResizeMode(3, QHeaderView.Fixed)    # 限制
        header.setSectionResizeMode(4, QHeaderView.Fixed)    # 账户过期
        header.setSectionResizeMode(5, QHeaderView.Fixed)    # 操作
        
        header.resizeSection(0, 60)   # 选择
        header.resizeSection(2, 100)  # 状态
        header.resizeSection(3, 150)  # 限制
        header.resizeSection(4, 120)  # 账户过期
        header.resizeSection(5, 280)  # 操作 (启动、刷新、编辑、删除)
        
        # 设置垂直表头
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 启用表头点击排序
        self.table_widget.setSortingEnabled(False)  # 禁用自动排序，我们手动控制
        header.sectionClicked.connect(self.on_header_clicked)
        
        # 设置默认排序指示器（账户过期列，升序）
        header.setSortIndicator(4, Qt.AscendingOrder)
    
    def update_select_all_header(self):
        """在表头第一列设置全选复选框"""
        # 设置表头文本，简单使用文本标识
        header_labels = [
            '全选',  # 选择列
            _('table_email') if hasattr(_, 'table_email') else '邮箱',
            _('table_status') if hasattr(_, 'table_status') else '状态', 
            _('table_limit') if hasattr(_, 'table_limit') else '限制',
            _('table_expiry') if hasattr(_, 'table_expiry') else '账户过期',
            _('table_actions') if hasattr(_, 'table_actions') else '操作'
        ]
        self.table_widget.setHorizontalHeaderLabels(header_labels)
    
    
    def update_table_view(self):
        """更新表格视图数据"""
        if not self.account_manager:
            return
        
        accounts = self.account_manager.get_accounts_with_health_and_limits()
        
        # 应用搜索过滤
        if hasattr(self, 'search_text') and self.search_text:
            accounts = self.filter_accounts(accounts, self.search_text)
        
        # 应用排序
        accounts = self.sort_accounts(accounts)
        
        self.table_widget.setRowCount(len(accounts))
        
        # 在表头第一列显示全选复选框
        self.update_select_all_header()
        
        for row, account in enumerate(accounts):
            # 选择列 - 复选框
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout()
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox = QCheckBox()
            checkbox.setProperty('account_id', account.get('id'))
            # 添加状态改变信号，用于更新全选框状态
            checkbox.stateChanged.connect(self.update_select_all_state)
            checkbox_layout.addWidget(checkbox)
            checkbox_widget.setLayout(checkbox_layout)
            self.table_widget.setCellWidget(row, 0, checkbox_widget)
            
            # 邮箱
            email_item = QTableWidgetItem(account.get('email', 'unknown'))
            email_item.setToolTip(account.get('email', 'unknown'))  # 显示完整邮箱
            self.table_widget.setItem(row, 1, email_item)
            
            # 状态
            status = self.get_account_status_text(account)
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignCenter)
            # 根据状态设置颜色
            if account.get('is_active'):
                status_item.setForeground(QColor('#10B981'))
            elif account.get('status') == 'banned':
                status_item.setForeground(QColor('#EF4444'))
            else:
                status_item.setForeground(QColor('#F59E0B'))
            self.table_widget.setItem(row, 2, status_item)
            
            # 限制 (显示用量/限制)
            usage = account.get('usage', '0')
            limit = account.get('limit', '2500')
            limit_text = f"{usage}/{limit} GB"
            limit_item = QTableWidgetItem(limit_text)
            limit_item.setTextAlignment(Qt.AlignCenter)
            # 根据使用率设置颜色
            try:
                usage_percent = (float(usage) / float(limit)) * 100
                if usage_percent >= 90:
                    limit_item.setForeground(QColor('#EF4444'))  # 红色
                elif usage_percent >= 70:
                    limit_item.setForeground(QColor('#F59E0B'))  # 橙色
                else:
                    limit_item.setForeground(QColor('#10B981'))  # 绿色
            except:
                pass
            self.table_widget.setItem(row, 3, limit_item)
            
            # 账户过期
            expiry = self.format_account_expiry(account)
            expiry_item = QTableWidgetItem(expiry)
            expiry_item.setTextAlignment(Qt.AlignCenter)
            self.table_widget.setItem(row, 4, expiry_item)
            
            # 操作按钮
            action_widget = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(5, 2, 5, 2)
            action_layout.setSpacing(3)
            
            # 启动按钮
            start_btn = QPushButton("🚀")
            start_btn.setToolTip(_('table_action_start') if hasattr(_, 'table_action_start') else '启动')
            start_btn.setStyleSheet(theme_manager.get_table_button_style('success'))
            start_btn.clicked.connect(lambda checked, acc=account: self.start_account(acc))
            action_layout.addWidget(start_btn)
            
            # 刷新按钮
            refresh_btn = QPushButton("🔄")
            refresh_btn.setToolTip(_('table_action_refresh') if hasattr(_, 'table_action_refresh') else '刷新')
            refresh_btn.setStyleSheet(theme_manager.get_table_button_style('primary'))
            refresh_btn.clicked.connect(lambda checked, acc=account: self.refresh_account(acc))
            action_layout.addWidget(refresh_btn)
            
            # 编辑按钮
            edit_btn = QPushButton("✏️")
            edit_btn.setToolTip(_('table_action_edit') if hasattr(_, 'table_action_edit') else '编辑')
            edit_btn.setStyleSheet(theme_manager.get_table_button_style('warning'))
            edit_btn.clicked.connect(lambda checked, acc=account: self.edit_account(acc))
            action_layout.addWidget(edit_btn)
            
            # 删除按钮
            delete_btn = QPushButton("🗑️")
            delete_btn.setToolTip(_('table_action_delete') if hasattr(_, 'table_action_delete') else '删除')
            delete_btn.setStyleSheet(theme_manager.get_table_button_style('danger'))
            delete_btn.clicked.connect(lambda checked, acc=account: self.delete_account(acc))
            action_layout.addWidget(delete_btn)
            
            action_widget.setLayout(action_layout)
            self.table_widget.setCellWidget(row, 5, action_widget)
    
    def get_account_status_text(self, account):
        """获取账户状态文本"""
        if account.get('is_active'):
            return '✅ 活跃'
        elif account.get('status') == 'banned':
            return '❌ 封禁'
        else:
            return '⚠️ 未活跃'
    
    def format_account_expiry(self, account):
        """格式化账户过期时间"""
        expiry = account.get('expiry', '')
        if expiry and expiry != 'N/A':
            expiry_str = str(expiry)
            if '-' in expiry_str or '/' in expiry_str:
                return expiry_str.split(' ')[0] if ' ' in expiry_str else expiry_str
            return expiry_str
        return '永久'
    
    def start_account(self, account):
        """启动账户 - 切换到此账户"""
        try:
            account_id = account.get('id')
            if self.account_manager:
                self.account_manager.switch_account(account_id)
                QMessageBox.information(self, '成功', f'已切换到账户: {account.get("email")}')
                self.load_accounts()
        except Exception as e:
            QMessageBox.warning(self, '错误', f'切换账户失败: {str(e)}')
    
    def refresh_account(self, account):
        """刷新账户信息"""
        try:
            if self.account_manager:
                # 刷新单个账户的限制和状态
                self.account_manager.refresh_account_status(account.get('id'))
                self.load_accounts()
        except Exception as e:
            QMessageBox.warning(self, '错误', f'刷新账户失败: {str(e)}')
    
    def edit_account(self, account):
        """编辑账户信息"""
        # TODO: 弹出编辑对话框
        QMessageBox.information(self, '提示', f'编辑功能正在开发中\n账户: {account.get("email")}')
    
    def switch_account(self, account):
        """切换账户 - 与start_account相同"""
        self.start_account(account)
    
    def toggle_select_all(self, state):
        """全选/取消全选"""
        is_checked = state == Qt.Checked
        
        # 临时断开信号连接，避免循环触发
        for row in range(self.table_widget.rowCount()):
            checkbox_widget = self.table_widget.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox:
                    checkbox.stateChanged.disconnect()
                    checkbox.setChecked(is_checked)
                    checkbox.stateChanged.connect(self.update_select_all_state)
    
    def update_select_all_state(self):
        """根据单个复选框状态更新全选框状态"""
        if not hasattr(self, 'select_all_checkbox'):
            return
        
        checked_count = 0
        total_count = self.table_widget.rowCount()
        
        # 统计选中的数量
        for row in range(total_count):
            checkbox_widget = self.table_widget.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    checked_count += 1
        
        # 更新全选框状态
        self.select_all_checkbox.stateChanged.disconnect()
        if checked_count == 0:
            self.select_all_checkbox.setCheckState(Qt.Unchecked)
        elif checked_count == total_count:
            self.select_all_checkbox.setCheckState(Qt.Checked)
        else:
            self.select_all_checkbox.setCheckState(Qt.PartiallyChecked)
        self.select_all_checkbox.stateChanged.connect(self.toggle_select_all)
    
    
    def load_accounts(self):
        """加载账户列表 - 直接更新表格"""
        if not self.account_manager:
            return
        
        # 直接更新表格视图
        self.update_table_view()
    
    def batch_delete(self):
        """批量删除选中的账户"""
        selected_accounts = []
        
        # 获取所有选中的账户
        for row in range(self.table_widget.rowCount()):
            checkbox_widget = self.table_widget.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    account_id = checkbox.property('account_id')
                    selected_accounts.append(account_id)
        
        if not selected_accounts:
            QMessageBox.warning(self, '提示', '请先选择要删除的账户')
            return
        
        # 确认删除
        reply = QMessageBox.question(
            self, '确认删除',
            f'确定要删除{len(selected_accounts)}个账户吗？',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            for account_id in selected_accounts:
                try:
                    self.account_manager.delete_account(account_id)
                except Exception as e:
                    print(f'删除账户{account_id}失败: {e}')
            
            self.load_accounts()
            QMessageBox.information(self, '成功', f'已删除{len(selected_accounts)}个账户')
    
    def add_account(self):
        """添加新账户"""
        # TODO: 弹出添加账户对话框
        QMessageBox.information(self, '提示', '添加账户功能正在开发中')
    
    def refresh_all(self):
        """刷新所有账户信息"""
        try:
            if self.account_manager:
                # 刷新所有账户的限制和状态
                accounts = self.account_manager.get_accounts_with_health_and_limits()
                for account in accounts:
                    self.account_manager.refresh_account_status(account.get('id'))
                
                self.load_accounts()
                QMessageBox.information(self, '成功', '已刷新所有账户信息')
        except Exception as e:
            QMessageBox.warning(self, '错误', f'刷新失败: {str(e)}')
    
    def delete_account(self, account):
        """删除单个账户"""
        reply = QMessageBox.question(
            self, '确认删除',
            f'确定要删除账户 {account.get("email")} 吗？',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if self.account_manager:
                    self.account_manager.delete_account(account.get('id'))
                    self.load_accounts()
                    QMessageBox.information(self, '成功', f'已删除账户: {account.get("email")}')
                else:
                    QMessageBox.warning(self, '错误', '账户管理器未初始化')
            except Exception as e:
                QMessageBox.warning(self, '错误', f'删除失败: {str(e)}')
    def refresh_ui_texts(self):
        """刷新UI文本当语言变化时"""
        # 重新加载页面以更新所有文本
        self.load_accounts()
    
    def on_search_text_changed(self, text):
        """搜索文本变化时触发"""
        self.search_text = text.lower()
        self.update_table_view()
    
    def filter_accounts(self, accounts, search_text):
        """根据搜索文本过滤账户"""
        if not search_text:
            return accounts
        
        filtered = []
        for account in accounts:
            # 搜索邮箱、用户ID、状态等
            if (search_text in account.get('email', '').lower() or
                search_text in account.get('user_id', '').lower() or
                search_text in account.get('status', '').lower() or
                search_text in str(account.get('usage', '')).lower()):
                filtered.append(account)
        return filtered
    
    def sort_accounts(self, accounts):
        """对账户进行排序"""
        if not hasattr(self, 'sort_column'):
            self.sort_column = 4  # 默认按账户过期列排序
            self.sort_order = Qt.AscendingOrder
        
        # 定义各列的排序函数
        def get_sort_key(account):
            if self.sort_column == 1:  # 邮箱列
                return account.get('email', '')
            elif self.sort_column == 2:  # 状态列
                status_order = {'active': 0, 'inactive': 1, 'banned': 2, 'expired': 3}
                return status_order.get(account.get('status', 'unknown'), 4)
            elif self.sort_column == 3:  # 限制列（使用率）
                try:
                    usage = float(account.get('usage', '0').replace('GB', '').strip())
                    limit = float(account.get('limit', '2500').replace('GB', '').strip())
                    return (usage / limit) * 100 if limit > 0 else 0
                except:
                    return 0
            elif self.sort_column == 4:  # 账户过期列
                return self.get_expiry_sort_key(account)
            else:
                return 0
        
        # 根据排序顺序排序
        reverse = (self.sort_order == Qt.DescendingOrder)
        return sorted(accounts, key=get_sort_key, reverse=reverse)
    
    def get_expiry_sort_key(self, account):
        """获取过期时间的排序键"""
        expiry = account.get('expiry', '')
        
        # 处理永久账户（放在最后）
        if not expiry or expiry == 'N/A' or expiry == '永久':
            return float('inf')
        
        # 处理已过期（放在最前）
        if account.get('status') == 'expired':
            return -1
        
        # 尝试解析日期字符串
        expiry_str = str(expiry)
        
        # 处理中文格式的剩余时间
        if '剩余' in expiry_str:
            try:
                if '分钟' in expiry_str:
                    minutes = int(expiry_str.split('剩余')[1].split('分钟')[0])
                    return minutes / (24 * 60)  # 转换为天数
                elif '小时' in expiry_str:
                    hours = int(expiry_str.split('剩余')[1].split('小时')[0])
                    return hours / 24  # 转换为天数
                elif '天' in expiry_str:
                    days = int(expiry_str.split('剩余')[1].split('天')[0])
                    return days
            except:
                pass
        
        # 处理日期格式 (YYYY-MM-DD 或 YYYY/MM/DD)
        if '-' in expiry_str or '/' in expiry_str:
            try:
                from datetime import datetime
                # 只取日期部分
                date_str = expiry_str.split(' ')[0] if ' ' in expiry_str else expiry_str
                
                # 尝试不同的日期格式
                for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y']:
                    try:
                        expiry_date = datetime.strptime(date_str, fmt)
                        # 计算距离今天的天数
                        days_remaining = (expiry_date - datetime.now()).days
                        return days_remaining if days_remaining >= 0 else -1
                    except:
                        continue
            except:
                pass
        
        # 默认放在中间
        return 9999
    
    def import_accounts(self):
        """导入账户"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, '导入账户', '', 'JSON Files (*.json);;CSV Files (*.csv);;All Files (*)'
        )
        
        if file_path:
            try:
                import json
                import csv
                
                accounts_to_import = []
                
                if file_path.endswith('.json'):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            accounts_to_import = data
                        elif isinstance(data, dict) and 'accounts' in data:
                            accounts_to_import = data['accounts']
                
                elif file_path.endswith('.csv'):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        accounts_to_import = list(reader)
                
                # 导入账户
                imported_count = 0
                for account_data in accounts_to_import:
                    try:
                        if self.account_manager:
                            self.account_manager.add_account(account_data)
                            imported_count += 1
                    except Exception as e:
                        print(f'导入账户失败: {e}')
                
                self.load_accounts()
                QMessageBox.information(self, '成功', f'成功导入 {imported_count} 个账户')
            
            except Exception as e:
                QMessageBox.warning(self, '错误', f'导入失败: {str(e)}')
    
    def export_accounts(self):
        """导出账户"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, '导出账户', 'warp_accounts.json', 'JSON Files (*.json);;CSV Files (*.csv)'
        )
        
        if file_path:
            try:
                accounts = self.account_manager.get_accounts_with_health_and_limits() if self.account_manager else []
                
                if file_path.endswith('.json'):
                    import json
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump({'accounts': accounts}, f, ensure_ascii=False, indent=2)
                
                elif file_path.endswith('.csv'):
                    import csv
                    if accounts:
                        with open(file_path, 'w', encoding='utf-8', newline='') as f:
                            writer = csv.DictWriter(f, fieldnames=accounts[0].keys())
                            writer.writeheader()
                            writer.writerows(accounts)
                
                QMessageBox.information(self, '成功', f'成功导出 {len(accounts)} 个账户')
            
            except Exception as e:
                QMessageBox.warning(self, '错误', f'导出失败: {str(e)}')
    
    def batch_activate(self):
        """批量激活选中的账户"""
        selected_accounts = self.get_selected_accounts()
        if not selected_accounts:
            QMessageBox.warning(self, '提示', '请先选择要激活的账户')
            return
        
        activated_count = 0
        for account_id in selected_accounts:
            try:
                if self.account_manager:
                    # 激活账户逻辑
                    self.account_manager.activate_account(account_id)
                    activated_count += 1
            except Exception as e:
                print(f'激活账户 {account_id} 失败: {e}')
        
        self.load_accounts()
        QMessageBox.information(self, '成功', f'成功激活 {activated_count} 个账户')
    
    def batch_pause(self):
        """批量暂停选中的账户"""
        selected_accounts = self.get_selected_accounts()
        if not selected_accounts:
            QMessageBox.warning(self, '提示', '请先选择要暂停的账户')
            return
        
        paused_count = 0
        for account_id in selected_accounts:
            try:
                if self.account_manager:
                    # 暂停账户逻辑
                    self.account_manager.pause_account(account_id)
                    paused_count += 1
            except Exception as e:
                print(f'暂停账户 {account_id} 失败: {e}')
        
        self.load_accounts()
        QMessageBox.information(self, '成功', f'成功暂停 {paused_count} 个账户')
    
    def batch_refresh_selected(self):
        """批量刷新选中的账户"""
        selected_accounts = self.get_selected_accounts()
        if not selected_accounts:
            QMessageBox.warning(self, '提示', '请先选择要刷新的账户')
            return
        
        refreshed_count = 0
        for account_id in selected_accounts:
            try:
                if self.account_manager:
                    self.account_manager.refresh_account_status(account_id)
                    refreshed_count += 1
            except Exception as e:
                print(f'刷新账户 {account_id} 失败: {e}')
        
        self.load_accounts()
        QMessageBox.information(self, '成功', f'成功刷新 {refreshed_count} 个账户')
    
    def copy_selected_emails(self):
        """复制选中账户的邮箱"""
        selected_accounts = self.get_selected_accounts()
        if not selected_accounts:
            QMessageBox.warning(self, '提示', '请先选择要复制邮箱的账户')
            return
        
        emails = []
        accounts = self.account_manager.get_accounts_with_health_and_limits() if self.account_manager else []
        
        for account in accounts:
            if account.get('id') in selected_accounts:
                emails.append(account.get('email', ''))
        
        if emails:
            from PyQt5.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText('\n'.join(emails))
            QMessageBox.information(self, '成功', f'已复制 {len(emails)} 个邮箱地址到剪贴板')
    
    def get_selected_accounts(self):
        """获取选中的账户ID列表"""
        selected = []
        for row in range(self.table_widget.rowCount()):
            checkbox_widget = self.table_widget.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    account_id = checkbox.property('account_id')
                    if account_id:
                        selected.append(account_id)
        return selected
    
    def show_advanced_filter(self):
        """显示高级筛选对话框"""
        dialog = AdvancedFilterDialog(self)
        if dialog.exec_():
            # 应用筛选条件
            self.apply_advanced_filter(dialog.get_filter_criteria())
    
    def apply_advanced_filter(self, criteria):
        """应用高级筛选条件"""
        # TODO: 实现高级筛选逻辑
        self.update_table_view()
    
    def on_header_clicked(self, logical_index):
        """处理表头点击事件进行排序"""
        # 不对选择列（第0列）和操作列（第5列）进行排序
        if logical_index == 0 or logical_index == 5:
            return
        
        # 如果点击的是同一列，切换排序顺序
        if self.sort_column == logical_index:
            self.sort_order = Qt.DescendingOrder if self.sort_order == Qt.AscendingOrder else Qt.AscendingOrder
        else:
            # 如果点击的是新列，设置为该列并使用默认排序顺序
            self.sort_column = logical_index
            # 账户过期列默认升序（最快过期的在前），其他列默认升序
            self.sort_order = Qt.AscendingOrder
        
        # 更新表头显示排序指示器
        header = self.table_widget.horizontalHeader()
        header.setSortIndicator(logical_index, self.sort_order)
        
        # 刷新表格显示
        self.update_table_view()


class AdvancedFilterDialog(QDialog):
    """高级筛选对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('高级筛选')
        self.setModal(True)
        self.setMinimumWidth(400)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 创建表单布局
        form_layout = QFormLayout()
        
        # 状态筛选
        self.status_combo = QComboBox()
        self.status_combo.addItems(['全部', '活跃', '未活跃', '已封禁', '已过期'])
        form_layout.addRow('状态:', self.status_combo)
        
        # 使用率筛选
        usage_layout = QHBoxLayout()
        self.usage_min = QSpinBox()
        self.usage_min.setRange(0, 100)
        self.usage_min.setSuffix('%')
        usage_layout.addWidget(self.usage_min)
        usage_layout.addWidget(QLabel('至'))
        self.usage_max = QSpinBox()
        self.usage_max.setRange(0, 100)
        self.usage_max.setValue(100)
        self.usage_max.setSuffix('%')
        usage_layout.addWidget(self.usage_max)
        form_layout.addRow('使用率:', usage_layout)
        
        # 过期时间筛选
        self.expiry_combo = QComboBox()
        self.expiry_combo.addItems([
            '全部', '永久', '7天内过期', '30天内过期', '已过期'
        ])
        form_layout.addRow('过期时间:', self.expiry_combo)
        
        layout.addLayout(form_layout)
        
        # 按钮
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        buttons.accepted.connect(self.accept)
        buttons.cancelled.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_filter_criteria(self):
        """获取筛选条件"""
        return {
            'status': self.status_combo.currentText(),
            'usage_min': self.usage_min.value(),
            'usage_max': self.usage_max.value(),
            'expiry': self.expiry_combo.currentText()
        }
