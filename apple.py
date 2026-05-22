import os
import json
import re
import random
import time
from datetime import datetime

README_PATH = "README.md"
HTML_PATH = "docs/index.html"
DATA_PATH = "data.txt"

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
                all_accounts.append({
                    "acc": parts[0],
                    "pwd": parts[1],
                    "region": parts[2] if len(parts) >= 3 else "未知"
                })
    print(f"✅ 读取到 {len(all_accounts)} 个账号")
except Exception as e:
    print(f"❌ 读取 data.txt 失败: {e}")

# 随机显示6个
slot = int(time.time() // 600)
random.seed(slot)
accounts = random.sample(all_accounts, min(6, len(all_accounts)))

print(f"✅ 本轮显示 {len(accounts)} 个账号")

# ==================== 更新 README.md ====================
try:
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()
except:
    content = ""

new_block = "\n".join([f"| `{a['acc']}` | {a['region']} |" for a in accounts])
content = re.sub(r'<!-- apple starts -->.*?<!-- apple ends -->', 
                 f'<!-- apple starts -->\n{new_block}\n<!-- apple ends -->', 
                 content, flags=re.DOTALL)

with open(README_PATH, "w", encoding="utf-8") as f:
    f.write(content)
print("✅ README.md 更新完成")

# ==================== 更新 docs/index.html（只更新账号部分） ====================
def obfuscate(text):
    return ','.join(str(ord(c) ^ 7) for c in text)

update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
data_json = json.dumps(accounts, ensure_ascii=False)
obf_data = obfuscate(data_json)

# 只替换账号数据部分，保留主站按钮和结构
html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>🍎 共享苹果id - 每日更新</title>
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:"Microsoft YaHei",system-ui,sans-serif;background:#f5f7fa;color:#333;line-height:1.6}}
    .header{{background:linear-gradient(135deg,#ff6b6b,#4ecdc4);color:white;padding:50px 20px;text-align:center}}
    .header h1{{font-size:2.5em;margin-bottom:10px}}
    .sub{{font-size:1.2em;opacity:0.95}}
    .container{{max-width:1200px;margin:30px auto;padding:0 15px}}
    .warning{{background:#fff3cd;padding:18px;border-radius:8px;border-left:6px solid #ffc107;margin:25px 0;color:#856404}}
    .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:20px}}
    .card{{background:white;border-radius:14px;padding:22px;box-shadow:0 4px 20px rgba(0,0,0,0.1)}}
    .region{{color:#0071e3;font-weight:bold;margin-bottom:10px;font-size:1.05em}}
    .acc{{font-family:monospace;font-size:1.08em;background:#f8f9fa;padding:14px;border-radius:8px;margin:12px 0;word-break:break-all}}
    button{{background:#007bff;color:white;border:none;padding:11px 20px;border-radius:8px;cursor:pointer;margin:5px}}
    button:hover{{background:#0056b3}}
    .buy-btn{{background:#ff4757;color:white;font-size:19px;padding:20px 40px;width:100%;font-weight:bold;border-radius:12px;margin:35px 0}}
    .buy-btn:hover{{background:#ff3746}}
    .footer{{text-align:center;color:#555;margin:60px 0;font-size:0.98em}}
  </style>
</head>
<body>

<div class="header">
  <h1>🍎 共享苹果id（每日更新）</h1>
  <p class="sub">日区 / 港区 / 台区 / 美区 Apple ID ·  Shadowrocket 节点</p>
</div>

<div class="container">
  <div class="warning">
    ⚠️ 请仅在 <strong>App Store</strong> 登录，切勿登录 iCloud 设置，否则可能导致锁机！
  </div>

  <div class="grid" id="grid"></div>

  <a href="https://www.qianxun1688.com/liebiao/2A2466E850439A7A" target="_blank">
    <button class="buy-btn">🛒 点击进入主站购买独享稳定账号 → 长期稳定 · 自动发货</button>
  </a>

  <div class="footer">
    短域名：<strong>ios3.cn</strong> | 喜欢本站请按 Ctrl + D 收藏
  </div>
</div>

<script>
const _d = [{obf_data}];

function deobf(arr){{return arr.map(n=>String.fromCharCode(n^7)).join('');}}

function render(){{
  let data = JSON.parse(deobf(_d));
  const grid = document.getElementById('grid');
  grid.innerHTML = data.map(item => `
    <div class="card">
      <div class="region">【${{item.region}}】</div>
      <div class="acc">${{item.acc}}</div>
      <div style="margin:12px 0">密码：${{item.pwd}}</div>
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

render();
</script>
</body>
</html>"""

os.makedirs("docs", exist_ok=True)
with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print("✅ docs/index.html 更新完成（保留主站按钮）")
