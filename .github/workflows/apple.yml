import re
import os
import sys
import requests
from datetime import datetime

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

# 访问密码（可自行修改）
ACCESS_PASSWORD = os.environ.get("PAGE_PASSWORD", "apple2026")

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

# ── 更新 README.md ─────────────────────────────────────────────
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
new_content = pattern.sub(replacement, content) if PLACEHOLDER_START in content else content + f"\n\n{replacement}\n"

try:
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("✅ README.md 更新完成")
except Exception as e:
    print(f"❌ 写入 README.md 失败: {e}")
    sys.exit(1)

# ── 生成混淆后的账号数据（JS用） ────────────────────────────────
def obfuscate(text):
    """简单异或混淆，key=7，防止直接在源码看到明文"""
    return ','.join(str(ord(c) ^ 7) for c in text)

update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if all_accounts:
    # 把所有账号打包成JSON再混淆
    import json
    data_json = json.dumps(all_accounts, ensure_ascii=False)
    obf_data = obfuscate(data_json)
    count = len(all_accounts)
else:
    obf_data = obfuscate("[]")
    count = 0

html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>🍎 共享 Apple ID</title>
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f5f5f7;color:#1d1d1f;padding:20px}}
    h1{{text-align:center;margin:30px 0 8px;font-size:2em}}
    .sub{{text-align:center;color:#6e6e73;margin-bottom:24px;font-size:.9em}}
    .lock-box{{max-width:360px;margin:80px auto;background:#fff;border-radius:16px;padding:32px;box-shadow:0 4px 20px rgba(0,0,0,.1);text-align:center}}
    .lock-box h2{{margin-bottom:8px;font-size:1.3em}}
    .lock-box p{{color:#6e6e73;font-size:.9em;margin-bottom:20px}}
    .lock-box input{{width:100%;padding:12px;border:1.5px solid #ddd;border-radius:10px;font-size:1em;text-align:center;outline:none}}
    .lock-box input:focus{{border-color:#0071e3}}
    .lock-box button{{width:100%;margin-top:12px;padding:12px;background:#0071e3;color:#fff;border:none;border-radius:10px;font-size:1em;cursor:pointer}}
    .lock-box button:hover{{background:#0077ed}}
    .lock-box .err{{color:#ff3b30;font-size:.85em;margin-top:8px;display:none}}
    .container{{max-width:720px;margin:0 auto;display:none}}
    .info{{text-align:center;color:#6e6e73;font-size:.85em;margin-bottom:14px}}
    table{{width:100%;border-collapse:collapse;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.08)}}
    thead{{background:#1d1d1f;color:#fff}}
    th,td{{padding:13px 16px;text-align:left;border-bottom:1px solid #f0f0f0}}
    tr:last-child td{{border-bottom:none}}
    tr:hover{{background:#f9f9f9}}
    .acc{{font-family:monospace;font-size:.9em}}
    .warn{{background:#fff8e1;border-left:4px solid #ffc107;padding:12px 16px;border-radius:8px;font-size:.85em;color:#7a6000;margin-bottom:16px}}
    button.copy{{background:#0071e3;color:#fff;border:none;padding:5px 12px;border-radius:7px;cursor:pointer;font-size:.82em}}
    button.copy:hover{{background:#0077ed}}
    button.copied{{background:#34c759}}
    .toast{{position:fixed;bottom:30px;left:50%;transform:translateX(-50%);background:#333;color:#fff;padding:10px 24px;border-radius:20px;font-size:.9em;opacity:0;transition:opacity .3s;pointer-events:none}}
    .toast.show{{opacity:1}}
  </style>
</head>
<body>

<!-- 锁屏层 -->
<div class="lock-box" id="lockBox">
  <div style="font-size:2.5em;margin-bottom:12px">🔐</div>
  <h2>访问验证</h2>
  <p>请输入访问密码查看共享账号</p>
  <input type="password" id="pwdInput" placeholder="请输入密码" onkeydown="if(event.key==='Enter')checkPwd()">
  <button onclick="checkPwd()">确认</button>
  <div class="err" id="errMsg">密码错误，请重试</div>
</div>

<!-- 内容层（默认隐藏） -->
<div class="container" id="mainContent">
  <h1>🍎 共享 Apple ID</h1>
  <p class="sub">每30分钟自动更新 · 仅供学习使用</p>
  <div class="warn">⚠️ 请仅在 <strong>App Store</strong> 登录，切勿登录 iCloud，否则可能锁机！</div>
  <div class="info" id="info">共 {count} 个账号 · 更新时间：{update_time}</div>
  <table>
    <thead><tr><th>Apple ID</th><th>操作</th></tr></thead>
    <tbody id="tbody"></tbody>
  </table>
</div>

<div class="toast" id="toast">✅ 已复制！</div>

<script>
// 混淆数据
const _d = [{obf_data}];
const _p = "{ACCESS_PASSWORD}";

// 解混淆
function deobf(arr) {{
  return arr.map(n => String.fromCharCode(n ^ 7)).join('');
}}

function checkPwd() {{
  const v = document.getElementById('pwdInput').value.trim();
  if (v === _p) {{
    document.getElementById('lockBox').style.display = 'none';
    document.getElementById('mainContent').style.display = 'block';
    renderTable();
    sessionStorage.setItem('auth','1');
  }} else {{
    document.getElementById('errMsg').style.display = 'block';
  }}
}}

function renderTable() {{
  const raw = deobf(_d);
  let accounts = [];
  try {{ accounts = JSON.parse(raw); }} catch(e) {{}}
  const tbody = document.getElementById('tbody');
  if (!accounts.length) {{
    tbody.innerHTML = '<tr><td colspan="2" style="text-align:center;color:#999;padding:30px">暂无账号，请稍后刷新</td></tr>';
    return;
  }}
  tbody.innerHTML = accounts.map(acc => `
    <tr>
      <td class="acc">${{acc}}</td>
      <td><button class="copy" onclick="copyText('${{acc}}',this)">复制</button></td>
    </tr>`).join('');
}}

function copyText(t, btn) {{
  navigator.clipboard.writeText(t).then(() => {{
    btn.textContent = '✅';
    btn.classList.add('copied');
    setTimeout(() => {{ btn.textContent = '复制'; btn.classList.remove('copied'); }}, 2000);
    const toast = document.getElementById('toast');
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 2000);
  }});
}}

// 若本次会话已验证，自动解锁
if (sessionStorage.getItem('auth') === '1') {{
  document.getElementById('lockBox').style.display = 'none';
  document.getElementById('mainContent').style.display = 'block';
  renderTable();
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
