# 三平台发布技能 - 环境安装指南

## 前置依赖

在目标电脑上安装以下 Python 包（需要 Python 3.12+）：

```bash
pip install xhs playwright camoufox browser-cookie3 --proxy="" --trusted-host pypi.org --trusted-host files.pythonhosted.org

# 安装 Playwright Chromium
playwright install chromium
```

## 技能安装

将整个 `three-platform-publisher` 文件夹复制到目标 Hermes 的 skills 目录：

```
~/.hermes/skills/multi-platform-uploader/three-platform-publisher/
```

## 配置（每台电脑独立）

### 小红书
- Cookie 从 Chrome DevTools → creator.xiaohongshu.com → 复制完整 Cookie 字符串
- 在 `scripts/xhs_publish.py` 中修改 `COOKIE` 变量

### 抖音
- 首次使用需运行 `scripts/douyin_login.py` 获取登录态
- 或从已登录的 Chrome 导出 Cookie 到 `~/.hermes/browser-profiles/douyin_state.json`

### 闲鱼
- 从 Chrome DevTools → goofish.com → 复制关键 cookies
- 在 `scripts/xianyu_publish.py` 中修改 `COOKIES` 列表
- 必需 cookies: cookie2, _tb_token_, cna, havana_lgc2_77, unb, _m_h5_tk, sgcookie, csg, tfstk

## 素材目录

默认素材路径（可在脚本中修改）：
```
D:\BaiduSyncdisk\8 本地推素材\chatgtp出图\
```

每个子文件夹为一个帖子（5张图），命名规则：数字编号（如 5, 6, 7...）

## 运行方式

通过 Hermes 的 terminal 调用系统 Python：
```
/c/Users/xxx13/AppData/Local/Programs/Python/Python312/python.exe scripts/xhs_publish.py
```
> ⚠️ 不能用 execute_code（沙箱环境无系统包）

## 已验证版本
- Python 3.12
- xhs 0.2.13
- playwright 1.59.0
- camoufox 0.4.11 (仅备用，Cookie注入方案不需要)
- Windows 11
