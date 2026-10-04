#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""扩量：批量生成新的 instruction（只要问题，不要答案）。

答案以后找老师模型要（比如继续找 Muse Spark，或任何强模型 API），
攒够一批就按 data/seed/part-06.jsonl 的格式追加，跑 make_dataset.py 校验。

用法：python3 scripts/expand.py --n 200 --out new_instructions.txt
"""
import argparse
import random

SEEDS = {
    "code-zh": ["解释这段报错", "这段代码能更快吗", "写一个处理 CSV 的脚本",
                "这个 SQL 怎么优化", "帮我 review 这段 diff",
                "怎么给这个函数写单测", "这个正则什么意思", "docker 容器起不来怎么查"],
    "code-agent": ["用户让你重构，你第一步做什么", "测试挂了但代码看着没错",
                   "怎么确认删文件是安全的", "线上 bug 的处理顺序",
                   "给这段代码写 commit message"],
    "zh": ["用一句话解释", "写个道歉/感谢/请假模板", "给父母解释一个技术概念",
           "分析一个生活现象背后的原因", "给产品写个更新公告"],
    "en": ["Explain X simply", "Write a polite email that says no",
           "What is the difference between A and B", "How do I debug X"],
    "math": ["鸡兔同笼变式", "概率计算", "数列求和", "方程求解", "百分比陷阱"],
    "reasoning": ["逻辑谜题", "横向思维谜语", "反直觉数学", "三段论改错"],
    "translation": ["中译英（技术文档风）", "英译中（保留术语）", "翻译一句报错并解释"],
}

TOPICS = ["Python 字典", "shell 管道", "git 分支", "HTTP 状态码", "正则表达式",
          "SQL 查询", "Docker", "进程线程", "密码学", "做饭", "租房", "面试",
          "时间管理", "健康", "理财", "旅行", "读书", "带团队", "写文档"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--out", default="new_instructions.txt")
    a = ap.parse_args()
    random.seed(20261004)
    cats = list(SEEDS)
    with open(a.out, "w", encoding="utf-8") as f:
        for i in range(a.n):
            c = cats[i % len(cats)]
            t = random.choice(TOPICS)
            f.write("%s | %s：关于「%s」的具体问题\n"
                    % (c, random.choice(SEEDS[c]), t))
    print("已生成 %d 条 instruction 骨架到 %s（找老师要答案后按 part 格式入库）"
          % (a.n, a.out))


if __name__ == "__main__":
    main()
