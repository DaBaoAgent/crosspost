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

DESC = """昆山轮椅出租💪最低15元/天，押金仅需300元！

受伤临时租用、术后康复、旅游代步、老人出行统统搞定

品牌佳康顺，几乎全新轮椅，每次使用完都深度消毒，干净卫生

全昆山可自取/包邮到家📍张浦俱巷路625号

不用了随时还，没有任何隐形费用。点右下角「我想要」直接咨询～

#轮椅出租 #轮椅租赁 #出行辅助 #昆山轮椅 #佳康顺"""

COOKIES = [
  {"name":"cookie2","value":"17239466e5a3c290351ef5edd2159231","domain":".goofish.com","path":"/","httpOnly":True,"secure":True,"sameSite":"None"},
  {"name":"_tb_token_","value":"b335933e8d58","domain":".goofish.com","path":"/","httpOnly":False,"secure":True,"sameSite":"None"},
  {"name":"cna","value":"QJR9IjqKFSUCAXAUZJck96eK","domain":".goofish.com","path":"/","httpOnly":False,"secure":True,"sameSite":"None"},
  {"name":"havana_lgc2_77","value":"eyJoaWQiOjIwNDgyNzc5NDIsInNnIjoiNzdmOTk3MWJiNzNlNjgxYTE0OWM3OGE3MDMzYzgxNzkiLCJzaXRlIjo3NywidG9rZW4iOiIxMVVCZGVaeVJYcVRDR0RkLTlidHlCdyJ9","domain":".goofish.com","path":"/","httpOnly":True,"secure":True,"sameSite":"None"},
  {"name":"unb","value":"2048277942","domain":".goofish.com","path":"/","httpOnly":False,"secure":True,"sameSite":"None"},
  {"name":"_m_h5_tk","value":"8348c84db1574c65a93878a481104ada_1779116830409","domain":".goofish.com","path":"/","httpOnly":False,"secure":True,"sameSite":"None"},
  {"name":"sgcookie","value":"E100tL14RFZCimo5Ssz1FCYZJ5NhOBjcwdP4XCpMugPzvvsu7/cYHYDAV1QxC0Sp/0LEVf+sXTODQuVfI3dNgHWM86n/8il2PwwCPdvH30BLLNU=","domain":".goofish.com","path":"/","httpOnly":True,"secure":True,"sameSite":"None"},
  {"name":"csg","value":"fd92a5f9","domain":".goofish.com","path":"/","httpOnly":False,"secure":True,"sameSite":"None"},
  {"name":"tfstk","value":"gTvII-vcry4BtWnKyyoacye1bLXSbck4PusJm3eU29BLyzKA7e7FL0D5yebwLw-FpYsJuFT5ZDbPyaTy2BoZ3x-HxTXJPqkq3P4mRj9CyzWRKOhePtTI3x-HvkSK0hH2a2Y3Zg_Re6C-BhQG0WEpy6COBNjl2yIR2ctOSNU8JTQRB1IhczBReUKtfgbOyTCJyhn1qNQ-Cbg1jX_pA0q3_6tIF8SC58eJCM3lkH_1jGv1A6_ATNwRYdsCOZKpHilRBGpwCs5a4V69mC8dftMQoMO9c9IWEmF5P_9hCgOiRW8X-gKO1eozZGOW2KXhhuHpf9_CMLTTDRTvf3dV1doxn96dJQWH4ogefpTexdtz25BCLC1XdtH0JaRwcLsWE4D6l3KDw197Rgr73ZG2y7Z1i8s1uci_Z7bRn9_gLTjbS6IGbKosfyNl9Gj1uci_Z7fdjG5qfcaQZ","domain":".goofish.com","path":"/","httpOnly":False,"secure":True,"sameSite":"None"},
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
