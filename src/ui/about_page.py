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
        self.title_label.setStyleSheet("color: #63b3ed;")
        layout.addWidget(self.title_label)
        
        # Content
        self.content_label = QLabel(content)
        self.content_label.setFont(QFont("Segoe UI", 10))
        self.content_label.setStyleSheet("color: #e2e8f0; line-height: 1.4;")
        self.content_label.setWordWrap(True)
        self.content_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(self.content_label)
        
        self.setLayout(layout)
        
        # Card styling
        self.setStyleSheet("""
            InfoCard {
                background-color: rgba(45, 55, 72, 0.6);
                border: 1px solid rgba(74, 85, 104, 0.5);
                border-radius: 12px;
                margin: 5px 0;
            }
            InfoCard:hover {
                border-color: rgba(99, 179, 237, 0.5);
            }
        """)


class AboutPage(QWidget):
    """About page with application information"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize about page UI"""
        # Main scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Content widget
        content_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(25)
        
        # Header section
        header_section = self.create_header_section()
        layout.addWidget(header_section)
        
        # Application info section (includes version and changelog)
        app_info_section = self.create_app_info_section()
        layout.addWidget(app_info_section)
        
        # Technology stack section
        tech_stack_section = self.create_tech_stack_section()
        layout.addWidget(tech_stack_section)
        
        # System info section (comprehensive system details)
        system_info_section = self.create_system_info_section()
        layout.addWidget(system_info_section)
        
        # Author and contact section
        author_section = self.create_author_section()
        layout.addWidget(author_section)
        
        # Credits section
        credits_section = self.create_credits_section()
        layout.addWidget(credits_section)
        
        # Links section (GitHub, Telegram)
        links_section = self.create_links_section()
        layout.addWidget(links_section)
        
        # License section (legal information)
        license_section = self.create_license_section()
        layout.addWidget(license_section)
        
        layout.addStretch()
        content_widget.setLayout(layout)
        
        scroll.setWidget(content_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)
    
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
        layout.addWidget(logo_label)
        
        # App title
        self.title_label = QLabel(_('about_app_title'))
        self.title_label.setFont(QFont("Segoe UI", 28, QFont.Bold))
        self.title_label.setStyleSheet("color: #63b3ed;")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)
        
        # Version
        self.version_label = QLabel(_('about_version'))
        self.version_label.setFont(QFont("Segoe UI", 14))
        self.version_label.setStyleSheet("color: #a0aec0;")
        self.version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.version_label)
        
        # Description
        self.desc_label = QLabel(_('about_description'))
        self.desc_label.setFont(QFont("Segoe UI", 12))
        self.desc_label.setStyleSheet("color: #e2e8f0; line-height: 1.5;")
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
        self.app_info_title.setStyleSheet("color: #e2e8f0; margin-bottom: 10px;")
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
        self.tech_title.setStyleSheet("color: #e2e8f0; margin-bottom: 10px;")
        layout.addWidget(self.tech_title)
        
        # Core technologies
        self.core_tech_card = InfoCard(
            _('about_core_tech_title'),
            _('about_core_tech_content', sys.version.split()[0])
        )
        layout.addWidget(self.core_tech_card)
        
        # Network & Security
        network_card = InfoCard(
            "🌐 Network & Security",
            "• requests 2.25+ - HTTP library for API calls\n"
            "• urllib3 - HTTP client for Python\n"
            "• mitmproxy 8.0+ - HTTP/HTTPS proxy server\n"
            "• cryptography - Cryptographic recipes and primitives\n"
            "• SSL/TLS - Secure communication protocols"
        )
        layout.addWidget(network_card)
        
        # System Integration
        system_card = InfoCard(
            "⚙️ System Integration",
            "• psutil - System and process utilities\n"
            "• winreg - Windows registry access (Windows only)\n"
            "• pathlib - Object-oriented filesystem paths\n"
            "• threading - Thread-based parallelism\n"
            "• json - JSON encoder and decoder"
        )
        layout.addWidget(system_card)
        
        section.setLayout(layout)
        return section
    
    def create_author_section(self):
        """Create author and contact information section"""
        section = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Section title
        title_label = QLabel("👤 Author & Contact")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_label.setStyleSheet("color: #e2e8f0; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Author info
        author_card = InfoCard(
            "🧑‍💻 Development Team",
            "• Lead Developer: Community Contributors\n"
            "• UI/UX Designer: Modern Interface Team\n"
            "• Security Consultant: Privacy Protection Team\n"
            "• Quality Assurance: Testing & Validation Team\n\n"
            "📧 Contact: warp.manager@protonmail.com\n"
            "🌐 Project Website: https://warp-manager.dev\n"
            "📚 Documentation: https://docs.warp-manager.dev"
        )
        layout.addWidget(author_card)
        
        section.setLayout(layout)
        return section
    
    def create_system_info_section(self):
        """Create comprehensive system information section"""
        section = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Section title
        title_label = QLabel("💻 System Information")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_label.setStyleSheet("color: #e2e8f0; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Operating System Info
        os_info = (
            f"• Operating System: {platform.system()} {platform.release()}\n"
            f"• Platform: {platform.platform()}\n"
            f"• Architecture: {platform.machine()}\n"
            f"• Node Name: {platform.node()}\n"
            f"• Processor: {platform.processor() or 'Unknown'}"
        )
        os_card = InfoCard("🖥️ Operating System", os_info)
        layout.addWidget(os_card)
        
        # Python Environment Info
        python_info = (
            f"• Python Version: {sys.version.split()[0]}\n"
            f"• Python Implementation: {platform.python_implementation()}\n"
            f"• Python Compiler: {platform.python_compiler()}\n"
            f"• Python Build: {' '.join(platform.python_build())}\n"
            f"• Executable Path: {sys.executable}"
        )
        python_card = InfoCard("🐍 Python Environment", python_info)
        layout.addWidget(python_card)
        
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
        app_card = InfoCard("🚀 Application Runtime", app_info)
        layout.addWidget(app_card)
        
        section.setLayout(layout)
        return section
    
    def create_credits_section(self):
        """Create credits and acknowledgments section"""
        section = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Section title
        title_label = QLabel("👥 Credits & Acknowledgments")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_label.setStyleSheet("color: #e2e8f0; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Credits info
        credits_card = InfoCard(
            "Development Team",
            "• Lead Developer: Community Contributors\n"
            "• UI/UX Design: Modern Dark Theme\n"
            "• Testing: Community Feedback\n"
            "• Documentation: Integrated Help System"
        )
        layout.addWidget(credits_card)
        
        thanks_card = InfoCard(
            "Special Thanks",
            "• Warp.dev for providing the AI coding platform\n"
            "• PyQt5 community for the excellent GUI framework\n"
            "• All users who provided feedback and suggestions\n"
            "• Open source contributors and maintainers"
        )
        layout.addWidget(thanks_card)
        
        section.setLayout(layout)
        return section
    
    def create_links_section(self):
        """Create links and contact section"""
        section = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Section title
        title_label = QLabel("🔗 Links & Contact")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_label.setStyleSheet("color: #e2e8f0; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
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
        title_label = QLabel("📏 License & Legal Information")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_label.setStyleSheet("color: #e2e8f0; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
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
        
        license_card = InfoCard("📜 Open Source License (MIT)", license_text)
        layout.addWidget(license_card)
        
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
        
        terms_card = InfoCard("⚠️ Usage Terms & Disclaimer", terms_text)
        layout.addWidget(terms_card)
        
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
        
        ack_card = InfoCard("🙏 Third-party Acknowledgments", acknowledgments_text)
        layout.addWidget(ack_card)
        
        # Copyright and Source Code notice
        footer_layout = QVBoxLayout()
        footer_layout.setSpacing(5)
        
        copyright_label = QLabel("© 2025 Warp Account Manager Contributors. Released under MIT License.")
        copyright_label.setFont(QFont("Segoe UI", 10))
        copyright_label.setStyleSheet("color: #718096; margin-top: 10px;")
        copyright_label.setAlignment(Qt.AlignCenter)
        footer_layout.addWidget(copyright_label)
        
        source_label = QLabel("📝 Source code available on GitHub: https://github.com/hj01857655/WARP_reg_and_manager")
        source_label.setFont(QFont("Segoe UI", 9))
        source_label.setStyleSheet("color: #63b3ed; margin-top: 5px;")
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
