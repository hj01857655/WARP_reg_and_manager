# Warp Terminal账号管理器项目文档

## 项目概述
基于PyQt5开发的现代化Warp Terminal账号管理工具，支持多账号管理、配置备份、设备同步等功能。项目采用模块化架构设计，具备完整的主题管理系统和现代化UI界面。

## 技术栈实现
- **主框架**: Python 3.9+ with PyQt5 5.15+
- **数据库**: SQLite 3.35+ (账号数据存储)
- **网络库**: requests, httpx (HTTP客户端)
- **配置管理**: json, configparser
- **加密**: base64, hashlib (数据安全)
- **代理管理**: mitmproxy集成
- **异步处理**: QThread (UI响应性)
- **UI系统**: 自定义主题管理器 + 现代化QSS样式

## 项目结构
```
WARP_reg_and_manager/
├── src/
│   ├── config/              # 配置管理
│   │   ├── languages.py     # 多语言支持
│   │   └── settings.py      # 应用设置
│   ├── core/                # 核心功能
│   │   ├── warp_account_manager.py  # 主窗口和账号管理核心
│   │   └── account_validator.py    # 账号验证
│   ├── managers/            # 业务管理器
│   │   ├── account_manager.py      # 账号管理逻辑
│   │   ├── database_manager.py     # 数据库操作
│   │   └── license_manager.py      # 许可证管理
│   ├── proxy/               # 代理系统
│   │   ├── proxy_windows.py        # Windows代理
│   │   ├── proxy_macos.py          # macOS代理
│   │   └── proxy_linux.py          # Linux代理
│   ├── ui/                  # 用户界面
│   │   ├── theme_manager.py        # 主题管理器
│   │   ├── home_page.py            # 仪表板页面
│   │   ├── account_card_page.py    # 账号管理页面
│   │   ├── about_page.py           # 关于页面
│   │   ├── cleanup_page.py         # 清理工具页面
│   │   ├── sidebar.py              # 侧边导航栏
│   │   └── ui_dialogs.py           # 对话框组件
│   ├── utils/               # 工具模块
│   │   ├── warp_user_data.py       # Warp用户数据解析
│   │   ├── account_processor.py    # 账号处理工具
│   │   └── system_info.py          # 系统信息获取
│   └── workers/             # 后台线程
│       ├── account_worker.py       # 账号操作线程
│       └── proxy_worker.py         # 代理操作线程
├── main.py                  # 应用入口
├── requirements.txt         # 依赖清单
└── pyproject.toml          # 项目配置
```

## 已实现的功能模块

### 1. 用户界面系统

#### 1.1 主窗口架构
- **左右分割布局**: 左侧边栏 + 右侧内容区
- **响应式设计**: 可拉伸分割器，支持侧边栏收缩
- **现代化导航**: 图标 + 文字的导航项，支持鼠标悬停效果

#### 1.2 主题管理系统
- **统一主题变量**: `theme_manager.py`提供全局颜色管理
- **动态样式生成**: 支持不同类型的按钮、卡片和组件样式
- **圆角设计**: 所有QLabel和组件都使用圆角，消除直角外框
- **语义化颜色**: 基于功能的颜色命名 (primary, success, warning, danger)

### 2. 页面功能实现

#### 2.1 仪表板页面 (home_page.py)
- **系统状态卡片**: 实时显示系统信息和资源使用情况
- **Warp用户信息**: 鱼抛 Warp Terminal 用户数据并显示
- **账号概览**: 当前登录账号的基本信息和状态
- **快捷操作**: 一键跳转到账号管理、刷新、添加账号等
- **实时时间**: 动态显示当前时间和日期

#### 2.2 账号管理页面 (account_card_page.py)
- **表格式显示**: 现代化表格显示所有账号信息
- **批量操作**: 支持全选/部分选择和批量删除
- **实时状态**: 显示账号在线状态、使用量、过期时间
- **快捷操作**: 表格内直接支持启动、刷新、编辑、删除
- **统一按钮样式**: 所有表格内按钮使用主题管理器的样式

