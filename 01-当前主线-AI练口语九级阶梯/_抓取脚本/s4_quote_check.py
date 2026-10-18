# -*- coding: utf-8 -*-
"""调研 #30：AI 练口语阶梯 —— 引语回源核对
规矩：只去空白（norm），不补标点，错字照录；字幕按 seg 相邻拼接。
"""
import json, os, re, sys

BASE = r"D:\11.project\iwen-dsh\doubao-list\ActivityWatch\selfQuestion\AI练口语阶梯-调研\原始数据\B站"
CMT = os.path.join(BASE, "评论")
SUB = os.path.join(BASE, "字幕")

def norm(s):
    return re.sub(r"\s+", "", s or "")

_cache = {}
def load_cmt(bv):
    if bv not in _cache:
        _cache[bv] = json.load(open(os.path.join(CMT, bv + ".json"), encoding="utf-8"))
    return _cache[bv]

def load_sub(bv):
    k = "s" + bv
    if k not in _cache:
        fp = os.path.join(SUB, bv + ".json")
        _cache[k] = json.load(open(fp, encoding="utf-8")) if os.path.exists(fp) else None
    return _cache[k]

def check_cmt(bv, quote):
    d = load_cmt(bv)
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
    if best:
        return True, best[0], best[1]
    return False, 0, "-"

def check_sub(bv, quote, span=4):
    d = load_sub(bv)
    if not d:
        return False, 0, "-"
    q = norm(quote)
    for p in d["subs"]:
        body = p["body"]
        for i in range(len(body)):
            if q in norm(body[i]["content"]):
                return True, int(body[i]["from"]), "单段"
        for i in range(len(body)):
            for L in range(2, span + 1):
                joined = "".join(norm(x["content"]) for x in body[i:i + L])
                if q in joined:
                    return True, int(body[i]["from"]), f"{L}段拼接"
    return False, 0, "-"

