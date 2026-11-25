# 本机（Windows + 中文用户名）踩过的坑

按出现频率排。每条都给出确认方法和改法。

## 1. 字体没下齐 → 页面永远不 READY

`vk.js` 结尾是 `document.fonts.load(...)` 八个字体族，任一文件 404 会让整个 `Promise.all` 拒绝，`window.READY` 永远不置 true，`render.py` 就卡在 `wait_for_function` 直到 180s 超时。

- 确认：`...\.skills\vibe-knowledge-film\engine\fonts\` 下应有 8 个 ttf（NotoSerifSC-VF、NotoSansSC-VF、CormorantGaramond、CormorantGaramond-Italic、Lora、Lora-Italic、JetBrainsMono、CourierPrime-Regular）。
- 仓库自带的 `get_fonts.py` 走 raw.githubusercontent，两个中文各 20MB，经常卡几分钟；改用 jsdelivr：
  `https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/<family>/<File>%5Bwght%5D.ttf`
  并行下载最快。注意 CourierPrime-Regular.ttf 本身只有 ~70KB，别用"小于 100KB 判定失败"的阈值。
- 症状对照：报错是 `Page.wait_for_function: Timeout 180000ms exceeded`，且控制台有 `[pageerror] xxx is not defined` 时，那是 film.js 自己的运行时错误（比如忘了解构 `rng`），跟字体无关。

## 2. PATH 里没有 ffmpeg

`render.py` 直接 `subprocess.Popen(["ffmpeg", ...])`。本机没有系统 ffmpeg，只有 imageio-ffmpeg 自带二进制。

- 兜底：`import imageio_ffmpeg; imageio_ffmpeg.get_ffmpeg_exe()`。
- 或复制到一个 `tools\` 目录并把该目录加进本次调用的 `$env:PATH`。
- 编码参数用 `-crf 14 -preset medium` 即可；`+faststart` 在管道输入时容易在收尾阶段挂住，分段编码不要加。

## 3. 多个渲染进程共用同一临时目录 → 互相删空

`shutil.rmtree` 与另一个进程写 PNG 撞车，结果是某段目录缺帧（例如只剩 00033.png 起始），ffmpeg 报 `Could find no file or sequence with path ...`，退出码 -2。

- 改法：临时目录名带 pid（`_tmp_<name>_<pid>`），编码时显式 `-start_number 0`，删目录用 `ignore_errors=True`。
- 只起一批进程；重复 `Start-Process` 会把上一批的目录删掉。

## 4. 引擎 `--jobs` 不可靠，自己分段

`frames_parallel` 会起 4 个 `--clip` 子进程，本机上 4 个页面同时拉 43MB 字体 + 4 条 ffmpeg 管道，实测会停在 48 字节的空 mp4。用 `render_range.py` + `assemble.py` 替代。

实测速率：4 路并行约 0.25s/帧·路，1980 帧（66s）约 11 分钟，产出约 17MB。

## 5. 字幕压到装置 / 装置压到字幕

字幕区是 y 900–1010。装置最低点必须 ≥ y=840。两罐并排时，右侧"摸出来的球"要落在 y≈688（球心），别放到 704 否则会盖住 y=684 的英文小标。

## 6. 中英小标重叠

`fr.text` 的 `track` 是像素字距，中文 4 字 22px + 12 字距实际宽度约 130px，英文起点别按估算排，直接 `fr.measure` 量一遍或用 190px 以上的偏移。

## 7. PowerShell 传参

- 不要用 `Start-Process -ArgumentList` 传含空格的路径而不加引号。
- `"a" + ($arr | %{...} -join ",")` 这种写法会触发参数绑定错误，先存变量再拼。
