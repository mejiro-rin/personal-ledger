"""
路径管理器
"""
from pathlib import Path
from utils.config import settings as st

class PathManager:
    @property
    def base_dir(self) -> Path:
        """获取项目根目录"""
        return Path(__file__).parent.parent

    @property
    def home(self) -> Path:
        """获取用户 ~ 目录"""
        return Path.home()

    @property
    def data_dir(self) -> Path:
        """
        获取数据目录
        开发环境：项目根目录下的 .personal-ledger
        生产环境：~ 目录下的 .personal-ledger
        """
        if st.dev_env:
            return self.base_dir / ".personal-ledger"
        else:
            return self.home / ".personal-ledger"

    @property
    def db_path(self) -> Path:
        """获取数据库文件路径"""
        db_file_name = "ledger_test.db" if st.dev_env else "ledger.db"
        return self.data_dir / db_file_name


paths = PathManager()

if __name__ == "__main__":
    print(f"base_dir: {paths.base_dir}")
    print(f"home: {paths.home}")
    print(f"data_dir: {st.dev_env} {paths.data_dir}")
    print(f"db_path: {paths.db_path}")