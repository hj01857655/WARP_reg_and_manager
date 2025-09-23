#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Import/Export Dialog for Account Management
"""

import json
import os
from datetime import datetime
from pathlib import Path
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, 
                            QWidget, QPushButton, QTextEdit, QLabel, 
                            QFileDialog, QMessageBox, QProgressBar, QCheckBox,
                            QGroupBox, QGridLayout, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QTextCursor
from src.config.languages import _
from src.ui.theme_manager import theme_manager


class ExportWorker(QThread):
    """Worker thread for exporting accounts"""
    progress = pyqtSignal(int)
    status_update = pyqtSignal(str)
    export_complete = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, accounts, file_path, selected_only=False):
        super().__init__()
        self.accounts = accounts
        self.file_path = file_path
        self.selected_only = selected_only
    
    def run(self):
        try:
            total = len(self.accounts)
            export_data = {
                "export_date": datetime.now().isoformat(),
                "total_accounts": total,
                "accounts": []
            }
            
            for i, account in enumerate(self.accounts):
                self.progress.emit(int((i + 1) / total * 100))
                self.status_update.emit(f"{_('exporting_account')}: {account.get('email', 'Unknown')}")
                export_data["accounts"].append(account)
            
            # Save to file
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.export_complete.emit(True, _('export_success').format(total))
        except Exception as e:
            self.export_complete.emit(False, f"{_('export_failed')}: {str(e)}")


class ImportWorker(QThread):
    """Worker thread for importing accounts"""
    progress = pyqtSignal(int)
    status_update = pyqtSignal(str)
    import_complete = pyqtSignal(bool, str, int, int)  # success, message, success_count, fail_count
    
    def __init__(self, file_path, account_manager, skip_duplicates=True):
        super().__init__()
        self.file_path = file_path
        self.account_manager = account_manager
        self.skip_duplicates = skip_duplicates
    
    def run(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            accounts = data.get('accounts', [])
            total = len(accounts)
            success_count = 0
            fail_count = 0
            
            for i, account in enumerate(accounts):
                self.progress.emit(int((i + 1) / total * 100))
                email = account.get('email', 'Unknown')
                self.status_update.emit(f"{_('importing_account')}: {email}")
                
                try:
                    # Check for duplicates
                    if self.skip_duplicates:
                        existing = self.account_manager.get_account_by_email(email)
                        if existing:
                            self.status_update.emit(f"{_('skipping_duplicate')}: {email}")
                            fail_count += 1
                            continue
                    
                    # Add account to database
                    success = self.account_manager.add_account_from_json(account)
                    if success:
                        success_count += 1
                    else:
                        fail_count += 1
                except Exception as e:
                    print(f"Error importing {email}: {e}")
                    fail_count += 1
            
            self.import_complete.emit(
                True, 
                _('import_complete'),
                success_count,
                fail_count
            )
        except Exception as e:
            self.import_complete.emit(False, f"{_('import_failed')}: {str(e)}", 0, 0)


class ImportExportDialog(QDialog):
    """Import/Export dialog for account management"""
    
    def __init__(self, account_manager, parent=None):
        super().__init__(parent)
        self.account_manager = account_manager
        self.init_ui()
        self.load_accounts_preview()
    
    def init_ui(self):
        """Initialize the dialog UI"""
        self.setWindowTitle(_('import_export_title'))
        self.setModal(True)
        self.setFixedSize(900, 650)
        
        # Apply modern styling using theme manager
        self.setStyleSheet(theme_manager.get_dialog_style())
        
        layout = QVBoxLayout()
        layout.setSpacing(16)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Export tab
        export_tab = self.create_export_tab()
        self.tab_widget.addTab(export_tab, _('export_tab'))
        
        # Import tab  
        import_tab = self.create_import_tab()
        self.tab_widget.addTab(import_tab, _('import_tab'))
        
        layout.addWidget(self.tab_widget)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(f"color: {theme_manager.get_color('accent_green')}; font-size: 12px; background: transparent; border: none; outline: none; border-radius: 6px; padding: 4px 8px;")
        layout.addWidget(self.status_label)
        
        # Close button
        close_btn = QPushButton(_('close'))
        close_btn.clicked.connect(self.accept)
        close_btn.setFixedWidth(120)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def create_export_tab(self):
        """Create export tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Export options
        options_group = QGroupBox(_('export_options'))
        options_layout = QVBoxLayout()
        
        self.export_all_checkbox = QCheckBox(_('export_all_accounts'))
        self.export_all_checkbox.setChecked(True)
        self.export_healthy_checkbox = QCheckBox(_('export_healthy_only'))
        
        options_layout.addWidget(self.export_all_checkbox)
        options_layout.addWidget(self.export_healthy_checkbox)
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Preview
        preview_group = QGroupBox(_('accounts_preview'))
        preview_layout = QVBoxLayout()
        
        self.export_preview_list = QListWidget()
        self.export_preview_list.setMaximumHeight(250)
        preview_layout.addWidget(self.export_preview_list)
        
        self.export_count_label = QLabel(_('total_accounts_count').format(0))
        self.export_count_label.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; background: transparent; border: none; outline: none; border-radius: 6px; padding: 4px 8px;")
        preview_layout.addWidget(self.export_count_label)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Export button
        self.export_button = QPushButton(_('export_to_file'))
        self.export_button.setObjectName("exportBtn")
        self.export_button.clicked.connect(self.export_accounts)
        layout.addWidget(self.export_button)
        
        # Export log
        self.export_log = QTextEdit()
        self.export_log.setReadOnly(True)
        self.export_log.setMaximumHeight(150)
        layout.addWidget(self.export_log)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_import_tab(self):
        """Create import tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # File selection
        file_group = QGroupBox(_('select_import_file'))
        file_layout = QHBoxLayout()
        
        self.file_path_label = QLabel(_('no_file_selected'))
        self.file_path_label.setStyleSheet(f"color: {theme_manager.get_color('text_muted')}; padding: 8px; background: transparent; border: none; outline: none; border-radius: 6px;")
        file_layout.addWidget(self.file_path_label, 1)
        
        browse_btn = QPushButton(_('browse'))
        browse_btn.clicked.connect(self.browse_import_file)
        file_layout.addWidget(browse_btn)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Import options
        options_group = QGroupBox(_('import_options'))
        options_layout = QVBoxLayout()
        
        self.skip_duplicates_checkbox = QCheckBox(_('skip_duplicate_accounts'))
        self.skip_duplicates_checkbox.setChecked(True)
        self.validate_checkbox = QCheckBox(_('validate_before_import'))
        self.validate_checkbox.setChecked(True)
        
        options_layout.addWidget(self.skip_duplicates_checkbox)
        options_layout.addWidget(self.validate_checkbox)
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Preview
        preview_group = QGroupBox(_('file_preview'))
        preview_layout = QVBoxLayout()
        
        self.import_preview = QTextEdit()
        self.import_preview.setReadOnly(True)
        self.import_preview.setMaximumHeight(200)
        preview_layout.addWidget(self.import_preview)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Import button
        self.import_button = QPushButton(_('import_accounts'))
        self.import_button.setObjectName("importBtn")
        self.import_button.clicked.connect(self.import_accounts)
        self.import_button.setEnabled(False)
        layout.addWidget(self.import_button)
        
        # Import log
        self.import_log = QTextEdit()
        self.import_log.setReadOnly(True)
        self.import_log.setMaximumHeight(150)
        layout.addWidget(self.import_log)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def load_accounts_preview(self):
        """Load accounts for export preview"""
        try:
            accounts = self.account_manager.get_all_accounts_for_export()
            self.export_preview_list.clear()
            
            for account in accounts:
                email = account.get('email', 'Unknown')
                health = account.get('health', 'unknown')
                item_text = f"{email} - {_(f'status_{health}')}"
                item = QListWidgetItem(item_text)
                
                # Color code by health status
                if health == 'healthy':
                    item.setForeground(Qt.green)
                elif health == 'banned':
                    item.setForeground(Qt.red)
                else:
                    item.setForeground(Qt.yellow)
                
                self.export_preview_list.addItem(item)
            
            self.export_count_label.setText(_('total_accounts_count').format(len(accounts)))
        except Exception as e:
            print(f"Error loading accounts preview: {e}")
    
    def browse_import_file(self):
        """Browse for import file"""
        file_path, selected_filter = QFileDialog.getOpenFileName(
            self,
            _('select_json_file'),
            str(Path.home()),
            "JSON Files (*.json);;All Files (*.*)"
        )
        
        if file_path:
            self.file_path_label.setText(file_path)
            self.import_button.setEnabled(True)
            self.preview_import_file(file_path)
    
    def preview_import_file(self, file_path):
        """Preview import file content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            preview_text = f"{_('export_date')}: {data.get('export_date', 'Unknown')}\n"
            preview_text += f"{_('total_accounts')}: {data.get('total_accounts', 0)}\n\n"
            
            accounts = data.get('accounts', [])
            preview_text += f"{_('accounts_list')}:\n"
            for i, account in enumerate(accounts[:10], 1):  # Show first 10
                email = account.get('email', 'Unknown')
                preview_text += f"{i}. {email}\n"
            
            if len(accounts) > 10:
                preview_text += f"... {_('and_more').format(len(accounts) - 10)}\n"
            
            self.import_preview.setText(preview_text)
        except Exception as e:
            self.import_preview.setText(f"{_('error_reading_file')}: {str(e)}")
    
    def export_accounts(self):
        """Export accounts to JSON file"""
        # Get save file path
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            _('save_export_file'),
            f"warp_accounts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json);;All Files (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            # Get accounts to export
            accounts = self.account_manager.get_all_accounts_for_export()
            
            # Filter if needed
            if self.export_healthy_checkbox.isChecked():
                accounts = [a for a in accounts if a.get('health') == 'healthy']
            
            if not accounts:
                QMessageBox.warning(self, _('warning'), _('no_accounts_to_export'))
                return
            
            # Show progress
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.export_button.setEnabled(False)
            
            # Start export worker
            self.export_worker = ExportWorker(accounts, file_path)
            self.export_worker.progress.connect(self.update_progress)
            self.export_worker.status_update.connect(self.update_status)
            self.export_worker.export_complete.connect(self.on_export_complete)
            self.export_worker.start()
            
        except Exception as e:
            QMessageBox.critical(self, _('error'), f"{_('export_failed')}: {str(e)}")
    
    def import_accounts(self):
        """Import accounts from JSON file"""
        file_path = self.file_path_label.text()
        if not file_path or file_path == _('no_file_selected'):
            QMessageBox.warning(self, _('warning'), _('please_select_file'))
            return
        
        # Validate file if needed
        if self.validate_checkbox.isChecked():
            if not self.validate_import_file(file_path):
                return
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.import_button.setEnabled(False)
        
        # Start import worker
        self.import_worker = ImportWorker(
            file_path, 
            self.account_manager,
            self.skip_duplicates_checkbox.isChecked()
        )
        self.import_worker.progress.connect(self.update_progress)
        self.import_worker.status_update.connect(self.update_status)
        self.import_worker.import_complete.connect(self.on_import_complete)
        self.import_worker.start()
    
    def validate_import_file(self, file_path):
        """Validate import file format"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'accounts' not in data:
                QMessageBox.warning(self, _('warning'), _('invalid_file_format'))
                return False
            
            accounts = data['accounts']
            if not isinstance(accounts, list):
                QMessageBox.warning(self, _('warning'), _('invalid_accounts_format'))
                return False
            
            # Check if accounts have required fields
            for account in accounts:
                if 'email' not in account or 'uid' not in account:
                    QMessageBox.warning(
                        self, 
                        _('warning'), 
                        _('missing_required_fields')
                    )
                    return False
            
            return True
        except json.JSONDecodeError:
            QMessageBox.critical(self, _('error'), _('invalid_json_file'))
            return False
        except Exception as e:
            QMessageBox.critical(self, _('error'), f"{_('validation_error')}: {str(e)}")
            return False
    
    def update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)
    
    def update_status(self, message):
        """Update status message"""
        self.status_label.setText(message)
        # Also log to appropriate text edit
        if self.tab_widget.currentIndex() == 0:  # Export tab
            self.export_log.append(f"{datetime.now().strftime('%H:%M:%S')} - {message}")
        else:  # Import tab
            self.import_log.append(f"{datetime.now().strftime('%H:%M:%S')} - {message}")
    
    def on_export_complete(self, success, message):
        """Handle export completion"""
        self.progress_bar.setVisible(False)
        self.export_button.setEnabled(True)
        
        if success:
            self.export_log.append(f"\n✅ {message}")
            QMessageBox.information(self, _('success'), message)
        else:
            self.export_log.append(f"\n❌ {message}")
            QMessageBox.critical(self, _('error'), message)
    
    def on_import_complete(self, success, message, success_count, fail_count):
        """Handle import completion"""
        self.progress_bar.setVisible(False)
        self.import_button.setEnabled(True)
        
        if success:
            result_message = f"{message}\n{_('import_results').format(success_count, fail_count)}"
            self.import_log.append(f"\n✅ {result_message}")
            QMessageBox.information(self, _('success'), result_message)
            # Refresh the export preview
            self.load_accounts_preview()
        else:
            self.import_log.append(f"\n❌ {message}")
            QMessageBox.critical(self, _('error'), message)