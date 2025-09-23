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
from src.ui.theme_manager import theme_manager


class SidebarButton(QPushButton):
    """Modern custom sidebar navigation button with animations and effects"""
    
    def __init__(self, text, icon_text="", parent=None):
        super().__init__(parent)
        self.full_text = text
        self.icon_text = icon_text
        
        self.setCheckable(True)
        self.setFixedHeight(80)  # 增加按钮高度
        self.setMinimumWidth(250)  # 减少按钮最小宽度
        self.setMaximumWidth(300)  # 减少按钮最大宽度
        self.setCursor(Qt.PointingHandCursor)
        
        # Set up layout
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 10, 20, 10)  # 适应正常按钮高度的内边距
        layout.setSpacing(15)  # 适当的组件间距
        
        # Simple icon without container - remove all borders and outlines
        self.icon_label = QLabel(icon_text)
        self.icon_label.setFont(QFont("Segoe UI Emoji", 24))  # 增加图标大小以适应更高的按钮
        self.icon_label.setFixedWidth(40)  # 适应正常按钮的图标宽度
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet(f"""
            QLabel {{
                color: {theme_manager.get_color('text_secondary')};
                background: transparent;
                border: none;
                outline: none;
                text-decoration: none;
            }}
        """)
        layout.addWidget(self.icon_label)
        
        # Text label - remove all borders and outlines
        self.text_label = QLabel(text)
        self.text_label.setFont(QFont("Segoe UI", 16, QFont.Medium))  # 增加文字大小以适应更高的按钮
        self.text_label.setStyleSheet(f"""
            QLabel {{
                color: {theme_manager.get_color('text_primary')};
                background: transparent;
                border: none;
                outline: none;
                text-decoration: none;
            }}
        """)
        layout.addWidget(self.text_label)
        
        # Active indicator
        self.indicator = QLabel()
        self.indicator.setFixedSize(4, 24)
        self.indicator.setStyleSheet(f"""
            QLabel {{
                background-color: {theme_manager.get_color('accent_blue')};
                border-radius: 2px;
            }}
        """)
        self.indicator.hide()
        
        layout.addStretch()
        layout.addWidget(self.indicator)
        
        self.setLayout(layout)
        
        # Remove shadow effect to avoid black outlines in light theme
        # self.shadow_effect = QGraphicsDropShadowEffect()
        # self.shadow_effect.setBlurRadius(15)
        # self.shadow_effect.setColor(QColor(0, 0, 0, 40))
        # self.shadow_effect.setOffset(0, 2)
        # self.setGraphicsEffect(self.shadow_effect)
        
        # Apply modern styles with enhanced effects
        self.update_button_style(False)
    
    
    def setChecked(self, checked):
        """Override to control indicator visibility"""
        super().setChecked(checked)
        if checked:
            self.indicator.show()
        else:
            self.indicator.hide()
        self.update_button_style(checked)
    
    def update_button_style(self, checked):
        """Update button style based on checked state"""
        if checked:
            # Active state - simple blue background
            self.setStyleSheet(f"""
                SidebarButton {{
                    background-color: {theme_manager.get_color('accent_blue')};
                    border: none;
                    outline: none;
                    border-radius: 8px;
                    text-align: left;
                    padding: 0px;
                    margin: 1px 4px;
                }}
                SidebarButton:focus {{
                    border: none;
                    outline: none;
                }}
            """)
            # Update text and icon color for active state using theme manager
            self.text_label.setStyleSheet("""
                QLabel {
                    color: white;
                    background: transparent;
                    border: none;
                    outline: none;
                    text-decoration: none;
                }
            """)
            self.icon_label.setStyleSheet("""
                QLabel {
                    color: white;
                    background: transparent;
                    border: none;
                    outline: none;
                    text-decoration: none;
                }
            """)
        else:
            # Normal state - transparent
            self.setStyleSheet(f"""
                SidebarButton {{
                    background: transparent;
                    border: none;
                    outline: none;
                    border-radius: 8px;
                    text-align: left;
                    padding: 0px;
                    margin: 1px 4px;
                }}
                
                SidebarButton:hover {{
                    background-color: {theme_manager.get_card_theme('blue')['background']};
                    border: none;
                    outline: none;
                }}
                
                SidebarButton:focus {{
                    border: none;
                    outline: none;
                }}
            """)
            # Reset text and icon color for light theme
            self.text_label.setStyleSheet(f"""
                QLabel {{
                    color: {theme_manager.get_color('text_primary')};
                    background: transparent;
                    border: none;
                    outline: none;
                    text-decoration: none;
                }}
            """)
            self.icon_label.setStyleSheet(f"""
                QLabel {{
                    color: {theme_manager.get_color('text_secondary')};
                    background: transparent;
                    border: none;
                    outline: none;
                    text-decoration: none;
                }}
            """)


