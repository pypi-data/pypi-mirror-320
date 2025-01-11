"""管理缓存"""

import os
import sqlite3
from pathlib import Path


class Database:
    """用于管理补全数据的 SQLite 数据库类"""

    def __init__(self):
        self.db_path = self.get_db_path()
        self.db_connection = sqlite3.connect(str(self.db_path))
        self.db_cursor = self.db_connection.cursor()
        self.create_table_if_not_exists()

    def get_db_path(self):
        """跨平台地获取数据库文件路径"""
        if os.name == "nt":  # Windows
            user_data_dir = os.path.join(
                os.environ.get("APPDATA", os.getcwd()), "Httpgogui"
            )
        else:  # macOS/Linux
            user_data_dir = Path.home() / "Documents" / "Httpgogui"

        # 确保目录存在
        Path(user_data_dir).mkdir(parents=True, exist_ok=True)

        # 拼接数据库文件路径
        db_path = Path(user_data_dir) / "httpgogui.db"
        return db_path

    def create_table_if_not_exists(self):
        """创建表格（如果不存在）"""
        self.db_cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS completion_list (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            value TEXT UNIQUE
        )"""
        )
        self.db_connection.commit()

    def load_completion_list(self):
        """从数据库加载补全数据"""
        self.db_cursor.execute("SELECT value FROM completion_list")
        return [row[0] for row in self.db_cursor.fetchall()]

    def save_completion(self, completion: str):
        """保存补全数据到数据库"""
        self.db_cursor.execute(
            "INSERT OR IGNORE INTO completion_list (value) VALUES (?)", (completion,)
        )
        self.db_connection.commit()

    def close(self):
        """关闭数据库连接"""
        self.db_connection.close()
