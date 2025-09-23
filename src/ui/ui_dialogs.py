#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
User interface dialogs
"""

import webbrowser
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, 
                             QTextEdit, QLabel, QMessageBox, QApplication)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from src.config.languages import _
from src.ui.theme_manager import theme_manager


class AddAccountDialog(QDialog):
    """Dialog for adding accounts manually"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_('add_account_title'))
        self.setGeometry(200, 200, 800, 600)
        self.setFixedSize(800, 600)  # Make dialog non-resizable
        self.init_ui()

    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # Create main content without tabs - only manual addition
        manual_content = self.create_manual_tab()
        main_layout.addWidget(manual_content)

        # Main buttons (common for both tabs)
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        # Create account button (left side)
        self.create_account_button = QPushButton(_('create_account'))
        self.create_account_button.setMinimumHeight(28)
        self.create_account_button.setProperty("class", "primary")
        self.create_account_button.clicked.connect(self.open_account_creation_page)

        self.add_button = QPushButton(_('add'))
        self.add_button.setMinimumHeight(28)
        self.add_button.clicked.connect(self.accept)

        self.cancel_button = QPushButton(_('cancel'))
        self.cancel_button.setMinimumHeight(28)
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.create_account_button)
        button_layout.addStretch()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def create_manual_tab(self):
        """Create manual JSON addition tab"""
        tab_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # Title
        title_label = QLabel(_('manual_method_title'))
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; background: transparent; border: none; outline: none; border-radius: 8px; padding: 6px 12px;")
        layout.addWidget(title_label)

        # Main layout (left-right)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(12)

        # Left panel (form)
        left_panel = QVBoxLayout()
        left_panel.setSpacing(8)

        # Explanation
        instruction_label = QLabel(_('add_account_instruction'))
        instruction_label.setFont(QFont("Arial", 10))
        instruction_label.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; background: transparent; border: none; outline: none; border-radius: 6px; padding: 4px 8px;")
        left_panel.addWidget(instruction_label)

        # Text edit
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText(_('add_account_placeholder'))
        left_panel.addWidget(self.text_edit)

        # Info button
        self.info_button = QPushButton(_('how_to_get_json'))
        self.info_button.setMaximumWidth(220)
        self.info_button.clicked.connect(self.toggle_info_panel)
        left_panel.addWidget(self.info_button)

        content_layout.addLayout(left_panel, 1)

        # Right panel (info panel) - hidden by default
        self.info_panel = self.create_info_panel()
        self.info_panel.hide()
        self.info_panel_visible = False
        content_layout.addWidget(self.info_panel, 1)

        layout.addLayout(content_layout)
        tab_widget.setLayout(layout)
        return tab_widget

    def create_info_panel(self):
        """Create info panel"""
        panel = QWidget()
        panel.setMaximumWidth(400)
        panel.setProperty("class", "info-panel")

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Title
        title = QLabel(_('json_info_title'))
        title.setFont(QFont("Arial", 11, QFont.Bold))
        title.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; background: transparent; border: none; outline: none; border-radius: 8px; padding: 6px 12px;")
        layout.addWidget(title)

        # Steps
        steps_text = f"""
{_('step_1')}<br><br>
{_('step_2')}<br><br>
{_('step_3')}<br><br>
{_('step_4')}<br><br>
{_('step_5')}<br><br>
{_('step_6')}<br><br>
{_('step_7')}
        """

        steps_label = QLabel(steps_text)
        steps_label.setWordWrap(True)
        steps_label.setProperty("class", "info-content")
        steps_label.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; background: transparent; border: none; outline: none; border-radius: 6px; padding: 4px 8px;")
        layout.addWidget(steps_label)

        # JavaScript code (hidden, only copy button)
        self.javascript_code = """(async () => {
  const request = indexedDB.open("firebaseLocalStorageDb");

  request.onsuccess = function (event) {
    const db = event.target.result;
    const tx = db.transaction("firebaseLocalStorage", "readonly");
    const store = tx.objectStore("firebaseLocalStorage");

    const getAllReq = store.getAll();

    getAllReq.onsuccess = function () {
      const results = getAllReq.result;

      // get first record's value
      const firstValue = results[0]?.value;
      console.log("Value (object):", firstValue);

      // convert to JSON string
      const valueString = JSON.stringify(firstValue, null, 2);

      // add button
      const btn = document.createElement("button");
      btn.innerText = "-> Copy JSON <--";
      btn.style.position = "fixed";
      btn.style.top = "20px";
      btn.style.right = "20px";
      btn.style.zIndex = 9999;
      btn.onclick = () => {
        navigator.clipboard.writeText(valueString).then(() => {
          alert("Copied!");
        });
      };
      document.body.appendChild(btn);
    };
  };
})();"""

        # Copy code button
        self.copy_button = QPushButton(_('copy_javascript'))
        self.copy_button.setProperty("class", "primary")
        self.copy_button.clicked.connect(self.copy_javascript_code)
        layout.addWidget(self.copy_button)

        layout.addStretch()
        panel.setLayout(layout)
        return panel

    def toggle_info_panel(self):
        """Toggle info panel open/close"""
        self.info_panel_visible = not self.info_panel_visible

        if self.info_panel_visible:
            self.info_panel.show()
            self.info_button.setText(_('how_to_get_json_close'))
            # Panel will expand within fixed dialog size
        else:
            self.info_panel.hide()
            self.info_button.setText(_('how_to_get_json'))
            # Panel hides, giving more space to left panel

    def copy_javascript_code(self):
        """Copy JavaScript code to clipboard"""
        try:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.javascript_code)

            # Temporarily change button text
            original_text = self.copy_button.text()
            self.copy_button.setText(_('copied'))

            # Revert to old text after 2 seconds
            QTimer.singleShot(2000, lambda: self.copy_button.setText(original_text))

        except Exception as e:
            self.copy_button.setText(_('copy_error'))
            QTimer.singleShot(2000, lambda: self.copy_button.setText(_('copy_javascript')))

    def open_account_creation_page(self):
        """Open account creation page"""
        webbrowser.open("https://app.warp.dev/login/")

    def get_json_data(self):
        """Get JSON data from text edit"""
        return self.text_edit.toPlainText().strip()