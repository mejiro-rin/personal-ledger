"""
personal-ledger TUI
依赖：rich
"""
import sys
from decimal import Decimal, InvalidOperation
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import box

from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engines.database import create_db_and_tables, get_session
from models.account import AccountCreate, AccountUpdate, AccountType
from models.category import CategoryCreate, CategoryUpdate, CategoryType
from models.tag import TagCreate, TagUpdate
from models.transaction import TransactionCreate, TransactionUpdate, TransactionType
from services.account_service import AccountService
from services.category_service import CategoryService
from services.tag_service import TagService
from services.transaction_service import TransactionService
from exceptions.service_exceptions import AppBaseException

console = Console()
account_svc = AccountService()
category_svc = CategoryService()
tag_svc = TagService()
transaction_svc = TransactionService()


# ── 工具函数 ──────────────────────────────────────────────────────────────────

def get_session_once():
    """获取一个数据库会话，用完后自动关闭。"""
    return next(get_session())

def pause():
    """暂停并等待用户按 Enter 继续。"""
    Prompt.ask("\n[dim]按 Enter 继续[/dim]")

def show_error(e: Exception):
    """在控制台显示错误信息。"""
    if isinstance(e, AppBaseException):
        console.print(f"[red]✗ {e.message}[/red]")
    else:
        console.print(f"[red]✗ 未知错误：{e}[/red]")

def pick_enum(label: str, enum_cls) -> str:
    """通过序号从枚举中选择一个值。"""
    members = [e.value for e in enum_cls]
    for i, v in enumerate(members, 1):
        console.print(f"  {i}. {v}")
    while True:
        raw = Prompt.ask(f"{label} (输入序号)")
        if raw.isdigit() and 1 <= int(raw) <= len(members):
            return members[int(raw) - 1]
        console.print("[yellow]请输入有效序号[/yellow]")

def pick_id(label: str) -> int:
    """让用户输入并返回一个数字 ID，输入无效时会重复提示。"""
    while True:
        raw = Prompt.ask(label)
        if raw.isdigit():
            return int(raw)
        console.print("[yellow]请输入数字 ID[/yellow]")

def pick_decimal(label: str) -> Decimal:
    """让用户输入并返回一个 Decimal 金额，输入无效时会重复提示。"""
    while True:
        raw = Prompt.ask(label)
        try:
            return Decimal(raw)
        except InvalidOperation:
            console.print("[yellow]请输入有效金额[/yellow]")


# ── Account ───────────────────────────────────────────────────────────────────

def account_menu():
    """账户管理子菜单，循环进入增删改查操作。"""
    while True:
        console.print(Panel("[bold]账户管理[/bold]", box=box.ROUNDED))
        console.print("1. 查看所有账户\n2. 创建账户\n3. 更新账户\n4. 删除账户\n0. 返回")
        choice = Prompt.ask("选择")
        if choice == "0":
            break
        elif choice == "1":
            list_accounts()
        elif choice == "2":
            create_account()
        elif choice == "3":
            update_account()
        elif choice == "4":
            delete_account()

def list_accounts():
    """以表格形式打印所有账户信息。"""
    with get_session_once() as session:
        accounts = account_svc.list(session)
    t = Table(box=box.SIMPLE)
    for col in ["ID", "名称", "类型", "余额", "货币", "备注"]:
        t.add_column(col)
    for a in accounts:
        t.add_row(str(a.id), a.name, a.account_type, str(a.balance.quantize(Decimal("0.01"))), a.currency, a.note or "")
    console.print(t)
    pause()

def create_account():
    """创建新账户，依次录入名称、类型、初始余额等信息。"""
    console.print("[bold]── 创建账户 ──[/bold]")
    name = Prompt.ask("名称")
    account_type = pick_enum("账户类型", AccountType)
    balance = pick_decimal("初始余额")
    
    # 货币暂时禁止自定义，默认人民币
    # currency = Prompt.ask("货币", default="CNY")
    currency = "CNY"

    note = Prompt.ask("备注（可空）", default="") or None
    try:
        with get_session_once() as session:
            result = account_svc.create(session, AccountCreate(
                name=name, account_type=account_type,
                balance=balance, currency=currency, note=note
            ))
        console.print(f"[green]✓ 账户已创建 ID={result.id}[/green]")
    except AppBaseException as e:
        show_error(e)
    pause()

