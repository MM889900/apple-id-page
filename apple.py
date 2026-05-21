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
HTML_PATH = "docs/index.html"
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

# ── 更新 README.md ─────────────────────────────────────────────────────────────
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

# ── 更新 docs/index.html ───────────────────────────────────────────────────────
from datetime import datetime
update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if all_accounts:
    rows = ""
    for acc in all_accounts:
        rows += f"""
        <tr>
          <td><span class="account">{acc}</span></td>
          <td><button onclick="copyText('{acc}')">复制</button></td>
        </tr>"""
    table_html = f"""
    <p class="count">共 {len(all_accounts)} 个账号 · 更新时间：{update_time}</p>
    <table>
      <thead><tr><th>Apple ID</th><th>操作</th></tr></thead>
      <tbody>{rows}
      </tbody>
    </table>"""
else:
    table_html = "<p class='empty'>暂未抓取到账号，请稍后刷新。</p>"

html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>🍎 共享 Apple ID</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
           background: #f5f5f7; color: #1d1d1f; padding: 20px; }}
    h1 {{ text-align: center; margin: 30px 0 10px; font-size: 2em; }}
    .subtitle {{ text-align: center; color: #6e6e73; margin-bottom: 30px; font-size: 0.9em; }}
    .count {{ text-align: center; color: #6e6e73; margin-bottom: 15px; font-size: 0.85em; }}
    .container {{ max-width: 700px; margin: 0 auto; }}
    table {{ width: 100%; border-collapse: collapse; background: white;
             border-radius: 12px; overflow: hidden;
             box-shadow: 0 2px 12px rgba(0,0,0,0.08); }}
    thead {{ background: #1d1d1f; color: white; }}
    th, td {{ padding: 14px 18px; text-align: left; border-bottom: 1px solid #f0f0f0; }}
    tr:last-child td {{ border-bottom: none; }}
    tr:hover {{ background: #f9f9f9; }}
    .account {{ font-family: monospace; font-size: 0.95em; }}
    button {{ background: #0071e3; color: white; border: none;
              padding: 6px 14px; border-radius: 8px; cursor: pointer; font-size: 0.85em; }}
    button:hover {{ background: #0077ed; }}
    button.copied {{ background: #34c759; }}
    .empty {{ text-align: center; padding: 40px; color: #6e6e73; }}
    .toast {{ position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%);
              background: #333; color: white; padding: 10px 24px;
              border-radius: 20px; font-size: 0.9em; opacity: 0; transition: opacity 0.3s; }}
    .toast.show {{ opacity: 1; }}
  </style>
</head>
<body>
  <div class="container">
    <h1>🍎 共享 Apple ID</h1>
    <p class="subtitle">每30分钟自动更新 · 仅供学习使用</p>
    {table_html}
  </div>
  <div class="toast" id="toast">✅ 已复制！</div>
  <script>
    function copyText(text) {{
      navigator.clipboard.writeText(text).then(() => {{
        const toast = document.getElementById('toast');
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 2000);
      }});
    }}
  </script>
</body>
</html>"""

os.makedirs("docs", exist_ok=True)
try:
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ docs/index.html 更新完成")
except Exception as e:
    print(f"❌ 写入 docs/index.html 失败: {e}")
    sys.exit(1)
