#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合并 LoRA 到基座，存 fp16 完整权重（转 GGUF 之前的一步）。

用法（有 GPU 的机器，Kaggle 训完的会话里直接跑）：
    python merge_lora.py --base openbmb/MiniCPM5-1B-Base \\
        --adapter spark-1b-lora --out spark-1b-merged-fp16
"""
import argparse

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="openbmb/MiniCPM5-1B-Base")
    ap.add_argument("--adapter", required=True)
    ap.add_argument("--out", default="spark-1b-merged-fp16")
    a = ap.parse_args()

    tok = AutoTokenizer.from_pretrained(a.base, trust_remote_code=True)
    base = AutoModelForCausalLM.from_pretrained(
        a.base, torch_dtype=torch.float16, device_map="auto",
        trust_remote_code=True)
    model = PeftModel.from_pretrained(base, a.adapter)
    merged = model.merge_and_unload()
    merged.save_pretrained(a.out, safe_serialization=True)
    tok.save_pretrained(a.out)
    print("已保存合并权重", a.out)


if __name__ == "__main__":
    main()