def update_account():
    """更新已有账户的名称或备注。"""
    list_accounts()
    id = pick_id("要更新的账户 ID")
    console.print("[dim]留空表示不修改[/dim]")
    name = Prompt.ask("新名称", default="") or None
    note = Prompt.ask("新备注", default="") or None
    try:
        with get_session_once() as session:
            result = account_svc.update(session, id, AccountUpdate(name=name, note=note))
        console.print(f"[green]✓ 账户已更新[/green]")
    except AppBaseException as e:
        show_error(e)
    pause()

def delete_account():
    """删除指定 ID 的账户，删除前需确认。"""
    list_accounts()
    id = pick_id("要删除的账户 ID")
    if Confirm.ask(f"确认删除账户 {id}？"):
        try:
            with get_session_once() as session:
                account_svc.delete(session, id)
            console.print("[green]✓ 已删除[/green]")
        except AppBaseException as e:
            show_error(e)
    pause()


# ── Category ──────────────────────────────────────────────────────────────────

def category_menu():
    """分类管理子菜单，循环进入增删改查操作。"""
    while True:
        console.print(Panel("[bold]分类管理[/bold]", box=box.ROUNDED))
        console.print("1. 查看所有分类\n2. 创建分类\n3. 更新分类\n4. 删除分类\n0. 返回")
        choice = Prompt.ask("选择")
        if choice == "0":
            break
        elif choice == "1":
            list_categories()
        elif choice == "2":
            create_category()
        elif choice == "3":
            update_category()
        elif choice == "4":
            delete_category()

def list_categories():
    """以表格形式打印所有分类信息。"""
    with get_session_once() as session:
        cats = category_svc.list(session)
    t = Table(box=box.SIMPLE)
    for col in ["ID", "名称", "类型", "父分类ID"]:
        t.add_column(col)
    for c in cats:
        t.add_row(str(c.id), c.name, c.category_type, str(c.parent_id))
    console.print(t)
    pause()

def create_category():
    """创建新分类，依次录入名称、分类类型、父分类 ID。"""
    console.print("[bold]── 创建分类 ──[/bold]")
    name = Prompt.ask("名称")
    category_type = pick_enum("分类类型", CategoryType)
    parent_id = Prompt.ask("父分类 ID（根分类填 0）", default="0")
    try:
        with get_session_once() as session:
            result = category_svc.create(session, CategoryCreate(
                name=name, category_type=category_type, parent_id=int(parent_id)
            ))
        console.print(f"[green]✓ 分类已创建 ID={result.id}[/green]")
    except AppBaseException as e:
        show_error(e)
    pause()

def update_category():
    """更新已有分类的名称。"""
    list_categories()
    id = pick_id("要更新的分类 ID")
    name = Prompt.ask("新名称（留空跳过）", default="") or None
    try:
        with get_session_once() as session:
            category_svc.update(session, id, CategoryUpdate(name=name))
        console.print("[green]✓ 分类已更新[/green]")
    except AppBaseException as e:
        show_error(e)
    pause()

def delete_category():
    """删除指定 ID 的分类，删除前需确认。"""
    list_categories()
    id = pick_id("要删除的分类 ID")
    if Confirm.ask(f"确认删除分类 {id}？"):
        try:
            with get_session_once() as session:
                category_svc.delete(session, id)
            console.print("[green]✓ 已删除[/green]")
        except AppBaseException as e:
            show_error(e)
    pause()


# ── Tag ───────────────────────────────────────────────────────────────────────

def tag_menu():
    """标签管理子菜单，循环进入增删改查操作。"""
    while True:
        console.print(Panel("[bold]标签管理[/bold]", box=box.ROUNDED))
        console.print("1. 查看所有标签\n2. 创建标签\n3. 更新标签\n4. 删除标签\n0. 返回")
        choice = Prompt.ask("选择")
        if choice == "0":
            break
        elif choice == "1":
            list_tags()
        elif choice == "2":
            create_tag()
        elif choice == "3":
            update_tag()
        elif choice == "4":
            delete_tag()

def list_tags():
    """以表格形式打印所有标签信息。"""
    with get_session_once() as session:
        tags = tag_svc.list(session)
    t = Table(box=box.SIMPLE)
    for col in ["ID", "名称"]:
        t.add_column(col)
    for tag in tags:
        t.add_row(str(tag.id), tag.name)
    console.print(t)
    pause()

def create_tag():
    """创建新标签，录入标签名称。"""
    name = Prompt.ask("标签名称")
    try:
        with get_session_once() as session:
            result = tag_svc.create(session, TagCreate(name=name))
        console.print(f"[green]✓ 标签已创建 ID={result.id}[/green]")
    except AppBaseException as e:
        show_error(e)
    pause()

