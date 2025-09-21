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
        
        # Application info section
        app_info_section = self.create_app_info_section()
        layout.addWidget(app_info_section)
        
        # System info section
        system_info_section = self.create_system_info_section()
        layout.addWidget(system_info_section)
        
        # Credits section
        credits_section = self.create_credits_section()
        layout.addWidget(credits_section)
        
        # Links section
        links_section = self.create_links_section()
        layout.addWidget(links_section)
        
        # License section
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
        desc_label = QLabel("A powerful tool for managing Warp.dev accounts with advanced features\\nand modern user interface")
        desc_label.setFont(QFont("Segoe UI", 12))
        desc_label.setStyleSheet("color: #e2e8f0; line-height: 1.5;")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        section.setLayout(layout)
        return section
    
    def create_app_info_section(self):
        """Create application information section"""
        section = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Section title
        title_label = QLabel("📋 Application Information")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_label.setStyleSheet("color: #e2e8f0; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Info cards
        features_card = InfoCard(
            "✨ Key Features",
            "• Multi-account management with health monitoring\\n"\n            "• Automatic token refresh and account switching\\n"\n            "• Modern responsive user interface\\n"\n            "• Real-time system status monitoring\\n"\n            "• Batch operations for account management\\n"\n            "• Multi-language support (English/中文)\\n"\n            "• Advanced proxy integration"\n        )\n        layout.addWidget(features_card)\n        \n        tech_card = InfoCard(\n            "🛠️ Technology Stack",\n            f"• Python {sys.version.split()[0]}\\n"\n            f"• PyQt5 GUI Framework\\n"\n            f"• SQLite Database\\n"\n            f"• Mitmproxy Integration\\n"\n            f"• Multi-threading Architecture\\n"\n            f"• Modern CSS Styling"\n        )\n        layout.addWidget(tech_card)\n        \n        section.setLayout(layout)\n        return section\n    \n    def create_system_info_section(self):\n        """Create system information section"""\n        section = QWidget()\n        layout = QVBoxLayout()\n        layout.setContentsMargins(0, 0, 0, 0)\n        layout.setSpacing(15)\n        \n        # Section title\n        title_label = QLabel("💻 System Information")\n        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))\n        title_label.setStyleSheet("color: #e2e8f0; margin-bottom: 10px;")\n        layout.addWidget(title_label)\n        \n        # System info\n        system_info = f"• Operating System: {platform.system()} {platform.release()}\\n"\n        system_info += f"• Architecture: {platform.machine()}\\n"\n        system_info += f"• Python Version: {sys.version.split()[0]}\\n"\n        system_info += f"• Platform: {platform.platform()}\\n"\n        system_info += f"• Processor: {platform.processor() or 'Unknown'}"\n        \n        system_card = InfoCard("System Details", system_info)\n        layout.addWidget(system_card)\n        \n        section.setLayout(layout)\n        return section\n    \n    def create_credits_section(self):\n        """Create credits and acknowledgments section"""\n        section = QWidget()\n        layout = QVBoxLayout()\n        layout.setContentsMargins(0, 0, 0, 0)\n        layout.setSpacing(15)\n        \n        # Section title\n        title_label = QLabel("👥 Credits & Acknowledgments")\n        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))\n        title_label.setStyleSheet("color: #e2e8f0; margin-bottom: 10px;")\n        layout.addWidget(title_label)\n        \n        # Credits info\n        credits_card = InfoCard(\n            "Development Team",\n            "• Lead Developer: Community Contributors\\n"\n            "• UI/UX Design: Modern Dark Theme\\n"\n            "• Testing: Community Feedback\\n"\n            "• Documentation: Integrated Help System"\n        )\n        layout.addWidget(credits_card)\n        \n        thanks_card = InfoCard(\n            "Special Thanks",\n            "• Warp.dev for providing the AI coding platform\\n"\n            "• PyQt5 community for the excellent GUI framework\\n"\n            "• All users who provided feedback and suggestions\\n"\n            "• Open source contributors and maintainers"\n        )\n        layout.addWidget(thanks_card)\n        \n        section.setLayout(layout)\n        return section\n    \n    def create_links_section(self):\n        """Create links and contact section"""\n        section = QWidget()\n        layout = QVBoxLayout()\n        layout.setContentsMargins(0, 0, 0, 0)\n        layout.setSpacing(15)\n        \n        # Section title\n        title_label = QLabel("🔗 Links & Contact")\n        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))\n        title_label.setStyleSheet("color: #e2e8f0; margin-bottom: 10px;")\n        layout.addWidget(title_label)\n        \n        # Links buttons\n        buttons_layout = QHBoxLayout()\n        buttons_layout.setSpacing(15)\n        \n        # GitHub repository\n        github_btn = QPushButton("📂 GitHub Repository")\n        github_btn.setFixedHeight(45)\n        github_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/hj01857655/WARP_reg_and_manager")))\n        github_btn.setStyleSheet(self.get_button_style("#4a5568"))\n        buttons_layout.addWidget(github_btn)\n        \n        # Telegram channel\n        telegram_btn = QPushButton("📱 Telegram Channel")\n        telegram_btn.setFixedHeight(45)\n        telegram_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://t.me/warp5215")))\n        telegram_btn.setStyleSheet(self.get_button_style("#0088cc"))\n        buttons_layout.addWidget(telegram_btn)\n        \n        # Telegram chat\n        chat_btn = QPushButton("💬 Telegram Chat")\n        chat_btn.setFixedHeight(45)\n        chat_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://t.me/warp1215")))\n        chat_btn.setStyleSheet(self.get_button_style("#0088cc"))\n        buttons_layout.addWidget(chat_btn)\n        \n        buttons_layout.addStretch()\n        layout.addLayout(buttons_layout)\n        \n        section.setLayout(layout)\n        return section\n    \n    def create_license_section(self):\n        """Create license information section"""\n        section = QWidget()\n        layout = QVBoxLayout()\n        layout.setContentsMargins(0, 0, 0, 0)\n        layout.setSpacing(15)\n        \n        # Section title\n        title_label = QLabel("📜 License & Legal")\n        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))\n        title_label.setStyleSheet("color: #e2e8f0; margin-bottom: 10px;")\n        layout.addWidget(title_label)\n        \n        # License text\n        license_text = \"\"\"\nThis software is provided \"as is\" without warranty of any kind.\n\nThe software is intended for educational and personal use only.\nUsers are responsible for complying with Warp.dev's terms of service.\n\nBy using this software, you agree to:\n• Use it responsibly and ethically\n• Comply with all applicable laws and regulations\n• Not use it for any malicious purposes\n• Respect the terms of service of all integrated services\n\nThe developers are not responsible for any misuse or damage\ncaused by the use of this software.\n        \"\"\".strip()\n        \n        license_card = InfoCard("License Agreement", license_text)\n        layout.addWidget(license_card)\n        \n        # Copyright notice\n        copyright_label = QLabel("© 2025 Warp Account Manager. All rights reserved.")\n        copyright_label.setFont(QFont("Segoe UI", 10))\n        copyright_label.setStyleSheet("color: #718096; margin-top: 10px;")\n        copyright_label.setAlignment(Qt.AlignCenter)\n        layout.addWidget(copyright_label)\n        \n        section.setLayout(layout)\n        return section\n    \n    def get_button_style(self, color):\n        """Get button style with specified color"""\n        return f\"\"\"\n            QPushButton {{\n                background-color: {color};\n                color: white;\n                border: none;\n                border-radius: 8px;\n                font-size: 13px;\n                font-weight: bold;\n                padding: 0 20px;\n            }}\n            QPushButton:hover {{\n                background-color: {color}dd;\n                transform: translateY(-1px);\n            }}\n            QPushButton:pressed {{\n                background-color: {color}aa;\n            }}\n        \"\"\"