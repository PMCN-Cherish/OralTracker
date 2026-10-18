# -*- coding: utf-8 -*-
"""调研 #30：AI 练口语阶梯 —— OpenAlex 学术检索
按问题结构分组：流利度测量 / 可懂度三分 / 语音训练 / 互动协商 / 自动化 / 词汇提取 / 焦虑 / ASR 偏差 / 语速阈值
输出：原始数据/学术/openalex_raw.json
"""
import json, os, time, urllib.parse, urllib.request

OUT = r"D:\11.project\iwen-dsh\doubao-list\ActivityWatch\selfQuestion\AI练口语阶梯-调研\原始数据\学术\openalex_raw.json"

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
 ("A_fluency_dims", "fluency dimensions second language speech breakdown repair speed"),
 ("A_segalowitz", "Segalowitz cognitive fluency second language oral fluency"),
 ("A_tavakoli", "Tavakoli Skehan fluency second language performance measures"),
 ("B_munro_derwing", "comprehensibility intelligibility accentedness second language Munro Derwing"),
 ("B_pron_meta", "pronunciation instruction meta-analysis effectiveness comprehensibility Derwing"),
 ("C_hvpt", "high variability phonetic training second language vowel consonants meta-analysis"),
 ("C_shadowing", "shadowing technique second language listening speaking effect"),
 ("D_negotiation", "negotiation for meaning interaction hypothesis Long second language acquisition"),
 ("D_corrective_fb", "oral corrective feedback meta-analysis second language acquisition effectiveness"),
 ("E_automatization", "DeKeyser automatization second language skill acquisition practice"),
 ("E_fitts_posner", "Fitts Posner stages motor skill learning cognitive associative autonomous"),
 ("E_formulaic", "formulaic sequences fluency second language speech Wray"),
 ("F_vocab_coverage", "vocabulary size coverage percentage spoken discourse comprehension Nation"),
 ("F_lexical_retrieval", "lexical retrieval speed speaking proficiency second language"),
 ("G_anxiety", "foreign language classroom anxiety scale Horwitz speaking anxiety"),
 ("H_asr_l2", "automatic speech recognition non-native accented speech error rate"),
 ("I_retrieval_practice", "retrieval practice speaking fluency second language"),
 ("J_speech_rate", "speech rate words per minute comprehensibility second language listeners"),
]

out = {}
for tag, q in QUERIES:
    url = ("https://api.openalex.org/works?search=" + urllib.parse.quote(q) +
           "&per-page=3&select=title,publication_year,doi,cited_by_count,primary_location,abstract_inverted_index,authorships")
    try:
        d = get(url)
    except Exception as e:
        print("FAIL", tag, e, flush=True)
        continue
    rows = []
    for w in d.get("results", []):
        src = ((w.get("primary_location") or {}).get("source") or {}).get("display_name")
        au = "; ".join((a.get("author") or {}).get("display_name", "") for a in (w.get("authorships") or [])[:3])
        ab = rebuild(w.get("abstract_inverted_index"))
        rows.append({
            "title": w.get("title"), "year": w.get("publication_year"), "venue": src,
            "doi": w.get("doi"), "cited": w.get("cited_by_count"),
            "authors": au, "abstract": ab[:1000],
        })
        print(f"[{tag}] {w.get('title')[:90]} | {w.get('publication_year')} | cites {w.get('cited_by_count')}", flush=True)
    out[tag] = {"query": q, "results": rows}
    time.sleep(1)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("saved", OUT, "tags", len(out), flush=True)
