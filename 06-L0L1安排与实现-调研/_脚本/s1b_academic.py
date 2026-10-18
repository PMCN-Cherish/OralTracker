# -*- coding: utf-8 -*-
"""调研 #31 修正版：用 filter=title_and_abstract.search 保证相关性，再按引用数排
前次问题：search= + sort=cited_by_count 会让高引无关文献占满前 8 条
"""
import json, os, time, urllib.parse, urllib.request

BASE = r"D:\11.project\iwen-codex\codex-list\OralTracker\06-L0L1安排与实现-调研\原始数据\学术"
OUT = os.path.join(BASE, "openalex_filtered.json")


def get(u):
    req = urllib.request.Request(u, headers={"User-Agent": "research-bot/1.0 (mailto:t@e.com)"})
    return json.loads(urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "ignore"))


def rebuild(inv):
    if not inv:
        return ""
    pos = []
    for w, ids in inv.items():
        for i in ids:
            pos.append((i, w))
    pos.sort()
    return " ".join(w for _, w in pos)


QUERIES = [
    ("A1_reread_meta", "repeated reading", "meta-analysis OR fluency"),
    ("A2_taskrep_l2", "task repetition", "second language speaking"),
    ("A3_432", "4/3/2 technique", "fluency"),
    ("A4_rep_pron", "repetition", "pronunciation second language"),
    ("B1_pron_dose", "pronunciation instruction", "duration OR weeks OR amount"),
    ("B2_asr_fb", "automatic speech recognition", "pronunciation feedback"),
    ("B3_hvpt_dose", "high variability phonetic training", "sessions OR duration OR dose"),
    ("B4_capt_meta", "computer assisted pronunciation training", "meta-analysis"),
    ("C1_comprehensibility", "comprehensibility", "second language speech listeners"),
    ("C2_intelligibility", "intelligibility", "second language speech measurement"),
    ("C3_wer", "word error rate", "accented speech recognition"),
    ("C4_selfassess", "self-assessment", "second language speaking"),
    ("C5_diagnostic", "diagnostic assessment", "second language speaking"),
    ("D1_topic_familiar", "topic familiarity", "second language speaking fluency"),
    ("D2_task_type", "task type", "second language fluency measures"),
    ("D3_readaloud", "reading aloud", "second language fluency OR pronunciation"),
    ("D4_shadowing", "shadowing", "second language listening OR pronunciation"),
    ("E1_percept_prod", "perceptual training", "production generalization second language"),
    ("E3_accent", "accent reduction", "intelligibility training"),
    ("F1_repeat_fixed", "repetition", "formulaic sequences fluency"),
]

results = {}
for name, core, extra in QUERIES:
    # 主体检索词精确，修饰词用 OR 组；再按引用数排
    f1 = "title_and_abstract.search:" + core
    url = ("https://api.openalex.org/works?filter=" + urllib.parse.quote(f1, safe=":")
           + "&search=" + urllib.parse.quote(extra)
           + "&per-page=10&sort=cited_by_count:desc&mailto=t@e.com")
    try:
        d = get(url)
    except Exception as e:
        print(f"[FAIL] {name}: {e}", flush=True)
        results[name] = {"core": core, "extra": extra, "error": str(e), "works": []}
        time.sleep(2)
        continue
    ws = []
    for w in d.get("results", []):
        ws.append({
            "title": w.get("title"), "year": w.get("publication_year"),
            "cited": w.get("cited_by_count"), "doi": w.get("doi"), "type": w.get("type"),
            "venue": ((w.get("primary_location") or {}).get("source") or {}).get("display_name"),
            "abstract": rebuild(w.get("abstract_inverted_index"))[:1400],
        })
    results[name] = {"core": core, "extra": extra, "count": d.get("meta", {}).get("count"), "works": ws}
    print(f"[OK] {name}: {len(ws)} (total {d.get('meta',{}).get('count')})", flush=True)
    time.sleep(1.0)

json.dump(results, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved ->", OUT, flush=True)

print("\n\n===== 标题速览 =====", flush=True)
for k, v in results.items():
    print(f"\n### {k}  [{v.get('count')}]", flush=True)
    for w in v["works"][:8]:
        print(f"  {w['year']} [{w['cited']}引] {str(w['title'])[:96]}", flush=True)
