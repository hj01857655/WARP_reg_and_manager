#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Certificate management functionality for mitmproxy
"""

import sys
import os
import subprocess
from pathlib import Path
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from src.config.languages import _


class CertificateManager:
    """Mitmproxy certificate management"""

    def __init__(self):
        self.mitmproxy_dir = Path.home() / ".mitmproxy"
        self.cert_file = self.mitmproxy_dir / "mitmproxy-ca-cert.cer"
        # Ensure directory exists
        self.mitmproxy_dir.mkdir(exist_ok=True)

    def _is_admin_windows(self):
        """Check if current process has administrative privileges on Windows"""
        try:
            if sys.platform != "win32":
                return False
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False

    def _is_cert_installed_in_store_windows(self, scope: str = "machine"):
        """Check if mitmproxy cert is installed in a specific Windows store scope.
        scope: 'machine' -> LocalMachine, 'user' -> CurrentUser
        """
        if sys.platform != "win32":
            return False
        try:
            if scope == "user":
                cmd = ["certutil", "-user", "-store", "root"]
            else:
                cmd = ["certutil", "-store", "root"]
            
            # Use shorter timeout and better error handling
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  timeout=15, creationflags=subprocess.CREATE_NO_WINDOW)
            
            if result.returncode == 0:
                # Check if mitmproxy certificate is in the output
                output_lower = result.stdout.lower()
                return ("mitmproxy" in output_lower or 
                       "mitmproxy-ca" in output_lower or
                       "mitmproxy ca" in output_lower)
            return False
            
        except subprocess.TimeoutExpired:
            print(f"⚠️ Certificate check timeout for {scope} store")
            return False
        except FileNotFoundError:
            print("⚠️ certutil command not found")
            return False
        except Exception as e:
            print(f"⚠️ Certificate check error for {scope} store: {e}")
            return False

    def check_certificate_exists(self):
        """Check if certificate file exists"""
        return self.cert_file.exists()

    def get_certificate_path(self):
        """Return certificate file path as platform-specific string"""
        return str(self.cert_file.resolve())

    def verify_certificate_trust_macos(self):
        """Verify if certificate is properly trusted on macOS"""
        if sys.platform != "darwin":
            return True
            
        try:
            cert_path = self.get_certificate_path()
            if not self.check_certificate_exists():
                return False
                
            # Check if certificate is in keychain and trusted
            cmd = ["security", "verify-cert", "-c", cert_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Certificate is properly trusted")
                return True
            else:
                print(f"⚠️ Certificate trust verification failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Certificate verification error: {e}")
            return False

    def fix_certificate_trust_macos(self):
        """Attempt to fix certificate trust issues on macOS"""
        if sys.platform != "darwin":
            return True
            
        try:
            cert_path = self.get_certificate_path()
            if not self.check_certificate_exists():
                print("❌ Certificate file not found")
                return False
            
            print("🔧 Attempting to fix certificate trust...")
            
            # Method 1: Remove and re-add with explicit trust
            print("Step 1: Removing existing certificate...")
            cmd_remove = ["security", "delete-certificate", "-c", "mitmproxy"]
            subprocess.run(cmd_remove, capture_output=True, text=True)
            
            # Method 2: Add with full trust settings
            print("Step 2: Adding certificate with full trust...")
            user_keychain = os.path.expanduser("~/Library/Keychains/login.keychain-db")
            
            # Import certificate
            cmd_import = ["security", "import", cert_path, "-k", user_keychain, "-A"]
            result_import = subprocess.run(cmd_import, capture_output=True, text=True)
            
            if result_import.returncode == 0:
                # Set trust policy explicitly for SSL
                cmd_trust = [
                    "security", "add-trusted-cert", 
                    "-d", "-r", "trustRoot",
                    "-k", user_keychain,
                    cert_path
                ]
                result_trust = subprocess.run(cmd_trust, capture_output=True, text=True)
                
                if result_trust.returncode == 0:
                    print("✅ Certificate trust fixed successfully")
                    return True
                else:
                    print(f"❌ Trust setting failed: {result_trust.stderr}")
            else:
                print(f"❌ Certificate import failed: {result_import.stderr}")
            
            return False
            
        except Exception as e:
            print(f"Certificate trust fix error: {e}")
            return False

    def is_certificate_installed_windows(self):
        """Check if certificate is already installed in Windows certificate store (either scope)"""
        if sys.platform != "win32":
            return False
            
        try:
            in_machine = self._is_cert_installed_in_store_windows("machine")
            in_user = self._is_cert_installed_in_store_windows("user")

            if in_machine:
                print("✅ Certificate found in LocalMachine\\Root store")
            if in_user:
                print("✅ Certificate found in CurrentUser\\Root store")

            if not in_machine and not in_user:
                print("ℹ️ Certificate not found in Windows certificate stores")
                return False

            return True
        except subprocess.TimeoutExpired:
            print("⚠️ Certificate check timed out")
            return False
        except Exception as e:
            print(f"⚠️ Certificate check error: {e}")
            return False

    def install_certificate_automatically(self):
        """Install certificate automatically for the current OS"""
        try:
            cert_path = self.get_certificate_path()
            if not self.check_certificate_exists():
                print(_('certificate_not_found'))
                return False

            print(_('cert_installing'))

            # Cross-platform certificate installation
            if sys.platform == "win32":
                # First check if certificate is already installed
                try:
                    if self._is_cert_installed_in_store_windows("machine"):
                        print("✅ Certificate already installed in LocalMachine\\Root")
                        return True
                    if self._is_cert_installed_in_store_windows("user"):
                        print("✅ Certificate already installed in CurrentUser\\Root")
                        # Warn that LocalMachine is preferred
                        print("⚠️ Warning: Certificate installed only for CurrentUser. LocalMachine\\Root is recommended for full trust.")
                        # Continue and try to upgrade to LocalMachine if possible
                except Exception as check_error:
                    print(f"⚠️ Certificate check failed: {check_error}")
                    # Continue with installation attempt
                    
                # Try to install into LocalMachine Root (preferred)
                try:
                    print("🔐 Attempting to install certificate to LocalMachine\\Root...")
                    cmd_machine = ["certutil", "-addstore", "root", cert_path]
                    result = subprocess.run(cmd_machine, capture_output=True, text=True, 
                                          timeout=30, creationflags=subprocess.CREATE_NO_WINDOW)
                    if result.returncode == 0:
                        print(_('cert_installed_success'))
                        print("✅ mitmproxy CA installed in LocalMachine\\Root")
                        return True
                    else:
                        error_msg = (result.stderr or result.stdout or "").strip()
                        print(f"⚠️ LocalMachine install failed: {error_msg}")
                        
                        # Provide specific guidance based on error
                        if "access is denied" in error_msg.lower():
                            print("💡 Solution: Run the application as Administrator to install system-wide certificate")
                        elif "already exists" in error_msg.lower():
                            print("ℹ️ Certificate may already be installed, checking...")
                            if self._is_cert_installed_in_store_windows("machine"):
                                print("✅ Certificate confirmed installed in LocalMachine\\Root")
                                return True
                                
                except subprocess.TimeoutExpired:
                    print("⚠️ Certificate installation to LocalMachine timed out (30s)")
                    print("💡 Try running as Administrator or use manual installation")
                except Exception as e:
                    print(f"⚠️ LocalMachine install error: {e}")

                # If LocalMachine failed (likely due to no admin), try CurrentUser as fallback and WARN
                try:
                    print("🧩 Falling back to CurrentUser\\Root installation...")
                    cmd_user = ["certutil", "-user", "-addstore", "root", cert_path]
                    result_user = subprocess.run(cmd_user, capture_output=True, text=True, 
                                                timeout=30, creationflags=subprocess.CREATE_NO_WINDOW)
                    if result_user.returncode == 0:
                        print(_('cert_installed_success'))
                        print("✅ mitmproxy CA installed in CurrentUser\\Root")
                        print("⚠️ WARNING: LocalMachine\\Root installation is recommended for best compatibility.")
                        print("💡 To install system-wide: Run the app as Administrator")
                        return True
                    else:
                        error_msg = (result_user.stderr or result_user.stdout or "").strip()
                        print(f"⚠️ CurrentUser install failed: {error_msg}")
                        
                        # Check if certificate already exists in CurrentUser store
                        if "already exists" in error_msg.lower():
                            print("ℹ️ Certificate may already be installed, checking...")
                            if self._is_cert_installed_in_store_windows("user"):
                                print("✅ Certificate confirmed installed in CurrentUser\\Root")
                                return True
                        
                        # Suggest manual installation as last resort
                        print("💡 Consider manual installation using the batch script")
                        return False
                        
                except subprocess.TimeoutExpired:
                    print("⚠️ Certificate installation to CurrentUser timed out (30s)")
                    print("💡 Try manual installation or restart the application")
                    return False
                except Exception as e:
                    print(f"⚠️ CurrentUser install error: {e}")
                    print("💡 Use manual installation: double-click fix_certificate.bat")
                    return False
                    
            elif sys.platform == "darwin":
                # macOS: Use security command with multiple strategies
                print("🍎 macOS Certificate Installation")
                
                try:
                    # Strategy 1: Try to add to system keychain with trust settings
                    print("Attempting to install certificate to system keychain...")
                    cmd_system = [
                        "security", "add-trusted-cert", 
                        "-d",  # Add to admin cert store
                        "-r", "trustRoot",  # Set trust policy 
                        "-k", "/Library/Keychains/System.keychain",
                        cert_path
                    ]
                    result_system = subprocess.run(cmd_system, capture_output=True, text=True, timeout=30)
                    
                    if result_system.returncode == 0:
                        print(_('cert_installed_success'))
                        print("✅ Certificate installed to system keychain")
                        return True
                    else:
                        error_msg = result_system.stderr.strip()
                        print(f"⚠️ System keychain installation failed: {error_msg}")
                        
                        # Check for specific errors
                        if "not permitted" in error_msg.lower() or "authorization" in error_msg.lower():
                            print("💡 Tip: System keychain requires administrator privileges")
                    
                except subprocess.TimeoutExpired:
                    print("⚠️ System keychain installation timed out")
                except Exception as e:
                    print(f"⚠️ System keychain installation error: {e}")
                
                # Strategy 2: Add to login keychain with explicit trust
                try:
                    print("Attempting to install certificate to login keychain...")
                    user_keychain = os.path.expanduser("~/Library/Keychains/login.keychain-db")
                    
                    # First add the certificate
                    cmd_add = ["security", "add-cert", "-k", user_keychain, cert_path]
                    result_add = subprocess.run(cmd_add, capture_output=True, text=True, timeout=20)
                    
                    if result_add.returncode == 0 or "already exists" in result_add.stderr:
                        # Then set trust policy explicitly
                        cmd_trust = [
                            "security", "add-trusted-cert",
                            "-d",  # Add to admin cert store 
                            "-r", "trustRoot",  # Trust for SSL
                            "-k", user_keychain,
                            cert_path
                        ]
                        result_trust = subprocess.run(cmd_trust, capture_output=True, text=True, timeout=20)
                        
                        if result_trust.returncode == 0:
                            print(_('cert_installed_success'))
                            print("✅ Certificate installed and trusted in login keychain")
                            return True
                        else:
                            trust_error = result_trust.stderr.strip()
                            print(f"⚠️ Trust setting failed: {trust_error}")
                            
                            if "already exists" in trust_error.lower():
                                print("✅ Certificate may already be trusted")
                                return True
                    else:
                        add_error = result_add.stderr.strip()
                        print(f"⚠️ Certificate add failed: {add_error}")
                        
                except subprocess.TimeoutExpired:
                    print("⚠️ Login keychain installation timed out")
                except Exception as e:
                    print(f"⚠️ Login keychain installation error: {e}")
                
                # Strategy 3: Manual approach with user guidance
                print("🛠️ Automatic installation failed. Manual installation required.")
                self._show_manual_certificate_instructions(cert_path)
                return False
                
            else:
                # Linux: Multiple certificate installation strategies
                print("🐧 Linux Certificate Installation")
                
                # Strategy 1: Try to install to system certificate store
                success = False
                installation_attempts = []
                
                try:
                    # Copy to user directory first
                    user_cert_dir = os.path.expanduser("~/.local/share/ca-certificates")
                    os.makedirs(user_cert_dir, exist_ok=True)
                    
                    import shutil
                    user_cert_path = os.path.join(user_cert_dir, "mitmproxy-ca-cert.crt")
                    shutil.copy2(cert_path, user_cert_path)
                    
                    print(f"✅ Certificate copied to: {user_cert_path}")
                    installation_attempts.append("User certificate directory")
                    
                    # Try to update system certificates (might require sudo)
                    try:
                        print("Attempting system certificate store update...")
                        result = subprocess.run(["update-ca-certificates"], 
                                               capture_output=True, text=True, timeout=15)
                        if result.returncode == 0:
                            print("✅ Certificate installed to system certificate store")
                            success = True
                            installation_attempts.append("System certificate store")
                        else:
                            error_msg = result.stderr.strip()
                            print(f"⚠️ System certificate update failed: {error_msg}")
                            if "permission" in error_msg.lower():
                                print("💡 Tip: System certificate update requires sudo privileges")
                                
                    except FileNotFoundError:
                        print("⚠️ update-ca-certificates command not found (not Ubuntu/Debian?)")
                    except subprocess.TimeoutExpired:
                        print("⚠️ update-ca-certificates timed out")
                    
                    # Strategy 2: Install for browser certificate stores
                    if not success:
                        print("Installing certificate for browser use...")
                        
                        # Create .pki directory for NSS databases
                        nss_dir = os.path.expanduser("~/.pki/nssdb")
                        if os.path.exists(nss_dir):
                            try:
                                print("Installing to NSS database (Firefox, Chrome)...")
                                # Try using certutil for NSS databases (Firefox, Chrome on some distros)
                                result_nss = subprocess.run([
                                    "certutil", "-A", "-n", "mitmproxy-ca", 
                                    "-t", "TC,C,T", "-i", cert_path, "-d", nss_dir
                                ], capture_output=True, text=True, timeout=15)
                                
                                if result_nss.returncode == 0:
                                    print("✅ Certificate installed to NSS database")
                                    success = True
                                    installation_attempts.append("NSS database (browsers)")
                                else:
                                    nss_error = result_nss.stderr.strip()
                                    print(f"⚠️ NSS certificate installation failed: {nss_error}")
                                    if "already exists" in nss_error.lower():
                                        print("✅ Certificate may already exist in NSS database")
                                        success = True
                                        installation_attempts.append("NSS database (existing)")
                                        
                            except FileNotFoundError:
                                print("⚠️ certutil not available for NSS installation")
                                print("💡 Install with: sudo apt-get install libnss3-tools")
                            except subprocess.TimeoutExpired:
                                print("⚠️ NSS installation timed out")
                        else:
                            print("ℹ️ NSS database not found (~/.pki/nssdb)")
                    
                    if success:
                        print("✅ Linux certificate installation completed")
                        print(f"📝 Installed to: {', '.join(installation_attempts)}")
                        print("🔄 Please restart your browser for changes to take effect")
                        return True
                    else:
                        print("⚠️ Automatic installation partially successful")
                        print(f"📝 Attempted: {', '.join(installation_attempts)}")
                        print("🛠️ Manual browser configuration may be required")
                        self._show_manual_certificate_instructions_linux(cert_path)
                        return True  # Consider partial success as success
                        
                except Exception as e:
                    print(f"⚠️ Linux certificate installation error: {e}")
                    print("📝 Showing manual installation instructions...")
                    self._show_manual_certificate_instructions_linux(cert_path)
                    return True  # Consider showing instructions as success

        except Exception as e:
            error_msg = str(e) if e else "Unknown error"
            print(f"Certificate installation exception: {error_msg}")
            if error_msg.strip():
                print(_('cert_install_error').format(error_msg))
            else:
                print(_('cert_install_error').format("Unknown installation error occurred"))
            return False

    def _show_manual_certificate_instructions(self, cert_path):
        """Show manual certificate installation instructions for macOS"""
        print("\n" + "="*60)
        print("🔒 MANUAL CERTIFICATE INSTALLATION REQUIRED")
        print("="*60)
        print(f"Certificate location: {cert_path}")
        print("\nPlease follow these steps:")
        print("1. Open Keychain Access app (Applications → Utilities → Keychain Access)")
        print("2. Drag the certificate file to the 'System' or 'login' keychain")
        print("3. Double-click the installed certificate")
        print("4. Expand 'Trust' section")
        print("5. Set 'When using this certificate' to 'Always Trust'")
        print("6. Close the window and enter your password when prompted")
        print("\n🌐 For browsers like Chrome/Safari:")
        print("7. Restart your browser")
        print("8. The proxy should now work correctly")
        print("\n" + "="*60)

    def _show_manual_certificate_instructions_linux(self, cert_path):
        """Show manual certificate installation instructions for Linux"""
        print("\n" + "="*60)
        print("🔒 LINUX CERTIFICATE INSTALLATION INSTRUCTIONS")
        print("="*60)
        print(f"Certificate location: {cert_path}")
        print("\n📋 For System-wide Installation (Ubuntu/Debian):")
        print("1. Copy certificate to system directory:")
        print(f"   sudo cp {cert_path} /usr/local/share/ca-certificates/mitmproxy-ca.crt")
        print("2. Update certificate store:")
        print("   sudo update-ca-certificates")
        print("\n🌐 For Browser-specific Installation:")
        print("\n📱 Chrome/Chromium:")
        print("1. Open Chrome → Settings → Privacy and security → Security")
        print("2. Click 'Manage certificates' → 'Authorities' tab")
        print("3. Click 'Import' and select the certificate file")
        print("4. Check 'Trust this certificate for identifying websites'")
        print("\n🦊 Firefox:")
        print("1. Open Firefox → Preferences → Privacy & Security")
        print("2. Scroll to 'Certificates' section → Click 'View Certificates'")
        print("3. Go to 'Authorities' tab → Click 'Import'")
        print("4. Select the certificate file and check 'Trust for websites'")
        print("\n⚙️ For Environment Variables (alternative):")
        print("Add to ~/.bashrc or ~/.profile:")
        print(f"export SSL_CERT_FILE={cert_path}")
        print(f"export REQUESTS_CA_BUNDLE={cert_path}")
        print("\n🔄 After installation:")
        print("- Restart your browser")
        print("- The proxy should now work correctly")
        print("\n" + "="*60)


class ManualCertificateDialog(QDialog):
    """Manual certificate installation dialog"""

    def __init__(self, cert_path, parent=None):
        super().__init__(parent)
        self.cert_path = cert_path
        self.setWindowTitle(_('cert_manual_title'))
        self.setGeometry(300, 300, 650, 550)
        self.setFixedSize(650, 550)  # Make dialog non-resizable
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title = QLabel(_('cert_manual_title'))
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setProperty("class", "cert-title")
        layout.addWidget(title)

        # Explanation
        explanation = QLabel(_('cert_manual_explanation'))
        explanation.setWordWrap(True)
        explanation.setProperty("class", "cert-warning")
        layout.addWidget(explanation)

        # Certificate path
        path_label = QLabel(_('cert_manual_path'))
        path_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(path_label)

        path_display = QLabel(self.cert_path)
        path_display.setProperty("class", "cert-path")
        path_display.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(path_display)

        # Steps
        steps_label = QLabel(_('cert_manual_steps'))
        steps_label.setWordWrap(True)
        steps_label.setProperty("class", "cert-steps")
        layout.addWidget(steps_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # Open folder button
        self.open_folder_button = QPushButton(_('cert_open_folder'))
        self.open_folder_button.setProperty("class", "primary")
        self.open_folder_button.clicked.connect(self.open_certificate_folder)

        # Installation complete button
        self.completed_button = QPushButton(_('cert_manual_complete'))
        self.completed_button.setProperty("class", "primary")
        self.completed_button.clicked.connect(self.accept)

        # Cancel button
        cancel_button = QPushButton(_('cancel'))
        cancel_button.setProperty("state", "stop")
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.open_folder_button)
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(self.completed_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def open_certificate_folder(self):
        """Open certificate folder in file explorer"""
        try:
            cert_dir = os.path.dirname(self.cert_path)
            if os.path.exists(cert_dir):
                if sys.platform == "win32":
                    subprocess.Popen(['explorer', cert_dir])
                elif sys.platform == "darwin":
                    subprocess.Popen(['open', cert_dir])
                else:
                    # Linux
                    subprocess.Popen(['xdg-open', cert_dir])
            else:
                QMessageBox.warning(self, _('error'), _('certificate_not_found'))
        except Exception as e:
            QMessageBox.warning(self, _('error'), _('file_open_error').format(str(e)))