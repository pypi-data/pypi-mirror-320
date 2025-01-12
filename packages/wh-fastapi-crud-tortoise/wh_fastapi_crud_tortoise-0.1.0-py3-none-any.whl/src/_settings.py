'''
Descripttion: 
version: 0.x
Author: zhai
Date: 2025-01-11 23:29:50
LastEditors: zhai
LastEditTime: 2025-01-11 23:33:24
'''
import sys
from pathlib import Path


def _GetBaseDir():
    if getattr(sys, "frozen", False):
        # 如果是被打包的应用程序，使用 sys.executable 获取路径
        root_path = Path(sys.executable).resolve()
    else:
        # 如果是普通的脚本，使用 __file__
        root_path = Path(__file__).resolve().parent.parent

    # print("PROJECT_ROOT:", root_path)
    # print("BASE_DIR:", root_path.parent)

    return root_path.parent

_BASE_DIR: Path = _GetBaseDir()

CRUD_FILE_ROOT: Path = _BASE_DIR / "app/upload"
CRUD_DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"

