# 生成材料音频（edge-tts 可复用脚本）

> 用法：改 TEXT（新材料的 3 句，句与句之间空行），改 JOBS（音色/语速/文件名），然后：
> `"C:/Users/Rose/.workbuddy-ai/binaries/python/envs/default/Scripts/python.exe" 本脚本.py`
> 输出到 `record/L1材料音频/`。**整周只用其中一版，选定后不换。**

import asyncio, os, sys
import edge_tts

TEXT = (
    "The AI gives me a training plan that tells me how many pull-ups I should do each week, and I just follow it."
    "\n\n"
    "When my form is off, I can ask it to explain the movement again."
    "\n\n"
    "My goal is to add weight little by little until I can bench press 70 kilos."
)

WORDS = 54  # 原文词数，用于语速估算

OUT_DIR = r"D:/11.project/iwen-codex/codex-list/OralTracker/record/L1材料音频"

JOBS = [
    # (voice, rate, 文件名)
    ("en-US-AriaNeural",   "-20%", "材料A1_标准157_Aria.mp3"),   # ≈160 wpm，本周选定
    ("en-US-AriaNeural",   "-10%", "材料A1_进阶175_Aria.mp3"),   # ≈179 wpm
    ("en-GB-SoniaNeural",  "-15%", "材料A1_英音165_Sonia.mp3"),  # ≈176 wpm
]

BR2 = [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160, 0]  # MPEG-2 L3 码率表


def mp3_duration(path):
    """无 ffprobe 时用帧头码率估算时长（edge-tts 输出为 CBR）。"""
    d = open(path, "rb").read()
    i = 0
    if d[:3] == b"ID3":
        sz = (d[6] << 21) | (d[7] << 14) | (d[8] << 7) | d[9]
        i = 10 + sz
    while i < len(d) - 4 and not (d[i] == 0xFF and (d[i + 1] & 0xE0) == 0xE0):
        i += 1
    br = BR2[(d[i + 2] >> 4) & 15]
    return (len(d) - i) * 8 / (br * 1000)


async def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for voice, rate, name in JOBS:
        out = os.path.join(OUT_DIR, name)
        await edge_tts.Communicate(TEXT, voice, rate=rate).save(out)
        dur = mp3_duration(out)
        print("%-30s %5.1fs  ~%d wpm (%d words)" % (name, dur, round(WORDS / dur * 60), WORDS))


if __name__ == "__main__":
    asyncio.run(main())
