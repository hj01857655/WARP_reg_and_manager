#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cleanup Tools Page - System cleanup and maintenance tools
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QFrame, QTextEdit, QGroupBox, QMessageBox,
                             QProgressBar, QScrollArea)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon
from src.config.languages import _
from src.ui.theme_manager import theme_manager


class CleanupWorker(QThread):
    """Worker thread for cleanup operations"""
    progress = pyqtSignal(int)
    status_update = pyqtSignal(str)
    cleanup_complete = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, cleanup_type):
        super().__init__()
        self.cleanup_type = cleanup_type
    
    def run(self):
        """Execute cleanup operation"""
        try:
            if self.cleanup_type == "reset_machine_id":
                self.reset_machine_id()
            elif self.cleanup_type == "one_click_cleanup":
                self.one_click_cleanup()
        except Exception as e:
            self.cleanup_complete.emit(False, str(e))
    
    def reset_machine_id(self):
        """Reset machine ID operation"""
        self.status_update.emit(_('cleanup_resetting_machine_id'))
        self.progress.emit(20)
        
        # TODO: Implement actual reset machine ID logic
        import time
        time.sleep(1)  # Simulate operation
        
        self.progress.emit(50)
        self.status_update.emit(_('cleanup_clearing_registry'))
        time.sleep(1)
        
        self.progress.emit(80)
        self.status_update.emit(_('cleanup_finalizing'))
        time.sleep(0.5)
        
        self.progress.emit(100)
        self.cleanup_complete.emit(True, _('cleanup_machine_id_reset_success'))
    
    def one_click_cleanup(self):
        """One-click cleanup operation"""
        self.status_update.emit(_('cleanup_scanning_system'))
        self.progress.emit(10)
        
        # TODO: Implement actual cleanup logic
        import time
        time.sleep(0.5)
        
        self.progress.emit(30)
        self.status_update.emit(_('cleanup_clearing_cache'))
        time.sleep(0.5)
        
        self.progress.emit(50)
        self.status_update.emit(_('cleanup_removing_temp_files'))
        time.sleep(0.5)
        
        self.progress.emit(70)
        self.status_update.emit(_('cleanup_optimizing_database'))
        time.sleep(0.5)
        
        self.progress.emit(90)
        self.status_update.emit(_('cleanup_finalizing'))
        time.sleep(0.5)
        
        self.progress.emit(100)
        self.cleanup_complete.emit(True, _('cleanup_one_click_success'))


class ActionButton(QPushButton):
    """Custom styled action button for cleanup tools"""
    
    def __init__(self, text, icon_emoji="", color_theme="blue", parent=None):
        super().__init__(parent)
        self.setText(f"{icon_emoji} {text}" if icon_emoji else text)
        self.setMinimumHeight(80)
        self.setCursor(Qt.PointingHandCursor)
        
        # Color themes
        themes = {
            "blue": {
                "normal": "qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #4299e1, stop: 1 #3182ce)",
                "hover": "qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #63b3ed, stop: 1 #4299e1)",
                "pressed": "qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #3182ce, stop: 1 #2c5282)"
            },
            "red": {
                "normal": "qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #f56565, stop: 1 #e53e3e)",
                "hover": "qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #fc8181, stop: 1 #f56565)",
                "pressed": "qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #e53e3e, stop: 1 #c53030)"
            },
            "green": {
                "normal": "qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #48bb78, stop: 1 #38a169)",
                "hover": "qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #68d391, stop: 1 #48bb78)",
                "pressed": "qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #38a169, stop: 1 #2f855a)"
            }
        }
        
        theme = themes.get(color_theme, themes["blue"])
        
        self.setStyleSheet(f"""
            QPushButton {{
                background: {theme['normal']};
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
                padding: 20px;
            }}
            QPushButton:hover {{
                background: {theme['hover']};
            }}
            QPushButton:pressed {{
                background: {theme['pressed']};
            }}
            QPushButton:disabled {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #4a5568, stop: 1 #2d3748);
                color: #a0aec0;
            }}
        """)


