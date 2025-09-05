#!/usr/bin/env python3
import os
import sys
import subprocess
import sqlite3
import getpass

# ---------------- 彩色输出 ----------------
RED    = "\033[0;31m"
GREEN  = "\033[0;32m"
YELLOW = "\033[0;33m"
BLUE   = "\033[0;34m"
RESET  = "\033[0m"

# ---------------- 配置 ----------------
CONTAINER_NAME = "lanyuechat"
DB_PATH = "./data/backend/webui.db"
REQUIRED_LIBS = ["passlib"]

# ---------------- 函数 ----------------
def check_sudo():
    script_name = os.path.basename(__file__)
    if os.geteuid() != 0:
        print(f"{RED}[✖] 请使用 sudo 执行本脚本 ({script_name})，否则无法访问数据库！{RESET}")
        print(f"{YELLOW}例如: sudo python3 {script_name}{RESET}")
        sys.exit(1)

def check_python_libs():
    for lib in REQUIRED_LIBS:
        try:
            __import__(lib)
        except ImportError:
            print(f"{RED}[✖] 缺少依赖库: {lib}{RESET}")
            print(f"{YELLOW}请使用 pip 安装，例如:{RESET}")
            print(f"    pip install {lib}")
            sys.exit(1)
    global pwd_context
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def check_container():
    try:
        running = subprocess.check_output(
            ["docker", "ps", "-q", "-f", f"name={CONTAINER_NAME}"],
            text=True
        ).strip()
    except Exception as e:
        print(f"{RED}[✖] 检查 Docker 容器失败: {e}{RESET}")
        sys.exit(1)
    if running:
        answer = input(f"{YELLOW}[⚠] 容器 {CONTAINER_NAME} 正在运行，是否停止以继续？(y/n): {RESET}")
        if answer.lower() == "y":
            subprocess.run(["docker", "stop", CONTAINER_NAME])
            print(f"{GREEN}[✔] 容器 {CONTAINER_NAME} 已停止{RESET}")
        else:
            print(f"{RED}[✖] 脚本退出{RESET}")
            sys.exit(0)
    else:
        print(f"{GREEN}[✔] 容器 {CONTAINER_NAME} 没有运行，继续执行{RESET}")

def input_password_with_confirm():
    while True:
        try:
            pw1 = getpass.getpass(f"{BLUE}[🔑] 请输入新管理员密码: {RESET}")
            pw2 = getpass.getpass(f"{BLUE}[🔑] 请再次输入确认密码: {RESET}")
        except KeyboardInterrupt:
            print(f"\n{RED}[✖] 用户取消操作，脚本退出{RESET}")
            sys.exit(1)
        if pw1 == pw2:
            if not pw1:
                print(f"{RED}[✖] 密码不能为空，请重新输入！{RESET}\n")
                continue
            return pw1
        else:
            print(f"{RED}[✖] 两次输入的密码不一致，请重新输入！{RESET}\n")

def main():
    check_sudo()
    check_python_libs()
    check_container()

    try:
        email = input(f"{BLUE}[📧] 请输入新管理员邮箱: {RESET}")
    except KeyboardInterrupt:
        print(f"\n{RED}[✖] 用户取消操作，脚本退出{RESET}")
        sys.exit(1)

    # 检查邮箱是否存在
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT email FROM auth WHERE email = ?", (email,))
        row = cur.fetchone()
        if not row:
            cur.execute("SELECT email FROM auth")
            all_emails = [r[0] for r in cur.fetchall()]
            print(f"{RED}[✖] 邮箱 {email} 不存在！{RESET}")
            if all_emails:
                print(f"{YELLOW}[ℹ] 当前邮箱列表:{RESET}")
                for e in all_emails:
                    print(f"    {e}")
            conn.close()
            sys.exit(1)
    except Exception as e:
        print(f"{RED}[✖] 数据库访问失败: {e}{RESET}")
        sys.exit(1)

    password = input_password_with_confirm()
    hashed_password = pwd_context.hash(password)
    print(f"{GREEN}[✔] 生成的 bcrypt 哈希: {hashed_password}{RESET}")

    try:
        cur.execute("UPDATE auth SET password = ? WHERE email = ?", (hashed_password, email))
        conn.commit()
        conn.close()
        print(f"{GREEN}[✔] 管理员密码已更新成功{RESET}")
    except Exception as e:
        print(f"{RED}[✖] 更新数据库失败: {e}{RESET}")
        sys.exit(1)

    print(f"{YELLOW}[ℹ] 请执行 ./run.sh --start 启动应用{RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}[✖] 用户取消操作，脚本退出{RESET}")
        sys.exit(1)
