# -*- coding: utf-8 -*-
"""调研 #31：L0/L1 的安排与实现 —— B站搜索
分组逻辑：按「L0/L1 的哪个决策」分（遍数 / 剂量 / 自测 / 材料 / 可懂度）
输出：原始数据/B站/搜索清单.json
"""
import sys, os, re, json, time, hashlib, urllib.parse
import requests
sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool

OUT = r"D:\11.project\iwen-codex\codex-list\OralTracker\06-L0L1安排与实现-调研\原始数据\B站\搜索清单.json"

pool = BiliCookiePool()
s = requests.Session()
s.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Referer": "https://www.bilibili.com/"})

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,57,62,11,36,20,34,44,52]


def sign(params):
    nav = s.get("https://api.bilibili.com/x/web-interface/nav", timeout=15).json()
    wbi = nav["data"]["wbi_img"]
    img = wbi["img_url"].rsplit("/", 1)[-1].split(".")[0]
    sub = wbi["sub_url"].rsplit("/", 1)[-1].split(".")[0]
    mixin_key = "".join((img + sub)[i] for i in MIXIN)[:32]
    p = dict(params)
    p["wts"] = str(int(time.time()))
    q = urllib.parse.urlencode(sorted(p.items()))
    p["w_rid"] = hashlib.md5((q + mixin_key).encode()).hexdigest()
    return p


keyword_groups = [
    ("遍数与重复", ["英语 朗读 几遍", "跟读 多少遍", "英语 重复 练习", "精听 几遍", "回音法 英语"]),
    ("发音剂量与周期", ["发音 练习 多久", "纠音 训练", "中式口音 怎么改", "音标 重学 有用吗", "发音 每天 练"]),
    ("可懂度与听不清", ["英语 别人听不懂", "老外 听不懂 我说话", "英语 语速 快 听不清", "英语 连读 听不出来"]),
    ("录音与自测", ["录音 练英语", "口语 录音 复盘", "自己 练口语 方法", "口语 自查"]),
    ("材料与选材", ["跟读 材料 怎么选", "英语 朗读 材料", "新概念 背诵 有用吗", "TED 跟读"]),
    ("AI纠音实测", ["AI 纠音", "发音 打分 准吗", "AI 学英语 实测", "语音识别 测发音"]),
    ("时间少的成年人", ["每天 10分钟 英语", "碎片时间 练口语", "上班族 练口语 时间"]),
    ("成年人重学", ["成年人 重学英语", "工作后 英语 口语", "英语 退化 恢复"]),
]

all_results = {}
for group_name, keywords in keyword_groups:
    print(f"\n=== 分组: {group_name} ===", flush=True)
    for kw in keywords:
        cookie = pool.get_cookie()
        s.headers["Cookie"] = cookie
        try:
            p = sign({"search_type": "video", "keyword": kw, "page": 1, "page_size": 20})
            r = s.get("https://api.bilibili.com/x/web-interface/wbi/search/type", params=p, timeout=20)
            d = r.json()
            if d.get("code") == 0 and d.get("data", {}).get("result"):
                results = d["data"]["result"]
                print(f"  [{kw}] {len(results)}条", flush=True)
                for v in results:
                    bvid = v.get("bvid", "")
                    if bvid and bvid not in all_results:
                        title = re.sub(r"<[^>]+>", "", v.get("title", ""))
                        all_results[bvid] = {
                            "bvid": bvid, "title": title, "author": v.get("author", ""),
                            "play": v.get("play", 0), "duration": v.get("duration", ""),
                            "keyword": kw, "group": group_name,
                        }
                pool.report_success()
            else:
                print(f"  [{kw}] code={d.get('code')} msg={d.get('message','')}", flush=True)
                if d.get("code") == -412:
                    pool.report_412()
        except Exception as e:
            print(f"  [{kw}] 错误: {e}", flush=True)
        time.sleep(1.5)

print(f"\n\n=== 总计去重后: {len(all_results)} 个视频 ===", flush=True)

# 权重：本次主题是「安排与实现」，故「几遍/多久/每天/周期/录音/自测/材料」权重最高
W = [("几遍", 14), ("重复", 13), ("每天", 12), ("多久", 12), ("分钟", 11), ("周期", 12),
     ("录音", 12), ("自测", 12), ("纠音", 12), ("发音", 11), ("口音", 10), ("连读", 9),
     ("语调", 8), ("跟读", 11), ("精听", 10), ("材料", 9), ("方法", 7), ("教程", 7),
     ("零基础", 8), ("上班族", 10), ("碎片", 9), ("成年人", 9), ("误区", 9), ("真相", 8),
     ("亲测", 9), ("实操", 8), ("经验", 7), ("原理", 7), ("口语", 8), ("英语", 3)]


def score(v):
    t = (v["title"] or "").lower()
    sc = sum(w for k, w in W if k.lower() in t)
    p = v.get("play") or 0
    sc += 4 if p > 500000 else 3 if p > 150000 else 2 if p > 40000 else 1 if p > 10000 else -2
    return sc


scored = sorted(all_results.values(), key=lambda x: score(x), reverse=True)
for i, v in enumerate(scored[:50]):
    print(f"  #{i+1} [{score(v)}分] {v['title'][:56]} | {v['author']} | 播放={v['play']} | {v['bvid']}", flush=True)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump({"total": len(all_results), "top50": scored[:50], "all": list(all_results.values())},
              f, ensure_ascii=False, indent=2)
print(f"\n已保存到: {OUT}", flush=True)