#### 2.3 关于页面 (about_page.py)
- **应用信息**: 版本、更新日志、功能介绍
- **技术栈信息**: 使用的技术和依赖库
- **系统信息**: 操作系统、Python环境、应用运行信息
- **外部链接**: GitHub仓库、Telegram群组等快捷访问
- **许可信息**: MIT许可证和使用声明

#### 2.4 清理工具页面 (cleanup_page.py)
- **登录状态检查**: 检查并显示当前登录状态
- **数据清理**: 支持清理本地配置和缓存数据
- **批量操作**: 可一键清理多个目录和文件

### 3. 数据管理系统

#### 3.1 账号管理器 (account_manager.py)
- **SQLite数据库**: 本地存储账号信息和配置
- **CRUD操作**: 完整的账号增删改查功能
- **数据加密**: 敏感信息采用base64简单加密
- **账号切换**: 支持一键切换到指定账号

#### 3.2 数据库结构
```sql
CREATE TABLE accounts (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL,
    license_key TEXT,
    private_key TEXT,
    account_id TEXT,
    account_token TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 0
);
```

### 4. 系统集成功能

#### 4.1 Warp用户数据解析 (warp_user_data.py)
- **配置文件读取**: 解析Warp Terminal的本地配置
- **用户信息提取**: 获取当前登录用户的详细信息
- **跨平台支持**: Windows/macOS/Linux配置目录自动识别

#### 4.2 代理系统集成
- **多平台代理**: Windows/macOS/Linux各自的代理设置管理
- **mitmproxy集成**: 支持启动和管理mitmproxy服务
- **自动配置**: 一键设置系统代理和恢复

#### 4.3 多语言支持 (languages.py)
- **国际化框架**: 支持中英文切换
- **动态加载**: 语言切换无需重启应用
- **完整翻译**: 所有UI文本都支持多语言

## 核心代码示例

### 1. 主题管理器实现

```python
# src/ui/theme_manager.py - 主题管理器核心代码
class ThemeManager:
    """主题管理器 - 提供动态主题变量"""
    
    def __init__(self, theme_name="light"):
        self.theme_name = theme_name
        self._load_theme_variables()
    
    def _load_light_theme(self):
        """加载亮色主题变量"""
        self.colors = {
            # 背景色
            'background_primary': '#ffffff',
            'background_secondary': '#f8fafc',
            'background_tertiary': '#f1f5f9',
            
            # 文字颜色
            'text_primary': '#1e293b',
            'text_secondary': '#64748b',
            'text_muted': '#94a3b8',
            
            # 强调色
            'accent_blue': '#3b82f6',
            'accent_green': '#10b981',
            'accent_orange': '#f59e0b',
            'accent_red': '#ef4444',
        }
    
    def get_button_style(self, button_type='primary'):
        """获取按钮样式"""
        if button_type == 'primary':
            return f"""
                QPushButton {{
                    background: qlineargradient(
                        x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 {self.colors['accent_blue']},
                        stop: 1 #2563eb
                    );
                    color: white;
                    border: 1px solid rgba(59, 130, 246, 0.3);
                    border-radius: 10px;
                    padding: 8px 16px;
                }}
            """
    
    def get_table_button_style(self, button_type='primary'):
        """获取表格内按钮样式"""
        base_style = """
            QPushButton {
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                font-weight: 500;
                min-width: 32px;
                min-height: 32px;
            }
        """
        
        if button_type == 'success':  # 启动按钮
            return base_style + f"""
            QPushButton {{
                background-color: {self.colors['accent_green']};
                color: white;
            }}
            QPushButton:hover {{
                background-color: #059669;
            }}
            """

# 全局主题管理器实例
theme_manager = ThemeManager("light")
```

### 2. 账号管理器实现

