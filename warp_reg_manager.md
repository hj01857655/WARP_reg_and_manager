# Warp账号管理器开发提示词

## 项目概述
我需要开发一个功能完整的Cloudflare Warp账号管理工具，这是一个基于PyQt5的桌面应用程序，用于管理多个Warp账号，支持自动注册、令牌刷新、流量监控、代理拦截等高级功能。该工具应该具有现代化的用户界面、稳定的后台服务和完善的安全机制。

## 技术栈要求
- **主框架**: Python 3.8+ with PyQt5 5.15+
- **数据库**: SQLite 3.x (内置)
- **网络库**: requests, urllib3, aiohttp
- **代理**: mitmproxy 8.0+
- **加密**: cryptography, hashlib
- **系统监控**: psutil, winreg (Windows)
- **UI样式**: 现代化CSS3样式 + 自定义主题
- **多线程**: QThread, asyncio

## 核心需求

### 1. 用户界面设计
- **主窗口结构**: 采用左侧边栏 + 右侧内容区的布局
- **侧边导航栏包含**:
  - 1.1 仪表板/首页 (📊 Dashboard)
  - 1.2 账号管理 (👥 Accounts) 
  - 1.3 关于页面 (ℹ️ About)
- **设计风格**: 现代化暗色主题，支持动画效果和响应式布局
- **技术栈**: PyQt5 + 现代化CSS样式

### 2. 页面功能详细设计

#### 2.1 仪表板页面 (Dashboard)
**功能要求**:
- 显示当前Warp客户端状态信息
- 读取Warp数据文件:
  - `%LOCALAPPDATA%/Warp/Warp/data/dev.warp.Warp-User` (加密文件，需要解密)
  - `%LOCALAPPDATA%/Warp/Warp/data/warp.sqlite` (数据库文件)
- 实时显示系统资源监控 (CPU、内存使用率)
- 账号统计信息 (总数、活跃数、已过期数)
- 代理服务器状态显示
- 快捷操作按钮 (添加账号、刷新所有账号等)

#### 2.2 账号管理页面 (Accounts)
**功能要求**:
- **账号列表表格**:
  - 显示字段: 邮箱、设备ID、令牌状态、流量使用情况、过期时间、状态
  - 支持排序、筛选、搜索功能
  - 实时状态指示器 (绿色=正常，黄色=警告，红色=异常)
- **账号操作功能**:
  - 添加账号 (手动输入或自动注册)
  - 删除账号 (单个或批量删除)
  - 刷新令牌 (单个或批量刷新)
  - 查看详情 (显示完整账号信息)
  - 导出账号数据 (JSON格式)
  - 复制账号信息到剪切板
- **自动化功能**:
  - 定时自动刷新令牌
  - 自动检测账号健康状态
  - 流量耗尽时自动切换账号
  - 批量注册新账号功能

#### 2.3 关于页面 (About)
**内容要求**:
- 软件版本号和更新日志
- 作者信息和联系方式
- GitHub项目链接
- Telegram频道/群组链接
- 开源许可证信息
- 系统信息 (操作系统、Python版本等)
- 技术栈和依赖库介绍

### 3. 数据存储和管理

#### 3.1 数据库设计
- **使用SQLite数据库**
- **表结构设计**:
```sql
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    device_id TEXT NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    token_expires_at INTEGER NOT NULL,
    account_data TEXT NOT NULL,  -- JSON格式存储完整账号信息
    usage_limit TEXT,            -- 流量使用情况
    next_refresh_time TEXT,      -- 下次刷新时间
    health_status TEXT DEFAULT 'healthy',  -- 健康状态
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 3.2 Warp数据文件解析
**文件位置和结构**:
```python
# Windows路径
WARP_DATA_DIR = os.path.expandvars("%LOCALAPPDATA%/Warp/Warp/data/")
WARP_USER_FILE = "dev.warp.Warp-User"  # 加密的用户数据
WARP_SQLITE_FILE = "warp.sqlite"       # SQLite数据库

# macOS路径
# ~/Library/Application Support/Warp/data/

# Linux路径  
# ~/.local/share/Warp/data/
```

**加密文件解析实现**:
```python
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def decrypt_warp_user_file(file_path: str) -> dict:
    """
    解密Warp用户数据文件
    注意: 具体的加密算法需要通过逆向工程获得
    """
    with open(file_path, 'rb') as f:
        encrypted_data = f.read()
    
    # 这里需要实现具体的解密逻辑
    # 可能使用AES或其他加密算法
    decrypted_data = decrypt_algorithm(encrypted_data)
    return json.loads(decrypted_data.decode('utf-8'))
```

**解密后JSON数据结构**:
```json
{
  "account_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "private_key": "...",
  "public_key": "...",
  "token": "...",
  "warp_enabled": true,
  "account_type": "free",
  "created": "2023-01-01T00:00:00.000Z",
  "updated": "2023-01-01T12:00:00.000Z",
  "premium_data": 0,
  "quota": 1073741824,
  "usage": 0,
  "warp_plus": false
}
```

**SQLite数据库读取**:
```python
import sqlite3

