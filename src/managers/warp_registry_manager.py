#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Warp Registry Manager
管理Warp相关的Windows注册表设置，包括监控和自动修正功能
"""

import os
import winreg
import random
import time
import threading
import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List


class WarpRegistryManager:
    """Warp注册表管理器"""
    
    def __init__(self):
        self.user_sid = self._get_current_user_sid()
        self.warp_registry_path = f"S-{self.user_sid}\\Software\\Warp.dev\\Warp" if self.user_sid else None
        self.monitoring_active = False
        self.monitor_thread = None
        
    def _get_current_user_sid(self) -> Optional[str]:
        """获取当前用户的SID"""
        try:
            import subprocess
            result = subprocess.run([
                'wmic', 'useraccount', 'where', f'name="{os.getlogin()}"', 
                'get', 'sid', '/value'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.startswith('SID='):
                        sid = line.split('=', 1)[1].strip()
                        if sid.startswith('S-1-5-21-'):
                            return sid.replace('S-', '')
                        
            # 备用方法：使用当前用户的已知SID格式
            return "1-5-21-1975947051-2922622289-44519384-1002"
            
        except Exception as e:
            print(f"获取用户SID失败: {e}")
            # 使用您提供的默认SID
            return "1-5-21-1975947051-2922622289-44519384-1002"
    
    def _open_warp_registry_key(self, access=winreg.KEY_READ):
        """打开Warp注册表键"""
        try:
            if not self.warp_registry_path:
                raise Exception("无法确定Warp注册表路径")
                
            return winreg.OpenKey(
                winreg.HKEY_USERS,
                self.warp_registry_path,
                0,
                access
            )
        except FileNotFoundError:
            if access == winreg.KEY_READ:
                return None
            # 如果是写入权限且键不存在，创建它
            return winreg.CreateKey(winreg.HKEY_USERS, self.warp_registry_path)
        except Exception as e:
            print(f"打开Warp注册表键失败: {e}")
            return None
    
    def get_registry_value(self, value_name: str) -> Optional[Any]:
        """获取注册表值"""
        try:
            key = self._open_warp_registry_key(winreg.KEY_READ)
            if not key:
                return None
                
            value, reg_type = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            return value
            
        except FileNotFoundError:
            return None
        except Exception as e:
            print(f"读取注册表值 {value_name} 失败: {e}")
            return None
    
    def set_registry_value(self, value_name: str, value: Any, reg_type: int = winreg.REG_SZ, silent: bool = False) -> bool:
        """设置注册表值"""
        try:
            key = self._open_warp_registry_key(winreg.KEY_WRITE)
            if not key:
                return False
                
            winreg.SetValueEx(key, value_name, 0, reg_type, value)
            winreg.CloseKey(key)
            if not silent:
                print(f"✅ 注册表值已更新: {value_name} = {value}")
            return True
            
        except Exception as e:
            print(f"设置注册表值 {value_name} 失败: {e}")
            return False
    
    def generate_experiment_id(self) -> str:
        """生成UUID格式的实验ID"""
        def hex_chunk(length):
            return ''.join(random.choice('0123456789abcdef') for _ in range(length))
        
        return f"{hex_chunk(8)}-{hex_chunk(4)}-{hex_chunk(4)}-{hex_chunk(4)}-{hex_chunk(12)}"
    
    def check_and_fix_reverse_pro_trial(self) -> bool:
        """检查并修正ReverseProTrialModalDismissed值"""
        try:
            current_value = self.get_registry_value("ReverseProTrialModalDismissed")
            
            # Warp应用中，ReverseProTrialModalDismissed使用REG_SZ格式存储: "false"/"true"
            if current_value == 1 or str(current_value).lower() == 'true':
                print("⚠️ 检测到ReverseProTrialModalDismissed为true，正在修正...")
                success = self.set_registry_value("ReverseProTrialModalDismissed", "false", winreg.REG_SZ)
                if success:
                    print("✅ ReverseProTrialModalDismissed已重置为false")
                    return True
                else:
                    print("❌ 修正ReverseProTrialModalDismissed失败")
                    return False
            elif current_value == 0 or str(current_value).lower() == 'false':
                # 状态正常，不打印信息
                return True
            elif current_value is None:
                # 如果值不存在，不做任何操作，直接返回True
                return True
            else:
                # 尝试强制设置为false
                print(f"⚠️ ReverseProTrialModalDismissed值异常: {current_value}，强制设置为false")
                return self.set_registry_value("ReverseProTrialModalDismissed", "false", winreg.REG_SZ)
                
        except Exception as e:
            print(f"检查ReverseProTrialModalDismissed失败: {e}")
            return False
    
    def check_and_fix_telemetry_enabled(self) -> bool:
        """检查并修正TelemetryEnabled值"""
        try:
            current_value = self.get_registry_value("TelemetryEnabled")
            
            # Warp应用中，TelemetryEnabled使用REG_SZ格式存储: "false"/"true"
            if current_value == 1 or str(current_value).lower() == 'true':
                print("⚠️ 检测到TelemetryEnabled为true，正在修正...")
                success = self.set_registry_value("TelemetryEnabled", "false", winreg.REG_SZ)
                if success:
                    print("✅ TelemetryEnabled已重置为false")
                    return True
                else:
                    print("❌ 修正TelemetryEnabled失败")
                    return False
            elif current_value == 0 or str(current_value).lower() == 'false':
                # 状态正常，不打印信息
                return True
            elif current_value is None:
                # 如果值不存在，不做任何操作，直接返回True
                return True
            else:
                # 尝试强制设置为false
                print(f"⚠️ TelemetryEnabled值异常: {current_value}，强制设置为false")
                return self.set_registry_value("TelemetryEnabled", "false", winreg.REG_SZ)
                
        except Exception as e:
            print(f"检查TelemetryEnabled失败: {e}")
            return False
    
    def update_experiment_id(self) -> bool:
        """更新ExperimentId到注册表"""
        try:
            new_experiment_id = self.generate_experiment_id()
            old_value = self.get_registry_value("ExperimentId")
            
            success = self.set_registry_value("ExperimentId", new_experiment_id, winreg.REG_SZ)
            if success:
                print(f"🧪 ExperimentId已更新:")
                print(f"   旧值: {old_value}")
                print(f"   新值: {new_experiment_id}")
                return True
            else:
                print("❌ ExperimentId更新失败")
                return False
                
        except Exception as e:
            print(f"更新ExperimentId失败: {e}")
            return False
    
    def monitor_registry_values(self):
        """监控注册表值的线程函数"""
        print("🔍 开始监控Warp注册表值...")
        
        while self.monitoring_active:
            try:
                # 检查并修正ReverseProTrialModalDismissed
                self.check_and_fix_reverse_pro_trial()
                
                # 检查并修正TelemetryEnabled
                self.check_and_fix_telemetry_enabled()
                
                # 每10秒检查一次
                time.sleep(10)
                
            except Exception as e:
                print(f"监控过程中出错: {e}")
                time.sleep(10)
                continue
    
    def start_monitoring(self):
        """启动监控"""
        if self.monitoring_active:
            print("⚠️ 注册表监控已经在运行")
            return
            
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self.monitor_registry_values, daemon=True)
        self.monitor_thread.start()
        print("✅ Warp注册表监控已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        if not self.monitoring_active:
            print("⚠️ 注册表监控未在运行")
            return
            
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        print("🛑 Warp注册表监控已停止")
    
    def prepare_for_registration(self) -> bool:
        """为注册准备：更新ExperimentId和检查其他设置"""
        print("🔧 准备Warp注册环境...")
        
        success = True
        
        # 1. 更新ExperimentId
        if not self.update_experiment_id():
            success = False
            
        # 2. 确保ReverseProTrialModalDismissed为false
        if not self.check_and_fix_reverse_pro_trial():
            success = False
            
        # 3. 确保TelemetryEnabled为false
        if not self.check_and_fix_telemetry_enabled():
            success = False
        
        if success:
            print("✅ Warp注册环境准备完成")
        else:
            print("⚠️ Warp注册环境准备过程中遇到问题")
            
        return success
    
    def get_current_settings(self) -> Dict[str, Any]:
        """获取当前Warp注册表设置"""
        settings = {}
        
        try:
            settings['ReverseProTrialModalDismissed'] = self.get_registry_value("ReverseProTrialModalDismissed")
            settings['TelemetryEnabled'] = self.get_registry_value("TelemetryEnabled")
            settings['ExperimentId'] = self.get_registry_value("ExperimentId")
            settings['AIRequestLimitInfo'] = self.get_ai_request_limit_info()
            settings['ChangelogVersions'] = self.get_changelog_versions()
            
            print("📋 当前Warp注册表设置:")
            for key, value in settings.items():
                if key == 'AIRequestLimitInfo' and isinstance(value, dict):
                    print(f"   {key}:")
                    print(f"      - 使用量: {value.get('num_requests_used_since_refresh')}/{value.get('limit')}")
                    print(f"      - 账户过期: {value.get('next_refresh_time_formatted')}")
                    print(f"      - 刷新周期: {value.get('refresh_duration_formatted')}")
                elif key == 'ChangelogVersions':
                    print(f"   {key}: {value[0] if value else '未知'}")
                else:
                    print(f"   {key}: {value}")
                
        except Exception as e:
            print(f"获取注册表设置失败: {e}")
            
        return settings
    
    def get_ai_request_limit_info(self) -> Dict[str, Any]:
        """获取并解析AI请求限制信息"""
        try:
            ai_limit_info = self.get_registry_value("AIRequestLimitInfo")
            if ai_limit_info:
                # 解析JSON数据
                if isinstance(ai_limit_info, str):
                    limit_data = json.loads(ai_limit_info)
                else:
                    limit_data = ai_limit_info
                
                # 添加格式化后的字段
                if limit_data:
                    # 格式化账户过期时间
                    next_refresh = limit_data.get("next_refresh_time", "")
                    if next_refresh:
                        try:
                            expiry_date = datetime.fromisoformat(next_refresh.replace('Z', '+00:00'))
                            limit_data['next_refresh_time_formatted'] = expiry_date.strftime("%Y-%m-%d %H:%M")
                            
                            # 计算剩余天数
                            now = datetime.now(timezone.utc)
                            days_left = (expiry_date - now).days
                            limit_data['days_until_refresh'] = days_left
                        except:
                            limit_data['next_refresh_time_formatted'] = next_refresh[:19]
                            limit_data['days_until_refresh'] = -1
                    
                    # 格式化刷新周期
                    refresh_duration = limit_data.get("request_limit_refresh_duration", "")
                    duration_map = {
                        "EveryTwoWeeks": "每两周",
                        "Monthly": "每月",
                        "Weekly": "每周",
                        "Daily": "每天"
                    }
                    limit_data['refresh_duration_formatted'] = duration_map.get(refresh_duration, refresh_duration)
                    
                    # 计算使用率
                    limit = limit_data.get("limit", 1)
                    used = limit_data.get("num_requests_used_since_refresh", 0)
                    limit_data['usage_percentage'] = round((used / limit * 100) if limit > 0 else 0, 1)
                    
                return limit_data
            
        except Exception as e:
            print(f"获取AI请求限制信息失败: {e}")
        
        # 返回默认值
        return {
            "limit": 2500,
            "num_requests_used_since_refresh": 0,
            "next_refresh_time": "",
            "next_refresh_time_formatted": "未知",
            "days_until_refresh": -1,
            "is_unlimited": False,
            "request_limit_refresh_duration": "EveryTwoWeeks",
            "refresh_duration_formatted": "每两周",
            "usage_percentage": 0.0
        }
    
    def get_changelog_versions(self) -> List[str]:
        """获取并解析软件版本信息"""
        try:
            changelog = self.get_registry_value("ChangelogVersions")
            if changelog:
                # 解析JSON数据
                if isinstance(changelog, str):
                    versions_data = json.loads(changelog)
                else:
                    versions_data = changelog
                
                # 返回版本列表
                if isinstance(versions_data, dict):
                    return list(versions_data.keys())
                
        except Exception as e:
            print(f"获取版本信息失败: {e}")
        
        return []
    
    def get_latest_version(self) -> str:
        """获取最新软件版本"""
        versions = self.get_changelog_versions()
        return versions[0] if versions else "未知"
    
    def update_ai_request_usage(self, new_usage: int) -> bool:
        """更新AI请求使用量（仅用于测试或调试）"""
        try:
            limit_info = self.get_ai_request_limit_info()
            if limit_info:
                limit_info['num_requests_used_since_refresh'] = new_usage
                
                # 移除格式化字段，只保留原始数据
                for key in ['next_refresh_time_formatted', 'days_until_refresh', 
                           'refresh_duration_formatted', 'usage_percentage']:
                    limit_info.pop(key, None)
                
                # 保存回注册表
                json_str = json.dumps(limit_info)
                return self.set_registry_value("AIRequestLimitInfo", json_str, winreg.REG_SZ, silent=True)
        
        except Exception as e:
            print(f"更新AI请求使用量失败: {e}")
        
        return False


# 单例实例
warp_registry_manager = WarpRegistryManager()


def test_registry_manager():
    """测试注册表管理器功能"""
    print("🧪 测试Warp注册表管理器...")
    
    manager = WarpRegistryManager()
    
    # 1. 获取当前设置
    print("\n1️⃣ 当前设置:")
    manager.get_current_settings()
    
    # 2. 测试ExperimentId更新
    print("\n2️⃣ 测试ExperimentId更新:")
    manager.update_experiment_id()
    
    # 3. 测试ReverseProTrialModalDismissed检查
    print("\n3️⃣ 测试ReverseProTrialModalDismissed检查:")
    manager.check_and_fix_reverse_pro_trial()
    
    # 4. 测试注册准备
    print("\n4️⃣ 测试注册准备:")
    manager.prepare_for_registration()
    
    print("\n✅ 注册表管理器测试完成")


if __name__ == "__main__":
    import os
    test_registry_manager()