```python
# src/managers/account_manager.py - 账号管理核心功能
class AccountManager:
    """账号管理器 - 负责账号的CRUD操作"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.current_account = None
    
    def add_account_data(self, account_data):
        """添加账号数据"""
        try:
            # 加密敏感信息
            encrypted_data = {
                'email': account_data.get('email'),
                'license_key': self._encrypt_data(account_data.get('license_key', '')),
                'private_key': self._encrypt_data(account_data.get('private_key', '')),
                'account_id': account_data.get('account_id', ''),
                'account_token': self._encrypt_data(account_data.get('account_token', ''))
            }
            
            return self.db_manager.add_account(encrypted_data)
        except Exception as e:
            print(f"添加账号失败: {e}")
            return False
    
    def get_accounts_with_health_and_limits(self):
        """获取带有健康状态和限制信息的账号列表"""
        accounts = self.db_manager.get_all_accounts()
        enhanced_accounts = []
        
        for account in accounts:
            # 解密敏感数据
            account['license_key'] = self._decrypt_data(account.get('license_key', ''))
            account['private_key'] = self._decrypt_data(account.get('private_key', ''))
            account['account_token'] = self._decrypt_data(account.get('account_token', ''))
            
            # 添加状态信息
            account['status'] = self._get_account_status(account)
            account['usage'] = self._get_account_usage(account)
            account['limit'] = '2500'  # 默认限制
            account['expiry'] = self._get_account_expiry(account)
            
            enhanced_accounts.append(account)
        
        return enhanced_accounts
    
    def switch_account(self, account_id):
        """切换到指定账号"""
        try:
            # 获取账号信息
            account = self.db_manager.get_account_by_id(account_id)
            if not account:
                return False
            
            # 更新活跃状态
            self.db_manager.set_active_account(account_id)
            self.current_account = account
            
            print(f"✅ 已切换到账号: {account['email']}")
            return True
        except Exception as e:
            print(f"切换账号失败: {e}")
            return False
```

### 3. UI组件实现

```python
# src/ui/account_card_page.py - 账号管理页面核心代码
class AccountCardPage(QWidget):
    """账号管理页面 - 表格式显示和管理账号"""
    
    def create_table_view(self):
        """创建表格视图"""
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(6)  # 选择, 邮箱, 状态, 限制, 账户过期, 操作
        self.table_widget.setHorizontalHeaderLabels([
            '', '邮箱', '状态', '限制', '账户过期', '操作'
        ])
        
        # 现代化表格样式
        self.table_widget.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                gridline-color: #f0f0f0;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                color: #495057;
                padding: 12px 8px;
                border: none;
                border-bottom: 2px solid #dee2e6;
                font-weight: bold;
            }
        """)
    
    def update_table_view(self):
        """更新表格视图数据"""
        accounts = self.account_manager.get_accounts_with_health_and_limits()
        self.table_widget.setRowCount(len(accounts))
        
        for row, account in enumerate(accounts):
            # 操作按钮组
            action_widget = QWidget()
            action_layout = QHBoxLayout()
            
            # 使用主题管理器的统一样式
            start_btn = QPushButton("🚀")
            start_btn.setStyleSheet(theme_manager.get_table_button_style('success'))
            start_btn.clicked.connect(lambda checked, acc=account: self.start_account(acc))
            
            refresh_btn = QPushButton("🔄")
            refresh_btn.setStyleSheet(theme_manager.get_table_button_style('primary'))
            refresh_btn.clicked.connect(lambda checked, acc=account: self.refresh_account(acc))
            
            action_layout.addWidget(start_btn)
            action_layout.addWidget(refresh_btn)
            action_widget.setLayout(action_layout)
            
            self.table_widget.setCellWidget(row, 5, action_widget)
```

### 4. Warp数据解析实现

