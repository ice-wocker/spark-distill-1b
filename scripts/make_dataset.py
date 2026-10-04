#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""数据集校验与合并：python3 scripts/make_dataset.py。

检查 data/seed/part-*.jsonl：
- 每行合法 JSON，含 id/instruction/output（input 可空）
- id 全局唯一，instruction/output 非空，output 不超过 2000 字符
- 输出合并文件 data/distill.jsonl + 统计 + 按 9:1 切 train/eval（eval 写入 data/eval_split.jsonl）
"""
import glob
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED = sorted(glob.glob(os.path.join(ROOT, "data", "seed", "part-*.jsonl")))


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def main():
    if not SEED:
        fail("data/seed 下没有 part-*.jsonl")
    rows, seen = [], set()
    for f in SEED:
        with open(f, encoding="utf-8") as fh:
            for i, line in enumerate(fh, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    o = json.loads(line)
                except json.JSONDecodeError as e:
                    fail("%s:%d JSON 非法：%s" % (f, i, e))
                for k in ("id", "instruction", "output"):
                    if k not in o:
                        fail("%s:%d 缺字段 %s" % (f, i, k))
                if o["id"] in seen:
                    fail("id 重复：" + o["id"])
                seen.add(o["id"])
                ins = str(o["instruction"]).strip()
                out = str(o["output"]).strip()
                if not ins or not out:
                    fail("%s:%d instruction/output 为空" % (f, i))
                if len(out) > 2000:
                    fail("%s:%d output 超 2000 字符（蒸馏数据要短平快）" % (f, i))
                rows.append({"id": o["id"],
                             "category": o.get("category", "misc"),
                             "instruction": ins,
                             "input": str(o.get("input", "") or "").strip(),
                             "output": out})
    # 去重：instruction 去掉空白后哈希相同算重复
    hs = {}
    for r in rows:
        h = hashlib.sha256("".join(r["instruction"].split()).encode()).hexdigest()[:12]
        hs.setdefault(h, []).append(r["id"])
    dups = {k: v for k, v in hs.items() if len(v) > 1}
    if dups:
        fail("instruction 重复 %d 组，如 %s" % (len(dups), list(dups.values())[0]))
    # 去重：output 逐字相同也算重复（防模板灌水，训练吃重复答案等于白训）
    oh = {}
    for r in rows:
        oh.setdefault(r["output"], []).append(r["id"])
    odups = {k: v for k, v in oh.items() if len(v) > 1}
    if odups:
        fail("output 重复 %d 组，如 %s" % (len(odups), list(odups.values())[0]))

    rows.sort(key=lambda r: r["id"])
    n_eval = max(10, len(rows) // 10)
    # 按 id 哈希稳定切分，保证可复现
    train = [r for r in rows
             if int(hashlib.sha256(r["id"].encode()).hexdigest(), 16) % 10 != 0]
    evalr = [r for r in rows
             if int(hashlib.sha256(r["id"].encode()).hexdigest(), 16) % 10 == 0]
    if len(evalr) < 10:  # 太少就从 train 头上补
        evalr += train[:10 - len(evalr)]

    def dump(path, items):
        with open(path, "w", encoding="utf-8") as f:
            for r in items:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    dump(os.path.join(ROOT, "data", "distill.jsonl"), rows)
    dump(os.path.join(ROOT, "data", "train.jsonl"), train)
    dump(os.path.join(ROOT, "data", "eval_split.jsonl"), evalr)

    cats = {}
    for r in rows:
        cats[r["category"]] = cats.get(r["category"], 0) + 1
    print("PASS: %d 条，train %d / eval %d" % (len(rows), len(train), len(evalr)))
    print("分类：%s" % json.dumps(cats, ensure_ascii=False))


if __name__ == "__main__":
    main()
