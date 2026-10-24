# Git 共享仓库 + Python 依赖配置 · 上手清单

照顺序做完就能有一个多人协作的仓库。命令在 Windows Git Bash / PowerShell / macOS 下通用，激活虚拟环境那一步有差异，已标注。

---

## 一、一次性准备（只做一次）

### 1. 配置 Git 身份

**没配这个，`git commit` 会直接报错。** 先确认：

```bash
git config --global user.name
git config --global user.email
```

输出为空就是没配，补上：

```bash
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"
```

顺便把换行符和默认分支理顺（Windows 建议）：

```bash
git config --global core.autocrlf true
git config --global init.defaultBranch main
```

### 2. 在远端建「共享仓库」

两种做法，选一个：

- **GitHub / Gitee 网页建**：新建仓库 → **不要勾选** "Add a README / .gitignore / license"（勾了会有一个初始提交，后面推送要先 pull，新手容易卡住）→ 建完拿到仓库地址。
- **公司内网 / 自己服务器建裸仓库**：

```bash
# 在服务器上
mkdir -p /srv/git/myproject.git && cd /srv/git/myproject.git
git init --bare
# 队友用这个地址克隆
# ssh://user@server/srv/git/myproject.git
```

`--bare` 是关键：裸仓库没有工作区，只存历史，专门当"共享中心"用。

### 3. 把队友加成协作者

GitHub：仓库 → Settings → Collaborators → 邀请。
Gitee：仓库 → 管理 → 仓库成员管理。

私有仓库不加成员，别人 clone 会 403。

---

## 二、创建本地仓库并推送

```bash
cd 你的项目目录
git init
git add .
git commit -m "chore: 初始化项目"
git branch -M main                      # 确保分支叫 main
git remote add origin <仓库地址>
git push -u origin main                 # -u 只需第一次，之后直接 git push
```

验证：

```bash
git remote -v      # 看远端地址对不对
git status         # 应该是 clean
```

---

## 三、日常协作循环（每天重复的只有这 5 步）

```bash
git pull                    # 1. 开工前先拉，避免基于旧代码干活
git switch -c feat/login    # 2. 开一个功能分支，别直接在 main 上改
# ...改代码...
git add -A
git commit -m "feat: 加登录接口"   # 3. 小步提交，一次一件事
git push -u origin feat/login     # 4. 推到远端自己的分支
```

5. 在网页上发 Pull Request（Gitee 叫 Pull Request / 合并请求），让队友 review 后合并进 main。

**为什么必须开分支**：两个人同时改 main，先推的人成功，后推的人被拒。分支让冲突在合并时解决，而不是卡在推送时。

### 队友怎么加入

```bash
git clone <仓库地址>
cd 项目名
```

之后就是上面那 5 步循环。

### 遇到冲突怎么办

`git pull` 报 `CONFLICT` 时，打开冲突文件，会看到：

```
<<<<<<< HEAD
你的版本
=======
对方的版本
>>>>>>> origin/main
```

手工保留想要的内容、删掉这三行标记，然后：

```bash
git add 冲突文件
git commit
```

**别用 `git push -f` 解决冲突** —— 会覆盖掉别人的提交，这是协作里最危险的操作。

---

## 四、Python 环境依赖配置

核心原则：**虚拟环境不进仓库，依赖清单进仓库。** 别人 clone 下来照清单装，环境就能复现。

### 1. 建虚拟环境（每个项目一个，独立）

```bash
cd 项目目录
python -m venv .venv
```

激活：

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1
# Windows CMD
.venv\Scripts\activate.bat
# Git Bash
source .venv/Scripts/activate
# macOS / Linux
source .venv/bin/activate
```

激活成功的标志：命令行前面出现 `(.venv)`。

PowerShell 若报"禁止运行脚本"，执行一次：
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

### 2. 装依赖

```bash
pip install -r requirements.txt
```

### 3. 导出依赖（你加了新包之后）

```bash
pip freeze > requirements.txt
```

更稳的写法是手动维护 `requirements.txt` 并锁大版本区间（`requests>=2.32,<3.0`），避免 `pip freeze` 把一堆无关的传递依赖也倒进去。

### 4. 新队友拿到仓库后只做三件事

```bash
python -m venv .venv
source .venv/Scripts/activate     # 或对应平台的激活命令
pip install -r requirements.txt
```

跑一下 `python src/main.py`，能打印出解释器路径和版本就说明环境对了。

---

## 五、必须在 .gitignore 里挡住的东西

已经在这个仓库的 `.gitignore` 里配好了，重点是这三类：

| 类别 | 例子 | 为什么 |
|---|---|---|
| 虚拟环境 | `.venv/` `venv/` | 里面是几万个平台相关的二进制文件，提交必炸 |
| 密钥配置 | `.env` | 一旦推到远端就是泄露，历史里也删不干净 |
| 编译缓存 | `__pycache__/` `*.pyc` | 每次运行都变，制造无意义 diff |

密钥的正确做法：提交 `.env.example`（模板，空值），`.env` 留在本地。

**已经误提交了密钥怎么办**：立刻去服务商后台轮换密钥，别指望从 git 历史里抹掉——只要推过，就当它已泄露。

---

## 六、新手最常踩的 4 个坑

1. **`git commit` 报 "Please tell me who you are"** → 没配 `user.name` / `user.email`，回第一节。
2. **`git push` 报 `rejected (fetch first)`** → 远端有你没有的提交，先 `git pull` 再推。
3. **`git pull` 报 "refusing to merge unrelated histories"** → 远端建仓库时勾了 README，两边历史无关联。用 `git pull origin main --allow-unrelated-histories`，或干脆把远端清空重建。
4. **改了代码 `git status` 看不到** → 文件被 `.gitignore` 挡了，用 `git check-ignore -v 文件名` 查是哪条规则。

---

## 七、命令行记不住就用 GUI

命令行值得会，但日常没必要硬扛。装 **GitHub Desktop** 或 **VS Code 内置 Git 面板**，分支、提交、冲突解决都能点，底层还是同一套 Git。
