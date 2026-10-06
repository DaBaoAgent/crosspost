"""
小红书 API 图文发布脚本
使用 xhs 库纯 Python API，无需浏览器
用法: 修改下面的 COOKIE、FOLDER、TITLE、DESC、TOPICS，然后:
  /c/Users/xxx13/AppData/Local/Programs/Python/Python312/python.exe xhs_publish.py
"""
import os, sys
os.environ['PYTHONUTF8'] = '1'
sys.stdout.reconfigure(encoding='utf-8')

from pathlib import Path
from xhs import XhsClient
from xhs.help import sign

# ================ 配置区 ================
# Cookie 从统一文件读取（避免硬编码过期）
COOKIE_FILE = os.path.expanduser(r"~\.hermes\data\xhs_cookie_latest.txt")
with open(COOKIE_FILE, encoding='utf-8') as f:
    COOKIE = f.read().strip()

def sign_wrapper(uri, data=None, a1="", web_session=""):
    """纯Python签名，无需Playwright。a1必须keyword传参"""
    return sign(uri, data, a1=a1)

# 素材文件夹（每个子文件夹5张图 = 1个帖子）
FOLDER = Path(r"D:\BaiduSyncdisk\8 本地推素材\@自动发图文素材库\大宝小红书\29-已发(抖音)")
files = sorted([str(f) for f in FOLDER.glob("*.png")] + [str(f) for f in FOLDER.glob("*.jpg")])

# 文案（标题≤20字，正文无emoji）
TITLE = "爸妈来苏州旅游？昆山轮椅日租✨"
DESC = """爸妈来苏州玩走不动路？别让出行成为遗憾👨‍👩‍👧

昆山佳康顺轮椅日租来帮忙！几乎全新品牌轮椅，干净卫生，每次用完都深度消毒🧹

全昆山可自取，也可以配送到家，超方便🚗

不管是老人出行、术后康复还是临时受伤，随租随用，不用了随时还～

👉 点主页了解更多，或直接私信咨询

📍昆山佳康顺UNQ

#轮椅出租 #轮椅租赁 #出行辅助 #昆山轮椅 #佳康顺"""

# 话题标签（必须 [{"name":"xxx"}, ...] 格式）
TOPICS = [{"name": "轮椅出租"}, {"name": "轮椅租赁"}, {"name": "出行辅助"}]
# ========================================


print(f"📁 文件夹: {FOLDER.name}")
print(f"📷 图片: {len(files)}张")
for f in files:
    print(f"   - {Path(f).name}")

print(f"\n🚀 开始发布...")
client = XhsClient(cookie=COOKIE, timeout=60, sign=sign_wrapper)
result = client.create_image_note(
    title=TITLE, desc=DESC, files=files,
    topics=TOPICS, is_private=False
)
print(f"✅ 小红书发布成功! 笔记ID: {result['id']}")
print(f"🔗 链接: https://www.xiaohongshu.com/discovery/item/{result['id']}")

# 标记已发
new_name = f"{FOLDER.name}-已发(小红书)"
FOLDER.rename(FOLDER.parent / new_name)
print(f"✅ 已标记: {FOLDER.name} → {new_name}")
