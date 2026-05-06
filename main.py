"""
Personal Ledger 统一入口
用法：
  python main.py --mode tui    # 启动终端界面
  python main.py --mode web    # 启动 Web 界面（待实现）
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from engines.database import create_db_and_tables


def main():
    mode = _parse_mode()

    if mode == "tui":
        from ui.tui import run_tui
        run_tui()
    elif mode == "web":
        print("WebUI 尚未实现")
    else:
        print(f"未知模式: {mode}")


def _parse_mode() -> str:
    args = sys.argv[1:]
    if "--mode" in args:
        idx = args.index("--mode")
        if idx + 1 < len(args):
            return args[idx + 1]
    if "-m" in args:
        idx = args.index("-m")
        if idx + 1 < len(args):
            return args[idx + 1]
    return "tui"


if __name__ == "__main__":
    create_db_and_tables()
    main()