def update_tag():
    """更新已有标签的名称。"""
    list_tags()
    id = pick_id("要更新的标签 ID")
    name = Prompt.ask("新名称")
    try:
        with get_session_once() as session:
            tag_svc.update(session, id, TagUpdate(name=name))
        console.print("[green]✓ 标签已更新[/green]")
    except AppBaseException as e:
        show_error(e)
    pause()

def delete_tag():
    """删除指定 ID 的标签，删除前需确认。"""
    list_tags()
    id = pick_id("要删除的标签 ID")
    if Confirm.ask(f"确认删除标签 {id}？"):
        try:
            with get_session_once() as session:
                tag_svc.delete(session, id)
            console.print("[green]✓ 已删除[/green]")
        except AppBaseException as e:
            show_error(e)
    pause()


# ── Transaction ───────────────────────────────────────────────────────────────

def transaction_menu():
    """交易记录管理子菜单，循环进入查看、创建、删除操作。"""
    while True:
        console.print(Panel("[bold]交易记录[/bold]", box=box.ROUNDED))
        console.print("1. 查看所有记录\n2. 创建记录\n3. 删除记录\n0. 返回")
        choice = Prompt.ask("选择")
        if choice == "0":
            break
        elif choice == "1":
            list_transactions()
        elif choice == "2":
            create_transaction()
        elif choice == "3":
            delete_transaction()

def list_transactions():
    """以表格形式打印所有交易记录，含账户、分类、金额、标签等信息。"""
    with get_session_once() as session:
        txs = transaction_svc.list(session)
    t = Table(box=box.SIMPLE)
    for col in ["ID", "账户", "分类", "金额", "类型", "标签", "备注", "时间"]:
        t.add_column(col)
    for tx in txs:
        tag_names = ", ".join(tag.name for tag in tx.tags)
        t.add_row(
            str(tx.id), str(tx.account_id), str(tx.category_id),
            str(tx.amount.quantize(Decimal("0.01"))), tx.transaction_type,
            tag_names, tx.note or "", str(tx.occurred_at)
        )
    console.print(t)
    pause()

def create_transaction():
    """创建新交易记录，支持收入、支出和转账三种类型。"""
    console.print("[bold]── 创建交易记录 ──[/bold]")
    transaction_type = pick_enum("交易类型", TransactionType)
    if transaction_type == TransactionType.TRANSFER:
        from_account_id = pick_id("转出账户 ID")
        to_account_id = pick_id("转入账户 ID")
        amount = pick_decimal("金额")
        account_id = from_account_id
        category_id = None
    else:
        account_id = pick_id("账户 ID")
        category_id = pick_id("分类 ID")
        amount = pick_decimal("金额")
        from_account_id = None
        to_account_id = None
    note = Prompt.ask("备注（可空）", default="") or None
    tag_ids_raw = Prompt.ask("标签 ID（多个用逗号分隔，可空）", default="")
    tag_ids = [int(x.strip()) for x in tag_ids_raw.split(",") if x.strip().isdigit()]
    try:
        with get_session_once() as session:
            result = transaction_svc.create(session, TransactionCreate(
                account_id=account_id, category_id=category_id,
                amount=amount, transaction_type=transaction_type,
                note=note, tag_ids=tag_ids,
                transfer_from_account_id=from_account_id,
                transfer_to_account_id=to_account_id
            ))
        console.print(f"[green]✓ 交易已创建 ID={result.id}[/green]")
    except AppBaseException as e:
        show_error(e)
    pause()

def delete_transaction():
    """删除指定 ID 的交易记录，删除前需确认。"""
    list_transactions()
    id = pick_id("要删除的记录 ID")
    if Confirm.ask(f"确认删除交易 {id}？"):
        try:
            with get_session_once() as session:
                transaction_svc.delete(session, id)
            console.print("[green]✓ 已删除[/green]")
        except AppBaseException as e:
            show_error(e)
    pause()


# ── 主菜单 ────────────────────────────────────────────────────────────────────

def run_tui():
    """启动 TUI 主程序，初始化数据库并进入主菜单循环。"""
    create_db_and_tables()
    console.print(Panel("[bold green]Personal Ledger TUI[/bold green]", box=box.DOUBLE))
    while True:
        console.print("\n1. 账户管理\n2. 分类管理\n3. 标签管理\n4. 交易记录\n0. 退出")
        choice = Prompt.ask("选择")
        if choice == "0":
            console.print("[dim]再见[/dim]")
            break
        elif choice == "1":
            account_menu()
        elif choice == "2":
            category_menu()
        elif choice == "3":
            tag_menu()
        elif choice == "4":
            transaction_menu()


if __name__ == "__main__":
    run_tui()
