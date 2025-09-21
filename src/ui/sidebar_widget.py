#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sidebar Widget - Modern Collapsible Navigation Sidebar
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QFrame, QScrollArea, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QRect, QEasingCurve, QTimer
from PyQt5.QtGui import QFont, QIcon, QColor, QPainter, QLinearGradient
from src.config.languages import _


class SidebarButton(QPushButton):
    """Modern custom sidebar navigation button with animations and effects"""
    
    def __init__(self, text, icon_text="", parent=None):
        super().__init__(parent)
        self.full_text = text
        self.icon_text = icon_text
        self.is_collapsed = False
        self.hover_animation = None
        
        self.setCheckable(True)
        self.setFixedHeight(56)
        self.setCursor(Qt.PointingHandCursor)
        
        # Set up layout
        layout = QHBoxLayout()
        layout.setContentsMargins(18, 0, 18, 0)
        layout.setSpacing(16)
        
        # Icon container with background
        icon_container = QWidget()
        icon_container.setFixedSize(36, 36)
        icon_container.setStyleSheet("""
            QWidget {
                background-color: rgba(99, 179, 237, 0.15);
                border-radius: 18px;
                border: 1px solid rgba(99, 179, 237, 0.3);
            }
        """)
        
        icon_layout = QHBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        
        # Icon label
        self.icon_label = QLabel(icon_text)
        self.icon_label.setFont(QFont("Segoe UI Emoji", 18))
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("color: #63b3ed; background: transparent; border: none;")
        icon_layout.addWidget(self.icon_label)
        
        layout.addWidget(icon_container)
        
        # Text label
        self.text_label = QLabel(text)
        self.text_label.setFont(QFont("Segoe UI", 12, QFont.Medium))
        self.text_label.setStyleSheet("color: #e2e8f0; background: transparent;")
        layout.addWidget(self.text_label)
        
        # Active indicator
        self.indicator = QLabel()
        self.indicator.setFixedSize(4, 24)
        self.indicator.setStyleSheet("""
            QLabel {
                background-color: #63b3ed;
                border-radius: 2px;
            }
        """)
        self.indicator.hide()
        
        layout.addStretch()
        layout.addWidget(self.indicator)
        
        self.setLayout(layout)
        
        # Add shadow effect
        self.shadow_effect = QGraphicsDropShadowEffect()
        self.shadow_effect.setBlurRadius(15)
        self.shadow_effect.setColor(QColor(0, 0, 0, 40))
        self.shadow_effect.setOffset(0, 2)
        self.setGraphicsEffect(self.shadow_effect)
        
        # Apply modern styles (PyQt5 compatible)
        self.setStyleSheet("""
            SidebarButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 rgba(45, 55, 72, 0.8),
                                          stop: 1 rgba(26, 32, 44, 0.8));
                border: 1px solid rgba(74, 85, 104, 0.4);
                border-radius: 12px;
                text-align: left;
                padding: 0px;
                margin: 4px 12px;
            }
            
            SidebarButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 rgba(56, 67, 84, 0.9),
                                          stop: 1 rgba(37, 47, 63, 0.9));
                border: 1px solid rgba(99, 179, 237, 0.6);
            }
            
            SidebarButton:checked {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 rgba(99, 179, 237, 0.25),
                                          stop: 1 rgba(66, 153, 225, 0.15));
                border: 1px solid rgba(99, 179, 237, 0.8);
            }
            
            SidebarButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 rgba(99, 179, 237, 0.35),
                                          stop: 1 rgba(66, 153, 225, 0.25));
            }
        """)
    
    def set_collapsed(self, collapsed):
        """Set button collapsed state with smooth animation"""
        self.is_collapsed = collapsed
        if collapsed:
            self.text_label.hide()
            self.indicator.hide()
            self.setFixedWidth(70)
            self.setToolTip(self.full_text)
            # Update margins for collapsed state
            self.layout().setContentsMargins(17, 0, 17, 0)
        else:
            self.text_label.show()
            if self.isChecked():
                self.indicator.show()
            self.setMinimumWidth(220)
            self.setMaximumWidth(300)
            self.setToolTip("")
            # Restore margins for expanded state
            self.layout().setContentsMargins(18, 0, 18, 0)
    
    def setChecked(self, checked):
        """Override to control indicator visibility"""
        super().setChecked(checked)
        if checked and not self.is_collapsed:
            self.indicator.show()
        else:
            self.indicator.hide()