class SidebarWidget(QWidget):
    """Modern collapsible sidebar navigation widget with glassmorphism effects"""
    
    # Signals
    menu_selected = pyqtSignal(int)  # Emit selected menu index
    sidebar_toggled = pyqtSignal(bool)  # Emit when sidebar is toggled
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
        # Add breathing animation for status indicator (disabled for now)
        # self.status_timer = QTimer()
        # self.status_timer.timeout.connect(self.animate_status)
        # self.status_timer.start(2000)  # Every 2 seconds
        
    def init_ui(self):
        """Initialize the modern sidebar UI"""
        self.expanded_width = 300  # 进一步减少展开状态宽度
        self.collapsed_width = 70   # 折叠状态宽度
        self.is_expanded = True
        self.setFixedWidth(self.expanded_width)
        self.setMinimumHeight(800)  # 增加最小高度
        
        # Add subtle shadow effect to entire sidebar for light theme
        sidebar_shadow = QGraphicsDropShadowEffect()
        sidebar_shadow.setBlurRadius(15)
        sidebar_shadow.setColor(QColor(0, 0, 0, 20))  # Much lighter shadow
        sidebar_shadow.setOffset(2, 0)
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
        # Use theme manager for separator styling
        blue_theme = theme_manager.get_card_theme('blue')
        separator_style = f"""
            QFrame {{ 
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 transparent,
                                          stop: 0.5 {blue_theme['border']},
                                          stop: 1 transparent);
                margin: 10px 20px;
                border: none;
            }}
        """
        separator.setStyleSheet(separator_style)
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
        
        # Use theme manager for sidebar background
        self.setStyleSheet(f"""
            SidebarWidget {{
                background-color: {theme_manager.get_color('background_primary')};
                border: none;
                border-right: 1px solid {theme_manager.get_color('border_light')};
            }}
        """)
    
    def create_header(self):
        """Create modern sidebar header with logo and toggle button"""
        header = QWidget()
        header.setFixedHeight(140)  # 再次增加头部高度
        
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 15, 15, 15)
        layout.setSpacing(15)
        
        # Simple logo icon
        logo_icon = QLabel("📦")
        logo_icon.setFont(QFont("Segoe UI Emoji", 42))  # 再次增加logo字体大小
        logo_icon.setFixedSize(40, 40)
        logo_icon.setAlignment(Qt.AlignCenter)
        logo_icon.setStyleSheet(f"color: {theme_manager.get_color('accent_blue')}; background: transparent; border: none; outline: none; border-radius: 8px; padding: 6px;")
        layout.addWidget(logo_icon)
        
        # Title with gradient text effect
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(2)
        
        self.title_label = QLabel("Warp Tools")
        self.title_label.setFont(QFont("Segoe UI", 28, QFont.Bold))  # 再次增加标题字体大小
        self.title_label.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; background: transparent; border: none; outline: none; border-radius: 8px; padding: 6px 12px;")
        title_layout.addWidget(self.title_label)
        
        self.subtitle_label = QLabel(_('sidebar_subtitle'))
        self.subtitle_label.setFont(QFont("Segoe UI", 16))  # 再次增加副标题字体大小
        self.subtitle_label.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; background: transparent; border: none; outline: none; border-radius: 6px; padding: 4px 8px;")
        title_layout.addWidget(self.subtitle_label)
        
        layout.addWidget(title_container)
        layout.addStretch()
        
        # Toggle button for expand/collapse
        self.toggle_button = QPushButton("«")
        self.toggle_button.setFont(QFont("Arial", 18, QFont.Bold))
        self.toggle_button.setFixedSize(35, 35)
        # Use theme manager for toggle button styling
        blue_theme = theme_manager.get_card_theme('blue')
        self.toggle_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {blue_theme['background']};
                border: 1px solid {blue_theme['border']};
                border-radius: 18px;
                color: {theme_manager.get_color('accent_blue')};
            }}
            QPushButton:hover {{
                background-color: rgba(59, 130, 246, 0.2);
                border: 1px solid {blue_theme['hover_border']};
            }}
            QPushButton:pressed {{
                background-color: rgba(59, 130, 246, 0.3);
            }}
        """)
        self.toggle_button.clicked.connect(self.toggle_sidebar)
        layout.addWidget(self.toggle_button)
        
        header.setLayout(layout)
        return header
    
    def create_menu(self):
        """Create modern navigation menu"""
        menu_widget = QWidget()
        menu_widget.setMinimumHeight(400)  # 设置导航区域最小高度
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 20, 0, 20)  # 恢复一些上下边距
        layout.setSpacing(15)  # 增加菜单项之间的间距
        
        # Menu section label
        self.section_label = QLabel(_('sidebar_navigation'))
        self.section_label.setFont(QFont("Segoe UI", 20, QFont.Bold))  # 大幅增加导航标签字体大小
        # Use theme manager for navigation section label
        blue_theme = theme_manager.get_card_theme('blue')
        self.section_label.setStyleSheet(f"""
            color: {blue_theme['accent']};
            padding: 0px 25px 15px 25px;  
            background: transparent;
            letter-spacing: 1px;
            border: none;
            outline: none;
            border-radius: 8px;
        """)
        layout.addWidget(self.section_label)
        
        # Enhanced menu items with better icons
        menu_items = [
            ("📊", _('sidebar_dashboard')),
            ("👥", _('sidebar_accounts')),
            ("🧹", _('sidebar_cleanup')),
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
        footer.setMinimumHeight(100)
        footer.setMaximumHeight(100)
        
        # Main footer layout
        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(15, 10, 15, 10)
        footer_layout.setSpacing(0)
        
        # Simple status card
        status_card = QFrame()
        self.status_card = status_card
        status_card.setObjectName("statusCard")
        status_card.setFixedHeight(60)
        # Use theme manager for status card styling
        status_card.setStyleSheet(f"""
            QFrame#statusCard {{
                background-color: {theme_manager.get_color('background_secondary')};
                border: 1px solid {theme_manager.get_color('border_light')};
                border-radius: 8px;
            }}
        """)
        
        # Status card internal layout
        status_layout = QVBoxLayout(status_card)
        status_layout.setContentsMargins(10, 10, 10, 10)
        status_layout.setSpacing(2)
        status_layout.setAlignment(Qt.AlignCenter)
        
        # Status label
        self.status_label = QLabel(_('sidebar_status'))
        self.status_label.setFont(QFont("Segoe UI", 11, QFont.Medium))
        self.status_label.setStyleSheet(f"color: {theme_manager.get_color('accent_green')}; background: transparent; border: none; outline: none; border-radius: 6px; padding: 4px 8px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFixedHeight(20)
        status_layout.addWidget(self.status_label)
        
        # Version label
        self.version_label = QLabel("v1.3.0")
        self.version_label.setFont(QFont("Segoe UI", 10))
        self.version_label.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; background: transparent; border: none; outline: none; border-radius: 6px; padding: 4px 8px;")
        self.version_label.setAlignment(Qt.AlignCenter)
        self.version_label.setFixedHeight(18)
        status_layout.addWidget(self.version_label)
        
        footer_layout.addWidget(status_card)
        footer_layout.addStretch()
        
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
            _('sidebar_cleanup'),
            _('sidebar_about')
        ]
        
        for i, btn in enumerate(self.menu_buttons):  # Update all navigation buttons
            if i < len(menu_texts):
                btn.full_text = menu_texts[i]
                btn.text_label.setText(menu_texts[i])
        
        # Update status and version labels
        self.status_label.setText(_('sidebar_status'))
        self.version_label.setText(_('sidebar_version'))
    
    def toggle_sidebar(self):
        """Toggle sidebar between expanded and collapsed state"""
        self.is_expanded = not self.is_expanded
        
        if self.is_expanded:
            self.setFixedWidth(self.expanded_width)
            self.toggle_button.setText("«")  # Double left chevron
            # Show text in buttons and labels
            for btn in self.menu_buttons:
                btn.text_label.show()
            self.title_label.show()
            self.subtitle_label.show()
            self.section_label.show()
        else:
            self.setFixedWidth(self.collapsed_width)
            self.toggle_button.setText("»")  # Double right chevron
            # Hide text in buttons and labels
            for btn in self.menu_buttons:
                btn.text_label.hide()
            self.title_label.hide()
            self.subtitle_label.hide()
            self.section_label.hide()
        
        # Emit signal to notify main window
        self.sidebar_toggled.emit(self.is_expanded)