```python
# src/utils/warp_user_data.py - Warp用户数据解析
class WarpUserDataManager:
    """管理和解析 Warp Terminal 的用户数据"""
    
    def __init__(self):
        self.config_dir = self._get_warp_config_dir()
    
    def _get_warp_config_dir(self):
        """获取Warp配置目录"""
        import platform
        import os
        
        system = platform.system()
        if system == "Windows":
            return os.path.join(os.environ.get('APPDATA', ''), 'warp-terminal')
        elif system == "Darwin":  # macOS
            return os.path.expanduser('~/Library/Application Support/dev.warp.Warp-Stable')
        else:  # Linux
            return os.path.expanduser('~/.config/warp-terminal')
    
    def get_current_user_data(self):
        """获取当前用户数据"""
        try:
            user_file = os.path.join(self.config_dir, 'user_preferences.json')
            if os.path.exists(user_file):
                with open(user_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return {
                        'email': data.get('email', 'Unknown'),
                        'user_id': data.get('user_id', 'N/A'),
                        'subscription': data.get('subscription_type', 'Free'),
                        'login_status': '已登录' if data.get('is_logged_in') else '未登录'
                    }
        except Exception as e:
            print(f"读取Warp用户数据失败: {e}")
        
        return {
            'email': 'Unknown',
            'user_id': 'N/A', 
            'subscription': 'Free',
            'login_status': '未知'
        }
```

## 开发进度和路线图

### 已完成的功能 (✅)

#### 第一阶段 - 基础架构
- ✅ PyQt5基础框架搭建
- ✅ 模块化项目结构设计
- ✅ SQLite数据库和账号CRUD操作
- ✅ 基础UI界面和导航系统
- ✅ 多语言支持框架

#### 第二阶段 - 核心功能
- ✅ 主题管理系统实现
- ✅ 账号管理和切换功能
- ✅ Warp用户数据解析
- ✅ 表格式账号显示和操作
- ✅ 批量操作功能

#### 第三阶段 - UI优化
- ✅ 现代化界面设计
- ✅ 统一的按钮和组件样式
- ✅ 圆角设计和无直角外框
- ✅ 响应式布局和动态尺寸
- ✅ 实时状态显示和更新

### 正在开发的功能 (🚧)
- 🚧 账号导入导出功能
- 🚧 配置备份和恢复
- 🚧 代理系统集成优化

### 计划中的功能 (📝)
- 📝 账号健康状态监控
- 📝 自动切换和调度
- 📝 日志系统和错误处理
- 📝 配置文件监控和同步
- 📝 性能优化和内存管理

## 技术亮点

### 1. 模块化架构设计
- **分层清晰**: UI层、业务层、数据层分离
- **低耦合高内聚**: 每个模块责任单一，接口清晰
- **易于扩展**: 新功能添加不影响现有模块

### 2. 主题管理系统
- **统一样式管理**: 所有组件样式集中管理
- **动态生成**: 根据不同主题变量生成样式
- **易于维护**: 修改样式无需遍历所有文件

### 3. 数据安全
- **加密存储**: 敏感信息在本地加密存储
- **无云端依赖**: 所有数据本地存储，保证隐私
- **安全隔离**: 账号数据独立存储，互不影响

### 4. 用户体验
- **现代化界面**: 符合现代设计语言的UI
- **响应式设计**: 适配不同屏幕尺寸
- **操作简单**: 一键操作，减少用户学习成本

## 性能指标

### 当前性能表现
- **启动时间**: < 2秒
- **内存占用**: < 50MB
- **响应速度**: UI操作 < 100ms
- **数据库操作**: < 50ms

### 目标性能
- **支持账号数量**: 1000+
- **并发操作**: 支持多线程并发
- **内存优化**: 长时间运行稳定

## 使用说明

### 安装和运行

```bash
# 克隆项目
git clone https://github.com/hj01857655/WARP_reg_and_manager.git
cd WARP_reg_and_manager

# 安装依赖
pip install -r requirements.txt

# 运行应用
python main.py
```

### 主要功能使用

#### 1. 账号管理
- 点击左侧导航栏的“账号管理”
- 使用“添加账号”按钮添加新账号
- 在表格中直接操作账号（启动、刷新、编辑、删除）
- 支持批量选择和批量删除

#### 2. 仪表板查看
- 在仪表板页面查看系统状态
- 实时显示Warp Terminal用户信息
- 使用快捷操作按钮进行常用操作

#### 3. 账号切换
- 在账号管理页面点击账号行的“启动”按钮
- 系统会自动切换到该账号
- 在仪表板可以看到当前活跃账号信息

