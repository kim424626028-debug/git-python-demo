"""入口文件 —— 用来验证环境装对了没有。"""

import os
import sys

from dotenv import load_dotenv

load_dotenv()


def main() -> int:
    print(f"Python: {sys.version.split()[0]}")
    print(f"解释器路径: {sys.executable}")
    print(f"API_KEY 是否读到: {'是' if os.getenv('API_KEY') else '否（先 cp .env.example .env）'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
