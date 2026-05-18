"""
抖音登录态保存脚本
打开可见 Playwright 浏览器 → 用户手动扫码/验证码登录 → 保存 storage_state
用法:
  /c/Users/xxx13/AppData/Local/Programs/Python/Python312/python.exe douyin_login.py
登录成功后自动保存到 ~/.hermes/browser-profiles/douyin_state.json
"""
import os, sys, json

LOG = os.path.expanduser(r'~\.hermes\logs\douyin_login.log')
os.makedirs(os.path.dirname(LOG), exist_ok=True)

def log(msg):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')
    print(msg, flush=True)

from playwright.sync_api import sync_playwright

STATE_FILE = os.path.expanduser(r'~\.hermes\browser-profiles\douyin_state.json')
os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)

log("🔄 启动浏览器...")

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        args=['--disable-blink-features=AutomationControlled']
    )
    context = browser.new_context(
        viewport={'width': 1280, 'height': 800},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    )
    page = context.new_page()
    page.goto('https://creator.douyin.com', wait_until='domcontentloaded')
    log("📄 已打开抖音创作者中心，请扫码或验证码登录...")

    # 等待登录成功 - 监控URL变化到 /creator-micro/
    try:
        page.wait_for_url('**/creator-micro/**', timeout=300000)
        log("✅ URL检测: 已进入创作者后台!")
    except:
        cookies = context.cookies()
        session_cookies = [c for c in cookies if 'session' in c['name'].lower() or 'uid' in c['name'].lower()]
        log(f"⚠️ URL未跳转, 已获取 {len(session_cookies)} 个session cookies")

    page.wait_for_timeout(2000)

    # 保存
    context.storage_state(path=STATE_FILE)
    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        state = json.load(f)
    log(f"💾 保存完成! cookies: {len(state['cookies'])} 个")

    browser.close()
    log("✅ 完成")
