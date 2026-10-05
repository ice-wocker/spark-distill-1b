# spark-distill-1b 🧪

[![CI](https://github.com/ice-wocker/spark-distill-1b/actions/workflows/ci.yml/badge.svg)](https://github.com/ice-wocker/spark-distill-1b/actions/workflows/ci.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Base: MiniCPM5-1B](https://img.shields.io/badge/base-MiniCPM5--1B-green.svg)](https://huggingface.co/openbmb/MiniCPM5-1B-Base)

把 **Muse Spark 1.3** 的问答风格，蒸馏进 **MiniCPM5-1B**（1B，手机能跑）。

**Distill Muse Spark 1.3's style into MiniCPM5-1B: 780 pairs + free-GPU LoRA pipeline.**

## 这是什么蒸馏（先讲清方法，再谈效果）

API 拿不到 Muse 的 logits，所以是**黑盒数据蒸馏**：老师（Muse Spark）出高质量问答，
学生（MiniCPM5-1B-Base）用 SFT 吃下去。这是业界标准做法，效果上限取决于
数据量和多样性——目前 780 条（200 种子 + 500 扩量 + 80 长答案，含 code-en/terminal），
覆盖代码、终端、中文、英文、数学、推理主要分类，可跑完整蒸馏。

- 基座：`openbmb/MiniCPM5-1B-Base`（标准 Llama 架构，Apache-2.0，无需魔改）。
  用 Base 不用 SFT 版：风格从零学，不跟原厂 SFT 打架。
- 方法：Unsloth QLoRA（r16），3 epoch，T4 免费卡约半小时。
- 目标形态：GGUF Q4_K_M，直接塞进 Termux llama.cpp / iceLLM 跑。

## 数据（780 条：200 种子 + 500 扩量 part-06..13 + 80 长答案 part-14..15）

| 分类 | 数量 | 内容 |
|---|---|---|
| code-zh | 120 | Python/shell 调试、解释、改写（含 40 条带代码长答案） |
| code-agent | 52 | 终端助手工作法（读文件先行、todo、验证） |
| code-en | 125 | 英文代码问答（Python/JS/Node/调试） |
| terminal | 165 | 终端操作（Termux/tmux/shell/git/npm，含 40 条带现场长答案） |
| zh | 84 | 中文问答、写作、概念解释 |
| en | 72 | 英文通用问答 |
| math | 30 | 带步骤的数学 |
| reasoning | 30 | 逻辑谜题 |
| translation | 20 | 中英互译（技术语境） |
| tool-use | 45 | 工具调用式问答 |
| safety | 22 | 拒绝模板（把老师的安全行为一起蒸下去） |
| misc | 15 | 杂项 |

格式见 [`data/schema.md`](data/schema.md)，
合并校验：`python3 scripts/make_dataset.py`（输出 `distill.jsonl` 780 /
`train.jsonl` 703 / `eval_split.jsonl` 77）。
扩量脚本：`python3 scripts/gen_expand_700.py` 生成 `part-06..13`，
`python3 scripts/gen_long_1415.py` 生成 `part-14..15`（带 input 长答案）
（`expand.py` 只出 instruction 骨架，答案需找老师模型要）。

## 训练（三步，你只点三次鼠标）

1. 打开 Kaggle，新建 Notebook，右侧 Settings → Accelerator 选 **GPU T4 x2**
   （每周 30h 免费；Colab 选 T4 也行，见 notebook 开头）。
2. 把 `train/notebook.ipynb` 内容贴进去（或上传），**Run All**，
   中途去喝杯水（约 20-40 分钟）。
3. 把 `spark-1b-lora/` 下载下来（或推到 HF，notebook 里有 `HF_TOKEN` 的位置）。

Unsloth 抽风就用 `train/train_fallback.py`（纯 transformers+PEFT，慢一倍但稳）。

## 评测

```bash
python train/eval.py --adapter spark-1b-lora   # eval 集打分 + 生成抽查 gens.jsonl
```

`gens.jsonl` 拿 `eval.py` 头上的 JUDGE_PROMPT 找大模型当裁判打分。
当前成绩单（都会更新）：

| 版本 | 数据量 | eval 说明 | 备注 |
|---|---|---|---|
| v0.1-seed | 173 train | 待跑 | 种子链路验证 |
| v0.2-700 | 630 train | 待跑 | 200 种子 + 500 扩量（含 code-en/terminal） |
| v0.3-780 | 703 train | 待跑 | +80 长答案（code-zh/terminal 带 input，150 字起） |

## 导出上手机

```bash
python train/merge_lora.py --adapter spark-1b-lora --out spark-1b-merged-fp16
bash export/to_gguf.sh spark-1b-merged-fp16 spark-1b-q4_k_m.gguf
llama-server -m spark-1b-q4_k_m.gguf -c 4096 --port 8080
export OPENAI_BASE_URL=http://127.0.0.1:8080/v1   # 接 mini-code / iceLLM
```

## 合规说明（一段）

用 API 输出训练其他模型，各家条款不一（Muse API 目前是受邀预览，具体以 Meta
公布的条款为准）。本仓库默认你是**个人研究用途**：数据和 adapter 别商用分发，
真要发布先读两遍条款。这是忠告，不是法律意见。

## License

Apache-2.0（跟基座保持一致），见 [LICENSE](LICENSE)。
