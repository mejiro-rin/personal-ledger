# Personal Ledger
个人账本工具，用于记录日常收支与转账流水。

## 技术栈
- **语言**：Python 3.10+
- **ORM**：SQLModel + SQLAlchemy
- **数据库**：SQLite
- **数据校验**：Pydantic v2
- **界面**：Rich（TUI）

## 项目结构
```
personal-ledger/
├── engines/         # 数据库引擎与会话管理
├── exceptions/      # 业务异常类
├── models/          # ORM 建表模型 + Schema
├── repositories/    # 数据访问层
├── services/        # 业务逻辑层
├── ui/              # 用户界面模块
├── utils/           # 配置与路径管理
└── main.py          # 统一入口（按参数选择 UI）
```

## 架构分层
```
main.py（统一入口）
   ↓
ui/（用户界面层：TUI / WebUI）
   ↓
Service 层（业务逻辑、事务边界、余额联动）
   ↓
Repository 层（纯数据库读写）
   ↓
SQLite
```

## 快速开始
- **使用 uv**
```bash
# 安装依赖
uv sync

# 运行 TUI（推荐）
python main.py

# 或显式指定模式
python main.py --mode tui
```
- **或使用 pip**
```bash
# 安装依赖
pip install -r requirements.txt

# 运行 TUI（推荐）
python main.py
```

数据文件存放路径：

- 开发环境：`项目根目录/.personal-ledger/ledger_test.db`
- 生产环境：`~/.personal-ledger/ledger.db`

## 功能
- 账户管理（现金、支付宝、微信、银行卡、信用卡）
- 分类管理（支持父子层级）
- 标签管理
- 交易记录（收入、支出、转账）
- 创建/删除交易时自动联动更新账户余额

## 当前版本
`v0.1.1-alpha` — 针对 v0.1.0 测试版的结构重构：
- 将 TUI 拆分为独立模块 `ui/tui.py`
- 新增 `main.py` 统一入口，支持通过 `--mode` 参数选择 UI（预留 WebUI）

## 许可证
MIT License