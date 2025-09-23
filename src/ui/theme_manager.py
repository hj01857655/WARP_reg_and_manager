#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Theme Manager - Dynamic theme variables and utilities
避免硬编码，提供主题变量管理
"""

class ThemeManager:
    """主题管理器 - 提供动态主题变量"""
    
    def __init__(self, theme_name="light"):
        self.theme_name = theme_name
        self._load_theme_variables()
    
    def _load_theme_variables(self):
        """加载主题变量"""
        if self.theme_name == "light":
            self._load_light_theme()
        else:
            self._load_light_theme()  # 默认使用亮色主题
    
    def _load_light_theme(self):
        """加载亮色主题变量"""
        # 基础颜色
        self.colors = {
            # 背景色
            'background_primary': '#ffffff',
            'background_secondary': '#f8fafc',
            'background_tertiary': '#f1f5f9',
            
            # 文字颜色
            'text_primary': '#1e293b',
            'text_secondary': '#64748b',
            'text_muted': '#94a3b8',
            
            # 强调色
            'accent_blue': '#3b82f6',
            'accent_green': '#10b981',
            'accent_orange': '#f59e0b',
            'accent_red': '#ef4444',
            'accent_purple': '#8b5cf6',
            
            # 边框和分割线
            'border_light': '#e2e8f0',
            'border_medium': '#cbd5e1',
            'border_dark': '#94a3b8',
            
            # 卡片和容器
            'card_background': '#ffffff',
            'card_hover': '#f8fafc',
            'card_border': 'rgba(226, 232, 240, 0.8)',
        }
        
        # 组件主题
        self.card_themes = {
            'blue': {
                'accent': '#3b82f6',
                'background': 'rgba(59, 130, 246, 0.1)',
                'border': 'rgba(59, 130, 246, 0.3)',
                'hover_border': 'rgba(59, 130, 246, 0.5)'
            },
            'green': {
                'accent': '#10b981',
                'background': 'rgba(16, 185, 129, 0.1)',
                'border': 'rgba(16, 185, 129, 0.3)',
                'hover_border': 'rgba(16, 185, 129, 0.5)'
            },
            'orange': {
                'accent': '#f59e0b',
                'background': 'rgba(245, 158, 11, 0.1)',
                'border': 'rgba(245, 158, 11, 0.3)',
                'hover_border': 'rgba(245, 158, 11, 0.5)'
            },
            'red': {
                'accent': '#ef4444',
                'background': 'rgba(239, 68, 68, 0.1)',
                'border': 'rgba(239, 68, 68, 0.3)',
                'hover_border': 'rgba(239, 68, 68, 0.5)'
            },
            'purple': {
                'accent': '#8b5cf6',
                'background': 'rgba(139, 92, 246, 0.1)',
                'border': 'rgba(139, 92, 246, 0.3)',
                'hover_border': 'rgba(139, 92, 246, 0.5)'
            }
        }
    
    def get_color(self, color_name):
        """获取颜色值"""
        return self.colors.get(color_name, '#ffffff')
    
    def get_label_style(self, style_type='default'):
        """获取QLabel圆角样式"""
        base_style = f"""
            QLabel {{
                background: transparent;
                border: none;
                outline: none;
                border-radius: 6px;
                padding: 4px 8px;
            }}
        """
        
        if style_type == 'primary':
            return base_style + f"""
            QLabel {{
                color: {self.colors['text_primary']};
                background-color: {self.colors['background_secondary']};
                border-radius: 8px;
                padding: 6px 12px;
            }}
            """
        elif style_type == 'secondary':
            return base_style + f"""
            QLabel {{
                color: {self.colors['text_secondary']};
                background-color: rgba(100, 116, 139, 0.1);
                border-radius: 6px;
                padding: 4px 8px;
            }}
            """
        elif style_type == 'accent':
            return base_style + f"""
            QLabel {{
                color: {self.colors['accent_blue']};
                background-color: {self.card_themes['blue']['background']};
                border-radius: 8px;
                padding: 6px 12px;
            }}
            """
        elif style_type == 'success':
            return base_style + f"""
            QLabel {{
                color: {self.colors['accent_green']};
                background-color: {self.card_themes['green']['background']};
                border-radius: 8px;
                padding: 6px 12px;
            }}
            """
        elif style_type == 'warning':
            return base_style + f"""
            QLabel {{
                color: {self.colors['accent_orange']};
                background-color: {self.card_themes['orange']['background']};
                border-radius: 8px;
                padding: 6px 12px;
            }}
            """
        else:  # default
            return base_style + f"""
            QLabel {{
                color: {self.colors['text_primary']};
            }}
            """
    
    def get_card_theme(self, theme_name):
        """获取卡片主题"""
        return self.card_themes.get(theme_name, self.card_themes['blue'])
    
    def get_main_container_style(self):
        """获取主容器样式"""
        return f"""
            QFrame {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 {self.colors['background_primary']},
                    stop: 0.5 {self.colors['background_secondary']},
                    stop: 1 {self.colors['background_tertiary']}
                );
                border: 1px solid {self.colors['card_border']};
                border-radius: 20px;
                margin: 10px;
            }}
        """
    
    def get_card_style(self, card_theme='blue'):
        """获取卡片样式"""
        theme = self.get_card_theme(card_theme)
        return f"""
            QFrame {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 {self.colors['card_background']},
                    stop: 0.5 {self.colors['background_secondary']},
                    stop: 1 {self.colors['background_tertiary']}
                );
                border: 1px solid {theme['border']};
                border-radius: 16px;
            }}
            QFrame:hover {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 {self.colors['card_hover']},
                    stop: 0.5 {self.colors['background_secondary']},
                    stop: 1 {self.colors['background_tertiary']}
                );
                border: 1px solid {theme['hover_border']};
            }}
            /* 全局QLabel圆角样式 - 强制所有QLabel都有圆角 */
            QLabel {{
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 6px 10px;
                margin: 2px;
            }}
            /* 特殊容器样式 - 用于包含多个组件的QWidget */
            QWidget#UsageContainer {{
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 6px 10px;
                margin: 2px;
            }}
        """
    
    def get_button_style(self, button_type='primary'):
        """获取按钮样式"""
        if button_type == 'secondary':
            return self.get_secondary_button_style()
        elif button_type == 'warning':
            return self.get_warning_button_style()
        elif button_type == 'danger':
            return self.get_danger_button_style()
        elif button_type == 'primary':
            return f"""
                QPushButton {{
                    background: qlineargradient(
                        x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 {self.colors['accent_blue']},
                        stop: 1 #2563eb
                    );
                    color: white;
                    border: 1px solid rgba(59, 130, 246, 0.3);
                    border-radius: 10px;
                    padding: 8px 16px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(
                        x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #60a5fa,
                        stop: 1 {self.colors['accent_blue']}
                    );
                    border: 1px solid rgba(96, 165, 250, 0.5);
                }}
                QPushButton:pressed {{
                    background: qlineargradient(
                        x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #2563eb,
                        stop: 1 #1d4ed8
                    );
                }}
            """
        elif button_type == 'danger_outline':  # 危险轮廓按钮
            return f"""
                QPushButton {{
                    background-color: {self.colors['background_primary']};
                    color: {self.colors['accent_red']};
                    border: 1px solid {self.colors['accent_red']};
                    border-radius: 10px;
                    padding: 8px 16px;
                }}
                QPushButton:hover {{
                    background-color: rgba(239, 68, 68, 0.1);
                    border-color: #dc2626;
                }}
                QPushButton:pressed {{
                    background-color: rgba(239, 68, 68, 0.2);
                }}
            """
        elif button_type == 'success':
            return f"""
                QPushButton {{
                    background: qlineargradient(
                        x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 {self.colors['accent_green']},
                        stop: 1 #059669
                    );
                    color: white;
                    border: 1px solid rgba(16, 185, 129, 0.3);
                    border-radius: 10px;
                    padding: 8px 16px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(
                        x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #34d399,
                        stop: 1 {self.colors['accent_green']}
                    );
                    border: 1px solid rgba(52, 211, 153, 0.5);
                }}
                QPushButton:pressed {{
                    background: qlineargradient(
                        x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #059669,
                        stop: 1 #047857
                    );
                }}
            """
    
    def get_time_container_style(self):
        """获取时间容器样式"""
        return f"""
            QWidget {{
                background: rgba(59, 130, 246, 0.05);
                border: 1px solid rgba(59, 130, 246, 0.15);
                border-radius: 10px;
                padding: 4px 10px;
            }}
        """
    
    def get_global_label_style(self):
        """获取全局QLabel圆角样式 - 确保没有直角"""
        return f"""
            QLabel {{
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 10px;
                padding: 8px 12px;
                margin: 3px;
            }}
            QLabel[class="title"] {{
                background: transparent;
                border: none;
                padding: 0;
                margin: 0;
            }}
            QLabel[class="icon"] {{
                background: transparent;
                border: none;
                padding: 0;
                margin: 0;
            }}
        """

    def get_table_button_style(self, button_type='primary'):
        """获取表格内按钮样式"""
        base_style = """
            QPushButton {
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                font-weight: 500;
                min-width: 32px;
                min-height: 32px;
            }
        """
        
        if button_type == 'success':  # 启动按钮
            return base_style + f"""
            QPushButton {{
                background-color: {self.colors['accent_green']};
                color: white;
            }}
            QPushButton:hover {{
                background-color: #059669;
            }}
            QPushButton:pressed {{
                background-color: #047857;
            }}
            """
        elif button_type == 'primary':  # 刷新按钮
            return base_style + f"""
            QPushButton {{
                background-color: {self.colors['accent_blue']};
                color: white;
            }}
            QPushButton:hover {{
                background-color: #2563eb;
            }}
            QPushButton:pressed {{
                background-color: #1d4ed8;
            }}
            """
        elif button_type == 'warning':  # 编辑按钮
            return base_style + f"""
            QPushButton {{
                background-color: {self.colors['accent_orange']};
                color: white;
            }}
            QPushButton:hover {{
                background-color: #d97706;
            }}
            QPushButton:pressed {{
                background-color: #b45309;
            }}
            """
        elif button_type == 'danger':  # 删除按钮
            return base_style + f"""
            QPushButton {{
                background-color: {self.colors['accent_red']};
                color: white;
            }}
            QPushButton:hover {{
                background-color: #dc2626;
            }}
            QPushButton:pressed {{
                background-color: #b91c1c;
            }}
            """
        else:
            return base_style + f"""
            QPushButton {{
                background-color: {self.colors['background_secondary']};
                color: {self.colors['text_primary']};
                border: 1px solid {self.colors['border_medium']};
            }}
            QPushButton:hover {{
                background-color: {self.colors['background_tertiary']};
            }}
            """
    
    def get_secondary_button_style(self):
        """获取次要按钮样式"""
        return f"""
            QPushButton {{
                background-color: {self.colors['background_secondary']};
                color: {self.colors['text_primary']};
                border: 1px solid {self.colors['border_light']};
                border-radius: 10px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: {self.colors['background_tertiary']};
                border-color: {self.colors['border_medium']};
            }}
            QPushButton:pressed {{
                background-color: {self.colors['background_primary']};
            }}
        """
    
    def get_warning_button_style(self):
        """获取警告按钮样式"""
        return f"""
            QPushButton {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {self.colors['accent_orange']},
                    stop: 1 #d97706
                );
                color: white;
                border: 1px solid rgba(245, 158, 11, 0.3);
                border-radius: 10px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #fbbf24,
                    stop: 1 {self.colors['accent_orange']}
                );
            }}
            QPushButton:pressed {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #d97706,
                    stop: 1 #b45309
                );
            }}
        """
    
    def get_danger_button_style(self):
        """获取危险按钮样式"""
        return f"""
            QPushButton {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {self.colors['accent_red']},
                    stop: 1 #dc2626
                );
                color: white;
                border: 1px solid rgba(239, 68, 68, 0.3);
                border-radius: 10px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f87171,
                    stop: 1 {self.colors['accent_red']}
                );
            }}
            QPushButton:pressed {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #dc2626,
                    stop: 1 #b91c1c
                );
            }}
        """
    
    def get_search_input_style(self):
        """获取搜索输入框样式"""
        return f"""
            QLineEdit {{
                background-color: {self.colors['background_primary']};
                border: 1px solid {self.colors['border_light']};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                color: {self.colors['text_primary']};
                min-width: 250px;
            }}
            QLineEdit:focus {{
                border-color: {self.colors['accent_blue']};
                outline: none;
            }}
            QLineEdit:hover {{
                border-color: {self.colors['border_medium']};
            }}
        """
    
    def get_table_style(self):
        """获取表格统一样式"""
        return f"""
            QTableWidget {{
                background-color: {self.colors['background_primary']};
                border: 1px solid {self.colors['border_light']};
                border-radius: 12px;
                gridline-color: {self.colors['border_light']};
                selection-background-color: rgba(59, 130, 246, 0.1);
            }}
            QTableWidget::item {{
                padding: 10px;
                border: none;
                color: {self.colors['text_primary']};
            }}
            QTableWidget::item:selected {{
                background-color: rgba(59, 130, 246, 0.1);
                color: {self.colors['text_primary']};
            }}
            QTableWidget::item:hover {{
                background-color: {self.colors['background_secondary']};
            }}
            QHeaderView::section {{
                background-color: {self.colors['background_secondary']};
                color: {self.colors['text_primary']};
                padding: 12px 8px;
                border: none;
                border-bottom: 2px solid {self.colors['border_light']};
                font-weight: 600;
                min-height: 45px;
            }}
            QHeaderView::section:hover {{
                background-color: {self.colors['background_tertiary']};
            }}
        """
    def get_dialog_style(self):
        """获取对话框样式"""
        return f"""
            QDialog {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {self.colors['background_primary']},
                    stop: 1 {self.colors['background_secondary']}
                );
            }}
            QTabWidget::pane {{
                background-color: {self.colors['background_primary']};
                border: 1px solid {self.colors['border_medium']};
                border-radius: 8px;
            }}
            QTabBar::tab {{
                background: {self.colors['background_secondary']};
                color: {self.colors['text_secondary']};
                padding: 12px 24px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 600;
            }}
            QTabBar::tab:selected {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {self.colors['accent_blue']},
                    stop: 1 #2563eb
                );
                color: white;
            }}
            QTabBar::tab:hover {{
                background: {self.colors['background_tertiary']};
                color: {self.colors['text_primary']};
            }}
            QLabel {{
                color: {self.colors['text_primary']};
                font-size: 14px;
            }}
            QTextEdit {{
                background-color: {self.colors['background_primary']};
                color: {self.colors['text_primary']};
                border: 1px solid {self.colors['border_medium']};
                border-radius: 6px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }}
            QListWidget {{
                background-color: {self.colors['background_primary']};
                color: {self.colors['text_primary']};
                border: 1px solid {self.colors['border_medium']};
                border-radius: 6px;
                padding: 8px;
            }}
            QListWidget::item {{
                padding: 6px;
                border-radius: 4px;
                margin: 2px;
            }}
            QListWidget::item:hover {{
                background-color: {self.colors['background_secondary']};
            }}
            QListWidget::item:selected {{
                background-color: {self.colors['accent_blue']};
                color: white;
            }}
            QPushButton {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {self.colors['background_tertiary']},
                    stop: 1 {self.colors['background_secondary']}
                );
                color: {self.colors['text_primary']};
                border: 1px solid {self.colors['border_medium']};
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #e2e8f0,
                    stop: 1 {self.colors['background_tertiary']}
                );
                border-color: {self.colors['accent_blue']};
            }}
            QPushButton:pressed {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {self.colors['background_secondary']},
                    stop: 1 {self.colors['background_primary']}
                );
            }}
            QPushButton#exportBtn {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {self.colors['accent_green']},
                    stop: 1 #059669
                );
                color: white;
            }}
            QPushButton#exportBtn:hover {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #34d399,
                    stop: 1 {self.colors['accent_green']}
                );
            }}
            QPushButton#importBtn {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {self.colors['accent_blue']},
                    stop: 1 #2563eb
                );
                color: white;
            }}
            QPushButton#importBtn:hover {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #60a5fa,
                    stop: 1 {self.colors['accent_blue']}
                );
            }}
            QProgressBar {{
                background-color: {self.colors['background_secondary']};
                border: 1px solid {self.colors['border_medium']};
                border-radius: 4px;
                text-align: center;
                color: {self.colors['text_primary']};
                height: 24px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 {self.colors['accent_blue']},
                    stop: 1 #60a5fa
                );
                border-radius: 3px;
            }}
            QCheckBox {{
                color: {self.colors['text_primary']};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                background-color: {self.colors['background_primary']};
                border: 2px solid {self.colors['border_medium']};
                border-radius: 4px;
            }}
            QCheckBox::indicator:checked {{
                background-color: {self.colors['accent_blue']};
                border-color: {self.colors['accent_blue']};
            }}
            QGroupBox {{
                color: {self.colors['text_primary']};
                border: 1px solid {self.colors['border_medium']};
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 16px;
                font-weight: 600;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
        """

# 创建全局主题管理器实例
theme_manager = ThemeManager("light")