# -*- coding: utf-8 -*-
"""调研 #29：技能沉淀周期 —— 汇总高赞评论 + 字幕片段，产出引语候选池"""
import os, json, glob

BASE = r"D:\11.project\iwen-dsh\doubao-list\ActivityWatch\selfQuestion\AI练口语阶梯-调研\原始数据\B站"
CMT_DIR = os.path.join(BASE, "评论")
SUB_DIR = os.path.join(BASE, "字幕")

print("========== 高赞评论候选池（每视频按点赞排序） ==========\n")
for fp in sorted(glob.glob(os.path.join(CMT_DIR, "*.json"))):
    d = json.load(open(fp, encoding="utf-8"))
    print(f"\n### {d['bvid']} | {d['title'][:46]} | 评论{d['count']}条")
    cs = sorted(d["comments"], key=lambda x: x["like"], reverse=True)
    for c in cs[:14]:
        msg = c["message"].replace("\r", " ").replace("\n", " ⏎ ")
        print(f"  [{c['like']:>5}赞] {msg[:110]}")
        for sc in sorted(c["subs"], key=lambda x: x["like"], reverse=True)[:2]:
            sm = sc["message"].replace("\r", " ").replace("\n", " ⏎ ")
            print(f"        └ [{sc['like']:>4}赞] {sm[:90]}")

print("\n\n========== 字幕片段（每视频抽样，含时间戳） ==========\n")
for fp in sorted(glob.glob(os.path.join(SUB_DIR, "*.json"))):
    d = json.load(open(fp, encoding="utf-8"))
    print(f"\n### {d['bvid']} | {d['title'][:46]}")
    for sub in d["subs"]:
        body = sub["body"]
        picks = list(range(0, len(body), max(1, len(body)//14)))[:14]
        for i in picks:
            seg = body[i]
            t = int(seg.get("from", 0))
            print(f"  [{t//60:02d}:{t%60:02d}] {seg['content'][:80]}")
