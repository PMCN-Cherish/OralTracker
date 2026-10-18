# -*- coding: utf-8 -*-
import json,urllib.parse,urllib.request,time
BASE=r"D:/11.project/iwen-codex/codex-list/OralTracker/06-L0L1安排与实现-调研/原始数据/学术"
def get(u):
    for a in range(4):
        try:
            return json.loads(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"research-bot/1.0 (mailto:t@e.com)"}),timeout=60).read().decode("utf-8","ignore"))
        except Exception as e:
            print("  retry",a,e,flush=True); time.sleep(20)
    return {}
def rb(inv):
    if not inv: return ""
    p=[]
    for w,ids in inv.items():
        for i in ids: p.append((i,w))
    p.sort(); return " ".join(w for _,w in p)
Q={
 "A1_reread":"'repeated reading'",
 "A3_432":"'4/3/2'",
 "B4_capt":"'computer assisted pronunciation training'",
 "C2_intelligibility":"'intelligibility' AND 'second language'",
 "E3_accent":"'accent reduction'",
 "F1_taskrep_pron":"'task repetition' AND 'pronunciation'",
}
out={}
for k,v in Q.items():
    u="https://api.openalex.org/works?filter="+urllib.parse.quote("title_and_abstract.search:"+v,safe=":")+"&per-page=10&sort=cited_by_count:desc&mailto=t@e.com"
    d=get(u)
    ws=[{"title":w.get("title"),"year":w.get("publication_year"),"cited":w.get("cited_by_count"),"doi":w.get("doi"),"type":w.get("type"),"venue":((w.get("primary_location") or {}).get("source") or {}).get("display_name"),"abstract":rb(w.get("abstract_inverted_index"))[:1400]} for w in d.get("results",[])]
    out[k]={"core":v,"count":d.get("meta",{}).get("count"),"works":ws}
    print("\n###",k,d.get("meta",{}).get("count"),flush=True)
    for w in ws: print("  %s [%s引] %s"%(w["year"],w["cited"],str(w["title"])[:92]),flush=True)
    time.sleep(8)
json.dump(out,open(BASE+r"\openalex_missing.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print("\nsaved",flush=True)
