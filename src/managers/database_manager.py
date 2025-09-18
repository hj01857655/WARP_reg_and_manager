#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Database manager for Warp Account Manager
Handles all database operations for accounts and proxy settings
"""

import json
import sqlite3
from typing import Tuple, List, Optional


class DatabaseManager:
    """
    Centralized database manager for Warp Account Manager
    Handles all SQLite operations for accounts and proxy settings
    """
    
    def __init__(self, db_path: str = "accounts.db"):
        """Initialize database manager with database path"""
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database and create tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create accounts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                account_data TEXT NOT NULL,
                health_status TEXT DEFAULT 'healthy',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Add created_at column to existing table (if doesn't exist)
        try:
            # Check if created_at column exists
            cursor.execute("PRAGMA table_info(accounts)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'created_at' not in columns:
                # Add column without default first
                cursor.execute('ALTER TABLE accounts ADD COLUMN created_at TIMESTAMP')
                # Then update existing records with current timestamp
                cursor.execute('UPDATE accounts SET created_at = datetime("now") WHERE created_at IS NULL')
                conn.commit()
                print("✅ Added created_at column to accounts table")
        except sqlite3.OperationalError as e:
            print(f"Database migration warning: {e}")

        # Add health_status column to existing table (if doesn't exist)
        try:
            cursor.execute('ALTER TABLE accounts ADD COLUMN health_status TEXT DEFAULT "healthy"')
        except sqlite3.OperationalError:
            # Column already exists
            pass

        # Add limit_info column to existing table (if doesn't exist)
        # First check if column exists and if it has Turkish default value
        try:
            cursor.execute("PRAGMA table_info(accounts)")
            columns = {col[1]: col for col in cursor.fetchall()}
            
            if 'limit_info' not in columns:
                # Column doesn't exist, create it with correct default
                cursor.execute('ALTER TABLE accounts ADD COLUMN limit_info TEXT DEFAULT "Not updated"')
                print("✅ Added limit_info column with English default")
            else:
                # Column exists, check if it has Turkish default by checking existing NULL values
                cursor.execute('SELECT COUNT(*) FROM accounts WHERE limit_info IS NULL')
                null_count = cursor.fetchone()[0]
                
                if null_count > 0:
                    # Update NULL values to English default
                    cursor.execute('UPDATE accounts SET limit_info = "Not updated" WHERE limit_info IS NULL')
                    print(f"✅ Updated {null_count} NULL limit_info values to English default")
                    
        except sqlite3.OperationalError as e:
            print(f"limit_info column migration warning: {e}")
        
        # Create proxy settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS proxy_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        ''')

        # Add default value for certificate approval status
        cursor.execute('''
            INSERT OR IGNORE INTO proxy_settings (key, value)
            VALUES ('certificate_approved', 'false')
        ''')
        
        conn.commit()
        conn.close()

    # Account management methods
    def add_account(self, account_json: str) -> Tuple[bool, str]:
        """Add or update account in database"""
        try:
            account_data = json.loads(account_json)
            email = account_data.get('email')
            
            if not email:
                return False, "Email not found in account data"
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if account with this email already exists
            cursor.execute("SELECT id FROM accounts WHERE email = ?", (email,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing account (don't change created_at)
                cursor.execute(
                    "UPDATE accounts SET account_data = ?, last_updated = CURRENT_TIMESTAMP WHERE email = ?",
                    (account_json, email)
                )
                conn.commit()
                conn.close()
                return True, f"Account {email} updated"
            else:
                # Add new account (set created_at to current time)
                cursor.execute(
                    "INSERT INTO accounts (email, account_data, health_status, created_at) VALUES (?, ?, ?, datetime('now'))",
                    (email, account_json, 'healthy')
                )
                conn.commit()
                conn.close()
                return True, f"Account {email} added"
                
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON format: {e}"
        except sqlite3.Error as e:
            return False, f"Database error: {e}"
        except Exception as e:
            return False, f"Unexpected error: {e}"

    def get_accounts(self) -> List[Tuple[str, str]]:
        """Get all accounts (email, account_data) sorted by creation date (earliest first)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if created_at column exists
        try:
            cursor.execute('SELECT email, account_data FROM accounts ORDER BY created_at ASC')
        except sqlite3.OperationalError:
            # Fallback to email sorting if created_at doesn't exist
            cursor.execute('SELECT email, account_data FROM accounts ORDER BY email')
            
        accounts = cursor.fetchall()
        conn.close()
        return accounts

    def get_accounts_with_health(self) -> List[Tuple[str, str, str]]:
        """Get all accounts with health status (email, account_data, health_status) sorted by creation date (earliest first)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if created_at column exists
        try:
            cursor.execute('SELECT email, account_data, health_status FROM accounts ORDER BY created_at ASC')
        except sqlite3.OperationalError:
            # Fallback to email sorting if created_at doesn't exist
            cursor.execute('SELECT email, account_data, health_status FROM accounts ORDER BY email')
            
        accounts = cursor.fetchall()
        conn.close()
        return accounts

    def get_accounts_with_health_and_limits(self) -> List[Tuple[str, str, str, str]]:
        """Get all accounts with health status and limits (email, account_data, health_status, limit_info) sorted by creation date (earliest first)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Query with correct field order from database
        try:
            cursor.execute('SELECT email, account_data, health_status, limit_info FROM accounts ORDER BY created_at ASC')
        except sqlite3.OperationalError:
            # Fallback to email sorting if created_at doesn't exist
            cursor.execute('SELECT email, account_data, health_status, limit_info FROM accounts ORDER BY email')
            
        accounts = cursor.fetchall()
        conn.close()
        return accounts
    
    def get_accounts_with_all_info(self) -> List[Tuple[str, str, str, str, str, str]]:
        """Get all accounts with complete info following DB structure order: (id, email, account_data, health_status, created_at, limit_info)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Select fields matching DB structure order (excluding last_updated)
        # DB order: id, email, account_data, health_status, created_at, last_updated, limit_info
        # We select: id, email, account_data, health_status, created_at, limit_info
        try:
            cursor.execute('SELECT id, email, account_data, health_status, created_at, limit_info FROM accounts ORDER BY created_at ASC')
        except sqlite3.OperationalError:
            # Fallback without created_at if column doesn't exist
            cursor.execute('SELECT id, email, account_data, health_status, NULL, limit_info FROM accounts ORDER BY email')
            
        accounts = cursor.fetchall()
        conn.close()
        return accounts

    def update_account_health(self, email: str, health_status: str) -> bool:
        """Update account health status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE accounts SET health_status = ?, last_updated = CURRENT_TIMESTAMP
                WHERE email = ?
            ''', (health_status, email))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Health status update error: {e}")
            return False

    def update_account_token(self, email: str, new_token_data: dict) -> bool:
        """Update account token information"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT account_data FROM accounts WHERE email = ?', (email,))
            result = cursor.fetchone()

            if result:
                account_data = json.loads(result[0])
                account_data['stsTokenManager'].update(new_token_data)

                cursor.execute('''
                    UPDATE accounts SET account_data = ?, last_updated = CURRENT_TIMESTAMP
                    WHERE email = ?
                ''', (json.dumps(account_data), email))
                conn.commit()
                conn.close()
                return True
            return False
        except Exception as e:
            print(f"Token update error: {e}")
            return False

    def update_account(self, email: str, updated_json: str) -> bool:
        """Update complete account information (as JSON string)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE accounts SET account_data = ?, last_updated = CURRENT_TIMESTAMP
                WHERE email = ?
            ''', (updated_json, email))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Account update error: {e}")
            return False

    def update_account_limit_info(self, email: str, limit_info: str) -> bool:
        """Update account limit information"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE accounts SET limit_info = ?, last_updated = CURRENT_TIMESTAMP
                WHERE email = ?
            ''', (limit_info, email))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Limit info update error: {e}")
            return False

    def delete_account(self, email: str) -> bool:
        """Delete account and clear it from active if it was active"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Delete account
            cursor.execute('DELETE FROM accounts WHERE email = ?', (email,))

            # If deleted account was active, clear active account
            cursor.execute('SELECT value FROM proxy_settings WHERE key = ?', ('active_account',))
            result = cursor.fetchone()
            if result and result[0] == email:
                cursor.execute('DELETE FROM proxy_settings WHERE key = ?', ('active_account',))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Account delete error: {e}")
            return False

    # Proxy settings methods
    def set_active_account(self, email: str) -> bool:
        """Set active account"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO proxy_settings (key, value)
                VALUES ('active_account', ?)
            ''', (email,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Active account set error: {e}")
            return False

    def get_active_account(self) -> Optional[str]:
        """Get active account email"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM proxy_settings WHERE key = ?', ('active_account',))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else None
        except:
            return None

    def clear_active_account(self) -> bool:
        """Clear active account"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM proxy_settings WHERE key = ?', ('active_account',))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Active account clear error: {e}")
            return False

    # Certificate management methods
    def is_certificate_approved(self) -> bool:
        """Check if certificate was previously approved"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM proxy_settings WHERE key = ?', ('certificate_approved',))
            result = cursor.fetchone()
            conn.close()
            return result and result[0] == 'true'
        except:
            return False

    def set_certificate_approved(self, approved: bool = True) -> bool:
        """Save certificate approval to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO proxy_settings (key, value)
                VALUES ('certificate_approved', ?)
            ''', ('true' if approved else 'false',))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Certificate confirmation save error: {e}")
            return False

    # General proxy settings methods
    def get_proxy_setting(self, key: str) -> Optional[str]:
        """Get a proxy setting by key"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM proxy_settings WHERE key = ?', (key,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else None
        except:
            return None

    def set_proxy_setting(self, key: str, value: str) -> bool:
        """Set a proxy setting"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO proxy_settings (key, value)
                VALUES (?, ?)
            ''', (key, value))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Proxy setting update error: {e}")
            return False

    def delete_proxy_setting(self, key: str) -> bool:
        """Delete a proxy setting"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM proxy_settings WHERE key = ?', (key,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Proxy setting delete error: {e}")
            return False


# Legacy compatibility wrapper
class AccountManager(DatabaseManager):
    """
    Legacy compatibility wrapper for existing code
    Inherits all functionality from DatabaseManager
    """
    pass