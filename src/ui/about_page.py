#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
About Page Widget - Application information and credits
"""

import sys
import platform
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QPushButton, QScrollArea, QTextEdit)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QFont, QDesktopServices, QPixmap
from src.config.languages import _
from src.ui.theme_manager import theme_manager


class InfoCard(QFrame):
    """Information display card"""
    
    def __init__(self, title, content, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)
        
        # Title
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.title_label.setStyleSheet(f"color: {theme_manager.get_color('accent_blue')}; background: transparent; border: none; outline: none; border-radius: 8px; padding: 6px 12px;")
        layout.addWidget(self.title_label)
        
        # Content
        self.content_label = QLabel(content)
        self.content_label.setFont(QFont("Segoe UI", 10))
        self.content_label.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; line-height: 1.4; background: transparent; border: none; outline: none; border-radius: 6px; padding: 4px 8px;")
        self.content_label.setWordWrap(True)
        self.content_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(self.content_label)
        
        self.setLayout(layout)
        
        # Card styling - Light theme
        self.setStyleSheet("""
            InfoCard {
                background-color: rgba(255, 255, 255, 0.9);
                border: 1px solid rgba(226, 232, 240, 0.8);
                border-radius: 12px;
                margin: 5px 0;
            }
            InfoCard:hover {
                border-color: rgba(59, 130, 246, 0.5);
                background-color: rgba(248, 250, 252, 0.95);
            }
        """)


class AboutPage(QWidget):
    """About page with application information"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize about page UI"""
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
        
        # 应用信息
        app_info_section = self.create_app_info_section()
        content_layout.addWidget(app_info_section)
        
        # 技术栈
        tech_stack_section = self.create_tech_stack_section()
        content_layout.addWidget(tech_stack_section)
        
        # 系统信息
        system_info_section = self.create_system_info_section()
        content_layout.addWidget(system_info_section)
        
        # 作者与联系
        author_section = self.create_author_section()
        content_layout.addWidget(author_section)
        
        # 致谢
        credits_section = self.create_credits_section()
        content_layout.addWidget(credits_section)
        
        # 链接
        links_section = self.create_links_section()
        content_layout.addWidget(links_section)
        
        # 许可证
        license_section = self.create_license_section()
        content_layout.addWidget(license_section)
        
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
        layout.setContentsMargins(0, 0, 0, 10)  # 与home_page和cleanup_page一致
        layout.setSpacing(12)  # 与home_page和cleanup_page一致
        
        # Left side - Title and description
        left_layout = QVBoxLayout()
        left_layout.setSpacing(4)  # 与home_page和cleanup_page一致
        
        # Page title - 统一所有页面的标题样式
        title_label = QLabel("📝 关于")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))  # 统一字号
        title_label.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; background: transparent; border: none; outline: none; border-radius: 8px; padding: 6px 12px;")
        title_label.setObjectName("title")  # 设置objectName以排除全局样式
        left_layout.addWidget(title_label)
        
        # Page description - 统一所有页面的描述样式
        desc_label = QLabel("应用程序信息和版本说明")
        desc_label.setFont(QFont("Segoe UI", 11))  # 统一字号
        desc_label.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; background: transparent; border: none; outline: none; border-radius: 6px; padding: 4px 8px;")
        desc_label.setObjectName("title")  # 设置objectName以排除全局样式
        left_layout.addWidget(desc_label)
        
        layout.addLayout(left_layout)
        layout.addStretch()
        
        header.setLayout(layout)
        return header
    
    def create_header_section(self):
        """Create header with logo and title"""
        section = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # App icon/logo (using emoji for now)
        logo_label = QLabel("🚀")
        logo_label.setFont(QFont("Segoe UI Emoji", 48))
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("background: transparent; border: none; outline: none; border-radius: 8px; padding: 6px;")
        layout.addWidget(logo_label)
        
        # App title
        self.title_label = QLabel(_('about_app_title'))
        self.title_label.setFont(QFont("Segoe UI", 28, QFont.Bold))
        self.title_label.setStyleSheet(f"color: {theme_manager.get_color('accent_blue')}; background: transparent; border: none; outline: none; border-radius: 8px; padding: 6px 12px;")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)
        
        # Version
        self.version_label = QLabel(_('about_version'))
        self.version_label.setFont(QFont("Segoe UI", 14))
        self.version_label.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; background: transparent; border: none; outline: none; border-radius: 6px; padding: 4px 8px;")
        self.version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.version_label)
        
        # Description
        self.desc_label = QLabel(_('about_description'))
        self.desc_label.setFont(QFont("Segoe UI", 12))
        self.desc_label.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; line-height: 1.5; background: transparent; border: none; outline: none; border-radius: 6px; padding: 4px 8px;")
        self.desc_label.setAlignment(Qt.AlignCenter)
        self.desc_label.setWordWrap(True)
        layout.addWidget(self.desc_label)
        
        section.setLayout(layout)
        return section
    
    def create_app_info_section(self):
        """Create application information section with version and changelog"""
        section = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Section title
        self.app_info_title = QLabel(_('about_app_info_title'))
        self.app_info_title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.app_info_title.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; margin-bottom: 10px; background: transparent; border: none; outline: none; border-radius: 8px; padding: 6px 12px;")
        layout.addWidget(self.app_info_title)
        
        # Version and changelog card
        self.version_card = InfoCard(
            _('about_version_changelog_title'),
            _('about_version_changelog_content')
        )
        layout.addWidget(self.version_card)
        
        # Info cards
        self.features_card = InfoCard(
            _('about_features_title'),
            _('about_features_content')
        )
        layout.addWidget(self.features_card)
        
        section.setLayout(layout)
        return section
    
    def get_version_changelog(self):
        """Get version information and changelog"""
        return (
            "🔖 Current Version: v2.0.0\n"
            "📅 Release Date: 2025-01-19\n\n"
            "📋 Latest Changes:\n"
            "• Enhanced modern UI with glassmorphism effects\n"
            "• Improved sidebar navigation with animations\n"
            "• Added comprehensive error handling system\n"
            "• Implemented registry monitoring for auto-switching\n"
            "• Added multi-language support framework\n"
            "• Enhanced security with data encryption\n"
            "• Optimized performance and memory usage\n"
            "• Added automated testing framework\n\n"
            "🔗 Full changelog: https://github.com/hj01857655/WARP_reg_and_manager/releases"
        )
    
    def create_tech_stack_section(self):
        """Create technology stack section"""
        section = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Section title
        self.tech_title = QLabel(_('about_tech_title'))
        self.tech_title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.tech_title.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; margin-bottom: 10px; background: transparent; border: none; outline: none; border-radius: 8px; padding: 6px 12px;")
        layout.addWidget(self.tech_title)
        
        # Core technologies
        self.core_tech_card = InfoCard(
            _('about_core_tech_title'),
            _('about_core_tech_content', sys.version.split()[0])
        )
        layout.addWidget(self.core_tech_card)
        
        # Network & Security
        self.network_card = InfoCard(
            _('about_network_security_title'),
            _('about_network_security_content')
        )
        layout.addWidget(self.network_card)
        
        # System Integration
        self.system_integration_card = InfoCard(
            _('about_system_integration_title'),
            _('about_system_integration_content')
        )
        layout.addWidget(self.system_integration_card)
        
        section.setLayout(layout)
        return section
    
    def create_author_section(self):
        """Create author and contact information section"""
        section = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Section title
        self.author_title_label = QLabel(_('about_author_contact_title'))
        self.author_title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.author_title_label.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; margin-bottom: 10px; background: transparent; border: none; outline: none; border-radius: 8px; padding: 6px 12px;")
        layout.addWidget(self.author_title_label)
        
        # Author info
        self.author_card = InfoCard(
            _('about_dev_team_title'),
            _('about_dev_team_content')
        )
        layout.addWidget(self.author_card)
        
        section.setLayout(layout)
        return section
    
    def create_system_info_section(self):
        """Create comprehensive system information section"""
        section = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Section title
        self.system_info_title = QLabel(_('about_system_info_title'))
        self.system_info_title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.system_info_title.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; margin-bottom: 10px; background: transparent; border: none; outline: none; border-radius: 8px; padding: 6px 12px;")
        layout.addWidget(self.system_info_title)
        
        # Operating System Info
        os_info = (
            f"• Operating System: {platform.system()} {platform.release()}\n"
            f"• Platform: {platform.platform()}\n"
            f"• Architecture: {platform.machine()}\n"
            f"• Node Name: {platform.node()}\n"
            f"• Processor: {platform.processor() or 'Unknown'}"
        )
        self.os_card = InfoCard(_('about_os_info_title'), os_info)
        layout.addWidget(self.os_card)
        
        # Python Environment Info
        python_info = (
            f"• Python Version: {sys.version.split()[0]}\n"
            f"• Python Implementation: {platform.python_implementation()}\n"
            f"• Python Compiler: {platform.python_compiler()}\n"
            f"• Python Build: {' '.join(platform.python_build())}\n"
            f"• Executable Path: {sys.executable}"
        )
        self.python_card = InfoCard(_('about_python_env_title'), python_info)
        layout.addWidget(self.python_card)
        
        # Application Runtime Info
        import os
        import time
        from datetime import datetime
        
        app_info = (
            f"• Application PID: {os.getpid()}\n"
            f"• Working Directory: {os.getcwd()}\n"
            f"• Startup Time: {datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"• User Home: {os.path.expanduser('~')}\n"
            f"• Temp Directory: {os.path.dirname(os.path.abspath(__file__))}"
        )
        self.app_runtime_card = InfoCard(_('about_app_runtime_title'), app_info)
        layout.addWidget(self.app_runtime_card)
        
        section.setLayout(layout)
        return section
    
    def create_credits_section(self):
        """Create credits and acknowledgments section"""
        section = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Section title
        self.credits_title = QLabel(_('about_credits_title'))
        self.credits_title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.credits_title.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; margin-bottom: 10px; background: transparent; border: none; outline: none; border-radius: 8px; padding: 6px 12px;")
        layout.addWidget(self.credits_title)
        
        # Credits info
        self.credits_dev_team_card = InfoCard(
            _('about_dev_team_credits_title'),
            _('about_dev_team_credits_content')
        )
        layout.addWidget(self.credits_dev_team_card)
        
        self.thanks_card = InfoCard(
            _('about_special_thanks_title'),
            _('about_special_thanks_content')
        )
        layout.addWidget(self.thanks_card)
        
        section.setLayout(layout)
        return section
    
    def create_links_section(self):
        """Create links and contact section"""
        section = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Section title
        self.links_title = QLabel(_('about_links_contact_title'))
        self.links_title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.links_title.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; margin-bottom: 10px; background: transparent; border: none; outline: none; border-radius: 8px; padding: 6px 12px;")
        layout.addWidget(self.links_title)
        
        # Links buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        # GitHub repository
        self.github_btn = QPushButton(_('about_github_btn'))
        self.github_btn.setFixedHeight(45)
        self.github_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/hj01857655/WARP_reg_and_manager")))
        self.github_btn.setStyleSheet(self.get_button_style("#4a5568"))
        buttons_layout.addWidget(self.github_btn)
        
        # Telegram channel
        self.telegram_btn = QPushButton(_('about_telegram_channel_btn'))
        self.telegram_btn.setFixedHeight(45)
        self.telegram_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://t.me/warp5215")))
        self.telegram_btn.setStyleSheet(self.get_button_style("#0088cc"))
        buttons_layout.addWidget(self.telegram_btn)
        
        # Telegram chat
        self.chat_btn = QPushButton(_('about_telegram_chat_btn'))
        self.chat_btn.setFixedHeight(45)
        self.chat_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://t.me/warp1215")))
        self.chat_btn.setStyleSheet(self.get_button_style("#0088cc"))
        buttons_layout.addWidget(self.chat_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        section.setLayout(layout)
        return section
    
    def create_license_section(self):
        """Create comprehensive license and legal information section"""
        section = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Section title
        self.license_title = QLabel(_('about_license_title'))
        self.license_title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.license_title.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; margin-bottom: 10px; background: transparent; border: none; outline: none; border-radius: 8px; padding: 6px 12px;")
        layout.addWidget(self.license_title)
        
        # Open Source License
        license_text = """
📜 MIT License

Copyright (c) 2025 Warp Account Manager Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
        """.strip()
        
        self.license_card = InfoCard(_('about_mit_license_title'), _('about_mit_license_content'))
        layout.addWidget(self.license_card)
        
        # Usage Terms and Disclaimer
        terms_text = """
⚠️ Important Notice:

This software is provided "AS IS" without warranty of any kind.

📝 Terms of Use:
• Educational and personal use only
• Users must comply with Cloudflare Warp's terms of service
• Use responsibly and ethically
• Comply with all applicable laws and regulations
• Do not use for malicious purposes
• Respect third-party service terms

🚫 Disclaimer:
The developers are not responsible for any misuse, damage, or legal issues
arising from the use of this software. Users assume full responsibility.
        """.strip()
        
        self.terms_card = InfoCard(_('about_terms_disclaimer_title'), _('about_terms_disclaimer_content'))
        layout.addWidget(self.terms_card)
        
        # Third-party Acknowledgments
        acknowledgments_text = """
🙏 Special Thanks:

• Cloudflare - For the Warp service and API
• Qt Company - PyQt5 GUI framework
• Python Software Foundation - Python language
• mitmproxy contributors - Proxy server technology
• Open source community - Various libraries and tools
• All users and contributors - Feedback and improvements

This project is not affiliated with Cloudflare Inc.
        """.strip()
        
        self.ack_card = InfoCard(_('about_third_party_title'), _('about_third_party_content'))
        layout.addWidget(self.ack_card)
        
        # Copyright and Source Code notice
        footer_layout = QVBoxLayout()
        footer_layout.setSpacing(5)
        
        copyright_label = QLabel("© 2025 Warp Account Manager Contributors. Released under MIT License.")
        copyright_label.setFont(QFont("Segoe UI", 10))
        copyright_label.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; margin-top: 10px; background: transparent; border: none; outline: none; border-radius: 6px; padding: 4px 8px;")
        copyright_label.setAlignment(Qt.AlignCenter)
        footer_layout.addWidget(copyright_label)
        
        source_label = QLabel("📝 Source code available on GitHub: https://github.com/hj01857655/WARP_reg_and_manager")
        source_label.setFont(QFont("Segoe UI", 9))
        source_label.setStyleSheet(f"color: {theme_manager.get_color('accent_blue')}; margin-top: 5px; background: transparent; border: none; outline: none; border-radius: 6px; padding: 4px 8px;")
        source_label.setAlignment(Qt.AlignCenter)
        source_label.setOpenExternalLinks(True)
        source_label.setTextFormat(Qt.RichText)
        source_label.setText('<a href="https://github.com/hj01857655/WARP_reg_and_manager" style="color: #63b3ed; text-decoration: none;">📝 Source code available on GitHub</a>')
        footer_layout.addWidget(source_label)
        
        layout.addLayout(footer_layout)
        
        section.setLayout(layout)
        return section
    
    def get_button_style(self, color):
        """Get button style with specified color"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
            QPushButton:pressed {{
                background-color: {color}aa;
            }}
        """
    
    def refresh_ui_texts(self):
        """Refresh all UI texts when language changes"""
        # Update header section
        self.title_label.setText(_('about_app_title'))
        self.version_label.setText(_('about_version'))
        self.desc_label.setText(_('about_description'))
        
        # Update section titles
        self.app_info_title.setText(_('about_app_info_title'))
        self.tech_title.setText(_('about_tech_title'))
        
        # Update info cards
        self.version_card.title_label.setText(_('about_version_changelog_title'))
        self.version_card.content_label.setText(_('about_version_changelog_content'))
        
        self.features_card.title_label.setText(_('about_features_title'))
        self.features_card.content_label.setText(_('about_features_content'))
        
        self.core_tech_card.title_label.setText(_('about_core_tech_title'))
        self.core_tech_card.content_label.setText(_('about_core_tech_content', sys.version.split()[0]))
        
        # Update buttons
        self.github_btn.setText(_('about_github_btn'))
        self.telegram_btn.setText(_('about_telegram_channel_btn'))
        self.chat_btn.setText(_('about_telegram_chat_btn'))
        
        # Update network and system cards
        self.network_card.title_label.setText(_('about_network_security_title'))
        self.network_card.content_label.setText(_('about_network_security_content'))
        
        self.system_integration_card.title_label.setText(_('about_system_integration_title'))
        self.system_integration_card.content_label.setText(_('about_system_integration_content'))
        
        # Update author section
        self.author_title_label.setText(_('about_author_contact_title'))
        self.author_card.title_label.setText(_('about_dev_team_title'))
        self.author_card.content_label.setText(_('about_dev_team_content'))
        
        # Update system info section
        self.system_info_title.setText(_('about_system_info_title'))
        self.os_card.title_label.setText(_('about_os_info_title'))
        self.python_card.title_label.setText(_('about_python_env_title'))
        self.app_runtime_card.title_label.setText(_('about_app_runtime_title'))
        
        # Update credits section
        self.credits_title.setText(_('about_credits_title'))
        self.credits_dev_team_card.title_label.setText(_('about_dev_team_credits_title'))
        self.credits_dev_team_card.content_label.setText(_('about_dev_team_credits_content'))
        self.thanks_card.title_label.setText(_('about_special_thanks_title'))
        self.thanks_card.content_label.setText(_('about_special_thanks_content'))
        
        # Update links section
        self.links_title.setText(_('about_links_contact_title'))
        
        # Update license section
        self.license_title.setText(_('about_license_title'))
        self.license_card.title_label.setText(_('about_mit_license_title'))
        self.license_card.content_label.setText(_('about_mit_license_content'))
        self.terms_card.title_label.setText(_('about_terms_disclaimer_title'))
        self.terms_card.content_label.setText(_('about_terms_disclaimer_content'))
        self.ack_card.title_label.setText(_('about_third_party_title'))
        self.ack_card.content_label.setText(_('about_third_party_content'))