### 注意事项
- 确保已安装Warp Terminal
- 首次使用需要手动添加账号信息
- 账号数据加密存储在本地，请定期备份

## 贡献指南

### 参与开发
1. Fork 项目到你的 GitHub 账号
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的修改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 发起 Pull Request

### 代码规范
- 遵循 PEP 8 代码规范
- 使用有意义的变量和函数名
- 添加必要的注释和文档字符串
- 在提交前运行测试确保功能正常

## 许可证和声明

该项目采用 MIT 许可证。详细信息请查看 [LICENSE](LICENSE) 文件。

**免责声明**: 这个项目仅供学习和研究目的使用。请遵守当地法律法规和Warp Terminal的使用条款。开发者不承担任何因使用该软件而产生的法律后果。

## 联系信息

- **GitHub**: [WARP_reg_and_manager](https://github.com/hj01857655/WARP_reg_and_manager)
- **Telegram 频道**: [@warp5215](https://t.me/warp5215)
- **Telegram 群组**: [@warp1215](https://t.me/warp1215)

---

本文档最后更新日期：2025-01-19置
    monitor_config_changes: bool = True
    auto_backup_enabled: bool = True
    max_backups: int = 10
    
    class Config:
        env_file = ".env"
```

### 8. 项目结构
```
WARP_terminal_manager/
├── src/
│   ├── warp_terminal_manager/
│   │   ├── main.py              # 应用入口
│   │   ├── core/                # 核心功能
│   │   │   ├── config_parser.py # 配置文件解析
│   │   │   ├── sync_manager.py  # 同步管理
│   │   │   └── backup_manager.py # 备份管理
│   │   ├── api/                 # API客户端
│   │   │   └── warp_client.py   # Warp API客户端
│   │   ├── database/            # 数据存储
│   │   │   └── models.py        # 数据模型
│   │   └── ui/                  # 界面层
│   │       ├── views/           # 视图组件
│   │       ├── widgets/         # 自定义组件
│   │       └── themes/          # 主题样式
├── tests/                       # 测试目录
├── requirements.txt             # 依赖列表
└── pyproject.toml              # 项目配置
```

### 9. 开发优先级

#### 第一阶段 - 基础功能 (2-3周)
1. 搭建PyQt6基础框架和项目结构
2. 实现数据库和账号CRUD操作
3. 创建基础UI界面和导航
4. 实现Warp Terminal配置文件解析功能

#### 第二阶段 - 核心功能 (3-4周)
1. 集成Warp Terminal API客户端
2. 实现账号管理和切换功能
3. 添加配置备份和恢复功能
4. 实现配置文件监控和自动备份

#### 第三阶段 - 高级功能 (2-3周)
1. 完善UI动画和主题系统
2. 添加配置同步和团队协作功能
3. 实现工作流和主题的导入导出
4. 优化性能和用户体验

#### 第四阶段 - 发布准备 (1-2周)
1. 全面测试和bug修复
2. 创建安装包和文档
3. 性能优化和代码重构
4. 准备发布版本

## 关键实现要点

1. **异步优先**: 所有网络操作和耗时任务使用异步处理
2. **类型安全**: 全面使用类型注解，配合mypy检查
3. **模块化设计**: 清晰的分层架构，便于维护和扩展
4. **用户体验**: 现代化界面，流畅动画，响应式设计
5. **数据安全**: 本地加密存储，不上传敏感数据
6. **配置管理**: 智能的配置备份、同步和恢复机制
7. **跨平台**: 支持Windows/macOS/Linux三大平台
8. **团队协作**: 支持团队配置共享和同步功能

## 技术要求

- 遵循PEP 8代码规范
- 使用black进行代码格式化
- 完善的异常处理和日志记录
- 单元测试覆盖率 > 80%
- 启动时间 < 3秒，内存占用 < 100MB
- 支持热重载配置和主题切换
- 实时配置文件监控和自动备份
- 跨设备配置同步和团队协作
