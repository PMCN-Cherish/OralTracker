# -*- coding: utf-8 -*-
"""调研 #31：L0/L1 的安排与实现 —— 精抓（评论含楼中楼 + 中文字幕）
输出：原始数据/B站/{评论,字幕}/<bvid>.json
"""
import sys, os, re, json, time, hashlib, urllib.parse
import requests

OUT_DIR = r"D:\11.project\iwen-codex\codex-list\OralTracker\06-L0L1安排与实现-调研\原始数据\B站"
SUB_DIR = os.path.join(OUT_DIR, "字幕")
CMT_DIR = os.path.join(OUT_DIR, "评论")
os.makedirs(SUB_DIR, exist_ok=True)
os.makedirs(CMT_DIR, exist_ok=True)

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")


def load_cookie(p):
    return open(p, encoding="utf-8-sig").read().strip()


COOKIES = [load_cookie(r"D:\11.project\iwen-codex\bilibili-cookies\account2.txt"),
           load_cookie(r"D:\11.project\iwen-codex\bilibili-cookies\account3.txt")]
ci = 0
s = requests.Session()
s.headers.update({"User-Agent": UA, "Referer": "https://www.bilibili.com/"})


def apply_cookie():
    s.headers["Cookie"] = COOKIES[ci % len(COOKIES)]


def rotate():
    global ci
    ci += 1
    apply_cookie()


apply_cookie()

nav = s.get("https://api.bilibili.com/x/web-interface/nav", timeout=20).json()
dd = nav.get("data") or {}
assert dd.get("isLogin"), "cookie 无效"
print("login:", dd.get("uname"), flush=True)

MIXIN = [46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49, 33, 9,
         42, 19, 29, 28, 14, 39, 12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40, 61, 26, 17, 0, 1,
         60, 51, 30, 4, 22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11, 36, 20, 34, 44, 52]
wbi = dd["wbi_img"]
img = wbi["img_url"].rsplit("/", 1)[-1].split(".")[0]
sub = wbi["sub_url"].rsplit("/", 1)[-1].split(".")[0]
mixin = "".join((img + sub)[i] for i in MIXIN)[:32]


def sign(p):
    p = dict(p)
    p["wts"] = str(int(time.time()))
    q = urllib.parse.urlencode(sorted(p.items()))
    p["w_rid"] = hashlib.md5((q + mixin).encode()).hexdigest()
    return p


def api_get(url, params=None, headers=None, need_login=True):
    for attempt in range(3):
        try:
            r = s.get(url, params=params, headers=headers or {}, timeout=25)
            if r.status_code == 412:
                print("  412 -> rotate, cool 45s", flush=True)
                rotate()
                time.sleep(45)
                continue
            d = r.json()
            if d.get("code") == -412:
                rotate()
                time.sleep(25)
                continue
            if need_login and d.get("code") == -101:
                rotate()
                time.sleep(3)
                continue
            return d
        except Exception as e:
            print(f"  req err: {e}, retry 3s", flush=True)
            time.sleep(3)
    return {}


# 选题依据：全部围绕「L0/L1 怎么安排、重复多少遍、怎么自测」，含一条反方
GRAB = [
    ("BV1pV411v7cN", "100遍口语练习·打卡（176万）【重复遍数·正面】"),
    ("BV1n54y1B7bE", "不刷十遍都亏了·美音教程（337万）【重复遍数】"),
    ("BV1VA411q79R", "背诵20多遍的英文演讲（172万）【重复·背诵】"),
    ("BV1LEiKBwET2", "听力跟听多少遍都没关系！（62万）【重复遍数·反方】"),
    ("BV1M5m5Y2EP7", "享受极致的重复 才能呆在牌桌上（1.1万）【重复·观点】"),
    ("BV17T4y1P7Pn", "ESL Podcast A Day in the Life 模仿跟读（62万）【同一材料】"),
    ("BV1iZgnz8EpJ", "美剧一句话反复跟读 读了多少遍（0.3万）【实操计数】"),
    ("BV1z2421Z7C9", "20年经验：提升口语4个方法（32万）"),
    ("BV1mi4y117z1", "亲测：最常见英语发音错误（5.7万）【纠音】"),
    ("BV1xb411v7Xq", "超详细英语精听方法（100万）【精听剂量】"),
    ("BV18A411K7kJ", "好莱坞纠音师：每天一遍一个月（27万）【周期口径】"),
    ("BV1184y1E7zY", "如何有效复盘口译练习录音（0.23万）【自测方法】"),
    ("BV1Rv411W71b", "一个人怎么练口语·碎片时间（33万）【单人自练】"),
    ("BV1GL4y1i7bs", "突破瓶颈04：纠正单词重音（19万）【重音自测】"),
]

