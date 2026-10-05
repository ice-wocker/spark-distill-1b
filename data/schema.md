# 数据格式

每行一个 JSON：

```json
{"id": "code-zh-001", "category": "code-zh",
 "instruction": "问题", "input": "可选的补充材料（代码/报错，可空）",
 "output": "老师模型的回答（100-500 字，短平快）"}
```

- `id` 全局唯一，前缀即分类。历史例外：part-01..05 用缩写前缀
  （`agent-`=`code-agent`、`tool-`=`tool-use`、`trans-`=`translation`、
  `safe-`=`safety`、`reason-`=`reasoning`），已冻结不再改动；
  part-06 起严格执行 `category-NNN`。
- 分类：`code-zh` / `code-agent` / `zh` / `en` / `math` /
  `reasoning` / `translation` / `misc` / `safety` / `tool-use` /
  `code-en`（英文代码问答） / `terminal`（终端/Termux/shell/git 操作）。
- `output` 是蒸馏信号：要 Muse Spark 的风格（简洁、直接、先给答案），
  不要长篇大论（超 2000 字符校验会挂）。
- `data/eval_prompts.jsonl` 是纯问题集（无答案），留着给人出题用；
  训练/评测切分由 `make_dataset.py` 按 id 哈希稳定切出
  `train.jsonl` / `eval_split.jsonl`。