class CleanupPage(QWidget):
    """Cleanup tools page with various system maintenance options"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize cleanup page UI"""
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
        
        # 与第1/2页一致：主容器直接承载页头，设置统一边距/间距
        container_layout = QVBoxLayout(main_container)
        container_layout.setContentsMargins(30, 25, 30, 25)
        container_layout.setSpacing(25)
        
        # 统一页头（标题+描述）放在卡片顶部、滚动区域之外
        page_header = self.create_page_header()
        container_layout.addWidget(page_header)
        
        # 其余内容放入滚动区域，避免影响页头位置
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
        """)
        
        # 滚动内容容器
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(25)
        
        # 工具区
        tools_section = self.create_tools_section()
        content_layout.addWidget(tools_section)
        
        # 进度区
        self.progress_section = self.create_progress_section()
        self.progress_section.setVisible(False)
        content_layout.addWidget(self.progress_section)
        
        # 日志区
        log_section = self.create_log_section()
        content_layout.addWidget(log_section)
        
        content_layout.addStretch()
        content_widget.setLayout(content_layout)
        scroll.setWidget(content_widget)
        
        # 将滚动区加入主容器
        container_layout.addWidget(scroll)
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(main_container)
        self.setLayout(main_layout)
    
    def create_page_header(self):
        """Create unified page header with title and description"""
        header = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 20)
        layout.setSpacing(15)
        
        # Left side - Title and description
        left_layout = QVBoxLayout()
        left_layout.setSpacing(8)
        
        # Page title
        title_label = QLabel("🧹 清理工具")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))  # 与其他页面一致
        title_label.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; background: transparent; border: none; outline: none; border-radius: 8px; padding: 6px 12px;")
        left_layout.addWidget(title_label)
        
        # Page description
        desc_label = QLabel("系统维护和数据清理工具")
        desc_label.setFont(QFont("Segoe UI", 11))  # 与其他页面一致
        desc_label.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; background: transparent; border: none; outline: none; border-radius: 6px; padding: 4px 8px;")
        left_layout.addWidget(desc_label)
        
        layout.addLayout(left_layout)
        layout.addStretch()
        
        header.setLayout(layout)
        return header
    
    def create_header_section(self):
        """Create header with title and description"""
        section = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Title with icon
        title_container = QWidget()
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        icon_label = QLabel("🧹")
        icon_label.setFont(QFont("Segoe UI Emoji", 32))
        icon_label.setStyleSheet("background: transparent; border: none; outline: none; border-radius: 8px; padding: 6px;")
        title_layout.addWidget(icon_label)
        
        self.title_label = QLabel(_('cleanup_title'))
        self.title_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        self.title_label.setStyleSheet(f"color: {theme_manager.get_color('accent_blue')}; background: transparent; border: none; outline: none; border-radius: 8px; padding: 6px 12px;")
        title_layout.addWidget(self.title_label)
        
        title_layout.addStretch()
        title_container.setLayout(title_layout)
        layout.addWidget(title_container)
        
        # Description
        self.desc_label = QLabel(_('cleanup_description'))
        self.desc_label.setFont(QFont("Segoe UI", 12))
        self.desc_label.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; line-height: 1.5; background: transparent; border: none; outline: none; border-radius: 6px; padding: 4px 8px;")
        self.desc_label.setWordWrap(True)
        layout.addWidget(self.desc_label)
        
        section.setLayout(layout)
        return section
    
    def create_tools_section(self):
        """Create tools section with two side-by-side cards"""
        section = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Section title
        title_label = QLabel("🧹 维护工具")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; background: transparent; border: none; outline: none; border-radius: 8px; padding: 6px 12px;")
        layout.addWidget(title_label)
        
        # Cards container
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(25)
        
        # Left card - Reset Machine ID
        self.reset_card = self.create_reset_card()
        cards_layout.addWidget(self.reset_card)
        
        # Right card - One-click Cleanup
        self.cleanup_card = self.create_cleanup_card()
        cards_layout.addWidget(self.cleanup_card)
        
        layout.addLayout(cards_layout)
        
        section.setLayout(layout)
        return section
    
    def create_reset_card(self):
        """Create reset machine ID card"""
        card = QFrame()
        card.setFrameStyle(QFrame.NoFrame)
        card.setMinimumHeight(220)  # 适度减小最小高度
        card.setMinimumWidth(250)  # 设置最小宽度，避免内容被压缩
        
        # Card styling with red accent
        card.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 rgba(255, 255, 255, 0.95),
                    stop: 0.5 rgba(248, 250, 252, 0.9),
                    stop: 1 rgba(241, 245, 249, 0.95)
                );
                border: 1px solid rgba(239, 68, 68, 0.2);
                border-radius: 16px;
                padding: 20px;
            }
            QFrame:hover {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 rgba(255, 255, 255, 1.0),
                    stop: 0.5 rgba(248, 250, 252, 0.95),
                    stop: 1 rgba(241, 245, 249, 1.0)
                );
                border: 1px solid rgba(239, 68, 68, 0.4);
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Card header
        header_layout = QHBoxLayout()
        
        reset_icon = QLabel("🔄")
        reset_icon.setFont(QFont("Segoe UI Emoji", 18))
        reset_icon.setStyleSheet(f"color: {theme_manager.get_color('accent_red')}; background: transparent; border: none; outline: none; border-radius: 6px; padding: 4px;")
        header_layout.addWidget(reset_icon)
        
        reset_title = QLabel("重置机器码")
        reset_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        reset_title.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; background: transparent; border: none; outline: none; border-radius: 6px; padding: 4px 8px;")
        header_layout.addWidget(reset_title)
        
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Description
        reset_info = QLabel("重置系统机器标识以解决注册状态中出现的系统问题")
        reset_info.setFont(QFont("Segoe UI", 11))
        reset_info.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; background: transparent; line-height: 1.5; border: none; outline: none; border-radius: 6px; padding: 4px 8px;")
        reset_info.setWordWrap(True)
        reset_info.setMinimumHeight(50)  # 确保有足够高度显示文本
        layout.addWidget(reset_info)
        
        layout.addStretch()
        
        # Reset button with appropriate size
        self.reset_button = QPushButton("🔄 重置机器码")
        self.reset_button.setFont(QFont("Segoe UI", 12, QFont.Medium))
        self.reset_button.setMinimumHeight(40)
        self.reset_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(239, 68, 68, 0.8),
                    stop: 1 rgba(220, 38, 38, 0.8)
                );
                color: white;
                border: 1px solid rgba(239, 68, 68, 0.3);
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(248, 113, 113, 0.9),
                    stop: 1 rgba(239, 68, 68, 0.9)
                );
                border: 1px solid rgba(248, 113, 113, 0.5);
            }
            QPushButton:pressed {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(220, 38, 38, 0.9),
                    stop: 1 rgba(185, 28, 28, 0.9)
                );
            }
        """)
        self.reset_button.clicked.connect(self.on_reset_machine_id)
        layout.addWidget(self.reset_button)
        
        return card
    
    def create_cleanup_card(self):
        """Create one-click cleanup card"""
        card = QFrame()
        card.setFrameStyle(QFrame.NoFrame)
        card.setMinimumHeight(220)  # 适度减小最小高度
        card.setMinimumWidth(250)  # 设置最小宽度，避免内容被压缩
        
        # Card styling with green accent
        card.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 rgba(255, 255, 255, 0.95),
                    stop: 0.5 rgba(248, 250, 252, 0.9),
                    stop: 1 rgba(241, 245, 249, 0.95)
                );
                border: 1px solid rgba(34, 197, 94, 0.2);
                border-radius: 16px;
                padding: 20px;
            }
            QFrame:hover {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 rgba(255, 255, 255, 1.0),
                    stop: 0.5 rgba(248, 250, 252, 0.95),
                    stop: 1 rgba(241, 245, 249, 1.0)
                );
                border: 1px solid rgba(34, 197, 94, 0.4);
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Card header
        header_layout = QHBoxLayout()
        
        cleanup_icon = QLabel("✨")
        cleanup_icon.setFont(QFont("Segoe UI Emoji", 18))
        cleanup_icon.setStyleSheet(f"color: {theme_manager.get_color('accent_green')}; background: transparent; border: none; outline: none; border-radius: 6px; padding: 4px;")
        header_layout.addWidget(cleanup_icon)
        
        cleanup_title = QLabel("一键清理")
        cleanup_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        cleanup_title.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; background: transparent; border: none; outline: none; border-radius: 6px; padding: 4px 8px;")
        header_layout.addWidget(cleanup_title)
        
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Description
        cleanup_info = QLabel("自动清理缓存、临时文件和优化数据库以释放系统空间")
        cleanup_info.setFont(QFont("Segoe UI", 11))
        cleanup_info.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; background: transparent; line-height: 1.5; border: none; outline: none; border-radius: 6px; padding: 4px 8px;")
        cleanup_info.setWordWrap(True)
        cleanup_info.setMinimumHeight(50)  # 确保有足够高度显示文本
        layout.addWidget(cleanup_info)
        
        layout.addStretch()
        
        # Cleanup button with appropriate size
        self.cleanup_button = QPushButton("✨ 一键清理")
        self.cleanup_button.setFont(QFont("Segoe UI", 12, QFont.Medium))
        self.cleanup_button.setMinimumHeight(40)
        self.cleanup_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(34, 197, 94, 0.8),
                    stop: 1 rgba(21, 128, 61, 0.8)
                );
                color: white;
                border: 1px solid rgba(34, 197, 94, 0.3);
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(74, 222, 128, 0.9),
                    stop: 1 rgba(34, 197, 94, 0.9)
                );
                border: 1px solid rgba(74, 222, 128, 0.5);
            }
            QPushButton:pressed {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(21, 128, 61, 0.9),
                    stop: 1 rgba(20, 83, 45, 0.9)
                );
            }
        """)
        self.cleanup_button.clicked.connect(self.on_one_click_cleanup)
        layout.addWidget(self.cleanup_button)
        
        return card
    
    def create_progress_section(self):
        """Create progress section for showing cleanup progress"""
        section = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(30)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                text-align: center;
                color: #1e293b;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #3b82f6, stop: 1 #1d4ed8);
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel(_('cleanup_ready'))
        self.status_label.setFont(QFont("Segoe UI", 11))
        self.status_label.setStyleSheet(f"color: {theme_manager.get_color('accent_green')}; background: transparent; border: none; outline: none; border-radius: 6px; padding: 4px 8px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        section.setLayout(layout)
        return section
    
    def create_log_section(self):
        """Create log section for showing cleanup history"""
        section = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Section title
        title_label = QLabel("📋 操作历史")
        title_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title_label.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; background: transparent; border: none; outline: none; border-radius: 8px; padding: 6px 12px;")
        layout.addWidget(title_label)
        
        # Log text area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)  # 减少高度
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                color: #1e293b;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.log_text)
        
        # Add initial welcome message to log
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        welcome_msg = _('cleanup_log_welcome') if hasattr(self, '_') else "欢迎使用系统清理工具！选择上方操作开始清理。"
        self.log_text.append(f"[{current_time}] {welcome_msg}")
        
        section.setLayout(layout)
        return section
    
    def on_reset_machine_id(self):
        """Handle reset machine ID button click"""
        # Confirm dialog
        reply = QMessageBox.warning(
            self,
            _('cleanup_confirm_title'),
            _('cleanup_confirm_reset_machine_id'),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.start_cleanup("reset_machine_id")
    
    def on_one_click_cleanup(self):
        """Handle one-click cleanup button click"""
        # Confirm dialog
        reply = QMessageBox.question(
            self,
            _('cleanup_confirm_title'),
            _('cleanup_confirm_one_click'),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.start_cleanup("one_click_cleanup")
    
    def start_cleanup(self, cleanup_type):
        """Start cleanup operation in worker thread"""
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, _('warning'), _('cleanup_already_running'))
            return
        
        # Show progress section
        self.progress_section.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Disable buttons
        self.reset_button.setEnabled(False)
        self.cleanup_button.setEnabled(False)
        
        # Start worker thread
        self.worker = CleanupWorker(cleanup_type)
        self.worker.progress.connect(self.update_progress)
        self.worker.status_update.connect(self.update_status)
        self.worker.cleanup_complete.connect(self.on_cleanup_complete)
        self.worker.start()
        
        # Log start
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {_('cleanup_started')}: {cleanup_type}")
    
    def update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)
    
    def update_status(self, message):
        """Update status message"""
        self.status_label.setText(message)
        
        # Log status
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
    
    def on_cleanup_complete(self, success, message):
        """Handle cleanup completion"""
        # Re-enable buttons
        self.reset_button.setEnabled(True)
        self.cleanup_button.setEnabled(True)
        
        # Log completion
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        if success:
            self.log_text.append(f"[{timestamp}] ✅ {message}")
            QMessageBox.information(self, _('success'), message)
        else:
            self.log_text.append(f"[{timestamp}] ❌ {message}")
            QMessageBox.critical(self, _('error'), message)
        
        # Hide progress after delay
        QTimer.singleShot(3000, lambda: self.progress_section.setVisible(False))
    
    def refresh_ui_texts(self):
        """Refresh all UI texts when language changes"""
        self.title_label.setText(_('cleanup_title'))
        self.desc_label.setText(_('cleanup_description'))
        
        # Update button texts
        self.reset_button.setText(f"🔄 {_('cleanup_reset_machine_id_button')}")
        self.cleanup_button.setText(f"✨ {_('cleanup_one_click_button')}")
        
        # Update status
        if not self.worker or not self.worker.isRunning():
            self.status_label.setText(_('cleanup_ready'))