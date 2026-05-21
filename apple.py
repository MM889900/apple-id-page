import re
import os
import sys
import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}
TIMEOUT = 15
EMAIL_RE = re.compile(
    r'[a-zA-Z0-9._%+\-]+@(?:icloud\.com|me\.com|apple\.com|[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})',
    re.IGNORECASE,
)
README_PATH = "README.md"
PLACEHOLDER_START = "<!-- apple starts -->"
PLACEHOLDER_END   = "<!-- apple ends -->"

raw_urls = os.environ.get("URLS", "")
urls = [u.strip() for u in raw_urls.split(",") if u.strip()]

if not urls:
    print("⚠️  未读取到任何 URL，跳过抓取。")
    sys.exit(0)

all_accounts = []

for url in urls:
    try:
        print(f"🔍 正在抓取: {url}")
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        found = EMAIL_RE.findall(resp.text)
        found = list(dict.fromkeys(e for e in found if len(e) < 80))
        print(f"   ✅ 找到 {len(found)} 个账号")
        all_accounts.extend(found)
    except requests.exceptions.Timeout:
        print(f"   ⏰ 超时，跳过: {url}")
    except requests.exceptions.HTTPError as e:
        print(f"   ❌ HTTP 错误 {e.response.status_code}，跳过: {url}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ 请求失败，跳过: {url} — {e}")
    except Exception as e:
        print(f"   ❌ 未知错误，跳过: {url} — {e}")

all_accounts = list(dict.fromkeys(all_accounts))
print(f"\n📦 共获取 {len(all_accounts)} 个账号（去重后）")

if all_accounts:
    block_lines = ["| Apple ID | 备注 |", "|----------|------|"]
    for acc in all_accounts:
        block_lines.append(f"| `{acc}` | 自动抓取 |")
    new_block = "\n".join(block_lines)
else:
    new_block = "> 暂未抓取到账号，请稍后刷新。"

try:
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()
except FileNotFoundError:
    content = f"{PLACEHOLDER_START}\n{PLACEHOLDER_END}\n"

pattern = re.compile(
    rf"{re.escape(PLACEHOLDER_START)}.*?{re.escape(PLACEHOLDER_END)}",
    re.DOTALL,
)

replacement = f"{PLACEHOLDER_START}\n{new_block}\n{PLACEHOLDER_END}"

if PLACEHOLDER_START in content:
    new_content = pattern.sub(replacement, content)
else:
    new_content = content + f"\n\n{replacement}\n"

try:
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("✅ README.md 更新完成")
except Exception as e:
    print(f"❌ 写入 README.md 失败: {e}")
    sys.exit(1)