for idx, (bvid, note) in enumerate(GRAB, 1):
    print(f"\n[{idx}/{len(GRAB)}] {bvid}  {note}", flush=True)
    try:
        r = s.get(f"https://www.bilibili.com/video/{bvid}/", timeout=25)
        m = (re.search(r"window\.__INITIAL_STATE__=(.*?);\(function", r.text, re.S)
             or re.search(r"window\.__INITIAL_STATE__=(.*?);\s*</script>", r.text, re.S))
        vd = json.loads(m.group(1))["videoData"]
        aid, cid, title = vd["aid"], vd["cid"], vd["title"]
        owner, dur, desc = vd["owner"]["name"], vd["duration"], (vd.get("desc") or "")[:800]
        cids = [p["cid"] for p in vd.get("pages", [])] or [cid]
    except Exception as e:
        print(f"  HTML parse FAIL: {e}", flush=True)
        time.sleep(2)
        continue
    print(f"  {title[:44]} | aid={aid} | {dur}s", flush=True)

    cfp = os.path.join(CMT_DIR, f"{bvid}.json")
    if os.path.exists(cfp):
        print("  comments SKIP (exists)", flush=True)
    else:
        item = {"bvid": bvid, "title": title, "aid": aid, "owner": owner,
                "duration": dur, "desc": desc, "count": 0, "comments": []}
        total_seen = 0
        for pn in range(1, 8):
            d = api_get("https://api.bilibili.com/x/v2/reply",
                        {"oid": aid, "type": 1, "pn": pn, "ps": 20, "sort": 2},
                        {"Referer": f"https://www.bilibili.com/video/{bvid}/"})
            reps = (d.get("data") or {}).get("replies") or []
            if not reps:
                break
            for c in reps:
                entry = {"uname": c["member"]["uname"], "like": c.get("like", 0),
                         "rcount": c.get("rcount", 0), "rpid": c.get("rpid"),
                         "message": c["content"]["message"], "subs": []}
                if entry["rcount"] > 0:
                    for sp in range(1, min(3, (entry["rcount"] // 20) + 2)):
                        d2 = api_get("https://api.bilibili.com/x/v2/reply/reply",
                                     {"oid": aid, "type": 1, "root": entry["rpid"],
                                      "pn": sp, "ps": 20},
                                     {"Referer": f"https://www.bilibili.com/video/{bvid}/"},
                                     need_login=False)
                        subs = (d2.get("data") or {}).get("replies") or []
                        if not subs:
                            break
                        for sc in subs:
                            entry["subs"].append({"uname": sc["member"]["uname"],
                                                  "like": sc.get("like", 0),
                                                  "message": sc["content"]["message"]})
                        time.sleep(0.8)
                        if len(entry["subs"]) >= entry["rcount"]:
                            break
                item["comments"].append(entry)
                total_seen += 1 + len(entry["subs"])
            time.sleep(1.1)
        item["count"] = total_seen
        with open(cfp, "w", encoding="utf-8") as f:
            json.dump(item, f, ensure_ascii=False)
        print(f"  comments: {total_seen}", flush=True)

    sfp = os.path.join(SUB_DIR, f"{bvid}.json")
    if os.path.exists(sfp):
        print("  subtitles SKIP (exists)", flush=True)
        continue
    sub_bodies = []
    for pcid in cids:
        q = sign({"bvid": bvid, "cid": str(pcid), "web_location": "333.1007"})
        d = api_get("https://api.bilibili.com/x/player/wbi/v2", q,
                    {"Referer": f"https://www.bilibili.com/video/{bvid}/"})
        subs = ((d.get("data") or {}).get("subtitle") or {}).get("subtitles") or []
        pick = None
        for pref in ["zh-Hans", "zh-CN", "zh", "ai-zh"]:
            pick = next((x for x in subs if x.get("lan") == pref), None)
            if pick:
                break
        if not pick:
            continue
        u = pick["subtitle_url"]
        if u.startswith("//"):
            u = "https:" + u
        body = None
        for rt in range(3):
            try:
                body = s.get(u, headers={"Referer": f"https://www.bilibili.com/video/{bvid}/"},
                             timeout=25).json().get("body")
                if body:
                    break
            except Exception:
                pass
            time.sleep(4)
        if body:
            sub_bodies.append({"cid": pcid, "lan": pick["lan"], "n": len(body), "body": body})
    if sub_bodies:
        with open(sfp, "w", encoding="utf-8") as f:
            json.dump({"bvid": bvid, "title": title, "duration": dur,
                       "subs": sub_bodies}, f, ensure_ascii=False)
        print(f"  subtitles: {len(sub_bodies)}P, {sum(x['n'] for x in sub_bodies)} segs", flush=True)
    else:
        print("  subtitles: none", flush=True)
    time.sleep(1.0)

import glob

allc = {}
for fp in glob.glob(os.path.join(CMT_DIR, "*.json")):
    d = json.load(open(fp, encoding="utf-8"))
    allc[d["bvid"]] = d
n_c = sum(v["count"] for v in allc.values())
print(f"\nDONE: {len(allc)} videos | {n_c} comments", flush=True)