def read_warp_sqlite(db_path: str) -> list:
    """读取Warp的SQLite数据库"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查询账号信息表(具体表名需要检查)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    # 提取账号数据
    account_data = []
    for table in ['accounts', 'user_data', 'settings']:  # 常见表名
        try:
            cursor.execute(f"SELECT * FROM {table};")
            rows = cursor.fetchall()
            account_data.extend(rows)
        except sqlite3.OperationalError:
            continue
    
    conn.close()
    return account_data
```

### 4. 现代化UI设计和样式

#### 4.1 主题设计系统
**暗色主题色彩配置**:
```python
# 主题色彩定义
DARK_THEME_COLORS = {
    'primary': '#1a1b23',        # 主背景色
    'secondary': '#2d3748',      # 次要背景色  
    'accent': '#63b3ed',         # 强调色(蓝色)
    'accent_hover': '#4299e1',   # 强调色悬停
    'text_primary': '#e2e8f0',   # 主文本色
    'text_secondary': '#a0aec0', # 次要文本色
    'text_muted': '#718096',     # 弱化文本色
    'border': '#4a5568',         # 边框色
    'border_light': '#718096',   # 浅边框色
    'success': '#68d391',        # 成功色(绿色)
    'warning': '#fbb86f',        # 警告色(橙色)
    'error': '#f56565',          # 错误色(红色)
    'info': '#4fd1c7',           # 信息色(青色)
}
```

**现代化组件样式**:
```css
/* 侧边导航栏样式 */
QWidget#sidebar {
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 rgba(26, 32, 44, 0.95),
        stop: 0.3 rgba(45, 55, 72, 0.92),
        stop: 0.7 rgba(26, 32, 44, 0.95),
        stop: 1 rgba(13, 17, 23, 0.98)
    );
    border-right: 2px solid rgba(99, 179, 237, 0.3);
}

/* 现代化按钮样式 */
QPushButton.modern-button {
    background: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 rgba(45, 55, 72, 0.8),
        stop: 1 rgba(26, 32, 44, 0.8)
    );
    border: 1px solid rgba(74, 85, 104, 0.4);
    border-radius: 12px;
    color: #e2e8f0;
    padding: 8px 16px;
    font-weight: 500;
}

QPushButton.modern-button:hover {
    background: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 rgba(56, 67, 84, 0.9),
        stop: 1 rgba(37, 47, 63, 0.9)
    );
    border: 1px solid rgba(99, 179, 237, 0.6);
}

/* 表格样式 */
QTableWidget {
    background-color: rgba(45, 55, 72, 0.6);
    color: #e2e8f0;
    border: 1px solid rgba(74, 85, 104, 0.4);
    border-radius: 8px;
    selection-background-color: rgba(99, 179, 237, 0.3);
}

QHeaderView::section {
    background: rgba(26, 32, 44, 0.8);
    color: #63b3ed;
    border: 1px solid rgba(74, 85, 104, 0.4);
    padding: 8px 12px;
    font-weight: bold;
}
```

**动画效果实现**:
```python
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtWidgets import QGraphicsOpacityEffect

class AnimatedWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_animations()
    
    def setup_animations(self):
        # 渐隐渐现动画
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        
        # 移动动画  
        self.move_animation = QPropertyAnimation(self, b"geometry")
        self.move_animation.setDuration(300)
        self.move_animation.setEasingCurve(QEasingCurve.InOutQuart)
    
    def fade_in(self):
        self.opacity_animation.setDuration(200)
        self.opacity_animation.setStartValue(0)
        self.opacity_animation.setEndValue(1)
        self.opacity_animation.start()
    
    def slide_in(self, start_pos, end_pos):
        self.move_animation.setStartValue(QRect(*start_pos))
        self.move_animation.setEndValue(QRect(*end_pos))
        self.move_animation.start()
```

### 5. 网络功能和代理支持

#### 4.1 mitmproxy集成
- **功能要求**: 内置mitmproxy代理服务器
- **端口配置**: 默认使用8080端口，支持自定义
- **SSL证书**: 自动安装mitmproxy证书到系统
- **自动代理配置**: 自动设置系统代理
- **流量监控**: 监控通过代理的流量使用情况

### 4.2 Warp API接口集成
**API端点和方法**:
```python
# 主要API端点
WARP_API_BASE = "https://api.cloudflareclient.com"
REGISTER_ENDPOINT = "/v0a745/reg"  # 注册新账号
TOKEN_REFRESH_ENDPOINT = "/v0a745/reg/{account_id}/token"  # 刷新令牌
ACCOUNT_INFO_ENDPOINT = "/v0a745/reg/{account_id}"  # 账号信息
USAGE_STATS_ENDPOINT = "/v0a745/reg/{account_id}/account"  # 流量统计
```

**API调用实现要求**:
- **账号注册**: 生成随机设备ID，发送POST请求到注册端点
- **令牌刷新**: 使用refresh_token获取新的access_token
- **流量查询**: 定期获取账号的流量使用统计
- **错误处理**: 实现指数退避算法和重试机制
- **率限制**: 遵守API调用频率限制，避免被ban

**HTTP请求头配置**:
```python
HEADERS = {
    "CF-Client-Version": "a-6.30-0000",
    "Content-Type": "application/json; charset=UTF-8",
    "User-Agent": "okhttp/3.12.1",
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive"
}
```

### 5. 自动化和监控功能

#### 5.1 注册表监控
**Windows注册表监控实现**:
```python
import winreg
import threading
from typing import Callable

class WarpRegistryMonitor:
    def __init__(self, callback: Callable):
        self.callback = callback
        self.monitoring = False
        self.thread = None
        
        # Warp相关的注册表路径
        self.registry_paths = [
            r"HKEY_CURRENT_USER\Software\Cloudflare\Warp",
            r"HKEY_LOCAL_MACHINE\SOFTWARE\Cloudflare\Warp",
            r"HKEY_CURRENT_USER\Software\Classes\Local Settings\Software\Microsoft\Windows\CurrentVersion\AppModel\Repository\Packages"
        ]
    
    def start_monitoring(self):
        """开始监控注册表变更"""
        if not self.monitoring:
            self.monitoring = True
            self.thread = threading.Thread(target=self._monitor_registry)
            self.thread.daemon = True
            self.thread.start()
    
    def _monitor_registry(self):
        """监控注册表变更的主循环"""
        while self.monitoring:
            try:
                # 监控Warp相关注册表项的变更
                for path in self.registry_paths:
                    self._check_registry_changes(path)
                time.sleep(2)  # 每2秒检查一次
            except Exception as e:
                print(f"Registry monitoring error: {e}")
    
    def _check_registry_changes(self, registry_path: str):
        """检查特定注册表路径的变更"""
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                              registry_path.replace("HKEY_CURRENT_USER\\", "")) as key:
                # 读取当前值并与之前的值比较
                current_state = self._get_registry_state(key)
                if hasattr(self, '_last_state') and current_state != self._last_state:
                    self.callback(current_state)
                self._last_state = current_state
        except FileNotFoundError:
            pass  # 注册表项不存在
```

**监控目标和触发条件**:
- **Warp状态变更**: 监控Warp服务的启动/停止状态
- **配置文件变更**: 监控Warp配置文件的修改时间
- **账号切换检测**: 检测当前活跃账号的变更
- **代理设置变更**: 监控系统代理设置的变化

**自动切换逻辑**:
```python
def on_registry_change(self, registry_state: dict):
    """注册表变更回调函数"""
    if registry_state.get('warp_enabled') and not self.current_account_valid:
        # 当Warp启用但当前账号无效时，自动切换到下一个可用账号
        self.switch_to_next_available_account()
    
    elif not registry_state.get('warp_enabled'):
        # 当Warp被禁用时，暂停自动操作
        self.pause_automatic_operations()
```

#### 5.2 后台任务和定时器
- **令牌刷新任务**: 每小时检查并刷新即将过期的令牌
- **健康检查任务**: 每10分钟检查账号可用性
- **流量监控任务**: 实时监控当前账号流量使用情况
- **资源监控任务**: 监控CPU、内存使用情况

### 6. 用户体验和交互设计

#### 6.1 状态反馈
- **实时状态显示**: 在状态栏显示当前操作进度
- **通知系统**: 重要事件的弹窗通知 (账号过期、网络错误等)
- **日志系统**: 详细的操作日志记录和错误日志

#### 6.2 用户交互优化
- **键盘快捷键**: 常用操作的快捷键支持
- **右键菜单**: 表格中的右键上下文菜单
- **拖拽支持**: 支持拖拽文件导入账号数据
- **多选支持**: Ctrl+点击和Shift+点击的多选功能

### 7. 配置和设置

#### 7.1 程序设置
```json
{
  "ui": {
    "language": "zh_CN",  // 界面语言
    "theme": "dark",      // 主题风格
    "window_state": {},   // 窗口状态保存
    "auto_start": false   // 开机自启动
  },
  "proxy": {
    "enabled": true,      // 是否启用代理
    "port": 8080,         // 代理端口
    "auto_configure": true // 自动配置系统代理
  },
  "accounts": {
    "auto_refresh": true,    // 自动刷新令牌
    "refresh_interval": 3600, // 刷新间隔(秒)
    "auto_switch": true,     // 自动切换账号
    "health_check": true     // 健康检查
  },
  "advanced": {
    "log_level": "INFO",     // 日志级别
    "max_log_size": "10MB",  // 最大日志文件大小
    "backup_enabled": true   // 自动备份
  }
}
```

#### 7.2 多语言支持
- **支持语言**: 中文(简体)、英文
- **翻译文件**: JSON格式的语言包
- **动态切换**: 无需重启程序即可切换语言

### 8. 安全和隐私要求

#### 8.1 数据安全
- **本地存储**: 所有数据均在本地SQLite数据库中
- **加密存储**: 敏感信息(令牌等)采用加密存储
- **数据备份**: 支持数据库的导出和备份功能
- **安全删除**: 删除账号时确保数据不可恢复

#### 8.2 网络安全
- **HTTPS通信**: 所有API调用均使用HTTPS
- **SSL证书验证**: 严格验证服务器证书
- **代理安全**: mitmproxy的证书安装和管理
- **无数据上传**: 不向任何第三方服务器发送用户数据

### 9. 技术实现细节

#### 9.1 技术栈选型
- **GUI框架**: PyQt5 (跨平台兼容性好)
- **数据库**: SQLite (轻量级、嵌入式)
- **HTTP库**: requests + urllib3 (成熟稳定)
- **代理库**: mitmproxy (专业的HTTP代理工具)
- **加密库**: cryptography (安全加密)
- **系统监控**: psutil (系统资源监控)

#### 9.2 项目结构
```
WARP_reg_and_manager/
├── main.py                    # 主程序入口
├── requirements.txt            # 依赖列表  
├── src/                       # 源代码目录
│   ├── core/                  # 核心功能模块
│   │   └── warp_account_manager.py  # 主程序逻辑
│   ├── ui/                    # 用户界面模块
│   │   ├── sidebar_widget.py     # 侧边导航栏
│   │   ├── home_page.py          # 仪表板页面
│   │   ├── accounts_page.py      # 账号管理页面
│   │   ├── about_page.py         # 关于页面
│   │   └── ui_dialogs.py         # 对话框组件
│   ├── managers/              # 管理器模块
│   │   ├── database_manager.py   # 数据库管理
│   │   ├── warp_registry_manager.py  # 注册表监控
│   │   ├── certificate_manager.py    # SSL证书管理
│   │   └── mitmproxy_manager.py      # 代理管理
│   ├── proxy/                 # 代理功能模块  
│   │   ├── proxy_windows.py      # Windows代理配置
│   │   ├── proxy_macos.py        # macOS代理配置
│   │   └── proxy_linux.py        # Linux代理配置
│   ├── workers/               # 后台任务模块
│   │   └── background_workers.py # 后台线程任务
│   ├── utils/                 # 工具函数模块
│   │   ├── utils.py              # 通用工具
│   │   ├── account_processor.py  # 账号数据处理
│   │   └── resource_monitor.py   # 资源监控
│   └── config/                # 配置文件
│       └── languages/         # 语言包
├── assets/                    # 资源文件
│   └── styles/                # CSS样式文件
├── logs/                      # 日志文件目录
└── tests/                     # 测试文件目录
```

### 10. 开发和调试要求

#### 10.1 代码质量
- **代码规范**: 遵循 PEP 8 Python 代码规范
- **注释要求**: 关键函数和类必须有详细注释
- **异常处理**: 完善的异常捕获和错误处理
- **日志记录**: 关键操作必须有日志记录

#### 10.2 性能要求
- **应用启动**: 启动时间小于5秒
- **界面响应**: UI操作响应时间小于200ms
- **内存使用**: 空闲时内存使用小于100MB
- **数据库操作**: 单次查询时间小于100ms

### 11. 测试和发布要求

#### 11.1 测试类型
- **单元测试**: 核心功能模块的单元测试
- **集成测试**: API接口和数据库操作的集成测试
- **界面测试**: 主要界面流程的自动化测试
- **性能测试**: 大量账号数据的性能测试

#### 11.2 发布包装
- **跨平台**: 支持Windows/macOS/Linux
- **一键安装**: 提供安装包和安装脚本
- **依赖管理**: 自动处理Python依赖库安装
- **版本管理**: 支持自动更新检查和升级

## 实现优先级

### 第一阶段 - 基础功能
1. 搭建 PyQt5 基础界面框架
2. 实现侧边导航栏和页面切换
3. 实现 SQLite 数据库的账号存储功能
4. 实现账号列表显示和基本操作 (CRUD)

### 第二阶段 - 核心功能  
1. 实现 Warp 数据文件解析功能
2. 实现账号令牌刷新功能
3. 实现自动注册新账号功能
4. 实现 mitmproxy 代理功能集成

### 第三阶段 - 高级功能
1. 实现注册表监控和自动切换功能
2. 实现后台任务和定时器系统
3. 实现多语言支持和主题切换
4. 完善错误处理和日志系统

### 第四阶段 - 优化和发布
1. 性能优化和用户体验改进
2. 添加完善的测试用例
3. 完善文档和帮助系统
4. 打包和发布版本

## 开发最佳实践

### 代码组织和架构模式

#### MVC架构模式实现
```python
# Model - 数据模型
class AccountModel:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.accounts = []
    
    def get_all_accounts(self) -> List[WarpAccount]:
        return self.db_manager.get_accounts()
    
    def add_account(self, account: WarpAccount) -> bool:
        return self.db_manager.insert_account(account)

# View - 用户界面  
class AccountView(QWidget):
    account_selected = pyqtSignal(str)  # account_id
    account_action_requested = pyqtSignal(str, str)  # action, account_id
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def update_account_list(self, accounts: List[WarpAccount]):
        # 更新界面显示
        pass

# Controller - 业务逻辑
class AccountController:
    def __init__(self, model: AccountModel, view: AccountView):
        self.model = model
        self.view = view
        self.connect_signals()
    
    def connect_signals(self):
        self.view.account_action_requested.connect(self.handle_account_action)
    
    def handle_account_action(self, action: str, account_id: str):
        if action == 'refresh_token':
            self.refresh_account_token(account_id)
        elif action == 'delete':
            self.delete_account(account_id)
```

#### 单例模式和资源管理
```python
class DatabaseManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, db_path: str):
        if not hasattr(self, 'initialized'):
            self.db_path = db_path
            self.connection = None
            self.initialized = True
    
    def get_connection(self) -> sqlite3.Connection:
        if not self.connection:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.execute("PRAGMA foreign_keys = ON")
        return self.connection
    
    def __del__(self):
        if self.connection:
            self.connection.close()
```

### 错误处理和日志系统

#### 统一异常处理
```python
import logging
from functools import wraps
from typing import Callable, Any

# 自定义异常类
class WarpAccountError(Exception):
    """Warp账号相关错误"""
    pass

class WarpAPIError(WarpAccountError):
    """Warp API调用错误"""
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code

class WarpConfigError(WarpAccountError):
    """Warp配置错误"""
    pass

# 装饰器用于统一异常处理
def handle_exceptions(logger: logging.Logger = None):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except WarpAPIError as e:
                if logger:
                    logger.error(f"API error in {func.__name__}: {e} (status: {e.status_code})")
                raise
            except WarpAccountError as e:
                if logger:
                    logger.error(f"Account error in {func.__name__}: {e}")
                raise
            except Exception as e:
                if logger:
                    logger.exception(f"Unexpected error in {func.__name__}: {e}")
                raise WarpAccountError(f"Unexpected error: {str(e)}") from e
        return wrapper
    return decorator
```

#### 结构化日志系统
```python
import logging
import logging.handlers
from pathlib import Path

class WarpLogger:
    def __init__(self, name: str, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # 创建日志器
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # 清理既有的处理器
        self.logger.handlers.clear()
        
        # 设置格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 文件处理器 - 主日志
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / f"{name}.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # 错误日志处理器
        error_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / f"{name}_error.log",
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)
        
        # 控制台处理器(只在开发模式下)
        if self._is_debug_mode():
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
    
    def _is_debug_mode(self) -> bool:
        return Path("debug.txt").exists()
    
    def get_logger(self) -> logging.Logger:
        return self.logger
```

### 性能优化和线程管理

#### 异步任务处理
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from PyQt5.QtCore import QThread, QObject, pyqtSignal

class AsyncTaskManager(QObject):
    task_completed = pyqtSignal(str, object)  # task_id, result
    task_failed = pyqtSignal(str, str)        # task_id, error_message
    
    def __init__(self, max_workers: int = 5):
        super().__init__()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.running_tasks = {}
    
    def submit_task(self, task_id: str, func: Callable, *args, **kwargs):
        """提交异步任务"""
        future = self.executor.submit(self._run_task, task_id, func, *args, **kwargs)
        self.running_tasks[task_id] = future
        return future
    
    def _run_task(self, task_id: str, func: Callable, *args, **kwargs):
        """运行任务并发送信号"""
        try:
            result = func(*args, **kwargs)
            self.task_completed.emit(task_id, result)
            return result
        except Exception as e:
            self.task_failed.emit(task_id, str(e))
            raise
        finally:
            self.running_tasks.pop(task_id, None)
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        if task_id in self.running_tasks:
            return self.running_tasks[task_id].cancel()
        return False
    
    def shutdown(self):
        """关闭任务管理器"""
        self.executor.shutdown(wait=True)
```

#### 缓存机制和数据优化
```python
from functools import lru_cache, wraps
import time
from typing import Dict, Any, Optional

class DataCache:
    def __init__(self, ttl: int = 300):  # 5分钟缓存
        self.ttl = ttl
        self.cache: Dict[str, Dict[str, Any]] = {}
    
    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            data = self.cache[key]
            if time.time() - data['timestamp'] < self.ttl:
                return data['value']
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        self.cache[key] = {
            'value': value,
            'timestamp': time.time()
        }
    
    def clear(self):
        self.cache.clear()

# 缓存装饰器
def cached(ttl: int = 300):
    cache = DataCache(ttl)
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # 检查缓存
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            return result
        
        wrapper.clear_cache = cache.clear
        return wrapper
    return decorator
```

### 单元测试和质量保证

#### 测试框架设置
```python
import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from src.managers.database_manager import DatabaseManager
from src.core.warp_account import WarpAccount

class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        """Setup test database"""
        self.test_db_fd, self.test_db_path = tempfile.mkstemp()
        self.db_manager = DatabaseManager(self.test_db_path)
        self.db_manager.create_tables()
    
    def tearDown(self):
        """Cleanup test database"""
        os.close(self.test_db_fd)
        os.unlink(self.test_db_path)
    
    def test_insert_account(self):
        """Test account insertion"""
        account = WarpAccount(
            email="test@example.com",
            device_id="test-device-123",
            access_token="test-token",
            refresh_token="test-refresh"
        )
        
        result = self.db_manager.insert_account(account)
        self.assertTrue(result)
        
        # 验证插入结果
        accounts = self.db_manager.get_accounts()
        self.assertEqual(len(accounts), 1)
        self.assertEqual(accounts[0].email, "test@example.com")
    
    @patch('requests.post')
    def test_api_call_retry(self, mock_post):
        """Test API retry mechanism"""
        # 模拟网络错误
        mock_post.side_effect = [requests.RequestException(), Mock(status_code=200)]
        
        # 测试API调用重试
        result = api_call_with_retry("https://api.example.com", {})
        
        # 验证重试次数
        self.assertEqual(mock_post.call_count, 2)
```

#### 性能测试和基准测试
```python
import time
import psutil
from memory_profiler import profile

class PerformanceMonitor:
    def __init__(self):
        self.start_time = None
        self.start_memory = None
    
    def start_monitoring(self):
        self.start_time = time.time()
        self.start_memory = psutil.Process().memory_info().rss
    
    def get_metrics(self) -> dict:
        current_time = time.time()
        current_memory = psutil.Process().memory_info().rss
        
        return {
            'execution_time': current_time - self.start_time,
            'memory_usage': current_memory - self.start_memory,
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent
        }

# 性能测试用例
def test_large_dataset_performance():
    """Test performance with large dataset"""
    monitor = PerformanceMonitor()
    monitor.start_monitoring()
    
    # 创建大量测试数据
    db_manager = DatabaseManager(":memory:")
    accounts = [create_test_account(i) for i in range(1000)]
    
    # 测试批量插入性能
    start_time = time.time()
    for account in accounts:
        db_manager.insert_account(account)
    
    metrics = monitor.get_metrics()
    
    # 断言性能指标
    assert metrics['execution_time'] < 5.0  # 小于5秒
    assert metrics['memory_usage'] < 100 * 1024 * 1024  # 小于100MB
```

### 打包和部署

#### 使用PyInstaller打包
```python
# build.py - 打包脚本
import PyInstaller.__main__
import shutil
import os
from pathlib import Path

def build_application():
    # 清理之前的构建
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    # PyInstaller配置
    args = [
        'main.py',
        '--name=WarpAccountManager',
        '--windowed',
        '--onefile',
        '--icon=assets/icon.ico',
        '--add-data=src;src',
        '--add-data=assets;assets',
        '--hidden-import=PyQt5.sip',
        '--hidden-import=mitmproxy',
        '--exclude-module=tkinter',
        '--clean',
        '--noconfirm'
    ]
    
    PyInstaller.__main__.run(args)
    
    print("Build completed successfully!")
    print(f"Executable: {Path('dist/WarpAccountManager.exe').absolute()}")

if __name__ == "__main__":
    build_application()
```

#### 自动更新系统
```python
import requests
import json
from packaging import version
from PyQt5.QtWidgets import QMessageBox

class UpdateChecker:
    def __init__(self, current_version: str, update_url: str):
        self.current_version = current_version
        self.update_url = update_url
    
    def check_for_updates(self) -> dict:
        """Check for application updates"""
        try:
            response = requests.get(self.update_url, timeout=10)
            response.raise_for_status()
            
            update_info = response.json()
            latest_version = update_info.get('version')
            
            if version.parse(latest_version) > version.parse(self.current_version):
                return {
                    'update_available': True,
                    'latest_version': latest_version,
                    'download_url': update_info.get('download_url'),
                    'changelog': update_info.get('changelog', [])
                }
            
            return {'update_available': False}
            
        except Exception as e:
            print(f"Update check failed: {e}")
            return {'update_available': False, 'error': str(e)}
    
    def prompt_user_for_update(self, update_info: dict) -> bool:
        """Prompt user to download update"""
        changelog = '\n'.join(update_info.get('changelog', []))
        
        msg = QMessageBox()
        msg.setWindowTitle("更新可用")
        msg.setText(f"新版本 {update_info['latest_version']} 可用！")
        msg.setDetailedText(f"更新内容：\n{changelog}")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.Yes)
        
        return msg.exec_() == QMessageBox.Yes
```

## 安全性和合规性考虑

### 数据保护和隐私
- **本地存储**: 所有敏感数据仅在本地存储，不上传到任何云服务
- **数据加密**: 使用强加密算法保护用户凭据和令牌
- **数据清理**: 实现安全删除功能，确保数据不可恢复
- **访问控制**: 支持主密码保护和数据库加密

### 网络安全
- **HTTPS验证**: 所有网络请求均使用HTTPS并验证SSL证书
- **代理安全**: mitmproxy证书的安全管理和自动清理
- **API限流**: 遵守Cloudflare API的速率限制，避免被ban
- **错误处理**: 不在日志中记录敏感信息

### 法律合规
- **使用声明**: 明确说明工具的使用目的和限制
- **责任免责**: 明确开发者和用户的责任范围
- **开源许可**: 采用MIT或Apache 2.0等合适的开源许可证
- **用户协议**: 要求用户遵守Cloudflare的服务条款

---

**注意**: 这个提示词文档为开发Warp账号管理工具提供了全面的指导。请根据具体需求和技术环境进行调整和优化。在开发过程中，请确保遵守相关的法律法规和服务条款。

## 🖼️ 界面预览

### 主界面
```
┌─────────────────────────────────────────────────────────────┐
│ 🚀 Warp Manager                                    [─][□][×] │
├──────────────┬──────────────────────────────────────────────┤
│ 📊 Dashboard │                                              │
│ 👥 Accounts  │            主要内容区域                        │
│ ℹ️  About    │                                              │
│              │                                              │
│ ➕ Add Acc   │                                              │
│ 🔄 Refresh   │                                              │
│              │                                              │
│ 🟢 Ready     │                                              │
│ v2.0.0       │                                              │
└──────────────┴──────────────────────────────────────────────┘
```

### 账号列表视图
- 📋 详细的账号信息表格
- 🎯 实时状态指示器
- 📊 流量使用进度条
- 🔧 快捷操作按钮

## 🔧 安装要求

### 系统要求
- **操作系统**: Windows 10+ / macOS 10.14+ / Linux Ubuntu 18.04+
- **Python**: 3.8 或更高版本
- **内存**: 最少 512MB RAM
- **存储**: 100MB 可用空间

### 依赖库
```bash
# 核心依赖
PyQt5>=5.15.0
requests>=2.25.0
psutil>=5.8.0
sqlite3  # Python内置

# 可选依赖
mitmproxy>=8.0.0    # 代理功能
cryptography>=3.0.0 # 加密功能
```

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/hj01857655/WARP_reg_and_manager.git
cd WARP_reg_and_manager
```

### 2. 安装依赖
```bash
# 使用pip安装
pip install -r requirements.txt

# 或者使用conda
conda install --file requirements.txt
```

### 3. 运行程序
```bash
# 直接运行
python main.py

# 或者以模块方式运行
python -m src.core.warp_account_manager
```

### 4. 首次设置
1. 启动程序后，会自动检测Warp客户端
2. 如果需要代理功能，程序会引导安装SSL证书
3. 添加第一个账号或批量导入现有账号

## 📖 使用指南

### 🏠 仪表板页面
仪表板提供系统概览信息：
- 📊 **账号统计** - 总账号数、活跃账号、过期账号
- 🌐 **网络状态** - 当前代理状态、连接质量
- 💾 **系统信息** - CPU、内存使用情况
- 📈 **流量统计** - 今日使用量、历史趋势

### 👥 账号管理页面

#### 添加账号
1. 点击 `添加账号` 按钮
2. 选择添加方式：
   - **手动添加**: 输入账号信息
   - **自动注册**: 批量生成新账号
   - **导入文件**: 从JSON/CSV文件导入

#### 账号操作
- 🔄 **刷新令牌** - 手动刷新账号令牌
- 📊 **查看详情** - 查看完整账号信息
- 🗑️ **删除账号** - 移除不需要的账号
- 📋 **复制信息** - 快速复制账号数据

#### 批量操作
- ✅ **批量选择** - 使用复选框选择多个账号
- 🔄 **批量刷新** - 一次性刷新多个账号
- 📤 **批量导出** - 导出选中账号数据
- 🗑️ **批量删除** - 删除多个账号

### ⚙️ 设置页面
- 🌐 **语言设置** - 切换界面语言
- 🎨 **主题设置** - 自定义界面主题
- 🔧 **代理配置** - 配置代理服务器
- 📱 **通知设置** - 设置提醒和通知

## ⚙️ 配置说明

### 配置文件位置
```
应用程序目录/
├── config/
│   ├── settings.json      # 主要设置
│   ├── accounts.db        # 账号数据库
│   └── languages/         # 语言文件
├── logs/                  # 日志文件
└── temp/                  # 临时文件
```

### 主要配置项
```json
{
  "ui": {
    "language": "zh_CN",
    "theme": "dark",
    "auto_start": false
  },
  "proxy": {
    "enabled": true,
    "port": 8080,
    "auto_configure": true
  },
  "accounts": {
    "auto_refresh": true,
    "refresh_interval": 3600,
    "auto_switch": true
  }
}
```

## 🔒 安全说明

### 数据安全
- 🔐 所有账号数据均在本地加密存储
- 🚫 不会向任何第三方服务器发送数据
- 🔒 支持数据库密码保护
- 🗑️ 安全删除功能确保数据无法恢复

### 网络安全
- 🛡️ 使用HTTPS进行所有网络通信
- 🔒 SSL证书验证确保连接安全
- 🚫 不收集任何用户行为数据
- 🔐 支持代理加密传输

### 使用建议
- 📱 定期备份账号数据
- 🔄 及时更新程序版本
- 🚫 不要在公共计算机上使用
- 🔒 设置强密码保护数据库

## 🐛 故障排除

### 常见问题

#### Q: 程序无法启动
**A**: 检查Python版本和依赖是否正确安装
```bash
python --version  # 确保版本 >= 3.8
pip list | grep PyQt5  # 检查PyQt5是否安装
```

#### Q: 无法检测到Warp客户端
**A**: 确保Warp客户端已正确安装并运行
- Windows: 检查 `%LOCALAPPDATA%\Warp\` 目录
- macOS: 检查 `~/Library/Application Support/Warp/` 目录
- Linux: 检查 `~/.local/share/Warp/` 目录

#### Q: 代理功能无法使用
**A**: 
1. 确保mitmproxy已正确安装
2. 检查防火墙设置
3. 安装SSL证书到系统证书存储

#### Q: 账号令牌频繁失效
**A**: 
1. 检查系统时间是否准确
2. 确保网络连接稳定
3. 适当增加刷新间隔

### 日志文件
日志文件位于 `logs/` 目录下：
- `app.log` - 主程序日志
- `proxy.log` - 代理服务日志
- `error.log` - 错误日志

### 获取帮助
如果遇到问题，可以：
1. 查看日志文件获取详细错误信息
2. 在GitHub Issues中搜索相似问题
3. 提交新的Issue并附带日志信息

## 🤝 贡献指南

我们欢迎任何形式的贡献！

### 贡献方式
- 🐛 **报告Bug** - 提交Issue描述问题
- 💡 **功能建议** - 提出新功能想法
- 📝 **文档改进** - 完善文档和说明
- 💻 **代码贡献** - 提交Pull Request

### 开发环境设置
```bash
# 1. Fork项目到你的GitHub账号
# 2. 克隆你的fork
git clone https://github.com/YOUR_USERNAME/WARP_reg_and_manager.git

# 3. 创建开发分支
git checkout -b feature/your-feature-name

# 4. 安装开发依赖
pip install -r requirements-dev.txt

# 5. 运行测试
python -m pytest tests/
```

### 代码规范
- 使用 **Black** 进行代码格式化
- 遵循 **PEP 8** 编码规范
- 添加必要的注释和文档字符串
- 编写单元测试覆盖新功能

## 📊 技术架构

### 项目结构
```
WARP_reg_and_manager/
├── src/                    # 源代码目录
│   ├── core/              # 核心功能模块
│   │   └── warp_account_manager.py
│   ├── ui/                # 用户界面模块
│   │   ├── sidebar_widget.py
│   │   ├── home_page.py
│   │   └── about_page.py
│   ├── managers/          # 管理器模块
│   │   ├── database_manager.py
│   │   └── warp_registry_manager.py
│   ├── proxy/             # 代理功能模块
│   ├── utils/             # 工具函数
│   └── config/            # 配置文件
├── tests/                 # 测试文件
├── docs/                  # 文档
├── requirements.txt       # 依赖列表
└── main.py               # 主程序入口
```

### 技术栈
- **GUI框架**: PyQt5
- **数据库**: SQLite
- **网络请求**: requests
- **加密**: cryptography
- **代理**: mitmproxy
- **系统监控**: psutil

## 📱 联系方式

- **GitHub**: [hj01857655/WARP_reg_and_manager](https://github.com/hj01857655/WARP_reg_and_manager)
- **Telegram频道**: [@warp5215](https://t.me/warp5215)
- **Telegram群组**: [@warp1215](https://t.me/warp1215)

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

感谢以下项目和贡献者：
- **PyQt5** - 优秀的Python GUI框架
- **mitmproxy** - 强大的代理工具
- **所有贡献者** - 感谢每一个提交代码、报告问题、提出建议的人
- **用户社区** - 感谢使用和反馈，让项目变得更好

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给我们一个Star！**

*让我们一起构建更好的Warp账号管理工具！* 🚀

</div>
