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
REMOTE_DIR = "/FTP/config"
REMOTE_FILENAME = "activation_keys.json"


KEY_TYPES = ["PPPP", "FUCK", "YOUR", "TRIA", "ABCD", "XYZQ"]


RANDOM_CHARS = (
    string.ascii_letters
    + string.digits
    + "!@#$%^&*()_+-=[]{};:'\",.<>/?|\\"  # 尽量多的符号
)


def random_key() -> str:
    """生成更长、更乱的 key，例如 PERM-XXXXXXXX-XXXXXXXX-XXXXXXXX-XXXXXXXX。"""

    prefix = "PERM"

    def part(min_len: int = 8, max_len: int = 16) -> str:
        length = random.randint(min_len, max_len)
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))

    # 3~4 段随机长度的编码
    segments = [part() for _ in range(random.randint(3, 4))]

    # 有一定概率再追加一段更乱的尾巴
    if random.random() < 0.5:
        segments.append(part(4, 12))

    return f"{prefix}-" + "-".join(segments)


def random_device() -> str:
    """生成长串设备 ID，看起来像 32~64 位的混合乱码。"""

    length = random.randint(32, 64)
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))


def random_bool() -> bool:
    return bool(random.getrandbits(1))


def random_remark(min_len: int = 10, max_len: int = 200) -> str:
    """生成长字符串备注，包含中英文、数字和符号，尽量像乱码。"""

    # 掺杂一些常见中文字符
    chinese_part = "测试乱码数据自动生成随机备注字段内容"
    pool = RANDOM_CHARS + chinese_part
    length = random.randint(min_len, max_len)
    return "".join(random.choices(pool, k=length))


def random_datetime_strings(now: datetime) -> tuple[str, str]:
    """返回 (日期字符串, 日期时间字符串)。"""

    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    return date_str, time_str


def generate_activation_record(now: datetime) -> dict:
    """生成一条极度随机且字段较多的记录。"""

    date_str, time_str = random_datetime_strings(now)

    record: dict[str, object] = {
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

    # 有一定概率添加激活相关字段
    if random_bool():
        record["activated_date"] = date_str
        record["activated_at"] = date_str

    # 再随机添加大量扩展字段 f1 ~ f50，每个都是长乱码字符串
    extra_field_count = random.randint(20, 50)
    for i in range(1, extra_field_count + 1):
        field_name = f"f{i}"
        record[field_name] = random_remark(20, 300)

    return record


def generate_activation_keys(count: int = 20) -> list:
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
    records = generate_activation_keys(20)
    local_file = os.path.join(os.path.dirname(__file__), REMOTE_FILENAME)
    write_json_file(local_file, records)
    print(f"[INFO] Generated {len(records)} records to {local_file}.")

    # FTP 覆盖上传
    upload_via_ftp(local_file)


if __name__ == "__main__":
    main()
