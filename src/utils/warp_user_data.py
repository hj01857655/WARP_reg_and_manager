#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Warp User Data Manager - DPAPI加解密Warp用户数据
"""

import os
import json
from pathlib import Path
from typing import Dict, Any

# Windows DPAPI
import win32crypt


class WarpUserDataManager:
    """Warp用户数据管理器 - 仅DPAPI加解密功能"""

    def __init__(self):
        self.warp_data_dir = Path(os.path.expandvars(r"%LOCALAPPDATA%\warp\Warp\data"))
        self.user_file = self.warp_data_dir / "dev.warp.Warp-User"

    def encrypt_user_data(self, data: Dict[str, Any]) -> bytes:
        """使用DPAPI加密用户数据"""
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        json_bytes = json_str.encode('utf-8')
        encrypted_data = win32crypt.CryptProtectData(json_bytes, None, None, None, None, 0)
        return encrypted_data

    def decrypt_user_data(self, encrypted_data: bytes) -> Dict[str, Any]:
        """使用DPAPI解密Warp用户数据"""
        decrypted_data = win32crypt.CryptUnprotectData(encrypted_data, None, None, None, 0)
        json_str = decrypted_data[1].decode('utf-8')
        return json.loads(json_str)

    def read_user_file(self) -> Dict[str, Any]:
        """读取并解密Warp用户文件"""
        with open(self.user_file, 'rb') as f:
            encrypted_data = f.read()
        return self.decrypt_user_data(encrypted_data)

    def write_user_file(self, data: Dict[str, Any]) -> None:
        """加密并写入Warp用户文件"""
        encrypted_data = self.encrypt_user_data(data)
        with open(self.user_file, 'wb') as f:
            f.write(encrypted_data)
