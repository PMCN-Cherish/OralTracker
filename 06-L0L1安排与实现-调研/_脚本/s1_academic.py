# -*- coding: utf-8 -*-
"""调研 #31：L0/L1 的安排与实现（同题重复前提）—— OpenAlex 学术检索
分组逻辑：按「调研要裁决的问题」分，不按近义词分
输出：原始数据/学术/openalex_raw.json
"""
import json, os, time, urllib.parse, urllib.request

BASE = r"D:\11.project\iwen-codex\codex-list\OralTracker\06-L0L1安排与实现-调研\原始数据\学术"
OUT = os.path.join(BASE, "openalex_raw.json")
os.makedirs(BASE, exist_ok=True)


def get(u):
    req = urllib.request.Request(u, headers={"User-Agent": "research-bot/1.0 (mailto:t@e.com)"})
    return json.loads(urllib.request.urlopen(req, timeout=50).read().decode("utf-8", "ignore"))


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
    # A 重复的剂量与机制
    ("A1_reread_meta", "repeated reading fluency comprehension gains meta-analysis"),
    ("A2_taskrep_l2", "task repetition second language speaking performance complexity accuracy fluency"),
    ("A3_432", "4/3/2 technique repeated speaking fluency"),
    ("A4_rep_pron", "repetition practice pronunciation accuracy second language"),
    ("A5_freq_phon", "input frequency usage-based second language phonology acquisition"),
    # B 剂量 / 疗程（L1 的 2-4 周够不够）
    ("B1_pron_dose", "pronunciation instruction duration weeks effectiveness meta-analysis"),
    ("B2_asr_fb_dose", "automatic speech recognition feedback pronunciation training duration"),
    ("B3_hvpt_dose", "high variability phonetic training number of sessions dose response"),
    ("B4_short_pron", "short-term pronunciation training effectiveness longitudinal"),
    ("B5_capt_meta", "computer assisted pronunciation training CAPT meta-analysis"),
    # C 测量与判据
    ("C1_comprehensibility", "comprehensibility rating listeners scale second language speech"),
    ("C2_intelligibility", "intelligibility measurement second language speech index"),
    ("C3_wer_asr", "word error rate automatic speech recognition accented speech intelligibility"),
    ("C4_selfassess", "self-assessment accuracy second language speaking ability"),
    ("C5_diagnostic", "diagnostic assessment second language speaking error classification"),
    # D 材料与任务设计
    ("D1_topic_familiar", "topic familiarity speaking fluency second language"),
    ("D2_task_type", "monologue dialogue task type fluency measures second language"),
    ("D3_readaloud", "reading aloud versus spontaneous speech fluency second language"),
    ("D4_shadow_rep", "shadowing repetition listening perception second language"),
    # E 感知训练的迁移
    ("E1_percept_prod", "perceptual training production generalization second language"),
    ("E2_audiovisual", "audiovisual phonetic training multi-speaker accent"),
    ("E3_accent_reduce", "accent reduction intelligibility foreign accent training"),
]

results = {}
for name, q in QUERIES:
    url = ("https://api.openalex.org/works?search=" + urllib.parse.quote(q)
           + "&per-page=8&sort=cited_by_count:desc&mailto=t@e.com")
    try:
        d = get(url)
    except Exception as e:
        print(f"[FAIL] {name}: {e}", flush=True)
        results[name] = {"query": q, "error": str(e), "works": []}
        time.sleep(1.2)
        continue
    ws = []
    for w in d.get("results", []):
        ws.append({
            "title": w.get("title"),
            "year": w.get("publication_year"),
            "cited": w.get("cited_by_count"),
            "doi": w.get("doi"),
            "type": w.get("type"),
            "venue": ((w.get("primary_location") or {}).get("source") or {}).get("display_name"),
            "abstract": rebuild(w.get("abstract_inverted_index"))[:1200],
        })
    results[name] = {"query": q, "count": d.get("meta", {}).get("count"), "works": ws}
    print(f"[OK] {name}: {len(ws)} works (total {d.get('meta',{}).get('count')})", flush=True)
    time.sleep(1.0)

json.dump(results, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved ->", OUT, flush=True)
