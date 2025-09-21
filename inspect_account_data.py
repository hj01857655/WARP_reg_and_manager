#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
查看账户JSON数据结构的脚本
用于了解流量重置时间等信息的存储位置
"""

import json
import sqlite3
from pathlib import Path

def inspect_account_data():
    """检查账户数据结构"""
    db_path = "accounts.db"
    
    if not Path(db_path).exists():
        print(f"❌ 数据库文件不存在: {db_path}")
        return
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # 获取第一个账户的数据
            cursor.execute("SELECT email, account_data FROM accounts LIMIT 1")
            result = cursor.fetchone()
            
            if not result:
                print("❌ 数据库中没有找到任何账户")
                return
            
            email, account_json = result
            print(f"📧 账户: {email}")
            print("=" * 60)
            
            try:
                account_data = json.loads(account_json)
                print("📋 账户数据结构:")
                print(json.dumps(account_data, indent=2, ensure_ascii=False))
                
                # 查找可能的流量相关字段
                print("\n🔍 查找流量相关字段:")
                
                def find_keys_containing(data, search_terms, path=""):
                    """递归查找包含特定关键词的字段"""
                    if isinstance(data, dict):
                        for key, value in data.items():
                            current_path = f"{path}.{key}" if path else key
                            
                            # 检查键名是否包含搜索词
                            for term in search_terms:
                                if term.lower() in key.lower():
                                    print(f"   • {current_path}: {value}")
                            
                            # 递归搜索
                            find_keys_containing(value, search_terms, current_path)
                    elif isinstance(data, list):
                        for i, item in enumerate(data):
                            current_path = f"{path}[{i}]"
                            find_keys_containing(item, search_terms, current_path)
                
                search_terms = ["limit", "refresh", "reset", "time", "usage", "request"]
                find_keys_containing(account_data, search_terms)
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析错误: {e}")
                
    except sqlite3.Error as e:
        print(f"❌ 数据库错误: {e}")
    except Exception as e:
        print(f"❌ 意外错误: {e}")

if __name__ == "__main__":
    inspect_account_data()