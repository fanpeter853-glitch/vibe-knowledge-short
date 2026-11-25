# -*- coding: utf-8 -*-
"""公共解析：引擎目录、ffmpeg、Python。

三件事都做成"先看环境变量，再按已知位置找，找不到给明确报错"，
这样这份 skill 从 Windows 搬到 macOS / 别的 agent 上也能跑。
"""
import os, shutil, sys
from pathlib import Path

# vibe-knowledge-film 引擎的候选位置（相对当前 home 与常见技能根）
CANDIDATES = [
    "~/.claude/skills/vibe-knowledge-film/engine",
    "~/.codex/skills/vibe-knowledge-film/engine",
    "~/workspace/.user_skills/vibe-knowledge-film/engine",
    "~/workspace/.skills/vibe-knowledge-film/engine",
]


def engine():
    p = os.environ.get("VKF_ENGINE")
    if p and (Path(p) / "render.py").exists():
        return Path(p)
    # 1) 与本 skill 同级（仓库里把两个 skill 放在一起时）
    here = Path(__file__).resolve().parent.parent.parent
    for d in [here / "vibe-knowledge-film" / "engine", here.parent / "vibe-knowledge-film" / "engine"]:
        if (d / "render.py").exists():
            return d
    # 2) 常见技能根
    for c in CANDIDATES:
        d = Path(c).expanduser()
        if (d / "render.py").exists():
            return d
    # 3) Windows 上的豆包工作区（本机默认位置）
    base = Path(os.environ.get("LOCALAPPDATA", "")) / "Doubao/User Data/Default/.doubao/agent_mode/workspace"
    if base.exists():
        for sub in [".user_skills", ".skills"]:
            d = base / sub / "vibe-knowledge-film" / "engine"
            if (d / "render.py").exists():
                return d
    sys.exit("找不到 vibe-knowledge-film 引擎。设环境变量 VKF_ENGINE 指向它的 engine 目录，"
             "或把它克隆到 ~/.claude/skills/vibe-knowledge-film。")


def ffmpeg():
    p = os.environ.get("FFMPEG")
    if p and Path(p).exists():
        return p
    p = shutil.which("ffmpeg")
    if p:
        return p
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        sys.exit("找不到 ffmpeg：装一个（brew install ffmpeg / winget install ffmpeg），"
                 "或设 FFMPEG 指向可执行文件，或 pip install imageio-ffmpeg。")
