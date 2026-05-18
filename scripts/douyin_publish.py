"""
抖音 V3 - 页面验证 + Playwright原生上传
"""
import os, sys, time
from pathlib import Path

LOG = os.path.expanduser(r'~\.hermes\logs\douyin_v3.log')
os.makedirs(os.path.dirname(LOG), exist_ok=True)

def log(msg):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
    print(msg, flush=True)

from playwright.sync_api import sync_playwright

STATE_FILE = os.path.expanduser(r'~\.hermes\browser-profiles\douyin_state.json')
FOLDER = Path(r"D:\BaiduSyncdisk\8 本地推素材\chatgtp出图\4-已发(三平台)")
files = sorted([str(f.absolute()) for f in FOLDER.glob("*.png")] + 
               [str(f.absolute()) for f in FOLDER.glob("*.jpg")])

TITLE = "昆山轮椅出租同城配送"
HASHTAGS = "#轮椅出租 #轮椅租赁 #出行辅助 #昆山轮椅 #佳康顺"
DESC = f"""昆山也有轮椅出租啦，同城快速配送上门
受伤临时租用、旅游代步、老人出行统统搞定
品牌佳康顺，几乎全新，干净卫生
全昆山可自取/包邮到家
{HASHTAGS}"""

log(f"📁 {len(files)}张图")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, args=['--disable-blink-features=AutomationControlled'])
    context = browser.new_context(storage_state=STATE_FILE, viewport={'width': 1280, 'height': 900})
    page = context.new_page()
    
    # 1. 导航
    page.goto('https://creator.douyin.com/creator-micro/content/manage', wait_until='domcontentloaded', timeout=30000)
    page.wait_for_timeout(4000)
    log("1️⃣ 已登录")
    
    # 2. 高清发布 → 发布图文
    page.click('text="高清发布"')
    page.wait_for_timeout(2000)
    page.click('text="发布图文"')
    page.wait_for_timeout(6000)
    log(f"2️⃣ URL: {page.url}")
    
    # 关闭弹窗
    for t in ['我知道了', '确定']:
        try:
            btn = page.query_selector(f'text="{t}"')
            if btn and btn.is_visible(timeout=2000):
                btn.click(); page.wait_for_timeout(500)
        except: pass
    
    # === 验证是图文页 ===
    body = page.evaluate('document.body.innerText')
    is_image = '上传图文' in body or '图片' in body or '照片' in body
    is_video = '上传视频' in body or '视频文件' in body
    log(f"   图文页: {'✅' if is_image and not is_video else f'⚠️ video={is_video} image={is_image}'}")
    log(f"   页面文本: {body[:200]}")
    
    # 3. 上传图片 - 找正确的file input
    log("3️⃣ 上传图片...")
    all_fi = page.query_selector_all('input[type="file"]')
    log(f"   {len(all_fi)}个file input")
    
    uploaded = False
    for i, fi in enumerate(all_fi):
        try:
            accept = fi.get_attribute('accept') or ''
            multiple = fi.get_attribute('multiple')
            log(f"   [{i}] accept={accept[:60]} multiple={multiple}")
            if 'image' in accept and multiple:
                fi.set_input_files(files)
                log(f"   ✅ input[{i}] 上传 {len(files)}张")
                uploaded = True
                break
        except Exception as e:
            log(f"   [{i}] ❌ {str(e)[:50]}")
    
    if not uploaded and all_fi:
        # fallback: 用CDP第二个input
        cdp = page.context.new_cdp_session(page)
        doc = cdp.send('DOM.getDocument', {'depth': -1})
        node_ids = cdp.send('DOM.querySelectorAll', {'nodeId': doc['root']['nodeId'], 'selector': 'input[type="file"]'})['nodeIds']
        if len(node_ids) > 1:
            cdp.send('DOM.setFileInputFiles', {'files': files, 'nodeId': node_ids[1]})
            log(f"   ✅ CDP input[1]")
            uploaded = True
    
    # 4. 等处理
    log("4️⃣ 等待处理...")
    page.wait_for_timeout(12000)
    page.screenshot(path=os.path.expanduser(r'~\.hermes\logs\douyin_v3_uploaded.png'))
    
    # 5. 点"上传图文"按钮（如果存在）
    upload_btn = page.query_selector('text="上传图文"')
    if upload_btn and upload_btn.is_visible():
        upload_btn.click()
        log("5️⃣ 点击「上传图文」")
        page.wait_for_timeout(5000)
    
    # 6. 填标题
    log("6️⃣ 标题...")
    try:
        page.wait_for_selector('input[placeholder*="标题"]', timeout=15000)
        el = page.query_selector('input[placeholder*="标题"]')
        el.click(); el.fill(''); el.fill(TITLE)
        log(f"   ✅ {TITLE}")
    except:
        log("   ❌ 标题input未出现")
        # 尝试contenteditable
        r = page.evaluate(f'''(t) => {{
            for (const el of document.querySelectorAll('[contenteditable="true"]')) {{
                if (el.offsetParent) {{ el.focus(); el.innerText = t; return true; }}
            }}
            return false;
        }}''', TITLE)
        log(f"   fallback: {r}")
    
    # 7. 填正文
    log("7️⃣ 正文...")
    r = page.evaluate(f'''(d) => {{
        // 找第二个contenteditable（第一个是标题）
        const all = document.querySelectorAll('[contenteditable="true"]');
        const target = all.length > 1 ? all[1] : all[0];
        if (target && target.offsetParent) {{
            target.focus();
            target.innerHTML = d.replace(/\\n/g, '<br>');
            target.dispatchEvent(new Event('input', {{bubbles: true}}));
            return target.innerText.length;
        }}
        return 0;
    }}''', DESC)
    log(f"   {r}字 {'✅' if r > 10 else '❌'}")
    
    page.screenshot(path=os.path.expanduser(r'~\.hermes\logs\douyin_v3_filled.png'))
    
    # 8. 发布
    log("8️⃣ 🚀 发布...")
    page.evaluate('''() => {
        for (const btn of document.querySelectorAll('button')) {
            if (btn.innerText.trim() === '发布' && btn.offsetParent) {
                btn.dispatchEvent(new MouseEvent('click', {bubbles: true}));
                return;
            }
        }
    }''')
    page.wait_for_timeout(10000)
    log(f"   URL: {page.url}")
    
    success = 'enter_from=publish' in page.url or 'content/manage' in page.url
    log(f"   {'✅✅✅ 发布成功!' if success else '⚠️ URL未跳转'}")
    
    if not success:
        body = page.evaluate('document.body.innerText.substring(0, 300)')
        log(f"   页面: {body[:200]}")
    
    page.screenshot(path=os.path.expanduser(r'~\.hermes\logs\douyin_v3_result.png'))
    log("✅ 完成")
    page.wait_for_timeout(30000)
    browser.close()
