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

all_accounts = []
try:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("----")
            if len(parts) >= 2:
                acc = parts[0].strip()
                pwd = parts[1].strip()
                region = parts[2].strip() if len(parts) >= 3 else "未知"
                all_accounts.append({"acc": acc, "pwd": pwd, "region": region})
    print(f"✅ 读取到 {len(all_accounts)} 个账号")
except FileNotFoundError:
    print("⚠️  data.txt 不存在")
except Exception as e:
    print(f"❌ 读取失败: {e}")
    sys.exit(1)

# ── 每10分钟轮换显示6个账号 ──────────────────────────────────────
slot = int(time.time() // 600)
random.seed(slot)
shuffled = all_accounts.copy()
random.shuffle(shuffled)
accounts = shuffled[:4]
print(f"✅ 本轮显示 {len(accounts)} 个账号（slot={slot}）")

try:
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()
except FileNotFoundError:
    content = f"{PLACEHOLDER_START}\n{PLACEHOLDER_END}\n"

if accounts:
    block_lines = ["| Apple ID | 地区 |", "|----------|------|"]
    for a in accounts:
        block_lines.append(f"| `{a['acc']}` | {a['region']} |")
    new_block = "\n".join(block_lines)
else:
    new_block = "> 暂无账号数据。"

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

def obfuscate(text):
    return ','.join(str(ord(c) ^ 7) for c in text)

update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
count = len(accounts)
data_json = json.dumps(accounts, ensure_ascii=False)
obf_data = obfuscate(data_json)

html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>🍎 共享 Apple ID</title>
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f0f2f5;color:#1d1d1f}}
    .lock-box{{max-width:360px;margin:100px auto;background:#fff;border-radius:16px;padding:36px;box-shadow:0 4px 24px rgba(0,0,0,.1);text-align:center}}
    .lock-box .icon{{font-size:3em;margin-bottom:16px}}
    .lock-box h2{{font-size:1.4em;margin-bottom:8px}}
    .lock-box p{{color:#888;font-size:.9em;margin-bottom:20px}}
    .lock-box input{{width:100%;padding:12px;border:1.5px solid #ddd;border-radius:10px;font-size:1em;text-align:center;outline:none;transition:.2s}}
    .lock-box input:focus{{border-color:#0071e3}}
    .lock-box button{{width:100%;margin-top:12px;padding:12px;background:#0071e3;color:#fff;border:none;border-radius:10px;font-size:1em;cursor:pointer;transition:.2s}}
    .lock-box button:hover{{background:#005bb5}}
    .err{{color:#ff3b30;font-size:.85em;margin-top:10px;display:none}}
    .wrap{{max-width:1100px;margin:0 auto;padding:20px;display:none}}
    .header{{text-align:center;padding:30px 0 20px}}
    .header h1{{font-size:1.8em;margin-bottom:6px}}
    .header p{{color:#888;font-size:.9em}}
    .warn{{background:#fff8e1;border-left:4px solid #ffc107;padding:12px 16px;border-radius:8px;font-size:.85em;color:#7a6000;margin-bottom:20px;max-width:900px;margin-left:auto;margin-right:auto}}
    .stats{{text-align:center;color:#888;font-size:.85em;margin-bottom:20px}}
    .countdown{{text-align:center;font-size:.85em;color:#0071e3;margin-bottom:20px;font-weight:500}}
    .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:16px}}
    .card{{background:#fff;border-radius:14px;padding:18px;box-shadow:0 2px 10px rgba(0,0,0,.07);transition:.2s;border:2px solid transparent}}
    .card:hover{{border-color:#0071e3;box-shadow:0 4px 18px rgba(0,113,227,.15)}}
    .card-top{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px}}
    .acc{{font-family:monospace;font-size:.95em;font-weight:600;color:#1d1d1f;word-break:break-all}}
    .status{{display:flex;align-items:center;gap:5px;font-size:.8em;color:#34c759;white-space:nowrap}}
    .dot{{width:8px;height:8px;background:#34c759;border-radius:50%;animation:pulse 2s infinite}}
    @keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.4}}}}
    .region-tag{{display:inline-block;background:#e8f4fd;color:#0071e3;padding:3px 10px;border-radius:20px;font-size:.78em;font-weight:500;margin-bottom:12px}}
    .update-time{{font-size:.75em;color:#aaa;margin-bottom:14px}}
    .pwd-row{{display:flex;align-items:center;gap:8px;margin-bottom:14px;background:#f8f8f8;border-radius:8px;padding:8px 12px}}
    .pwd-label{{font-size:.8em;color:#888;white-space:nowrap}}
    .pwd-val{{font-family:monospace;font-size:.9em;filter:blur(5px);cursor:pointer;transition:.2s;flex:1}}
    .pwd-val:hover{{filter:none}}
    .btns{{display:grid;grid-template-columns:1fr 1fr;gap:8px}}
    .btn{{padding:9px;border:1.5px solid #0071e3;color:#0071e3;background:#fff;border-radius:9px;cursor:pointer;font-size:.85em;font-weight:500;transition:.2s}}
    .btn:hover{{background:#0071e3;color:#fff}}
    .btn.copied{{background:#34c759;border-color:#34c759;color:#fff}}
    .toast{{position:fixed;bottom:30px;left:50%;transform:translateX(-50%);background:#333;color:#fff;padding:10px 24px;border-radius:20px;font-size:.9em;opacity:0;transition:opacity .3s;pointer-events:none;z-index:999}}
    .toast.show{{opacity:1}}
    @media(max-width:600px){{.grid{{grid-template-columns:1fr}}}}
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
    <h1>🍎 共享 Apple ID</h1>
    <p>免费共享账号 · 仅供学习使用 · 请勿修改密码</p>
  </div>
  <div class="warn">⚠️ 请仅在 <strong>App Store</strong> 登录，切勿登录【设置/iCloud】，否则可能导致锁机或隐私泄露！</div>
  <div class="stats">本轮显示 {count} 个账号 · 更新时间：{update_time}</div>
  <div class="countdown" id="countdown">🔄 下次更换账号：计算中...</div>
  <div class="grid" id="grid"></div>
</div>

<div class="toast" id="toast">✅ 已复制！</div>

<script>
const _d = [{obf_data}];
const _p = "{ACCESS_PASSWORD}";

function deobf(arr){{return arr.map(n=>String.fromCharCode(n^7)).join('');}}

function checkPwd(){{
  if(document.getElementById('pwdInput').value.trim()===_p){{
    document.getElementById('lockBox').style.display='none';
    document.getElementById('mainContent').style.display='block';
    renderCards();
    startCountdown();
    sessionStorage.setItem('auth','1');
  }}else{{
    document.getElementById('errMsg').style.display='block';
  }}
}}

function renderCards(){{
  let data=[];
  try{{data=JSON.parse(deobf(_d));}}catch(e){{}}
  const grid=document.getElementById('grid');
  if(!data.length){{
    grid.innerHTML='<p style="text-align:center;color:#999;padding:40px;grid-column:1/-1">暂无账号数据</p>';
    return;
  }}
  grid.innerHTML=data.map((item,i)=>`
    <div class="card">
      <div class="card-top">
        <span class="acc">${{item.acc}}</span>
        <span class="status"><span class="dot"></span>正常</span>
      </div>
      <span class="region-tag">【${{item.region}}】</span>
      <div class="update-time">更新：{update_time}</div>
      <div class="pwd-row">
        <span class="pwd-label">密码</span>
        <span class="pwd-val" title="悬停查看密码">${{item.pwd}}</span>
      </div>
      <div class="btns">
        <button class="btn" onclick="cp('${{item.acc}}',this)">复制账号</button>
        <button class="btn" onclick="cp('${{item.pwd}}',this)">复制密码</button>
      </div>
    </div>`).join('');
}}

function startCountdown(){{
  function update(){{
    const now = Math.floor(Date.now()/1000);
    const next = (Math.floor(now/600)+1)*600;
    const left = next - now;
    const m = Math.floor(left/60);
    const s = left%60;
    document.getElementById('countdown').textContent =
      `🔄 下次更换账号：${{m}}分${{String(s).padStart(2,'0')}}秒`;
  }}
  update();
  setInterval(update,1000);
}}

function cp(t,btn){{
  navigator.clipboard.writeText(t).then(()=>{{
    const o=btn.textContent;
    btn.textContent='✅ 已复制';
    btn.classList.add('copied');
    setTimeout(()=>{{btn.textContent=o;btn.classList.remove('copied');}},2000);
    const toast=document.getElementById('toast');
    toast.classList。add('show');
    setTimeout(()=>toast.classList.remove('show'),2000);
  }});
}}

if(sessionStorage.getItem('auth')==='1'){{
  document.getElementById('lockBox').style.display='none';
  document.getElementById('mainContent').style.display='block';
  renderCards();
  startCountdown();
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
