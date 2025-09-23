#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Light Theme Stylesheet - macOS-inspired clean design
"""

def get_light_theme_stylesheet():
    """Return the complete light theme stylesheet"""
    return """
    /* Global Application Style */
    QWidget {
        background-color: #ffffff;
        color: #1a1a1a;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", Arial, sans-serif;
        font-size: 13px;
    }
    
    /* Main Window */
    QMainWindow {
        background-color: #ffffff;
    }
    
    /* Sidebar Style */
    QWidget#sidebar {
        background-color: #f7f7f7;
        border-right: 1px solid #e0e0e0;
    }
    
    /* Group Boxes */
    QGroupBox {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        margin-top: 12px;
        padding-top: 12px;
        font-weight: 600;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 8px;
        color: #666666;
    }
    
    /* Labels - 全部使用圆角 */
    QLabel {
        background: transparent;
        color: #1a1a1a;
        padding: 4px 8px;
        border: none;
        outline: none;
        border-radius: 6px;
    }
    
    QLabel#heading {
        font-size: 18px;
        font-weight: bold;
        color: #1a1a1a;
        border-radius: 8px;
        padding: 6px 12px;
    }
    
    QLabel#subheading {
        font-size: 14px;
        color: #666666;
        border-radius: 6px;
        padding: 4px 8px;
    }
    
    /* Line Edits and Text Edits */
    QLineEdit, QTextEdit, QPlainTextEdit {
        background-color: #ffffff;
        border: 1px solid #d0d0d0;
        border-radius: 6px;
        padding: 8px;
        color: #1a1a1a;
        selection-background-color: #007AFF;
        selection-color: #ffffff;
    }
    
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
        border: 2px solid #007AFF;
        outline: none;
    }
    
    QLineEdit:disabled, QTextEdit:disabled {
        background-color: #f5f5f5;
        color: #999999;
    }
    
    /* Buttons */
    QPushButton {
        background-color: #007AFF;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 500;
        min-height: 28px;
    }
    
    QPushButton:hover {
        background-color: #0051D5;
    }
    
    QPushButton:pressed {
        background-color: #0041A8;
    }
    
    QPushButton:disabled {
        background-color: #cccccc;
        color: #666666;
    }
    
    /* Secondary Button Style */
    QPushButton#secondary {
        background-color: #ffffff;
        color: #007AFF;
        border: 1px solid #007AFF;
    }
    
    QPushButton#secondary:hover {
        background-color: rgba(0, 122, 255, 0.1);
    }
    
    /* Danger Button Style */
    QPushButton#danger {
        background-color: #FF3B30;
        color: white;
    }
    
    QPushButton#danger:hover {
        background-color: #D70015;
    }
    
    /* Success Button Style */
    QPushButton#success {
        background-color: #34C759;
        color: white;
    }
    
    QPushButton#success:hover {
        background-color: #28A745;
    }
    
    /* ComboBox */
    QComboBox {
        background-color: #ffffff;
        border: 1px solid #d0d0d0;
        border-radius: 6px;
        padding: 6px 12px;
        min-height: 28px;
        color: #1a1a1a;
    }
    
    QComboBox:hover {
        border: 1px solid #007AFF;
    }
    
    QComboBox:focus {
        border: 2px solid #007AFF;
    }
    
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    
    QComboBox::down-arrow {
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid #666666;
        margin-right: 5px;
    }
    
    QComboBox QAbstractItemView {
        background-color: #ffffff;
        border: 1px solid #d0d0d0;
        border-radius: 6px;
        selection-background-color: #007AFF;
        selection-color: white;
        padding: 4px;
    }
    
    /* Table Widget */
    QTableWidget {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        gridline-color: #f0f0f0;
        selection-background-color: #007AFF;
        selection-color: white;
    }
    
    QTableWidget::item {
        padding: 8px;
        border: none;
    }
    
    QTableWidget::item:selected {
        background-color: #007AFF;
        color: white;
    }
    
    QTableWidget::item:hover {
        background-color: rgba(0, 122, 255, 0.1);
    }
    
    QHeaderView::section {
        background-color: #f7f7f7;
        color: #666666;
        padding: 8px;
        border: none;
        border-bottom: 1px solid #e0e0e0;
        font-weight: 600;
    }
    
    /* Scroll Bars */
    QScrollBar:vertical {
        background-color: transparent;
        width: 12px;
        border: none;
    }
    
    QScrollBar::handle:vertical {
        background-color: rgba(0, 0, 0, 0.2);
        border-radius: 6px;
        min-height: 30px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: rgba(0, 0, 0, 0.3);
    }
    
    QScrollBar:horizontal {
        background-color: transparent;
        height: 12px;
        border: none;
    }
    
    QScrollBar::handle:horizontal {
        background-color: rgba(0, 0, 0, 0.2);
        border-radius: 6px;
        min-width: 30px;
    }
    
    QScrollBar::handle:horizontal:hover {
        background-color: rgba(0, 0, 0, 0.3);
    }
    
    QScrollBar::add-line, QScrollBar::sub-line {
        border: none;
        background: none;
    }
    
    /* Tab Widget */
    QTabWidget::pane {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
    }
    
    QTabBar::tab {
        background-color: #f7f7f7;
        color: #666666;
        padding: 8px 16px;
        margin: 2px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
    }
    
    QTabBar::tab:selected {
        background-color: #ffffff;
        color: #007AFF;
        font-weight: 600;
    }
    
    QTabBar::tab:hover {
        background-color: #eeeeee;
    }
    
    /* Progress Bar */
    QProgressBar {
        background-color: #f0f0f0;
        border: none;
        border-radius: 6px;
        height: 8px;
        text-align: center;
    }
    
    QProgressBar::chunk {
        background-color: #007AFF;
        border-radius: 6px;
    }
    
    /* Status Bar */
    QStatusBar {
        background-color: #f7f7f7;
        border-top: 1px solid #e0e0e0;
        color: #666666;
    }
    
    /* Menu Bar */
    QMenuBar {
        background-color: #f7f7f7;
        border-bottom: 1px solid #e0e0e0;
    }
    
    QMenuBar::item {
        padding: 6px 12px;
        background: transparent;
        color: #1a1a1a;
    }
    
    QMenuBar::item:selected {
        background-color: rgba(0, 122, 255, 0.1);
        border-radius: 4px;
    }
    
    /* Menus */
    QMenu {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 4px;
    }
    
    QMenu::item {
        padding: 8px 24px;
        border-radius: 4px;
        color: #1a1a1a;
    }
    
    QMenu::item:selected {
        background-color: #007AFF;
        color: white;
    }
    
    /* Message Boxes */
    QMessageBox {
        background-color: #ffffff;
    }
    
    QMessageBox QPushButton {
        min-width: 80px;
    }
    
    /* Tool Tips */
    QToolTip {
        background-color: #1a1a1a;
        color: #ffffff;
        border: none;
        border-radius: 6px;
        padding: 6px 12px;
    }
    
    /* Splitters */
    QSplitter::handle {
        background-color: #e0e0e0;
    }
    
    QSplitter::handle:horizontal {
        width: 1px;
    }
    
    QSplitter::handle:vertical {
        height: 1px;
    }
    
    /* Frame */
    QFrame {
        border: none;
    }
    
    QFrame#card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 16px;
    }
    
    /* Check Box */
    QCheckBox {
        spacing: 8px;
        color: #1a1a1a;
    }
    
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border: 2px solid #d0d0d0;
        border-radius: 4px;
        background-color: white;
    }
    
    QCheckBox::indicator:checked {
        background-color: #007AFF;
        border-color: #007AFF;
        image: none;
    }
    
    QCheckBox::indicator:checked::after {
        content: "✓";
        color: white;
    }
    
    /* Radio Button */
    QRadioButton {
        spacing: 8px;
        color: #1a1a1a;
    }
    
    QRadioButton::indicator {
        width: 18px;
        height: 18px;
        border: 2px solid #d0d0d0;
        border-radius: 9px;
        background-color: white;
    }
    
    QRadioButton::indicator:checked {
        background-color: #007AFF;
        border-color: #007AFF;
    }
    
    /* Slider */
    QSlider::groove:horizontal {
        background-color: #f0f0f0;
        height: 4px;
        border-radius: 2px;
    }
    
    QSlider::handle:horizontal {
        background-color: #007AFF;
        width: 20px;
        height: 20px;
        margin: -8px 0;
        border-radius: 10px;
    }
    
    QSlider::handle:horizontal:hover {
        background-color: #0051D5;
    }
    """