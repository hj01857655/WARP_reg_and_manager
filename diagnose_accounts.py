#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
账户状态诊断脚本
用于诊断 "No healthy accounts available for switching" 问题
"""

import sys
import json
import time
import sqlite3
from pathlib import Path

def diagnose_accounts():
    """诊断账户状态"""
    print("🔍 开始诊断账户状态...")
    print("=" * 60)
    
    # 检查数据库文件
    db_path = "accounts.db"
    if not Path(db_path).exists():
        print(f"❌ 数据库文件不存在: {db_path}")
        return
    
    print(f"✅ 找到数据库文件: {db_path}")
    
    try:
        # 连接数据库
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # 获取所有账户
            cursor.execute("SELECT id, email, account_data, health_status, created_at, limit_info FROM accounts ORDER BY created_at ASC")
            accounts = cursor.fetchall()
            
            if not accounts:
                print("❌ 数据库中没有找到任何账户")
                print("\n💡 解决方案:")
                print("   1. 使用 '手动添加账户' 功能添加账户")
                print("   2. 使用 '自动添加账户' 功能创建新账户")
                return
            
            print(f"📊 总共找到 {len(accounts)} 个账户")
            print("\n详细账户状态:")
            print("-" * 100)
            print(f"{'ID':<3} {'邮箱':<25} {'健康状态':<10} {'令牌状态':<12} {'用量限制':<15} {'创建时间'}")
            print("-" * 100)
            
            healthy_count = 0
            banned_count = 0
            expired_count = 0
            available_count = 0
            
            current_time = int(time.time() * 1000)
            
            for account_id, email, account_json, health_status, created_at, limit_info in accounts:
                try:
                    # 解析账户数据
                    account_data = json.loads(account_json)
                    expiration_time = account_data['stsTokenManager']['expirationTime']
                    
                    if isinstance(expiration_time, str):
                        expiration_time = int(expiration_time)
                    
                    # 检查令牌状态
                    if current_time >= expiration_time:
                        token_status = "已过期"
                        expired_count += 1
                    else:
                        token_status = "有效"
                    
                    # 检查健康状态
                    if health_status == 'banned':
                        banned_count += 1
                        health_display = "🔴 封禁"
                    elif health_status == 'healthy':
                        healthy_count += 1
                        health_display = "🟢 健康"
                        
                        # 检查是否可用（健康 + 令牌有效 + 有流量）
                        if token_status == "有效":
                            # 检查流量限制
                            if limit_info and "/" in limit_info:
                                try:
                                    used, total = map(int, limit_info.split('/'))
                                    remaining = total - used
                                    if remaining > 15:  # 至少15个请求的余量
                                        available_count += 1
                                        health_display = "🟢 可用"
                                    else:
                                        health_display = "🟡 流量不足"
                                except:
                                    available_count += 1
                                    health_display = "🟢 可用"
                            else:
                                available_count += 1
                                health_display = "🟢 可用"
                    else:
                        health_display = f"🟡 {health_status}"
                    
                    # 格式化显示
                    email_short = email[:22] + "..." if len(email) > 25 else email
                    limit_display = limit_info or "未更新"
                    created_display = created_at[:16] if created_at else "未知"
                    
                    print(f"{account_id:<3} {email_short:<25} {health_display:<15} {token_status:<12} {limit_display:<15} {created_display}")
                    
                except Exception as e:
                    print(f"{account_id:<3} {email[:22]:<25} ❌ 数据错误     {str(e)[:30]}")
            
            print("-" * 100)
            print(f"\n📈 统计摘要:")
            print(f"   🟢 健康账户: {healthy_count}")
            print(f"   🟢 可用账户: {available_count}")
            print(f"   🔴 封禁账户: {banned_count}")
            print(f"   ⏰ 过期令牌: {expired_count}")
            
            print(f"\n🎯 诊断结果:")
            if available_count == 0:
                print(f"❌ 没有可用的健康账户可以切换")
                print(f"\n💡 可能的原因:")
                if banned_count > 0:
                    print(f"   • {banned_count} 个账户被封禁")
                if expired_count > 0:
                    print(f"   • {expired_count} 个账户令牌已过期")
                if healthy_count > 0 and available_count == 0:
                    print(f"   • 健康账户的流量可能已用完")
                
                print(f"\n🔧 解决方案:")
                print(f"   1. 使用 '🔄 刷新令牌' 功能刷新过期的令牌")
                print(f"   2. 使用 '🗑️ 删除封禁账号' 功能清理封禁的账户")
                print(f"   3. 添加新的健康账户")
                print(f"   4. 等待流量重置（根据账户的 requestLimitRefreshDuration 设置）")
                print(f"      • MONTHLY: 每月重置")
                print(f"      • EVERY_TWO_WEEKS: 每两周重置")
                print(f"      • WEEKLY: 每周重置")
                print(f"      • DAILY: 每日重置")
            else:
                print(f"✅ 找到 {available_count} 个可用的健康账户")
                
    except sqlite3.Error as e:
        print(f"❌ 数据库错误: {e}")
    except Exception as e:
        print(f"❌ 意外错误: {e}")

if __name__ == "__main__":
    diagnose_accounts()