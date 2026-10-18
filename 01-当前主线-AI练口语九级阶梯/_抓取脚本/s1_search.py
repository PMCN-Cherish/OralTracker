# -*- coding: utf-8 -*-
"""调研 #30：非母语者用 AI 提升口语的阶梯式学习 —— B站搜索
八组关键词（按问题结构分组，不按近义词分组）
输出：原始数据/B站/搜索清单.json
"""
import sys, os, re, json, time, hashlib, urllib.parse
import requests
sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool

OUT = r"D:\11.project\iwen-dsh\doubao-list\ActivityWatch\selfQuestion\AI练口语阶梯-调研\原始数据\B站\搜索清单.json"

pool = BiliCookiePool()
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                  "Referer": "https://www.bilibili.com/"})

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,57,62,11,36,20,34,44,52]

def sign(params):
    nav = s.get("https://api.bilibili.com/x/web-interface/nav", timeout=15).json()
    wbi = nav["data"]["wbi_img"]
    img = wbi["img_url"].rsplit("/",1)[-1].split(".")[0]
    sub = wbi["sub_url"].rsplit("/",1)[-1].split(".")[0]
    mixin_key = "".join((img+sub)[i] for i in MIXIN)[:32]
    p = dict(params)
    p["wts"] = str(int(time.time()))
    q = urllib.parse.urlencode(sorted(p.items()))
    p["w_rid"] = hashlib.md5((q+mixin_key).encode()).hexdigest()
    return p

keyword_groups = [
    ("AI练口语实操", ["AI练英语口语", "ChatGPT练口语", "AI外教 口语", "豆包 练口语", "AI口语陪练 效果"]),
    ("说不出口与卡壳", ["哑巴英语 怎么破", "英语 说不出口", "英语 卡壳 没词", "英语 脑子空白", "看得懂 说不出"]),
    ("发音与可懂度", ["英语 连读 弱读", "英语 重音 节奏", "英语 发音 纠正", "中式口音 怎么办", "英语 语调"]),
    ("流利度与思维", ["英语思维 怎么练", "英语 反应速度", "不翻译 直接说英语", "英语 组织句子 慢"]),
    ("跟读复述与精听", ["影子跟读 方法", "英语 复述 练习", "精听 方法", "回音法 英语", "英语 朗读 训练"]),
    ("真人迁移与陪练", ["英语 口语 外教 值不值", "语言交换 经验", "英语角 有用吗", "口语 从零到流利"]),
    ("可量化评分标准", ["雅思口语 评分标准", "雅思口语 6分 7分 差距", "托福口语 评分", "口语 流利度 怎么衡量"]),
    ("时间少的成年人", ["上班族 学英语 口语", "成年人 学英语 多久", "每天 半小时 英语口语", "英语口语 三个月"]),
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

W = [("AI", 10), ("ChatGPT", 12), ("口语", 12), ("流利", 12), ("哑巴", 12), ("说不出口", 13),
     ("卡", 8), ("发音", 10), ("口音", 9), ("连读", 10), ("重音", 9), ("语调", 9),
     ("思维", 10), ("跟读", 12), ("复述", 11), ("影子", 12), ("精听", 9), ("外教", 9),
     ("雅思", 9), ("托福", 8), ("方法", 7), ("多久", 9), ("教程", 7), ("零基础", 8),
     ("进阶", 8), ("突破", 9), ("自学", 8), ("实操", 8), ("亲测", 9), ("有效", 9),
     ("经验", 7), ("讲解", 6), ("原理", 7), ("误区", 9), ("真相", 8), ("上班族", 9)]
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
    json.dump({"total": len(all_results), "top50": scored[:50], "all": list(all_results.values())}, f, ensure_ascii=False, indent=2)
print(f"\n已保存到: {OUT}", flush=True)
