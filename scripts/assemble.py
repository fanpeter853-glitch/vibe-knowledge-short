# -*- coding: utf-8 -*-
"""拼接分段 + 垫 BGM + 抽封面：

  python assemble.py <工程目录> <BGM> <时长秒> <成片路径> [封面时刻=16.6]

要求 renders/ 里已有 p0.mp4 p1.mp4 …（由 render_range.py 出，按文件名顺序拼）。
BGM 从它的第 0 秒开始铺 —— 所以视频第 0 帧必须等于 BGM 第 0 秒。
"""
import subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _env


def main():
    if len(sys.argv) < 5:
        sys.exit(__doc__)
    proj = Path(sys.argv[1]).resolve()
    bgm = Path(sys.argv[2]).resolve()
    dur = float(sys.argv[3])
    out = Path(sys.argv[4]).resolve()
    cover_t = float(sys.argv[5]) if len(sys.argv) > 5 else 16.6
    ff = _env.ffmpeg()

    r = proj / "renders"
    parts = sorted(r.glob("p*.mp4"), key=lambda q: q.name)
    if not parts:
        sys.exit(f"{r} 里没有 p*.mp4，先跑 render_range.py")
    lst = r / "_parts.txt"
    lst.write_text("".join(f"file '{q.name}'\n" for q in parts), encoding="utf-8")
    joined = r / "joined.mp4"
    subprocess.run([ff, "-v", "warning", "-y", "-f", "concat", "-safe", "0",
                    "-i", str(lst), "-c", "copy", str(joined)], check=True)

    fade_st = max(0.0, dur - 1.5)
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([ff, "-v", "warning", "-y", "-i", str(joined), "-i", str(bgm),
                    "-map", "0:v", "-map", "1:a", "-t", f"{dur}", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k",
                    "-af", f"afade=in:st=0:d=0.25,afade=out:st={fade_st:.2f}:d=1.5", str(out)], check=True)

    cover = out.parent / f"封面_{out.stem}.png"
    subprocess.run([ff, "-v", "error", "-y", "-ss", f"{cover_t}", "-i", str(out),
                    "-frames:v", "1", str(cover)], check=True)
    print(f"成片 {out}  {out.stat().st_size / 1e6:.1f}MB\n封面 {cover}")


if __name__ == "__main__":
    main()
