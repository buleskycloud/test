import json
import os
import random
import string
from datetime import datetime, timedelta
from ftplib import FTP


FTP_HOST = "1.15.89.138"
FTP_USER = "XXYP"
FTP_PASS = "hyx&20030404"
REMOTE_DIR = "/FTP/config"
REMOTE_FILENAME = "activation_keys.json"


def random_key() -> str:
    """生成 PERM-XXXX-XXXX-XXXX 样式的 key。"""

    def part(min_len: int, max_len: int) -> str:
        length = random.randint(min_len, max_len)
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))

    segments = [part(6, 8), part(4, 5), part(4, 5)]
    return "PERM-" + "-".join(segments)


def random_device() -> str:
    """生成形如 ab12:34cd:.. 的设备 ID。"""

    segment_chars = string.ascii_lowercase + string.digits
    segments = ["".join(random.choices(segment_chars, k=4)) for _ in range(4)]
    return ":".join(segments)


def random_datetime_strings(base: datetime) -> tuple[str, str]:
    """返回 (日期字符串, 当日随机时间字符串)。"""

    date_str = base.strftime("%Y-%m-%d")
    midnight = base.replace(hour=0, minute=0, second=0, microsecond=0)
    random_time = midnight + timedelta(minutes=random.randint(0, 24 * 60 - 1))
    time_str = random_time.strftime("%Y-%m-%d %H:%M:%S")
    return date_str, time_str


def generate_activation_record(now: datetime) -> dict:
    """生成符合指定格式的记录。"""

    date_str, time_str = random_datetime_strings(now)
    return {
        "key": random_key(),
        "type": "PERM",
        "created_date": date_str,
        "created_at": date_str,
        "remark": "",
        "used": True,
        "locked": False,
        "bound_device": random_device(),
        "update_time": time_str,
    }


def generate_activation_keys(count: int | None = None) -> list:
    total = count if count is not None else random.randint(22, 66)
    now = datetime.utcnow()
    return [generate_activation_record(now) for _ in range(total)]


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

        # 尝试删除远程同名文件，避免被占用导致无法覆盖
        try:
            print(f"[INFO] Trying to delete existing {REMOTE_FILENAME} on server (if any)...")
            ftp.delete(REMOTE_FILENAME)
            print("[INFO] Existing file deleted.")
        except Exception as e:
            print(f"[WARN] Could not delete existing {REMOTE_FILENAME}: {e}")

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
    # 生成随机 activation_keys.json
    records = generate_activation_keys()
    local_file = os.path.join(os.path.dirname(__file__), REMOTE_FILENAME)
    write_json_file(local_file, records)
    print(f"[INFO] Generated {len(records)} records to {local_file}.")

    # FTP 覆盖上传
    upload_via_ftp(local_file)


if __name__ == "__main__":
    main()
