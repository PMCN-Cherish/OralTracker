# -*- coding: utf-8 -*-
"""调研 #31：汇总高赞评论 + 字幕片段，产出候选池（不分级，按视频列全部高赞）"""
import os, json, glob

BASE = r"D:\11.project\iwen-codex\codex-list\OralTracker\06-L0L1安排与实现-调研\原始数据\B站"
CMT_DIR = os.path.join(BASE, "评论")
SUB_DIR = os.path.join(BASE, "字幕")

tot = 0
print("========== 高赞评论 ==========")
for fp in sorted(glob.glob(os.path.join(CMT_DIR, "*.json"))):
    d = json.load(open(fp, encoding="utf-8"))
    tot += d["count"]
    print(f"\n### {d['bvid']} | {d['title'][:50]} | {d['count']}条")
    cs = sorted(d["comments"], key=lambda x: x["like"], reverse=True)
    for c in cs[:20]:
        msg = c["message"].replace("\r", " ").replace("\n", " ⏎ ")
        print(f"  [{c['like']:>5}赞] {msg[:120]}")
        for sc in sorted(c["subs"], key=lambda x: x["like"], reverse=True)[:2]:
            sm = sc["message"].replace("\r", " ").replace("\n", " ⏎ ")
            print(f"        └ [{sc['like']:>4}] {sm[:100]}")

print(f"\n\n合计评论：{tot} 条")

print("\n\n========== 字幕片段 ==========")
for fp in sorted(glob.glob(os.path.join(SUB_DIR, "*.json"))):
    d = json.load(open(fp, encoding="utf-8"))
    print(f"\n### {d['bvid']} | {d['title'][:50]}")
    for sub in d["subs"]:
        body = sub["body"]
        picks = list(range(0, len(body), max(1, len(body) // 16)))[:16]
        for i in picks:
            seg = body[i]
            t = int(seg.get("from", 0))
            print(f"  [{t//60:02d}:{t%60:02d}] {seg['content'][:90]}")
