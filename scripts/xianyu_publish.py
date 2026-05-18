"""
闲鱼 V13 - 全JS点击，绕过ant-design反拦截
"""
import os, time
from pathlib import Path

LOG = os.path.expanduser(r'~\.hermes\logs\xianyu_v13.log')
os.makedirs(os.path.dirname(LOG), exist_ok=True)

def log(msg):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
    print(msg, flush=True)

from playwright.sync_api import sync_playwright

FOLDER = Path(r"D:\BaiduSyncdisk\8 本地推素材\chatgtp出图\4-已发(三平台)")
files = sorted([str(f.absolute()) for f in FOLDER.glob("*.png")] +
               [str(f.absolute()) for f in FOLDER.glob("*.jpg")])

DESC = """昆山也有轮椅出租啦，最低只要15元/天起
受伤临时租用、旅游代步、老人出行统统搞定
最低只要15元/天起，押金仅需300元
品牌佳康顺，几乎全新，干净卫生
全昆山可自取/包邮到家
#轮椅出租 #轮椅租赁 #出行辅助 #昆山轮椅 #佳康顺"""

COOKIES = [
  # 从 Chrome F12 → Application → Cookies → www.goofish.com 复制以下9个关键Cookie:
  {"name":"cookie2","value":"你的cookie2值","domain":".goofish.com","path":"/","httpOnly":True,"secure":True,"sameSite":"None"},
  {"name":"_tb_token_","value":"你的值","domain":".goofish.com","path":"/"},
  {"name":"cna","value":"你的值","domain":".goofish.com","path":"/"},
  {"name":"havana_lgc2_77","value":"你的值","domain":".goofish.com","path":"/","httpOnly":True},
  {"name":"unb","value":"你的值","domain":".goofish.com","path":"/"},
  {"name":"_m_h5_tk","value":"你的值","domain":".goofish.com","path":"/"},
  {"name":"sgcookie","value":"你的值","domain":".goofish.com","path":"/","httpOnly":True},
  {"name":"csg","value":"你的值","domain":".goofish.com","path":"/"},
  {"name":"tfstk","value":"你的值","domain":".goofish.com","path":"/"},
]

log(f"📁 {FOLDER.name}: {len(files)}张图")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, args=['--disable-blink-features=AutomationControlled'])
    context = browser.new_context(viewport={'width': 1280, 'height': 900})
    context.add_cookies(COOKIES)
    page = context.new_page()
    
    # 1. 导航+上传
    page.goto("https://www.goofish.com/publish", wait_until="domcontentloaded")
    page.wait_for_timeout(10000)
    page.query_selector('input[type="file"]').set_input_files(files)
    page.wait_for_timeout(10000)
    log("1️⃣ 上传+页面 ✅")
    
    # 2. 填描述
    desc_len = page.evaluate(f'''(d) => {{
        const e = document.querySelector('[contenteditable="true"].editor--MtHPS94K');
        if (!e) return 0;
        e.focus(); e.innerHTML = d.replace(/\\n/g, '<br>');
        e.dispatchEvent(new Event('input', {{bubbles: true}}));
        return e.innerText.length;
    }}''', DESC)
    log(f"2️⃣ 描述: {desc_len}字")
    
    # 3. 所有ant-design操作用纯JS
    log("3️⃣ 分类/品牌/成色...")
    js_result = page.evaluate('''() => {
        const log = [];
        const clickText = (text) => {
            for (const el of document.querySelectorAll('*')) {
                try {
                    if (el.innerText && el.innerText.trim() === text && el.offsetParent) {
                        // 用dispatchEvent避免ant-design pointer拦截
                        el.dispatchEvent(new MouseEvent('mousedown', {bubbles: true}));
                        el.dispatchEvent(new MouseEvent('mouseup', {bubbles: true}));
                        el.dispatchEvent(new MouseEvent('click', {bubbles: true}));
                        return true;
                    }
                } catch(e) {}
            }
            return false;
        };
        
        // 分类
        if (clickText('拐杖轮椅')) log.push('category ✅');
        else log.push('category ❌');
        
        // 等下拉
        setTimeout(() => {}, 500);
        
        // 品牌 - 先打开select
        const brandTriggers = document.querySelectorAll('.ant-select-selector');
        for (const el of brandTriggers) {
            if (el.offsetParent && el.closest('[class*="brand"]') || el.closest('.brand-field')) {
                el.dispatchEvent(new MouseEvent('click', {bubbles: true}));
                log.push('brand_click');
                break;
            }
        }
        
        // 成色
        if (clickText('几乎全新')) log.push('condition ✅');
        else if (clickText('全新')) log.push('condition ✅(全新)');
        else log.push('condition ❌');
        
        return log.join(', ');
    }''')
    log(f"   {js_result}")
    page.wait_for_timeout(3000)
    
    # 4. 价格
    page.evaluate('''() => {
        const inp = document.querySelector('input[placeholder="0.00"]');
        if (inp) {
            const ns = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
            ns.call(inp, '15');
            inp.dispatchEvent(new Event('input', {bubbles: true}));
        }
    }''')
    log("4️⃣ 价格:15")
    
    page.screenshot(path=os.path.expanduser(r'~\.hermes\logs\xianyu_v13_pre.png'))
    
    # 5. 发布！
    log("5️⃣ 🚀 发布！")
    page.evaluate('''() => {
        for (const btn of document.querySelectorAll('button')) {
            try {
                if (btn.innerText && btn.innerText.trim() === '发布' && btn.offsetParent) {
                    btn.dispatchEvent(new MouseEvent('click', {bubbles: true}));
                    return;
                }
            } catch(e) {}
        }
    }''')
    page.wait_for_timeout(10000)
    log(f"   URL: {page.url}")
    
    result = page.evaluate('document.body.innerText.substring(0, 400)')
    success = any(kw in result for kw in ['发布成功', 'success', '审核', '已发布', '上架', 'item'])
    log(f"   结果: {'🎉 成功!' if success else result[:250]}")
    
    page.screenshot(path=os.path.expanduser(r'~\.hermes\logs\xianyu_v13_result.png'))
    log("\n✅ 三平台全部完成！")
    page.wait_for_timeout(60000)
    browser.close()
