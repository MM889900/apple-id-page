import os
import sys
import json
import re
import random
import time
from datetime import datetime

README_PATH = "README.md"
HTML_PATH = "docs/index.html"
DATA_PATH = "data.txt"
PLACEHOLDER_START = "<!-- apple starts -->"
PLACEHOLDER_END   = "<!-- apple ends -->"

ACCESS_PASSWORD = os.environ.get("PAGE_PASSWORD", "apple2026")

# ==================== 读取 data.txt ====================
all_accounts = []
try:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split("----")]
            if len(parts) >= 2:
                acc = parts[0]
                pwd = parts[1]
                region = parts[2] if len(parts) >= 3 else "未知"
                all_accounts.append({"acc": acc, "pwd": pwd, "region": region})
    print(f"✅ 从 data.txt 读取到 {len(all_accounts)} 个账号")
except Exception as e:
    print(f"❌ 读取 data.txt 失败: {e}")
    sys.exit(1)

if not all_accounts:
    print("⚠️ data.txt 中没有账号数据")
    sys.exit(1)

# ==================== 随机打乱显示 ====================
slot = int(time.time() // 600)
random.seed(slot)
shuffled = all_accounts.copy()
random.shuffle(shuffled)
accounts = shuffled[:6]   # 显示6个账号

print(f"✅ 本轮随机显示 {len(accounts)} 个账号")

# ==================== 更新 README.md ====================
try:
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()
except FileNotFoundError:
    content = ""

if accounts:
    block_lines = ["| Apple ID | 地区 |", "|----------|------|"]
    for a in accounts:
        block_lines.append(f"| `{a['acc']}` | {a['region']} |")
    new_block = "\n".join(block_lines)
else:
    new_block = "> 暂无账号数据。"

pattern = re.compile(rf"{re.escape(PLACEHOLDER_START)}.*?{re.escape(PLACEHOLDER_END)}", re.DOTALL)
replacement = f"{PLACEHOLDER_START}\n{new_block}\n{PLACEHOLDER_END}"
new_content = pattern.sub(replacement, content) if PLACEHOLDER_START in content else content + f"\n\n{replacement}\n"

with open(README_PATH, "w", encoding="utf-8") as f:
    f.write(new_content)
print("✅ README.md 更新完成")

# ==================== 生成 HTML ====================
def obfuscate(text):
    return ','.join(str(ord(c) ^ 7) for c in text)

update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
data_json = json.dumps(accounts, ensure_ascii=False)
obf_data = obfuscate(data_json)

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>🍎 小火箭共享账号</title>
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:"Microsoft YaHei",sans-serif;background:#f0f2f5;color:#1d1d1f}}
    .lock-box{{max-width:360px;margin:100px auto;background:#fff;border-radius:16px;padding:36px;box-shadow:0 4px 24px rgba(0,0,0,.1);text-align:center}}
    .lock-box .icon{{font-size:3em;margin-bottom:16px}}
    .lock-box h2{{font-size:1.4em;margin-bottom:8px}}
    .lock-box p{{color:#888;font-size:.9em;margin-bottom:20px}}
    .lock-box input{{width:100%;padding:12px;border:1.5px solid #ddd;border-radius:10px;font-size:1em;text-align:center;outline:none}}
    .lock-box input:focus{{border-color:#0071e3}}
    .lock-box button{{width:100%;margin-top:12px;padding:12px;background:#0071e3;color:#fff;border:none;border-radius:10px;font-size:1em;cursor:pointer}}
    .lock-box button:hover{{background:#005bb5}}
    .err{{color:#ff3b30;font-size:.85em;margin-top:10px;display:none}}
    .wrap{{max-width:1100px;margin:0 auto;padding:20px;display:none}}
    .header{{text-align:center;padding:30px 0 20px}}
    .header h1{{font-size:1.8em;margin-bottom:6px}}
    .header p{{color:#888;font-size:.9em}}
    .warn{{background:#fff8e1;border-left:4px solid #ffc107;padding:12px 16px;border-radius:8px;font-size:.85em;color:#7a6000;margin-bottom:20px}}
    .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:16px}}
    .card{{background:#fff;border-radius:14px;padding:18px;box-shadow:0 2px 10px rgba(0,0,0,.07);border:2px solid transparent}}
    .card:hover{{border-color:#0071e3}}
    button{{background:#0071e3;color:#fff;border:none;padding:9px 16px;border-radius:8px;cursor:pointer;margin:4px}}
    button:hover{{background:#005bb5}}
  </style>
</head>
<body>

<div class="lock-box" id="lockBox">
  <div class="icon">🔐</div>
  <h2>访问验证</h2>
  <p>请输入访问密码查看共享账号</p>
  <input type="password" id="pwdInput" placeholder="请输入密码" onkeydown="if(event.key==='Enter')checkPwd()">
  <button onclick="checkPwd()">确认进入</button>
  <div class="err" id="errMsg">密码错误，请重试</div>
</div>

<div class="wrap" id="mainContent">
  <div class="header">
    <h1>🍎 小火箭共享账号（每日更新）</h1>
    <p>2026年5月最新免费 ShadowRocket 美区账号</p>
  </div>
  <div class="warn">⚠️ 请仅在 App Store 登录，切勿登录 iCloud，否则可能被锁机！</div>
  <div class="grid" id="grid"></div>
</div>

<script>
const _d = [{obf_data}];
const _p = "{ACCESS_PASSWORD}";

function deobf(arr){{return arr.map(n=>String.fromCharCode(n^7)).join('');}}

function checkPwd(){{
  if(document.getElementById('pwdInput').value.trim()===_p){{
    document.getElementById('lockBox').style.display='none';
    document.getElementById('mainContent').style.display='block';
    renderCards();
    sessionStorage.setItem('auth','1');
  }}else{{
    document.getElementById('errMsg').style.display='block';
  }}
}}

function renderCards(){{
  let data = [];
  try{{data = JSON.parse(deobf(_d));}}catch(e){{}}
  const grid = document.getElementById('grid');
  grid.innerHTML = data.map(item => `
    <div class="card">
      <div style="font-size:1.05em;font-family:monospace">${{item.acc}}</div>
      <div style="margin:8px 0;color:#0071e3">地区：${{item.region}}</div>
      <div style="background:#f8f8f8;padding:10px;border-radius:8px;margin:10px 0">密码：${{item.pwd}}</div>
      <button onclick="copy('${{item.acc}}',this)">复制账号</button>
      <button onclick="copy('${{item.pwd}}',this)">复制密码</button>
    </div>
  `).join('');
}}

function copy(t,btn){{
  navigator.clipboard.writeText(t).then(()=>{{
    const old = btn.textContent;
    btn.textContent = '✅ 已复制';
    setTimeout(() => btn.textContent = old, 2000);
  }});
}}

if(sessionStorage.getItem('auth')==='1'){{
  document.getElementById('lockBox').style.display='none';
  document.getElementById('mainContent').style.display='block';
  renderCards();
}}
</script>
</body>
</html>"""

os.makedirs("docs", exist_ok=True)
with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html)
print("✅ docs/index.html 更新完成")
