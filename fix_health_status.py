#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复数据库中健康状态字段的脚本
将错误的 'status_healthy' 修复为 'healthy'
"""

import sqlite3
from pathlib import Path

def fix_health_status():
    """修复健康状态字段"""
    db_path = "accounts.db"
    
    if not Path(db_path).exists():
        print(f"❌ 数据库文件不存在: {db_path}")
        return
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # 查看当前状态
            cursor.execute("SELECT email, health_status FROM accounts")
            accounts = cursor.fetchall()
            
            print("🔍 当前账户健康状态:")
            for email, status in accounts:
                print(f"   {email}: {status}")
            
            # 修复错误的状态值
            fixes = [
                ('status_healthy', 'healthy'),
                ('status_banned', 'banned'), 
                ('status_unhealthy', 'unhealthy')
            ]
            
            total_fixed = 0
            
            for wrong_status, correct_status in fixes:
                cursor.execute("UPDATE accounts SET health_status = ? WHERE health_status = ?", 
                              (correct_status, wrong_status))
                fixed_count = cursor.rowcount
                if fixed_count > 0:
                    print(f"✅ 修复了 {fixed_count} 个账户的状态: '{wrong_status}' -> '{correct_status}'")
                    total_fixed += fixed_count
            
            # 处理NULL值
            cursor.execute("UPDATE accounts SET health_status = 'healthy' WHERE health_status IS NULL")
            null_fixed = cursor.rowcount
            if null_fixed > 0:
                print(f"✅ 修复了 {null_fixed} 个NULL状态为 'healthy'")
                total_fixed += null_fixed
            
            conn.commit()
            
            if total_fixed > 0:
                print(f"\n🎯 总共修复了 {total_fixed} 个账户的健康状态")
                
                # 显示修复后的状态
                print("\n📊 修复后的账户状态:")
                cursor.execute("SELECT email, health_status FROM accounts")
                accounts = cursor.fetchall()
                for email, status in accounts:
                    print(f"   {email}: {status}")
            else:
                print("\n✅ 所有账户的健康状态都是正确的，无需修复")
                
    except sqlite3.Error as e:
        print(f"❌ 数据库错误: {e}")
    except Exception as e:
        print(f"❌ 意外错误: {e}")

if __name__ == "__main__":
    fix_health_status()