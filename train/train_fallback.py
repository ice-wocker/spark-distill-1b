#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QLoRA 兜底训练（不用 Unsloth）：transformers + PEFT + bitsandbytes。

用法（Kaggle/Colab 有 GPU 的格子里）：
    pip install -q transformers datasets trl peft accelerate bitsandbytes
    python train_fallback.py --data spark-distill-1b/data/train.jsonl

比 Unsloth 慢约一倍、显存多用约 1GB，但依赖最素，架构兼容性最好。
"""
import argparse
import json

import torch
from datasets import Dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import (AutoModelForCausalLM, AutoTokenizer,
                          BitsAndBytesConfig, TrainingArguments)
from trl import SFTTrainer


def load_rows(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/train.jsonl")
    ap.add_argument("--base", default="openbmb/MiniCPM5-1B-Base")
    ap.add_argument("--out", default="spark-1b-lora-fallback")
    ap.add_argument("--epochs", type=float, default=3)
    ap.add_argument("--max-len", type=int, default=2048)
    a = ap.parse_args()

    tok = AutoTokenizer.from_pretrained(a.base, trust_remote_code=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        a.base,
        quantization_config=BitsAndBytesConfig(
            load_in_4bit=True, bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16
            if torch.cuda.is_bf16_supported() else torch.float16),
        device_map="auto", trust_remote_code=True)
    model = prepare_model_for_kbit_training(model)
    model = get_peft_model(model, LoraConfig(
        r=16, lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
        lora_dropout=0.0, bias="none", task_type="CAUSAL_LM"))
    model.print_trainable_parameters()

    rows = load_rows(a.data)
    eos = tok.eos_token

    def to_text(r):
        user = r["instruction"] + ("\n" + r["input"] if r.get("input") else "")
        msgs = [{"role": "user", "content": user},
                {"role": "assistant", "content": r["output"]}]
        return tok.apply_chat_template(msgs, tokenize=False,
                                       add_generation_prompt=False) + eos

    ds = Dataset.from_dict({"text": [to_text(r) for r in rows]})
    print("样本:", len(ds))

    trainer = SFTTrainer(
        model=model, tokenizer=tok, train_dataset=ds,
        dataset_text_field="text", max_seq_length=a.max_len,
        dataset_num_proc=2,
        args=TrainingArguments(
            per_device_train_batch_size=2, gradient_accumulation_steps=4,
            num_train_epochs=a.epochs, learning_rate=2e-4,
            lr_scheduler_type="cosine", warmup_steps=10,
            logging_steps=10, save_steps=50, save_total_limit=2,
            output_dir=a.out, optim="paged_adamw_8bit", seed=42,
            report_to="none", fp16=not torch.cuda.is_bf16_supported(),
            bf16=torch.cuda.is_bf16_supported()))
    trainer.train()
    model.save_pretrained(a.out)
    tok.save_pretrained(a.out)
    print("已保存", a.out)


if __name__ == "__main__":
    main()
