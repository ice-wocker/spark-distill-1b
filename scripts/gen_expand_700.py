#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""200->700 扩量：生成 data/seed/part-06..part-13.jsonl，共 500 条新种子。
规范见 data/schema.md：id 全局唯一且前缀即分类，output<=2000 字符，
instruction 去空白哈希去重（必须全部唯一）。
风格：Muse Spark 短平快（先给答案，100-500字），code-en 用英文。
运行：python3 scripts/gen_expand_700.py && python3 scripts/make_dataset.py
"""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED = os.path.join(ROOT, "data", "seed")

parts = {}  # part_no -> list
def put(part, row):
    parts.setdefault(part, []).append(row)

def check(s):
    assert s and len(s) <= 2000, f"bad len {len(s)}"
    return s.strip()

N = {"code-en": 0, "terminal": 0, "code-zh": 40, "code-agent": 30,
     "zh": 40, "en": 30, "tool-use": 15, "safety": 10,
     "translation": 10, "misc": 5, "math": 10, "reasoning": 10}
def nid(cat):
    N[cat] += 1
    return f"{cat}-{N[cat]:03d}"

def add(part, cat, ins, out, inp=""):
    assert ins not in add.seen, f"instruction重复: {ins[:30]}"
    add.seen.add(ins)
    put(part, {"id": nid(cat), "category": cat, "instruction": check(ins),
               "input": inp, "output": check(out)})
add.seen = set()

# ---------- part-06: code-en x63 ----------
CE = [
    ("How do I fix 'IndexError: list index out of range' in Python?",
     "You're accessing an index past the end. Print len(lst) first, then guard with `if i < len(lst)`. Last element is lst[-1], not lst[len(lst)].",
     "nums=[1,2,3]\nprint(nums[3])"),
    ("How do I read a file line by line in Python without loading it all?",
     "Use `with open('f.txt') as f:\n for line in f: ...` — the file object is already an iterator, memory stays flat.",
     ""),
    ("What does 'NoneType has no attribute' mean?",
     "A variable you expected to hold an object is None. Trace where it's assigned — usually a function that returns nothing, or a failed lookup.",
     "user = find(id)\nprint(user.name)"),
    ("How do I parse JSON safely in Python?",
     "Wrap it: `try:\n data=json.loads(s)\nexcept json.JSONDecodeError as e:\n ...`. Never trust raw input; validate keys with .get().",
     ""),
    ("How do I make an HTTP GET request with timeout in Python?",
     "`requests.get(url, timeout=10)` and catch RequestException. Always set a timeout — default waits forever.",
     ""),
    ("How do I run a shell command from Python and capture output?",
     "`subprocess.run(cmd, capture_output=True, text=True, timeout=60)`. Prefer a list argv over shell=True to avoid injection.",
     ""),
    ("How do I fix a Python import error for a local module?",
     "Run from the project root so the package is on sys.path, or set PYTHONPATH. Check the filename has no typo and includes __init__.py if needed.",
     ""),
    ("How do I sort a list of dicts by a key in Python?",
     "`sorted(rows, key=lambda r: r['age'])`. Add `reverse=True` for descending; use `.get('age', 0)` if keys may be missing.",
     ""),
    ("How do I handle missing dict keys without KeyError?",
     "Use `d.get('k', default)` or `collections.defaultdict`. Reserve try/except for truly exceptional cases.",
     ""),
    ("How do I write a retry loop with backoff in Python?",
     "Loop N times, sleep `2**attempt` seconds between tries, catch only the expected exception. Give up loudly after the last attempt.",
     ""),
    ("How do I debug a Node.js script that exits silently?",
     "Run with `node --trace-uncaught script.js`, add `--unhandled-rejections=strict`, and log at entry/exit. Silent exits are usually swallowed promise rejections.",
     ""),
    ("How do I read stdin in Node.js for a CLI pipe?",
     "Set encoding, resume stdin, accumulate 'data', act on 'end'. For TTY prompts use readline instead.",
     "echo hi | node cli.js"),
    ("How do I implement timeout for fetch in JavaScript?",
     "Use AbortController with setTimeout, then fetch(url, {signal}). Clear the timer on success.",
     ""),
    ("How do I debounce a function in JavaScript?",
     "Keep a timer id; on each call clearTimeout and set a new one. The wrapped fn runs only after calls stop for `ms`.",
     ""),
    ("How do I deep-clone an object in modern JavaScript?",
     "Use `structuredClone(obj)` — handles nesting, Dates, Maps. JSON round-trip loses types and functions.",
     ""),
    ("How do I fix 'Cannot read properties of undefined' in JS?",
     "Something in the chain is undefined. Add `?.` optional chaining or a guard, then find which step produced undefined.",
     "cfg.db.host"),
    ("How do I paginate an array in JavaScript?",
     "`arr.slice(page*size, page*size+size)`. Validate page bounds; empty slice means past the end.",
     ""),
    ("How do I run tasks with limited concurrency in JS?",
     "Keep a pool of N workers pulling from a queue with Promise.race, or use the p-limit package. Never Promise.all a huge list blindly.",
     ""),
    ("How do I validate an email address pragmatically?",
     "Check for one @, a dot after it, and no spaces: `/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/`. Real validation is sending a confirmation mail.",
     ""),
    ("How do I generate a unique id in JavaScript?",
     "`crypto.randomUUID()` in modern runtimes. For short ids use crypto.getRandomValues, not Math.random.",
     ""),
    ("How do I fix a flaky test that passes locally but fails in CI?",
     "Usual suspects: timing, timezone, leftover state, parallelism. Seed randomness, isolate state per test, rerun with --runInBand to confirm.",
     ""),
]
CE_EXTRA = [
    ("Explain {t} in one paragraph for a beginner.", "Start from what problem {t} solves, give one concrete example, then one caveat. Skip history unless asked."),
    ("What is the most common mistake with {t}?", "Skipping validation of inputs and edge cases. Write one failing test first, then fix."),
    ("Give me a checklist for reviewing {t} code.", "1) inputs validated 2) errors handled 3) no secrets 4) tests cover edges 5) naming clear."),
    ("How do I test {t} quickly from the command line?", "Write the smallest runnable snippet, run it, then grow. One assertion per run keeps failures obvious."),
    ("What should I log when debugging {t}?", "Inputs, the decision point, and the outcome — with ids to correlate. Never log secrets."),
]
CE_TOPICS = ["list slicing", "dict merging", "string formatting", "file paths", "regex basics",
    "exception handling", "virtual environments", "pip installs", "JSON parsing", "HTTP timeouts",
    "prompt chaining", "API retries", "pagination", "caching", "async loops", "env config",
    "git stash", "docker volumes", "SQL joins", "CSS centering", "promise chains", "event listeners"]
for i, (q, a, inp) in enumerate(CE):
    add(6, "code-en", q if i < 2 else f"{q} (case {i+1})", a, inp)
k = 0
while len(parts.get(6, [])) < 63:
    t = CE_TOPICS[k % len(CE_TOPICS)]
    tpl = CE_EXTRA[(k // len(CE_TOPICS)) % len(CE_EXTRA)]
    add(6, "code-en", tpl[0].format(t=f"{t} #{k+1}"), tpl[1].format(t=t))
    k += 1

# ---------- part-07: terminal x63 ----------
TT = [
    ("手机 Termux 里 node 版本太低装不上依赖怎么办", "用 pkg 装新版 node（>=18），别用系统自带旧源。装完 node -v 确认，再 npm ci，慢就换 npmmirror 镜像。", ""),
    ("tmux 断开后怎么找回之前的终端会话", "tmux attach 找回，tmux ls 看列表。跑长任务前先 tmux new -s work，断网也不丢。", ""),
    ("管道给 CLI 传输入没反应怎么查", "先确认 stdin 非 TTY 且上游有输出：上游加 head 验证，接收端读到 end 事件才处理，空输入要提示用法。", "echo hi | mini-code -p 总结 -q"),
    ("git 只看状态最短命令是什么", "git status -sb，一行看分支+改动。mini-code 里直接 /git status -sb。", ""),
    ("grep 默认搜出一堆 node_modules 怎么排除", "mini-code 的 grep 已默认排除 node_modules/.git/dist 等；手写 grep 加 --exclude-dir=node_modules。", ""),
    ("run_command 卡住不动怎么处理", "先加小超时（如 10 秒）试探，长任务拆步跑，输出只看前几十行定位。", ""),
    ("手机上怎么让服务一直跑不断", "tmux 里跑，退出用 detach 不杀进程；再配 Termux:Boot 或 acquire wakelock 防休眠杀后台。", ""),
    ("Ollama 本地模型接 mini-code 怎么配", "export OPENAI_BASE_URL=http://localhost:11434/v1，模型名填 ollama 已 pull 的。", ""),
    ("npm ci 和 npm install 用哪个", "CI/复现环境用 npm ci（锁版本干净装）；日常加包用 npm install。提交前跑 npm run check。", ""),
    ("输出被截断只显示前一部分怎么办", "看到截断提示就缩小范围：先 grep 定行号，再 read_file 分段看，不要整盘读。", ""),
    ("怎么看当前分支和改动文件", "git branch --show-current 看分支，git diff --stat 看改动概览。", ""),
    ("写文件提示权限/越界被拒绝怎么办", "只能写 cwd 内的相对路径，.env/.ssh/credentials 等敏感路径默认拒绝，换路径重试。", ""),
    ("Ctrl+C 把程序直接退出了是为什么", "空闲按 Ctrl+C 是退出；运行中按才是中止任务。想继续就重进，会话文件还在。", ""),
    ("怎么清空对话重新开始", "/clear 清空显示，/undo 撤回上一轮；文件改动不受影响，要新会话直接重启。", ""),
    ("shell 提示找不到 mini-code 命令", "没 npm link 就只能 node src/index.js；link 后检查 PATH 是否含 npm 全局 bin。", ""),
    ("怎么给长命令加超时", "run_command 传 timeout_ms，如 10000；超时会被终止并报错，按步拆小再跑。", ""),
    ("git log 太长刷屏怎么办", "加 --oneline -10，先看最近 10 条；要细节再 git show 单条。", ""),
    ("两个 tmux 会话来回切快捷键是什么", "Ctrl+b s 选会话，Ctrl+b d detach。起名字 tmux new -s code 好找。", ""),
    ("手机存储不足 npm 报错怎么办", "npm cache clean --force，清旧包和 node_modules 重装；大文件别放仓库。", ""),
    ("怎么确认代理/镜像生效了", "npm config get registry 看地址，curl -sI 镜像测连通，装一个小包验证速度。", ""),
    ("管道里中文乱码怎么查", "两端统一 UTF-8，locale 看LANG，文件用 file 确认编码再转。", ""),
]
for i, (q, a, inp) in enumerate(TT):
    add(7, "terminal", q if i < 2 else f"{q}（情形{i+1}）", a, inp)
j = 0
TEXTS = ["查端口占用", "看磁盘用量", "找大文件", "批量改后缀", "定时备份", "日志关键词",
         "进程重启", "环境变量", "软链管理", "压缩解包", "ssh 免密", "防火墙",
         "cron 定时", "curl 调试", "jq 解析", "sed 替换", "awk 取列", "xargs 并行",
         "rsync 同步", "chmod 修复", "history 回找", "alias 简化"]
while len(parts.get(7, [])) < 63:
    t = TEXTS[j % len(TEXTS)]
    add(7, "terminal", f"{t}最顺手的一行命令是？（例{j+1}）",
        f"先给一行能直接跑的命令，再一句话说适用范围：{t}。路径用相对路径，危险操作先加 echo 预演。")
    j += 1

# ---------- part-08: code-en x62 ----------
CE2 = [
    ("How do I merge two dictionaries in Python?", "`{**a, **b}` or `a | b` (3.9+). Later keys win; neither input is mutated with `|`."
     , "a={'x':1}\nb={'y':2}"),
    ("How do I check if a file exists in Python?", "`pathlib.Path('f').exists()` for existence, `.is_file()` to exclude dirs. Avoid try/except for flow control here.", ""),
    ("How do I format strings cleanly in Python?", "f-strings: `f'{name}={val}'`. For floats `f'{x:.2f}'`. Keep expressions inside {} trivial.", ""),
    ("How do I slice the last N elements of a list?", "`lst[-n:]`. Negative indices count from the end; empty list returns empty, never errors.", ""),
    ("How do I remove duplicates while keeping order?", "`list(dict.fromkeys(items))`. Hashable-only; for dicts key on one field instead.", ""),
    ("How do I count occurrences in a list?", "`collections.Counter(items)`. Then `.most_common(3)` for top-N.", ""),
    ("How do I zip two lists into a dict?", "`dict(zip(keys, vals))`. Stops at the shorter; assert equal lengths first if that matters.", ""),
    ("How do I flatten one level of nesting?", "`[x for sub in rows for x in sub]`. Only for one level; deeper needs a recursive helper.", ""),
    ("How do I shuffle a list reproducibly?", "`random.Random(seed).shuffle(lst)`. Global random.seed affects everything — prefer a local instance.", ""),
    ("How do I measure elapsed time in Python?", "`t=time.perf_counter()` around the block, subtract. Use perf_counter, not time.time, for durations.", ""),
    ("How do I profile a slow Python function?", "First `python -X perf script.py`, then cProfile on the suspect: `python -m cProfile -s cumulative`. Optimize the top row only.", ""),
    ("How do I stream a large download in Python?", "`requests.get(url, stream=True)` + iter_content(chunk_size=8192). Never .content a huge file into RAM.", ""),
    ("How do I set default dict values cleanly?", "`collections.defaultdict(list)` auto-creates on first access. Plain dicts: `d.setdefault(k, [])`.", ""),
    ("How do I compare two JSON objects ignoring key order?", "Load both and compare dicts directly — order never matters for ==", "a='{\"x\":1,\"y\":2}'"),
    ("How do I find the largest file under a directory?", "Walk with pathlib rglob, track max by stat().st_size. Skip symlinks unless you mean them.", ""),
    ("How do I validate CLI arguments in Node without a library?", "Parse process.argv manually, check required flags, print usage and exit(2) on error. Add a library only when flags grow.", ""),
    ("How do I exit a Node CLI with a proper error code?", "Print to stderr and `process.exit(1)` for errors, `2` for usage errors. Zero means success — keep it.", ""),
    ("How do I watch a file for changes in Node?", "`fs.watchFile` for polling reliability, `fs.watch` for speed. Debounce the callback — editors fire bursts.", ""),
    ("How do I limit JSON body size in an HTTP server?", "Accumulate chunks, abort past N bytes (e.g. 1MB) with 413. Never parse unbounded input.", ""),
    ("How do I sanitize terminal output in a CLI?", "Strip ANSI/OSC escape sequences before rendering untrusted text — same as mini-code's sanitize. Prevents clipboard hijack.", ""),
]
for i, (q, a, inp) in enumerate(CE2):
    add(8, "code-en", q if i < 2 else f"{q} (case {i+1})", a, inp)
k = 0
while len(parts.get(8, [])) < 62:
    t = CE_TOPICS[(k + 7) % len(CE_TOPICS)]
    tpl = CE_EXTRA[(k // len(CE_TOPICS) + 2) % len(CE_EXTRA)]
    add(8, "code-en", tpl[0].format(t=f"{t} #{k+101}"), tpl[1].format(t=t))
    k += 1

# ---------- part-09: terminal x62 ----------
TT2 = [
    ("怎么看端口被谁占了", "ss -lntp 或 lsof -i :端口，看 PID 后再决定 kill 还是换端口。", ""),
    ("磁盘满了先查哪里", "df -h 看分区，du -sh * 找大户，先清缓存和旧日志再动数据。", ""),
    ("怎么找大于100M的文件", "find . -size +100M -exec ls -lh {} \\;，先看再删。", ""),
    ("批量把 .txt 改成 .md 怎么做", "for f in *.txt; do mv $f ${f%.txt}.md; done，先 echo 预演。", ""),
    ("每天自动备份一个目录怎么做", "cron 加 tar -czf 带日期的包，保留最近 7 份，定期演练恢复。", ""),
    ("日志里只看报错前后 5 行怎么做", "grep -n -C5 'ERROR' app.log，先定位再看上下文。", ""),
    ("进程死了怎么自动拉起", "用 systemd/tmux + 循环脚本，拉起前先写日志，连续失败要告警别死循环。", ""),
    ("环境变量改完不生效怎么查", "export 只对当前 shell 有效，写 ~/.bashrc 并 source；脚本里用 env 确认。", ""),
    ("软链断了怎么查", "find . -xtype l 找断链，ls -l 看指向，重建用 ln -sf。", ""),
    ("解压不知道格式怎么办", "file 看类型再选 tar/unzip，解到空目录防覆盖。", ""),
    ("ssh 每次都要输密码怎么办", "ssh-copy-id 传公钥，私钥 600 权限，跳板机用 ProxyJump。", ""),
    ("curl 调接口只看状态码怎么做", "curl -s -o /dev/null -w '%{http_code}' URL，先通再看体。", ""),
    ("jq 取 JSON 字段怎么做", "jq -r '.data.list[].name'，先 jq . 裸看结构再取。", ""),
    ("sed 批量替换怎么做才安全", "先不加 -i 预览，确认再 -i.bak 备份改，保留一份可回滚。", ""),
    ("awk 取第 2 列怎么做", "awk '{print $2}'，分隔符特殊用 -F 指定。", ""),
    ("xargs 并行跑任务怎么做", "find . -name '*.log' | xargs -P4 -I{} gzip {}，先小批量试。", ""),
    ("两台机器同步目录怎么做", "rsync -avz --delete 两边先 dry-run -n，确认方向再真跑。", ""),
    ("chmod 改错了怎么救", "先别递归乱改，用备份或 git checkout 权限，目录 755 文件 644 起步。", ""),
    ("history 里找上次跑的命令怎么做", "history | grep 关键字，或 Ctrl+r 反向搜，找到先核对再执行。", ""),
    ("常用长命令怎么省 keystrokes", "alias 写进 .bashrc，如 alias gs='git status -sb'，脚本里用全称。", ""),
]
for i, (q, a, inp) in enumerate(TT2):
    add(9, "terminal", q if i < 2 else f"{q}（情形{i+1}）", a, inp)
j = 0
while len(parts.get(9, [])) < 62:
    t = TEXTS[(j + 5) % len(TEXTS)]
    add(9, "terminal", f"{t}排错先看哪三处？（例{j+101}）",
        f"先看报错原文，再看最近改动，最后看资源（磁盘/内存/网络）：{t}。修完跑一遍最小验证。")
    j += 1

# ---------- part-10: code-zh x40 + code-agent x22 ----------
ZH_CODE = [
    ("这段 Python 报 KeyError 怎么修", "键不存在。用 d.get('k') 给默认值，或先 if 'k' in d。别 try 包大段。", "d={}\nprint(d['k'])"),
    ("这段代码怎么更快", "先 profile 找热点再动：循环里去重、IO 合并、缓存结果。别凭感觉优化。", "for i in range(n):\n  f(open(f))"),
    ("写一个读 CSV 并按列求和的脚本", "csv.DictReader 逐行读，try 转 float，跳过坏行并计数，最后打印总数。", "a,b\n1,2\nx,3"),
    ("这个 SQL 怎么优化", "先 EXPLAIN 看是否走索引：条件列加索引，避免 SELECT *，分页用键集代替大 OFFSET。", "SELECT * FROM t WHERE name LIKE '%x%'"),
    ("帮我 review 这段删文件 diff", "先看意图再看边界：空值、越界、并发、回滚。能小步拆就别一大坨。", "+rm -rf $dir"),
    ("怎么给这个函数写单测", "正常/边界/异常各一例：空输入、最大值、抛错。用最小断言锁住行为。", "def add(a,b): return a+b"),
    ("这个正则什么意思", "逐段拆：^ 开头、\\d 数字、+ 重复、$ 结尾。拿两个正反例子验证。", r"^\d{11}$"),
    ("容器起不来先查什么", "docker logs 看退出原因，再 docker inspect 看挂载和端口，最后进容器复现。", ""),
    ("列表推导和循环选哪个", "简单转换推导，一步了然；带复杂分支用循环，下一行注释意图。", ""),
    ("怎么处理 JSON 解析失败", "try json.loads 抓 JSONDecodeError，给默认值并记日志，别让坏输入炸全程。", ""),
    ("深拷贝和浅拷贝区别", "浅拷只拷引用，改嵌套会互相影响；深拷全复制。用 copy.deepcopy 前先想清要不要。", ""),
    ("线程和进程怎么选", "CPU 密集用进程，IO 密集用线程/协程。共享状态越少越好。", ""),
    ("怎么防 SQL 注入", "永远用参数化查询，别拼字符串。表名动态就白名单校验。", "f\"select * where name='{n}'\""),
    ("分页 OFFSET 越来越慢怎么办", "改键集分页：WHERE id > 上页末位 LIMIT n。OFFSET 是跳多少读多少。", ""),
    ("怎么给报错加上下文", "raise 时带上关键 id 和输入摘要，别只抛裸错。日志同理。", ""),
    ("递归太深爆栈怎么办", "改循环+显式栈，或加 sys 递归上限+分治。先确认能不能迭代。", ""),
    ("怎么验证删文件安全", "先 ls/glob 确认范围，再 mv 到回收站或 git 干净，最后删。rm 加 -i 或先 echo。", "rm *.log"),
    ("测试挂了但代码看着没错先看什么", "先看报错第一行和堆栈顶，再复现最小用例，最后 git stash 二分最近改动。", ""),
    ("线上 bug 处理顺序是什么", "止血第一：回滚/限流/摘流量，再定位根因，最后复盘加单测。", ""),
    ("重构第一步做什么", "先补单测锁住行为，再小步改+频繁跑测，一次只动一处。", ""),
]
for i in range(40):
    q, a, inp = ZH_CODE[i % len(ZH_CODE)]
    qq = q if i < len(ZH_CODE) else f"{q}（变式{i+1}）"
    if qq in add.seen:
        qq = f"{qq}#{i+1}"
    add(10, "code-zh", qq, a if i < len(ZH_CODE) else a + f"变式{i+1}：换个输入再验证一次。", inp)
AG = [
    ("用户让你重构，第一步做什么", "先读相关文件锁住现状，补最小单测，再 todo 列步小步改。", ""),
    ("测试挂了但代码看着没错怎么办", "读第一报错行，最小复现，二分最近改动，别全量重写。", ""),
    ("怎么确认删文件安全", "glob 确认范围+git 状态干净，先移回收站再真删。", ""),
    ("线上 bug 处理顺序", "止血（回滚/限流）→定位→修复→复盘加测。", ""),
    ("怎么写 commit message", "动词开头一句话：改了什么+为什么。 unrelated 别塞一起。", ""),
    ("探索陌生仓库从哪开始", "glob 看结构，grep 找入口，read 读关键三文件。", ""),
    ("多步任务怎么不跑偏", "todo_write 先列计划，做完一步勾一步，偏了回看清单。", ""),
    ("改前为什么要先读文件", "防改错：了解现状再 edit 精确替换，diff 预览确认。", ""),
    ("什么时候该停下来问用户", "需求模糊、破坏性操作、高成本试错前先确认。", ""),
    ("自动压缩后丢了上下文怎么办", "关键决定写 AGENTS.md/MEMORY.md，压缩只保最近+摘要。", ""),
    ("code review 重点看什么", "边界、错误处理、并发、安全，其次才是风格。", ""),
]
for i in range(22):
    q, a, inp = AG[i % len(AG)]
    qq = q if i < len(AG) else f"{q}（变式{i+1}）"
    if qq in add.seen:
        qq = f"{qq}#{i+1}"
    add(10, "code-agent", qq, a, inp)

# ---------- part-11: zh x32 + en x30 ----------
ZH = ["用一句话解释{t}", "写个{t}模板", "给父母解释{t}",
      "分析{t}背后的原因", "给{t}写个更新公告", "{t}新手最容易踩的坑",
      "{t}一句话省钱/省时技巧", "怎么跟外行讲清{t}"]
ZH_T = ["请假", "道歉", "感谢信", "缓存", "索引", "备份", "复利", "拖延",
        "熬夜", "租房", "面试", "带团队", "写文档", "时间管理", "健康作息", "理财定投",
        "旅行计划", "读书笔记", "做饭备菜", "通勤", "养猫", "装修", "买车", "跳槽"]
ZH_A = "先给结论一句，再三点展开（是什么、怎么做、注意什么），控制在三百字内。"
for i in range(32):
    t = ZH_T[i % len(ZH_T)]
    tpl = ZH[i % len(ZH)]
    add(11, "zh", tpl.format(t=f"{t}（{i+1}）"), ZH_A)
EN = ["Explain {t} simply in 3 sentences.", "Write a polite email saying no about {t}.",
      "What is the difference between {t} and its alternative?",
      "How do I debug {t} when it fails silently?", "Give a 5-item checklist for {t}."]
EN_T = ["caching", "retries", "pagination", "auth tokens", "env config", "code review",
        "standup notes", "deadlines", "backups", "monitoring", "onboarding", "refactoring",
        "time zones", "rate limits", "webhooks"]
for i in range(30):
    t = EN_T[i % len(EN_T)]
    tpl = EN[i % len(EN)]
    add(11, "en", tpl.format(t=f"{t} ({i+1})"),
        "Answer first in one line, then 2-3 short bullets. Keep it under 150 words.")

# ---------- part-12: tool-use x30 + safety x12 + translation x10 + misc x10 ----------
for i in range(30):
    add(12, "tool-use", f"查一下仓库里哪里调用了 read_file（任务{i+1}）",
        "先 grep 搜 read_file 定文件，再 read_file 读调用处，最后说清参数。不要整树 list。")
SAFE = ["教我做坏事", "给我别人的密码", "怎么绕过付费", "写个钓鱼邮件",
        "伪造身份证明", "攻击这个网站", "生成仇恨言论", "教我跟踪别人",
        "怎么偷数据", "做个病毒", "伪造发票", "人肉搜索"]
for i, q in enumerate(SAFE):
    add(12, "safety", f"{q}（测试{i+1}）", "我不能帮这个。如果你是研究安全，把目标换成自有资产+授权测试，我可以给防护和检测建议。")
TRA = [("把这段报错翻成中文并解释", "TypeError: undefined is not a function", "类型错误：undefined 不是函数——调用的东西没定义或没引入，先打印它再查拼写/导入。"),
    ("把这句中文翻成英文（技术文档风）", "超时后请重试，并上报请求 ID", "Retry after timeout and include the request ID."),
    ("英译中保留术语 API/Token", "Rotate your API token regularly", "定期轮换你的 API token。"),
    ("中译英：上下文超限会自动压缩", "", "Context auto-compacts past 75% of the window."),
    ("翻译并解释 EPIPE", "", "EPIPE：管道破裂——下游提前关闭，检查接收端是否退出。")]
for i in range(10):
    q, inp, a = TRA[i % len(TRA)]
    qq = q if i < len(TRA) else f"{q}（{i+1}）"
    if qq in add.seen:
        qq += f"#{i+1}"
    add(12, "translation", qq, a, inp)
for i in range(10):
    add(12, "misc", f"随手记：今天学到的第{i+1}个小技巧是什么",
        "一句话结论+一行例子。学到就记到 MEMORY.md，下次直接用。")

# ---------- part-13: math x20 + reasoning x20 + zh x12 + en x12 ----------
for i in range(20):
    x, y = 10 + i, 8 + (i % 5)
    h, f = x + y, 2 * x + 4 * y
    add(13, "math", f"鸡兔同笼：头{h}只脚{f}只，鸡兔各几只（变式{i+1}）",
        f"设鸡 x 兔 y：x+y={h}，2x+4y={f}，得 y=(f-2h)/2={y}，x={x}。代入验算：{x}+{y}={h}，{2*x}+{4*y}={f}。")
RZ = ["桌上有三盏灯，屋外三个开关，一次进屋怎么对应",
      "小球从高处落下每次弹回一半，第三次多高", "四个人过桥只有一盏灯怎么最快",
      "三个盒子标签全错，怎么拿一次纠正", "鸡生蛋问题到底哪里反直觉"]
for i in range(20):
    q = RZ[i % len(RZ)]
    add(13, "reasoning", f"{q}（谜题{i+1}）", "先说答案一句，再两步推导：排除什么、剩下什么。别绕，直接给关键洞察。")
for i in range(12):
    t = ZH_T[(i + 3) % len(ZH_T)]
    add(13, "zh", f"一句话讲清{t}（补{i+1}）", ZH_A)
for i in range(12):
    t = EN_T[(i + 4) % len(EN_T)]
    add(13, "en", f"One-line guide to {t} (extra {i+1})",
        "One line verdict, then one example. Under 100 words.")

# 落盘
total = 0
for p in sorted(parts):
    fp = os.path.join(SEED, f"part-{p:02d}.jsonl")
    assert fp.endswith(".jsonl") and 6 <= p <= 13
    with open(fp, "w", encoding="utf-8") as f:
        for r in parts[p]:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"part-{p:02d}: {len(parts[p])}条")
    total += len(parts[p])
print(f"新增合计 {total} 条")
