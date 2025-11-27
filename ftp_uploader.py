import json
import os
import random
import string
import time
from datetime import datetime
from ftplib import FTP


FTP_HOST = "1.15.89.138"
FTP_USER = "XXYP"
FTP_PASS = "hyx&20030404"
REMOTE_DIR = "config"
REMOTE_FILENAME = "activation_keys.json"


KEY_TYPES = ["PERE", "PEEM", "PERM", "TRIAL"]


def random_key() -> str:
    prefix = "ABCD"
    def part(n):
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=n))
    return f"{prefix}-{part(8)}-{part(4)}-{part(4)}"


def random_device() -> str:
    # 生成类似 "Ed6f:7721:e12u:1u01" 的伪设备 ID
    def block():
        length = random.randint(3, 5)
        chars = string.ascii_letters + string.digits
        return "".join(random.choices(chars, k=length))
    return ":".join(block() for _ in range(4))


def random_bool() -> bool:
    return bool(random.getrandbits(1))


def random_remark() -> str:
    # 随机生成空字符串或一些占位备注
    choices = ["", "XXX", "test", "remark", "临时", "auto"]
    return random.choice(choices)


def generate_activation_record(now: datetime) -> dict:
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    return {
        "key": random_key(),
        "type": random.choice(KEY_TYPES),
        "created_date": date_str,
        "created_at": date_str,
        "remark": random_remark(),
        "used": random_bool(),
        "locked": random_bool(),
        "bound_device": random_device(),
        "update_time": time_str,
    }


def generate_activation_keys(count: int = 1000) -> list:
    now = datetime.utcnow()
    return [generate_activation_record(now) for _ in range(count)]


def write_json_file(path: str, data) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def upload_via_ftp(local_path: str) -> None:
    ftp = FTP()
    try:
        print(f"[INFO] Connecting to FTP {FTP_HOST}...")
        ftp.connect(FTP_HOST, 21, timeout=30)
        ftp.login(FTP_USER, FTP_PASS)
        print("[INFO] Login successful.")

        if REMOTE_DIR:
            try:
                ftp.cwd(REMOTE_DIR)
            except Exception:
                # 如果目录不存在则尝试创建（某些服务器可能不允许 MKD）
                try:
                    ftp.mkd(REMOTE_DIR)
                    ftp.cwd(REMOTE_DIR)
                except Exception as e:
                    print(f"[WARN] Cannot change/create directory '{REMOTE_DIR}': {e}")

        with open(local_path, "rb") as f:
            print(f"[INFO] Uploading {REMOTE_FILENAME}...")
            ftp.storbinary(f"STOR {REMOTE_FILENAME}", f)
        print("[INFO] Upload finished.")
    finally:
        try:
            ftp.quit()
        except Exception:
            pass


def main() -> None:
    # 1. 随机等待 1~5 分钟
    delay_seconds = random.randint(60, 300)
    print(f"[INFO] Sleeping for {delay_seconds} seconds before generating and uploading...")
    time.sleep(delay_seconds)

    # 2. 生成随机 activation_keys.json
    records = generate_activation_keys(1000)
    local_file = os.path.join(os.path.dirname(__file__), REMOTE_FILENAME)
    write_json_file(local_file, records)
    print(f"[INFO] Generated {len(records)} records to {local_file}.")

    # 3. FTP 覆盖上传
    upload_via_ftp(local_file)


if __name__ == "__main__":
    main()