QUOTES = [
 # ---- 诊断：卡在哪一环 ----
 ("Q01", "评论", "BV1z2421Z7C9", "我现在跟读没问题、听也没问题，但一到自己张嘴就卡"),
 ("Q02", "评论", "BV1qV411d72v", "因为你都不知道该怎样造句，怎样在要用的时候说出来"),
 ("Q03", "评论", "BV1qV411d72v", "一直看别人说的句子是别人造的，而不是自己的"),
 ("Q04", "评论", "BV1HBe9zdEMY", "我会的很熟的句型在我口述时就可以较为流利地说出来"),
 ("Q05", "评论", "BV1HBe9zdEMY", "在表述的时候我都需要在脑子里复盘很久"),
 ("Q06", "评论", "BV11j411278Q", "简单的东西说利索"),
 ("Q07", "评论", "BV11j411278Q", "我的语速会不自觉的变得很快，以至于有些词发音不清"),
 ("Q08", "评论", "BV11j411278Q", "边想边说增加刻意停顿"),
 # ---- AI 的能力边界 ----
 ("Q09", "评论", "BV1JXoNYwESP", "gpt唯一不好的就是不能帮助改进口音和错误发音"),
 ("Q10", "评论", "BV1JXoNYwESP", "之前试过别的ai，我发现每次没说完ai就抢答了"),
 ("Q11", "评论", "BV1JXoNYwESP", "但每次新对话都失忆了一样"),
 ("Q12", "评论", "BV1iCXvBxE5Y", "但问题是它太温柔了，我说什么它都能接住"),
 ("Q13", "评论", "BV1iCXvBxE5Y", "但后来发现ai的问题都太简单了，真跟人说话我还是很慌"),
 ("Q14", "评论", "BV1iCXvBxE5Y", "我一绕弯子他马上打断问我到底想表达什么"),
 ("Q15", "评论", "BV1DV4y1e75W", "人给的答案过于机械、过于套路，AI给的答案反而更自然更像个人"),
 ("Q16", "评论", "BV1JXoNYwESP", "不止英语口语，日语德语西班牙语发音都特别标准"),
 # ---- 影子跟读：正反方 ----
 ("Q17", "评论", "BV1j1rGBvEYv", "影子跟读对口语流畅度没大用，但是对发音就是有用的"),
 ("Q18", "评论", "BV1j1rGBvEYv", "影子跟读是要理解句子的前提下，再跟读"),
 ("Q19", "评论", "BV1j1rGBvEYv", "这个非专业用来练听力也是很好的"),
 ("Q20", "评论", "BV1j1rGBvEYv", "实则只有嘴机械的在动，脑袋完全不转圈"),
 ("Q21", "评论", "BV1j1rGBvEYv", "影子跟读一直都是练听力的啊"),
 ("Q22", "评论", "BV1j1rGBvEYv", "其实影子跟读法的核心在于盲听跟读，有些人就是看的文本读，所以没有用"),
 ("Q23", "评论", "BV1j1rGBvEYv", "练的是节奏，练的是英语句子的轻重缓急"),
 ("Q24", "评论", "BV1j1rGBvEYv", "第一个视频说看美剧没用，第二个视频说影子跟读没用，第三个视频说背单词没用，第四个视频说买课没用，太焦虑了"),
 ("Q25", "评论", "BV1E44y1U7mD", "材料选择：comprehensive material（95%听的懂）"),
 ("Q26", "评论", "BV1E44y1U7mD", "根本反应不过来"),
 ("Q27", "评论", "BV1fStt6SEe4", "这个可能会成为你自我感动的假努力例子"),
 ("Q28", "评论", "BV1yN411u7k6", "但是几天后就感觉好多了"),
 ("Q29", "评论", "BV1yN411u7k6", "每天看两小时油管母语者视频（四个月）现在听力真的很好"),
 # ---- 语块 / 句式 / 重复 ----
 ("Q30", "评论", "BV11j411278Q", "1.讲垃圾话"),
 ("Q31", "评论", "BV11j411278Q", "3.背固定搭配"),
 ("Q32", "评论", "BV1QL411j72S", "发音连读什么的在哪都能看到，，但是语调真的找了好久都没有"),
 # ---- 剂量与周期 ----
 ("Q33", "评论", "BV1z2421Z7C9", "英语这个东西学习是需要正向反馈感的"),
 ("Q34", "评论", "BV1z2421Z7C9", "一年多天天都在练习，每天听说一小时的时间"),
 ("Q35", "评论", "BV1z2421Z7C9", "我考了三次，每次学习周期三个月，每次单科最高分都在6以内"),
 # ---- 字幕 ----
 ("Q36", "字幕", "BV1j1rGBvEYv", "因为他强调的重点就是错的"),
 ("Q37", "字幕", "BV1j1rGBvEYv", "首先重要的是流畅度"),
 ("Q38", "字幕", "BV1iCXvBxE5Y", "所以呢就不要完全依赖他的这个打分了"),
 ("Q39", "字幕", "BV1iCXvBxE5Y", "比95分的这位同学发音上更棒一些"),
 ("Q40", "字幕", "BV1wshV6pEyR", "我不想每句话后都被纠正"),
 ("Q41", "字幕", "BV1wshV6pEyR", "因为会打断我的表达流畅度"),
 ("Q42", "字幕", "BV1HBe9zdEMY", "我认为这就是流利"),
 ("Q43", "字幕", "BV1E44y1U7mD", "因此千万不要边听边说"),
 ("Q44", "字幕", "BV1E44y1U7mD", "所以是listen echo repeat是这样的三个步骤"),
 ("Q45", "评论", "BV1z2421Z7C9", "从土猪到现在自由交流还好听"),
 ("Q46", "评论", "BV1z2421Z7C9", "我连问他周末去哪玩都说得磕磕巴巴"),
 ("Q47", "评论", "BV1wshV6pEyR", "我也开车的时候经常跟ai闲聊，前提是开辅助驾驶"),
 ("Q48", "评论", "BV1j1rGBvEYv", "一切焦虑都是因为你没有行动"),
 ("Q49", "评论", "BV1iCXvBxE5Y", "我前阵子每天晚上睡前都会跟AI聊十分钟"),
 ("Q50", "评论", "BV1DV4y1e75W", "口语考试见考官就跟见我丈母娘一样，紧张的无话可说"),
 ("Q51", "评论", "BV1HBe9zdEMY", "我也那天发现句子结构是最重要的"),
]

ok = fail = 0
rows = []
for qid, src, bv, text in QUOTES:
    if src == "评论":
        hit, like, loc = check_cmt(bv, text)
    else:
        hit, like, loc = check_sub(bv, text)
    tag = "PASS" if hit else "FAIL"
    if hit:
        ok += 1
    else:
        fail += 1
    rows.append((qid, tag, bv, src, like, loc, text))
    print(f"[{tag}] {qid} {bv} {src} like={like} {loc} :: {text}")

print(f"\n=== 合计 {len(QUOTES)} 条 | PASS {ok} | FAIL {fail} | PASS率 {ok/len(QUOTES)*100:.1f}% ===")
if fail:
    print("\nFAIL 明细：")
    for r in rows:
        if r[1] == "FAIL":
            print("  ", r[0], r[2], r[3], r[6])
