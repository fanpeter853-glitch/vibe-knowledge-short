---
name: vibe-knowledge-short
description: 按「Vibe 知识大赏」形态做知识短视频：深色夜底、宋体大字、代码逐帧演算、无旁白、中英双语字幕、用用户提供的 BGM 卡点。当用户给出一个主题或命题（如"创业的本质是和不确定性共存""为什么天空是蓝的"）要求做成片，要求"做一期知识短片 / vibe 知识大赏那种 / 概念讲解视频"，或给了 BGM 要求卡点出片时使用。不用于 AI 生图拼切、真人出镜、口播带货类视频。
---

# Vibe 知识短片（C 夜曲）

一条片 = 一个抽象命题，用几件实物当场演出来。观众读底部一行字幕的同时，看画面把这句话做完。

本 skill 是产线层：它调 `vibe-knowledge-film` 的渲染引擎，补上固定规格、本机适配脚本和卡点口径。

## 开工前：跑一次 setup

```bash
python scripts/setup.py
```

它做四件事：定位引擎（`vibe-knowledge-film/engine`）→ 补齐 8 个字体（约 45MB，走 CDN 并行）→ 找 ffmpeg → 查 playwright / Chrome。
引擎缺位时先装引擎（GitHub: `HeyChengC/vibe-knowledge-film`，克隆到 `~/.claude/skills/vibe-knowledge-film` 即可），或用 `VKF_ENGINE` 指到它的 engine 目录。

## 先读引擎

动笔前完整读这三份（在引擎目录下）：

- `SKILL.md`：讲解设计八条规矩
- `references/engine.md`：Frame / VKit 全部 API、坑位清单
- `references/worlds.md`：C 夜曲的色板、版式、片名卡、声音规格

`examples/fold_C/film.js`、`examples/info_C/film.js`：**看写法，不搬画面**。

## 固定规格（直接按这套做，不逐条问）

| | |
|---|---|
| 画幅 / 帧率 | 1920×1080，30fps，16:9 |
| 外观 | 只有 C 夜曲（`--world C`） |
| 时长 | 默认 60–70s；BGM 结构允许可到 90s，超过 90s 先问 |
| 字幕 | 中文 14 句左右（每句 3–5s）+ 一行英文；字幕永远最后画 |
| 声音 | 不合成配音、不写旁白；只垫用户 BGM |
| 章数 | 3–5 章，每章一台装置 + 一句定义 |
| 结尾 | 回扣开头的形象，最后只剩一个词，加一行品牌落版 |

## 品牌落版（可改）

收束句之后，右下角一行极淡小字：`好评学弟爱折腾`。换账号只改 film.js 收尾函数那一行，别动版式。

## 流程

1. **立题 + 事实表**。拆成 3–5 个能"当场算"的点，每点写清是哪条公认结论、谁提出、哪一年。片中数据一律示意（固定假随机），film.js 头注释写明"示意，不是真实数据"。
2. **找形象**。每点一件一眼认出的实物（罐子、硬币、曲尺、沙漏、卡片）。点、线、圈、柱子不算形象。全片只用一个世界、一把尺。
3. **文案 + 分镜表**。14 句，先中文再英文；提问、命名、结论不硬配图。模板见 `references/storyboard-template.md`。
4. **建工程**：`python <engine>/../scripts/new_film.py <工程目录> --world C`，照分镜写 `film.js`。先做最难那一镜：`--stills` 看单帧、`--sheet` 看节奏、`--motion` 看转场。
5. **渲片**：`scripts/render_range.py` 分 4 段并行（引擎自带 `--jobs` 不稳定，别用），渲完 `scripts/assemble.py` 拼段 + 垫 BGM + 抽封面。
6. **终检**：`--det` 自检；抽 6 帧看字幕有没有压到装置、装置最低点有没有低于 y=840；确认第 0 帧对齐 BGM 第 0 秒。

## 渲片命令

```bash
# 4 段并行（各自一个进程）
python scripts/render_range.py <工程目录> 0    495 p0
python scripts/render_range.py <工程目录> 495  990 p1
python scripts/render_range.py <工程目录> 990  1485 p2
python scripts/render_range.py <工程目录> 1485 1980 p3
# 拼接 + 混 BGM + 抽封面
python scripts/assemble.py <工程目录> <BGM 路径> 66 <成片路径>
```

总帧数 = 时长 × 30。实测 4 路并行约 0.25s/帧·路，66s 片约 11 分钟。

## 质量线（不可破）

- 中文单句 ≤1400px（`fr.measure` 量）；英文一行放得下。
- 装置最低点 ≥ y=840；y 900–1010 只属于字幕。
- 相邻两章时间窗重叠 0.5s，各自 `ss` 淡入淡出，不许 `if/else` 硬切。
- 随机只用 `rng(seed)` / `hash(n)`；模拟一次算完存表、按 t 查表。
- 每章骨架：暗一下 → 章节标换字 → 装置登场 → 小实验跑 → 年份人名 → 定义 → 暗一下。
- 屏上出现的每个事实都要有出处；没有出处的不写。

## BGM 卡点口径

不是每一拍都动。只卡四类点：满拍进入、鼓点抽空的静场段、鼓点回归、drop。
先量 BPM 和底鼓点，章首对到最近击点，全片最大揭晓（曲线穿零、清零、破掉）对到 drop。
BGM 用 ffmpeg 直接混入（`-t` 截齐、末尾约 1.5s 淡出）；不要用引擎 audio.py 的合成音效去和现成配乐打架。

## 坑位

见 `references/pitfalls.md`。三条最常复发：字体没下齐 → 页面永远不 READY；PATH 里没有 ffmpeg；多进程共用同一临时目录被互相删空。
