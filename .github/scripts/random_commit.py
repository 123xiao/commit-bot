#!/usr/bin/env python3
# 导入所需的标准库模块
import os, random, subprocess, time, datetime, sys

# 获取环境变量配置
repo = os.environ.get("REPO")  # 目标仓库名称
actor_name = os.environ.get("ACTOR_NAME") or "vaghr"  # Git 提交者姓名
actor_email = os.environ.get("ACTOR_EMAIL") or f"{actor_name}@users.noreply.github.com"  # Git 提交者邮箱
gha_token = os.environ.get("GITHUB_TOKEN")  # GitHub Actions 使用的 token
push_token = os.environ.get("PUSH_TOKEN")  # 专门用于推送的 token


# 配置参数设置
skip_prob = float(os.environ.get("SKIP_PROB") or 0.08)  # 跳过执行的概率（模拟休息日）
max_commits = int(os.environ.get("MAX_COMMITS") or 3)   # 最大提交次数
min_sleep = int(os.environ.get("MIN_SLEEP") or 15)      # 连续提交间的最小间隔时间（秒）
max_sleep = int(os.environ.get("MAX_SLEEP") or 120)     # 连续提交间的最大间隔时间（秒）
max_start_delay_min = int(os.environ.get("MAX_START_DELAY_MINUTES") or 60)  # 初始延迟最大分钟数

# 参数校验与调整
if max_commits < 0: max_commits = 0
if min_sleep < 1: min_sleep = 1
if max_sleep < min_sleep: max_sleep = min_sleep + 10

# 初始随机延迟，模拟人类行为
start_delay = random.randint(0, max_start_delay_min * 60)
if start_delay > 0:
    print(f"Initial randomized delay: {start_delay} seconds (~{start_delay//60} minutes)")
    time.sleep(start_delay)

# 模拟休息日机制：根据概率决定是否跳过本次运行
if random.random() < skip_prob:
    print("Simulated rest day: skipping commits for today.")
    sys.exit(0)

# 定义提交数量的选择权重分布
choices = [0,1,2,3]
weights = [10,40,30,20]  # 对应选择各数量的概率权重
commits_to_make = random.choices(choices, weights)[0]
commits_to_make = min(commits_to_make, max_commits)  # 不超过设定的最大值
print(f"Will make {commits_to_make} commit(s) this run.")

# 设置 Git 用户信息
subprocess.check_call(["git", "config", "user.name", actor_name])
subprocess.check_call(["git", "config", "user.email", actor_email])

# 配置远程仓库认证信息
effective_token = push_token or gha_token
if effective_token:
    remote = f"https://x-access-token:{effective_token}@github.com/{repo}.git"
    subprocess.check_call(["git", "remote", "set-url", "origin", remote])
else:
    print("Warning: no token found. Push may fail.")

# 可操作的文件列表
files = [
    "data/activity_log.txt",
    "data/status.log",
    "docs/diary.md",
    "changelog.md",
    "data/log.txt"
]

# 提交消息模板列表
messages = [
    "chore: update activity log",
    "docs: update status",
    "fix: minor log correction",
    "style: auto-format logs",
    "ci: scheduled update",
    "✨ bot activity",
    "🔧 routine check"
]

# 确保所有目标文件所在目录存在
for f in files:
    d = "/".join(f.split("/")[:-1])
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

# 执行指定次数的随机提交
for i in range(commits_to_make):
    f = random.choice(files)  # 随机选择一个文件进行修改
    op = random.choices(["append","replace","touch"], [60,25,15])[0]  # 随机选择一种操作方式
    
    # 获取当前 UTC 时间戳
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # 根据操作类型对文件进行相应更改
    if op == "append":
        with open(f, "a", encoding="utf-8") as fh:
            fh.write(f"{ts} - auto update\n")
    elif op == "replace":
        with open(f, "w", encoding="utf-8") as fh:
            fh.write(f"# Updated at {ts}\n- note: {random.randint(1000,9999)}\n")
    else:
        open(f, "a", encoding="utf-8").close()

    # 构造提交消息
    msg = random.choice(messages)
    if random.random() < 0.35:
        msg += f" ({random.choice(['minor','sync','tidy','daily'])})"
    if random.random() < 0.25:
        msg = f"{random.choice(['🔧','✨','📝'])} {msg}"

    # 添加并提交更改
    subprocess.call(["git", "add", f])
    try:
        subprocess.check_call(["git", "commit", "-m", msg])
        print(f"Committed: {msg} -> {f}")
    except subprocess.CalledProcessError:
        print("Nothing new to commit for this file.")

    # 如果不是最后一次提交，则等待一段时间后继续
    if i < commits_to_make - 1:
        s = random.randint(min_sleep, max_sleep)
        print(f"Sleeping {s}s before next commit...")
        time.sleep(s)

# 推送所有提交到主分支
try:
    subprocess.check_call(["git", "push", "origin", "HEAD:main"])
    print("Pushed commits successfully.")
except subprocess.CalledProcessError as e:
    print("Push failed:", e)
    sys.exit(1)