class SidebarWidget(QWidget):
    """Modern collapsible sidebar navigation widget with glassmorphism effects"""
    
    # Signals
    menu_selected = pyqtSignal(int)  # Emit selected menu index
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_collapsed = False
        self.expanded_width = 260
        self.collapsed_width = 80
        
        self.init_ui()
        self.setup_animations()
        
        # Add breathing animation for status indicator
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.animate_status)
        self.status_timer.start(2000)  # Every 2 seconds
        
    def init_ui(self):
        """Initialize the modern sidebar UI"""
        self.setFixedWidth(self.expanded_width)
        self.setMinimumHeight(600)
        
        # Add shadow effect to entire sidebar
        sidebar_shadow = QGraphicsDropShadowEffect()
        sidebar_shadow.setBlurRadius(25)
        sidebar_shadow.setColor(QColor(0, 0, 0, 80))
        sidebar_shadow.setOffset(3, 0)
        self.setGraphicsEffect(sidebar_shadow)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header section
        header = self.create_header()
        layout.addWidget(header)
        
        # Elegant separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFixedHeight(1)
        separator.setStyleSheet("""
            QFrame { 
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 transparent,
                                          stop: 0.5 rgba(99, 179, 237, 0.6),
                                          stop: 1 transparent);
                margin: 10px 20px;
                border: none;
            }
        """)
        layout.addWidget(separator)
        
        # Navigation menu
        self.menu_widget = self.create_menu()
        layout.addWidget(self.menu_widget)
        
        # Spacer
        layout.addStretch()
        
        # Another elegant separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setFixedHeight(1)
        separator2.setStyleSheet(separator.styleSheet())
        layout.addWidget(separator2)
        
        # Footer section
        footer = self.create_footer()
        layout.addWidget(footer)
        
        self.setLayout(layout)
        
        # Apply modern glassmorphism sidebar styles
        self.setStyleSheet("""
            SidebarWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 rgba(26, 32, 44, 0.95),
                                          stop: 0.3 rgba(45, 55, 72, 0.92),
                                          stop: 0.7 rgba(26, 32, 44, 0.95),
                                          stop: 1 rgba(13, 17, 23, 0.98));
                border: none;
                border-right: 2px solid rgba(99, 179, 237, 0.3);
            }
        """)
    
    def create_header(self):
        """Create modern sidebar header with logo and toggle button"""
        header = QWidget()
        header.setFixedHeight(85)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 15, 15, 15)
        layout.setSpacing(15)
        
        # Logo icon with glow effect
        logo_container = QWidget()
        logo_container.setFixedSize(45, 45)
        logo_container.setStyleSheet("""
            QWidget {
                background: qradialgradient(cx: 0.5, cy: 0.5, radius: 0.8,
                                          stop: 0 rgba(99, 179, 237, 0.3),
                                          stop: 1 rgba(99, 179, 237, 0.1));
                border: 2px solid rgba(99, 179, 237, 0.5);
                border-radius: 22px;
            }
        """)
        
        logo_layout = QHBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        
        logo_icon = QLabel("🚀")
        logo_icon.setFont(QFont("Segoe UI Emoji", 20))
        logo_icon.setAlignment(Qt.AlignCenter)
        logo_icon.setStyleSheet("background: transparent; border: none;")
        logo_layout.addWidget(logo_icon)
        
        layout.addWidget(logo_container)
        
        # Title with gradient text effect
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(2)
        
        self.title_label = QLabel(_('app_title'))
        self.title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.title_label.setStyleSheet("""
            color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                 stop: 0 #63b3ed, stop: 1 #4299e1);
            background: transparent;
        """)
        title_layout.addWidget(self.title_label)
        
        self.subtitle_label = QLabel(_('sidebar_subtitle'))
        self.subtitle_label.setFont(QFont("Segoe UI", 9))
        self.subtitle_label.setStyleSheet("color: rgba(226, 232, 240, 0.7); background: transparent;")
        title_layout.addWidget(self.subtitle_label)
        
        layout.addWidget(title_container)
        layout.addStretch()
        
        # Modern toggle button with animation
        self.toggle_btn = QPushButton("◀")
        self.toggle_btn.setFixedSize(36, 36)
        self.toggle_btn.setFont(QFont("Segoe UI", 11))
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.clicked.connect(self.toggle_sidebar)
        
        # Add shadow to toggle button
        toggle_shadow = QGraphicsDropShadowEffect()
        toggle_shadow.setBlurRadius(10)
        toggle_shadow.setColor(QColor(0, 0, 0, 60))
        toggle_shadow.setOffset(0, 2)
        self.toggle_btn.setGraphicsEffect(toggle_shadow)
        
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 rgba(74, 85, 104, 0.8),
                                          stop: 1 rgba(45, 55, 72, 0.9));
                border: 1px solid rgba(99, 179, 237, 0.4);
                border-radius: 18px;
                color: #e2e8f0;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 rgba(99, 179, 237, 0.6),
                                          stop: 1 rgba(66, 153, 225, 0.8));
                border: 1px solid rgba(99, 179, 237, 0.8);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 rgba(99, 179, 237, 0.8),
                                          stop: 1 rgba(66, 153, 225, 0.9));
            }
        """)
        layout.addWidget(self.toggle_btn)
        
        header.setLayout(layout)
        return header
    
    def create_menu(self):
        """Create modern navigation menu"""
        menu_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 15, 0, 15)
        layout.setSpacing(8)
        
        # Menu section label
        self.section_label = QLabel(_('sidebar_navigation'))
        self.section_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.section_label.setStyleSheet("""
            color: rgba(99, 179, 237, 0.8);
            padding: 0px 20px 10px 20px;
            background: transparent;
            letter-spacing: 1px;
        """)
        layout.addWidget(self.section_label)
        
        # Enhanced menu items with better icons
        menu_items = [
            ("📊", _('sidebar_dashboard')),
            ("👥", _('sidebar_accounts')),
            ("ℹ️", _('sidebar_about'))
        ]
        
        self.menu_buttons = []
        for i, (icon, text) in enumerate(menu_items):
            btn = SidebarButton(text, icon)
            btn.clicked.connect(lambda checked, idx=i: self.on_menu_clicked(idx))
            layout.addWidget(btn)
            self.menu_buttons.append(btn)
        
        # Set accounts as default active
        if len(self.menu_buttons) >= 2:
            self.menu_buttons[1].setChecked(True)  # Default to accounts page
        
        menu_widget.setLayout(layout)
        return menu_widget
    
    def create_footer(self):
        """Create modern sidebar footer with status"""
        footer = QWidget()
        footer.setFixedHeight(90)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(8)
        
        # Status card
        status_card = QWidget()
        status_card.setStyleSheet("""
            QWidget {
                background: rgba(45, 55, 72, 0.6);
                border: 1px solid rgba(74, 85, 104, 0.4);
                border-radius: 8px;
                padding: 8px;
            }
        """)
        
        status_layout = QVBoxLayout(status_card)
        status_layout.setContentsMargins(12, 8, 12, 8)
        status_layout.setSpacing(4)
        
        self.status_label = QLabel(_('sidebar_status'))
        self.status_label.setFont(QFont("Segoe UI", 9, QFont.Medium))
        self.status_label.setStyleSheet("color: #68d391; background: transparent;")
        self.status_label.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.status_label)
        
        self.version_label = QLabel(_('sidebar_version'))
        self.version_label.setFont(QFont("Segoe UI", 8))
        self.version_label.setStyleSheet("color: rgba(160, 174, 192, 0.8); background: transparent;")
        self.version_label.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.version_label)
        
        layout.addWidget(status_card)
        
        footer.setLayout(layout)
        return footer
    
    
    def animate_status(self):
        """Animate status indicator with breathing effect"""
        current_text = self.status_label.text()
        if "🟢" in current_text:
            # Breathing effect - just update the emoji
            if current_text.startswith("🟢"):
                self.status_label.setText(current_text.replace("🟢", "🔵"))
            else:
                self.status_label.setText(current_text.replace("🔵", "🟢"))
    
    def setup_animations(self):
        """Setup animation for sidebar collapse/expand"""
        self.animation = QPropertyAnimation(self, b"minimumWidth")
        self.animation.setDuration(250)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        
        self.animation2 = QPropertyAnimation(self, b"maximumWidth")
        self.animation2.setDuration(250)
        self.animation2.setEasingCurve(QEasingCurve.InOutQuart)
    
    def toggle_sidebar(self):
        """Toggle sidebar collapsed/expanded state with smooth animation"""
        self.is_collapsed = not self.is_collapsed
        
        if self.is_collapsed:
            # Collapse animation
            self.animation.setStartValue(self.expanded_width)
            self.animation.setEndValue(self.collapsed_width)
            self.animation2.setStartValue(self.expanded_width)
            self.animation2.setEndValue(self.collapsed_width)
            self.toggle_btn.setText("▶")
            
            # Hide text elements
            self.title_label.hide()
            self.subtitle_label.hide()
            self.version_label.hide()
            
            # Collapse menu buttons
            for btn in self.menu_buttons:
                if hasattr(btn, 'set_collapsed'):
                    btn.set_collapsed(True)
                
        else:
            # Expand animation
            self.animation.setStartValue(self.collapsed_width)
            self.animation.setEndValue(self.expanded_width)
            self.animation2.setStartValue(self.collapsed_width)
            self.animation2.setEndValue(self.expanded_width)
            self.toggle_btn.setText("◀")
            
            # Show text elements
            self.title_label.show()
            self.subtitle_label.show()
            self.version_label.show()
            
            # Expand menu buttons
            for btn in self.menu_buttons:
                if hasattr(btn, 'set_collapsed'):
                    btn.set_collapsed(False)
        
        self.animation.start()
        self.animation2.start()
    
    def on_menu_clicked(self, index):
        """Handle menu item click"""
        # Update button states
        for i, btn in enumerate(self.menu_buttons):
            btn.setChecked(i == index)
        
        # Emit signal
        self.menu_selected.emit(index)
    
    def set_status(self, status_text, color="#68d391"):
        """Update status label"""
        self.status_label.setText(status_text)
        self.status_label.setStyleSheet(f"color: {color};")
    
    def select_menu(self, index):
        """Programmatically select a menu item"""
        if 0 <= index < len(self.menu_buttons):
            self.on_menu_clicked(index)
    
    def refresh_ui_texts(self):
        """Refresh sidebar texts when language changes"""
        # Update title and subtitle
        self.title_label.setText(_('app_title'))
        self.subtitle_label.setText(_('sidebar_subtitle'))
        
        # Update section label
        self.section_label.setText(_('sidebar_navigation'))
        
        # Update menu button texts
        menu_texts = [
            _('sidebar_dashboard'),
            _('sidebar_accounts'),
            _('sidebar_about')
        ]
        
        for i, btn in enumerate(self.menu_buttons[:3]):  # Only update navigation buttons
            if i < len(menu_texts):
                btn.full_text = menu_texts[i]
                btn.text_label.setText(menu_texts[i])
        
        # Update status and version labels
        self.status_label.setText(_('sidebar_status'))
        self.version_label.setText(_('sidebar_version'))
