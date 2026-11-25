# -*- coding: utf-8 -*-
"""一条命令把环境准备好：python setup.py

做四件事：定位引擎 → 查/补 8 个字体 → 查 ffmpeg → 查 playwright。
换机器（或第一次在别的 agent 上打开这份 skill）先跑它。
"""
import concurrent.futures, sys, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _env

FONTS = {
    "NotoSerifSC-VF.ttf": "notoserifsc/NotoSerifSC%5Bwght%5D.ttf",
    "NotoSansSC-VF.ttf": "notosanssc/NotoSansSC%5Bwght%5D.ttf",
    "CormorantGaramond.ttf": "cormorantgaramond/CormorantGaramond%5Bwght%5D.ttf",
    "CormorantGaramond-Italic.ttf": "cormorantgaramond/CormorantGaramond-Italic%5Bwght%5D.ttf",
    "Lora.ttf": "lora/Lora%5Bwght%5D.ttf",
    "Lora-Italic.ttf": "lora/Lora-Italic%5Bwght%5D.ttf",
    "JetBrainsMono.ttf": "jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf",
    "CourierPrime-Regular.ttf": "courierprime/CourierPrime-Regular.ttf",
}
MIRRORS = [
    # 大文件（思源宋体 25MB）在 jsdelivr 上会 403，raw 是唯一稳定源，所以放最前
    "https://raw.githubusercontent.com/google/fonts/main/ofl/",
    "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/",
    "https://fastly.jsdelivr.net/gh/google/fonts@main/ofl/",
]


def one(item, fonts_dir):
    name, rel = item
    dst = fonts_dir / name
    if dst.exists() and dst.stat().st_size > 50_000:
        return name, "已有"
    for base in MIRRORS:
        try:
            req = urllib.request.Request(base + rel, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://github.com/"})
            with urllib.request.urlopen(req, timeout=240) as r:
                data = r.read()
            if len(data) > 50_000:
                tmp = dst.with_suffix(".part")
                tmp.write_bytes(data)
                tmp.replace(dst)
                return name, f"ok {len(data)//1024}KB"
        except Exception as e:
            last = str(e)[:50]
    return name, f"失败 {last}"


def main():
    eng = _env.engine()
    print(f"引擎  {eng}")
    fonts = eng / "fonts"
    fonts.mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        for name, msg in ex.map(lambda kv: one(kv, fonts), FONTS.items()):
            print(f"字体  {name:32s} {msg}")
    print(f"ffmpeg {_env.ffmpeg()}")
    try:
        import playwright  # noqa: F401
        print("playwright OK")
        import shutil as sh
        print("本机 Chrome:", sh.which("chrome") or sh.which("google-chrome") or
              ("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" if Path("C:/Program Files/Google/Chrome/Application/chrome.exe").exists() else "未找到（可用 playwright 自带 chromium）"))
    except ImportError:
        print("缺 playwright：pip install playwright；再 python -m playwright install chromium")
    print("下一步：照 SKILL.md 的流程建工程 → 写 film.js → render_range.py 分段 → assemble.py 出片")


if __name__ == "__main__":
    main()
