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
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title_label.setStyleSheet("color: #63b3ed;")
        layout.addWidget(title_label)
        
        # Content
        content_label = QLabel(content)
        content_label.setFont(QFont("Segoe UI", 10))
        content_label.setStyleSheet("color: #e2e8f0; line-height: 1.4;")
        content_label.setWordWrap(True)
        content_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(content_label)
        
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
        title_label = QLabel("Warp Account Manager")
        title_label.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title_label.setStyleSheet("color: #63b3ed;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Version
        version_label = QLabel("Version 2.0.0")
        version_label.setFont(QFont("Segoe UI", 14))
        version_label.setStyleSheet("color: #a0aec0;")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
        
        # Description
        desc_label = QLabel("A powerful tool for managing Warp.dev accounts with advanced features\nand modern user interface")
        desc_label.setFont(QFont("Segoe UI", 12))
        desc_label.setStyleSheet("color: #e2e8f0; line-height: 1.5;")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        section.setLayout(layout)
        return section
    
    def create_app_info_section(self):
        """Create application information section with version and changelog"""
        section = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Section title
        title_label = QLabel("📋 Application Information")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_label.setStyleSheet("color: #e2e8f0; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Version and changelog card
        version_changelog = self.get_version_changelog()
        version_card = InfoCard(
            "📌 Version & Changelog",
            version_changelog
        )
        layout.addWidget(version_card)
        
        # Info cards
        features_card = InfoCard(
            "✨ Key Features",
            "• Multi-account management with health monitoring\n"
            "• Automatic token refresh and account switching\n"
            "• Modern responsive user interface with animations\n"
            "• Real-time system status monitoring\n"
            "• Batch operations for account management\n"
            "• Multi-language support (English/中文)\n"
            "• Advanced mitmproxy integration\n"
            "• Registry monitoring and auto-switching\n"
            "• Secure local data encryption"
        )
        layout.addWidget(features_card)
        
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
        title_label = QLabel("🛠️ Technology Stack")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_label.setStyleSheet("color: #e2e8f0; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Core technologies
        core_tech_card = InfoCard(
            "🖥️ Core Technologies",
            f"• Python {sys.version.split()[0]} - Main development language\n"
            "• PyQt5 5.15+ - Cross-platform GUI framework\n"
            "• SQLite 3.x - Embedded database system\n"
            "• asyncio - Asynchronous programming support"
        )
        layout.addWidget(core_tech_card)
        
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
        github_btn = QPushButton("📂 GitHub Repository")
        github_btn.setFixedHeight(45)
        github_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/hj01857655/WARP_reg_and_manager")))
        github_btn.setStyleSheet(self.get_button_style("#4a5568"))
        buttons_layout.addWidget(github_btn)
        
        # Telegram channel
        telegram_btn = QPushButton("📱 Telegram Channel")
        telegram_btn.setFixedHeight(45)
        telegram_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://t.me/warp5215")))
        telegram_btn.setStyleSheet(self.get_button_style("#0088cc"))
        buttons_layout.addWidget(telegram_btn)
        
        # Telegram chat
        chat_btn = QPushButton("💬 Telegram Chat")
        chat_btn.setFixedHeight(45)
        chat_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://t.me/warp1215")))
        chat_btn.setStyleSheet(self.get_button_style("#0088cc"))
        buttons_layout.addWidget(chat_btn)
        
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