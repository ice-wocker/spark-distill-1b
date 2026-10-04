#!/bin/bash
# 合并权重 -> GGUF Q4_K_M（在 PC 或 Colab CPU 格跑，需要约 8GB 内存/磁盘）。
# 用法：bash export/to_gguf.sh spark-1b-merged-fp16 spark-1b-q4_k_m.gguf
set -euo pipefail
SRC="${1:?用法: to_gguf.sh <合并权重目录> <输出gguf>}"
OUT="${2:?用法: to_gguf.sh <合并权重目录> <输出gguf>}"

[ -d llama.cpp ] || git clone --depth 1 https://github.com/ggerganov/llama.cpp
cd llama.cpp
cmake -B build -DGGML_NATIVE=OFF > /dev/null && cmake --build build -j --target llama-quantize > /dev/null
echo "llama.cpp 工具链就绪"

python3 convert_hf_to_gguf.py "../$SRC" --outfile "/tmp/spark-1b-f16.gguf" --outtype f16
./build/bin/llama-quantize "/tmp/spark-1b-f16.gguf" "../$OUT" Q4_K_M
ls -lh "../$OUT"
echo "完成。手机端跑法：llama-server -m $OUT -c 4096 --port 8080"
echo "然后 export OPENAI_BASE_URL=http://127.0.0.1:8080/v1 即可接到 mini-code / iceLLM。"
