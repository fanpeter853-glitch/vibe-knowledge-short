# vibe-knowledge-short

[English](README.en.md) · **中文**

「Vibe 知识大赏」形态的知识短视频产线：深色夜底、宋体大字、**代码逐帧演算**、无旁白、
中英双语字幕、用你提供的 BGM 卡点。

一条片 = 一个抽象命题，用几件实物当场演出来。观众读底部一行字幕的同时，看画面把这句话做完。

![preview](preview.gif)

*（成片《创业的本质，是和不确定性共存》前 14.5 秒）*

这个 skill 只管**产线**：它调用 [`vibe-knowledge-film`](https://github.com/HeyChengC/vibe-knowledge-film)
的渲染引擎（Canvas + `seek(t)` 逐帧、C 夜曲外观），补上固定规格、本机适配脚本和卡点口径。

## 安装

```bash
git clone https://github.com/fanpeter853-glitch/vibe-knowledge-short.git ~/.claude/skills/vibe-knowledge-short
git clone https://github.com/HeyChengC/vibe-knowledge-film.git ~/.claude/skills/vibe-knowledge-film   # 引擎
python ~/.claude/skills/vibe-knowledge-short/scripts/setup.py                                        # 字体 + 依赖自检
```

任何"读 `SKILL.md` 干活"的 agent（Claude Code、Codex、Cursor、自建 agent）把文件夹放进它的
skills 目录即可。只吃 zip 的客户端，压缩这个目录再导入（不必包含引擎和字体，`setup.py` 会自己补齐）。

**Meta Muse 这类不接受自定义技能的 App**：用 [`MUSE-paste.md`](MUSE-paste.md)，把里面那段说明书
整段贴进对话即可——它只负责设计（分镜表 / 字幕表 / 卡点表），渲染回到本机跑。

依赖：Python 3.10+、`playwright`（用本机 Chrome，没有则用自带 chromium）、`numpy`、`scipy`、
`Pillow`、`ffmpeg`。

## 用起来是什么样

```
用户：做一期《为什么天空是蓝色的》，BGM 用这首，60 秒左右
agent：读 SKILL.md → 填分镜表 → 建工程 → 写 film.js → 分段渲 → 垫 BGM → 出片 + 封面
```

人工只需要给三样：**主题**、**BGM**、**时长偏好**。其余（形象、分镜、字幕、卡点、出处）由产线负责。

## 目录

```
SKILL.md                        产线规则（agent 读这个）
scripts/
  setup.py                      一次把引擎/字体/ffmpeg/playwright 备好
  _env.py                       路径解析（跨平台，可用 VKF_ENGINE / FFMPEG 覆盖）
  render_range.py               按帧区间渲染一段（4 段并行用）
  assemble.py                   拼段 + 混 BGM + 抽封面
references/
  pitfalls.md                   踩过的坑（字体、ffmpeg、临时目录、字幕压版）
  storyboard-template.md        分镜表 / 字幕表模板
MUSE-paste.md                   Meta Muse 用的粘贴版说明书
```

## 授权

MIT。引擎与字体各自遵循上游授权（引擎 MIT；字体 SIL OFL 1.1，由 `setup.py` 从 Google Fonts 下载，不入库）。
