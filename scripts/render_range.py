# -*- coding: utf-8 -*-
"""按帧区间渲一段：python render_range.py <工程目录> <起始帧> <结束帧> <名字>

引擎自带的 --jobs 有多页面同时拉字体、临时目录互相删的问题；这个脚本一段一个页面、
一段一个独立临时目录，出 PNG 后自己编码成 mp4，最后由 assemble.py 拼接。

依赖位置全部交给 _env：引擎目录、ffmpeg 都能用环境变量覆盖。
"""
import shutil, subprocess, sys, time, os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _env

ENG = _env.engine()
sys.path.insert(0, str(ENG))
import render as R
from playwright.sync_api import sync_playwright


def launch(p):
    """优先用本机 Chrome（出帧快）；没有就用 playwright 自带 chromium。"""
    try:
        return p.chromium.launch(channel="chrome", args=["--disable-lcd-text", "--force-color-profile=srgb"])
    except Exception:
        return p.chromium.launch(args=["--disable-lcd-text", "--force-color-profile=srgb"])


def main():
    if len(sys.argv) < 5:
        sys.exit(__doc__)
    proj = Path(sys.argv[1]).resolve()
    a, b, name = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    ff = _env.ffmpeg()
    (proj / "renders").mkdir(exist_ok=True)
    out = proj / "renders" / f"{name}.mp4"
    d = proj / "renders" / f"_tmp_{name}_{os.getpid()}"
    if d.exists():
        shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True)
    srv, url = R.serve(proj)
    t0 = time.time()
    with sync_playwright() as p:
        br = launch(p)
        pg = br.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
        pg.on("pageerror", lambda e: print("[pageerror]", str(e)[:200], flush=True))
        pg.goto(url)
        pg.wait_for_function("window.READY === true", timeout=120000)
        fps = pg.evaluate("FPS")
        for i in range(a, b):
            pg.evaluate(f"seek({i / fps})")
            (d / f"{i - a:05d}.png").write_bytes(pg.screenshot(type="png"))
            if (i - a) % 50 == 0:
                print(f"{name} {i - a}/{b - a} ({time.time() - t0:.0f}s)", flush=True)
        br.close()
    srv.shutdown()
    subprocess.run([ff, "-v", "warning", "-y", "-framerate", str(fps), "-start_number", "0",
                    "-i", str(d / "%05d.png"), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-crf", "14", "-preset", "medium", str(out)], check=True)
    shutil.rmtree(d, ignore_errors=True)
    print(f"{name} done {out.stat().st_size / 1e6:.1f}MB ({time.time() - t0:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
