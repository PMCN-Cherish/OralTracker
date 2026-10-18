# -*- coding: utf-8 -*-
"""调研 #31：引语回源核对
规矩沿用体系：只去空白（norm），不补标点，错字照录；命中取点赞最高。
用法：python s5_quote_check.py
"""
import json, os, re

BASE = r"D:\11.project\iwen-codex\codex-list\OralTracker\06-L0L1安排与实现-调研\原始数据\B站"
CMT = os.path.join(BASE, "评论")

_cache = {}


def norm(s):
    return re.sub(r"\s+", "", s or "")


def load(bv):
    if bv not in _cache:
        _cache[bv] = json.load(open(os.path.join(CMT, bv + ".json"), encoding="utf-8"))
    return _cache[bv]


def check(bv, quote):
    d = load(bv)
    q = norm(quote)
    best = None
    for c in d["comments"]:
        if q in norm(c["message"]):
            if best is None or c["like"] > best[0]:
                best = (c["like"], "主楼")
        for s in c.get("subs", []):
            if q in norm(s["message"]):
                if best is None or s["like"] > best[0]:
                    best = (s["like"], "楼中楼")
    return best


QUOTES = [
    ("Q01", "BV1pV411v7cN", "这种100遍跟读我真坚持过一阵，发音和语感确实会好一点，但一离开跟读的就会卡"),
    ("Q02", "BV1pV411v7cN", "我脑子里全是背过的句子，硬是接不上"),
    ("Q03", "BV1z2421Z7C9", "我现在跟读没问题、听也没问题，但一到自己张嘴就卡"),
    ("Q04", "BV1mi4y117z1", "单词发音准确性很低，但是自己意识不到这个准确性，听自己的录音也听不出来，怎么办"),
    ("Q05", "BV1LEiKBwET2", "读错了你记忆中的这个词声音就是错的了"),
    ("Q06", "BV1LEiKBwET2", "如果一半都听不懂，就说明你的听力材料有点难不适合你"),
    ("Q07", "BV1xb411v7Xq", "难度适中，至少懂70%"),
    ("Q08", "BV1xb411v7Xq", "刚开始的时候每天要花一到两个小时"),
    ("Q09", "BV1GL4y1i7bs", "听不出来还影响我说重音"),
    ("Q10", "BV18A411K7kJ", "口音就是英语的美丽所在，发音才是大部分中国英语学习者该纠正的问题。accent和pronunciation是有本质的区别的"),
    ("Q11", "BV18A411K7kJ", "我以为是21分钟，再看一眼210小时"),
    ("Q12", "BV1Rv411W71b", "手机计时一分钟，在此期间即兴选择一个主题不间断的使用英语演讲一分钟"),
    ("Q13", "BV1184y1E7zY", "不要反复改口，可以后来听自己的录音找语法错误，下一遍纠正"),
    ("Q14", "BV1M5m5Y2EP7", "第一轮过去基本没记住什么。但是我开启了第二轮，第三轮以后，掌握的就越来越多"),
    ("Q15", "BV1pV411v7cN", "只要你练的不流畅就一定有发音错误"),
    ("Q16", "BV17T4y1P7Pn", "方便录音对比"),
    ("Q17", "BV18A411K7kJ", "发音错误就是听不懂"),
    ("Q18", "BV1LEiKBwET2", "你必须会读，你才能听得懂听力"),
]

ok = 0
lines = []
for qid, bv, text in QUOTES:
    r = check(bv, text)
    if r:
        ok += 1
        lines.append(f"{qid} PASS | {bv} | {r[1]} | {r[0]}赞 | {text}")
    else:
        lines.append(f"{qid} FAIL | {bv} | 未命中 | {text}")

lines.append(f"\n结果：{ok}/{len(QUOTES)} PASS，{len(QUOTES)-ok} FAIL")
out = "\n".join(lines)
print(out)
open(os.path.join(os.path.dirname(BASE), "引语核对.txt"), "w", encoding="utf-8").write(out)
