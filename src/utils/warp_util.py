#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Warp Process Utility
Manages Warp application process operations (start, stop, check status)
"""

import os
import sys
import time
import subprocess
import psutil
from typing import Optional, List, Dict


class WarpProcessManager:
    """管理 Warp 应用程序进程"""
    
    def __init__(self):
        """初始化 Warp 进程管理器"""
        self.warp_process_name = "Warp.exe" if sys.platform == "win32" else "Warp"
        self.warp_path = self._find_warp_executable()
        
    def _find_warp_executable(self) -> Optional[str]:
        """查找 Warp 可执行文件路径"""
        if sys.platform == "win32":
            # Windows 常见安装路径
            possible_paths = [
                os.path.expanduser(r"~\AppData\Local\Programs\Warp\Warp.exe"),
                r"C:\Program Files\Warp\Warp.exe",
                r"C:\Program Files (x86)\Warp\Warp.exe",
                os.path.expanduser(r"~\scoop\apps\warp\current\Warp.exe"),
            ]
            
            # 从环境变量 LOCALAPPDATA 构建路径
            local_appdata = os.environ.get('LOCALAPPDATA')
            if local_appdata:
                possible_paths.insert(0, os.path.join(local_appdata, "Programs", "Warp", "Warp.exe"))
                
        elif sys.platform == "darwin":
            # macOS 路径
            possible_paths = [
                "/Applications/Warp.app/Contents/MacOS/Warp",
                os.path.expanduser("~/Applications/Warp.app/Contents/MacOS/Warp"),
            ]
        else:
            # Linux 路径
            possible_paths = [
                "/usr/bin/warp",
                "/usr/local/bin/warp",
                "/opt/warp/warp",
                os.path.expanduser("~/.local/bin/warp"),
            ]
        
        # 检查每个可能的路径
        for path in possible_paths:
            if os.path.exists(path):
                print(f"✅ Found Warp executable: {path}")
                return path
        
        print(f"⚠️ Warp executable not found in standard locations")
        return None
    
    def is_warp_running(self) -> bool:
        """检查 Warp 是否正在运行"""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] and self.warp_process_name.lower() in proc.info['name'].lower():
                    return True
            return False
        except Exception as e:
            print(f"Error checking Warp process: {e}")
            return False
    
    def get_warp_processes(self) -> List[Dict]:
        """获取所有 Warp 进程信息"""
        warp_processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
                if proc.info['name'] and self.warp_process_name.lower() in proc.info['name'].lower():
                    warp_processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cpu_percent': proc.info.get('cpu_percent', 0),
                        'memory_mb': proc.info['memory_info'].rss / 1024 / 1024 if proc.info.get('memory_info') else 0
                    })
        except Exception as e:
            print(f"Error getting Warp processes: {e}")
        return warp_processes
    
    def stop_warp(self, force: bool = False) -> bool:
        """
        停止 Warp 进程
        
        Args:
            force: 是否强制终止（True: 强制kill, False: 优雅关闭）
            
        Returns:
            bool: 成功返回 True，失败返回 False
        """
        try:
            if not self.is_warp_running():
                print("ℹ️ Warp is not running")
                return True
            
            print("🛑 Stopping Warp...")
            
            # 获取所有 Warp 进程
            warp_processes = []
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] and self.warp_process_name.lower() in proc.info['name'].lower():
                    warp_processes.append(proc)
            
            if not warp_processes:
                print("ℹ️ No Warp processes found")
                return True
            
            # 终止进程
            for proc in warp_processes:
                try:
                    if force:
                        proc.kill()  # 强制终止
                        print(f"⚡ Force killed Warp process (PID: {proc.pid})")
                    else:
                        proc.terminate()  # 优雅关闭
                        print(f"📤 Terminated Warp process (PID: {proc.pid})")
                except psutil.NoSuchProcess:
                    continue
                except psutil.AccessDenied:
                    print(f"❌ Access denied to terminate process (PID: {proc.pid})")
                    if sys.platform == "win32":
                        # Windows 上尝试使用 taskkill 命令
                        try:
                            if force:
                                subprocess.run(["taskkill", "/F", "/PID", str(proc.pid)], check=True, capture_output=True)
                            else:
                                subprocess.run(["taskkill", "/PID", str(proc.pid)], check=True, capture_output=True)
                            print(f"✅ Terminated via taskkill (PID: {proc.pid})")
                        except:
                            return False
            
            # 等待进程完全关闭
            time.sleep(2)
            
            # 验证是否成功关闭
            if not self.is_warp_running():
                print("✅ Warp stopped successfully")
                return True
            else:
                print("⚠️ Some Warp processes may still be running")
                return False
                
        except Exception as e:
            print(f"❌ Error stopping Warp: {e}")
            return False
    
    def start_warp(self, wait_for_startup: bool = True) -> bool:
        """
        启动 Warp 应用
        
        Args:
            wait_for_startup: 是否等待 Warp 完全启动
            
        Returns:
            bool: 成功返回 True，失败返回 False
        """
        try:
            # 检查是否已经在运行
            if self.is_warp_running():
                print("ℹ️ Warp is already running")
                return True
            
            # 检查可执行文件路径
            if not self.warp_path:
                print("❌ Warp executable path not found")
                return False
            
            print(f"🚀 Starting Warp from: {self.warp_path}")
            
            # 启动 Warp
            if sys.platform == "win32":
                # Windows: 直接使用 Popen 启动，不需要 shell=True
                # 使用 CREATE_NEW_PROCESS_GROUP 和 DETACHED_PROCESS 标志让进程独立运行
                import subprocess
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                subprocess.Popen(
                    [self.warp_path],
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
                )
            elif sys.platform == "darwin":
                # macOS: 使用 open 命令
                subprocess.Popen(["open", "-a", "Warp"])
            else:
                # Linux: 直接后台启动
                subprocess.Popen([self.warp_path], start_new_session=True)
            
            if wait_for_startup:
                # 等待 Warp 启动
                print("⏳ Waiting for Warp to start...")
                max_wait = 30  # 最多等待30秒
                start_time = time.time()
                
                while time.time() - start_time < max_wait:
                    if self.is_warp_running():
                        print("✅ Warp started successfully")
                        time.sleep(3)  # 额外等待3秒确保完全启动
                        return True
                    time.sleep(1)
                
                print("⚠️ Warp startup timeout")
                return False
            else:
                # 不等待，直接返回
                print("✅ Warp start command executed")
                return True
                
        except Exception as e:
            print(f"❌ Error starting Warp: {e}")
            return False
    
    def restart_warp(self, wait_time: int = 3) -> bool:
        """
        重启 Warp 应用
        
        Args:
            wait_time: 停止和启动之间的等待时间（秒）
            
        Returns:
            bool: 成功返回 True，失败返回 False
        """
        try:
            print("🔄 Restarting Warp...")
            
            # 先停止
            if not self.stop_warp():
                print("❌ Failed to stop Warp")
                return False
            
            # 等待
            print(f"⏳ Waiting {wait_time} seconds before starting...")
            time.sleep(wait_time)
            
            # 再启动
            if not self.start_warp():
                print("❌ Failed to start Warp")
                return False
            
            print("✅ Warp restarted successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error restarting Warp: {e}")
            return False
    
    def get_warp_status(self) -> Dict:
        """
        获取 Warp 状态信息
        
        Returns:
            Dict: 包含运行状态、进程信息等
        """
        status = {
            'running': self.is_warp_running(),
            'executable_path': self.warp_path,
            'processes': []
        }
        
        if status['running']:
            status['processes'] = self.get_warp_processes()
            status['process_count'] = len(status['processes'])
            status['total_memory_mb'] = sum(p['memory_mb'] for p in status['processes'])
        
        return status
    
    def ensure_warp_running(self) -> bool:
        """
        确保 Warp 正在运行，如果没有运行则启动
        
        Returns:
            bool: Warp 正在运行返回 True，否则返回 False
        """
        if self.is_warp_running():
            return True
        
        print("⚠️ Warp is not running, attempting to start...")
        return self.start_warp()


# 单例实例
warp_manager = WarpProcessManager()


def test_warp_manager():
    """测试 Warp 进程管理器功能"""
    print("🧪 Testing Warp Process Manager...")
    
    manager = WarpProcessManager()
    
    # 1. 获取状态
    print("\n1️⃣ Getting Warp status:")
    status = manager.get_warp_status()
    print(f"   Running: {status['running']}")
    print(f"   Executable: {status['executable_path']}")
    if status['running']:
        print(f"   Process count: {status['process_count']}")
        print(f"   Total memory: {status['total_memory_mb']:.2f} MB")
    
    # 2. 测试停止
    if status['running']:
        print("\n2️⃣ Testing stop Warp:")
        if manager.stop_warp():
            print("   ✅ Stop test passed")
        else:
            print("   ❌ Stop test failed")
        
        time.sleep(2)
    
    # 3. 测试启动
    print("\n3️⃣ Testing start Warp:")
    if manager.start_warp():
        print("   ✅ Start test passed")
    else:
        print("   ❌ Start test failed")
    
    print("\n✅ Warp Process Manager test completed")


if __name__ == "__main__":
    test_warp_manager()
