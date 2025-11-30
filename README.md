
这份文档按照“企业级项目文档标准”编写，涵盖：

* **项目背景 + 目的（Digital Twin 自主知识检索 AI）**
* **系统架构（Flask + FAISS + LangChain + OpenAI）**
* **从 7 月至今的全部更新历史**（你一直在做的内容全部整合）
* **最新更新：统一 API Key 管理、全局配置、README、目录结构、训练脚本、页面测试等**
* **开发/运行流程、版本兼容性要求、安全注意事项、未来计划**

非常完整，可直接用在正式文档中。

---

# ✅ **最终版 README.md（请直接复制到 GitHub）**

```markdown
# Digital Twin AI 项目（本地文档向量检索 + OpenAI API 问答）

## 📌 项目简介
本项目旨在构建一个 **个人 Digital Twin（数字分身）**，用于技术支持与知识自动化工作，包括：

- 本地文档库自动解析、清洗、分块、向量化  
- 使用 FAISS 建立高速向量检索库  
- LangChain / HuggingFace 提供 embedding 与检索链  
- Flask API 提供统一问答服务接口  
- OpenAI GPT 进行答案生成、总结和邮件风格重写  
- 支持训练“支持机器人”，长期构建专业知识库  

该系统运行于个人 AWS EC2（Ubuntu）环境中，可通过 PowerShell、本地脚本、或 Python 客户端直接调用。

---

# 📌 2024–2025 项目里程碑（按时间顺序整理）

## **2024 年 7 月 – 2024 年 12 月**
初版本实现：
- 文档上传 → 自动分块（chunking）→ FAISS embedding → 本地检索  
- Flask API 完成初代问答流程  
- 手动编写 embedding 逻辑（未用 LangChain）  
- 架构初步打通（Flask → FAISS → OpenAI）  

## **2025 年 1 月 – 2 月：测试与结构化阶段**
- 改进 PDF / Word 文档处理流程  
- 测试多版本 embedding 模型  
- 大文件处理导致多次 OOM（内存不足）  
- 开始探索 re-ranking、metadata filtering 等提升检索准确率功能  
- 添加 logging、调试工具、相似度分数打印  
- 开始考虑“反馈机制”：错误匹配时由用户指定正确文档页码用于再训练  

## **2025 年 3 月：LangChain 全面接入**
- **向量化构建方式从手写逻辑 → 全面切换为 LangChain**  
- 使用 SentenceTransformer / HuggingFace embeddings  
- 自动清洗、分块（chunk_size=1200, overlap=100）  
- 解决 LangChain / FAISS 版本兼容性问题  
- 建立完整的 build 流程：
```

python3 build_faiss_langchain.py

````

## **2025 年 4 月 – 6 月：Digital Twin 规划阶段**
- 完成 Flask API → LangChain → FAISS → OpenAI 的端到端流程  
- PowerShell 客户端实现问答测试  
- 建立文档自动上传/解析流水线（auto_process.py）  
- 解决大文件 embedding 内存不足问题  
- 引入 `.env` 与 config 目录规划  
- AI 邮件风格训练（基于你提供的脱敏邮件）

## **2025 年 7 月 – 11 月：项目重构 + 自动化阶段**
- 代码结构清理（拆分成 part1 / part2 / documents / outputs）
- 集成 AWS S3 同步（raw-docs/）
- 引入查询优化日志、embedding 助理功能  
- 集成 Codex 自动化（GitHub → AWS → 本地执行）  
- 多次修复 build pipeline / test pipeline  
- 引入 GitHub 版本控制、PR 流程  
- 大量优化 auto_process.py、FAISS 构建、训练脚本  

---

# 📌 **2025 年 12 月核心更新（今日最新）**

### ✅ **OpenAI API Key 管理全面重构**
**新增 `config/global_config.py`：统一、干净、安全的 API Key 管理系统**

- `.env` 是**唯一凭证来源**  
- `.env` **强制覆盖** OS 环境变量（避免旧 key 污染）  
- 禁止任何硬编码密钥  
- 所有模块都使用：

```python
from config.global_config import get_openai_api_key
api_key = get_openai_api_key()
````

* 新增 `.env.example`（示例，不含真实密钥）

### ✅ **PR 分拆策略（小步可控）**

Codex 改动被拆成 3 个提交：

1. 创建全局配置骨架
2. Flask app 改为统一引用全局 API 配置
3. 旧脚本清除所有硬编码 key、改为 import config

### ✅ **解决 Codex diff 超限问题**

* 大改动拆成小 commit
* 形成可持续的自动化工作流

### ✅ **README 全面重写（当前文件）**

* 加入项目历史
* 最新架构
* 新运行流程
* 全局配置说明
* 启动/测试命令
* 安全警示
* 未来 roadmap

---

# 📁 **目录结构（最新版本）**

```
ai_env/
├── app.py                     # Flask API 主入口
├── auto_process.py            # 文档处理流水线（旧版）
├── build_faiss_langchain.py   # 全新的向量库构建脚本（LangChain）
├── test_faiss2.py             # 检索测试脚本
│
├── config/
│   ├── global_config.py       # （新增）全局 API Key 管理
│   └── ...
│
├── documents/                 # 上传文档 + 解析后的 chunk 文本
│   ├── AI_Training_Material/
│   └── all_training_docs/
│
├── faiss_index/               # 生成的向量索引
├── outputs/                   # 生成的 jsonl / 调试日志
├── part1/ part2/              # AI pipeline 分阶段代码
└── requirements.txt
```

---

# 🚀 **运行流程（最新）**

## ① 构建向量库

```bash
python3 build_faiss_langchain.py
```

## ② 启动 Flask API

```bash
python3 app.py
```

## ③ 测试本地向量检索

```bash
python3 test_faiss2.py
```

## ④ PowerShell（Windows）远程调用 API

```powershell
$question = "How to configure DHCP?"
$body = @{ question = $question } | ConvertTo-Json
$apiUrl = "http://<你的服务器IP>:5000/ask"

$response = Invoke-WebRequest -Uri $apiUrl `
    -Method Post `
    -Body $body `
    -ContentType "application/json" `
    -TimeoutSec 10 `
    -UseBasicParsing

$response.Content
```

---

# ⚠️ 重要注意事项（2025 最新）

### ✔ OpenAI API Key 安全

* **不要上传 `.env` 到 GitHub**
* 使用 `.env.example` 作为示例文件
* Flask 错误日志禁止打印完整 API Key（已修复）

### ✔ FAISS / LangChain 版本兼容性

推荐组合：

```
langchain==0.1.20
langchain-community==0.0.38
langchain-core==0.1.52
sentence-transformers>=2.2
faiss-cpu>=1.7
```

### ✔ 大型文档建议

* 每个文档 < 50MB
* 建议先转 text → chunk → embed
* 避免一次性处理大量大文件（OOM 风险）

---

# 📅 Roadmap（下一阶段）

### 🔧 2026 Q1 计划

* 支持 re-ranking（Cross-Encoder / ColBERT）
* 多文档来源混合检索（S3 / 本地 / GitHub / Sharepoint）
* 用户反馈机制（wrong match → retrain）
* 多模型选择（OpenAI、DeepSeek、LlamaIndex）
* 引入日志可视化工具（例如 web dashboard）

---

# 🤝 贡献与反馈

如有任何想法、Bug、改进建议，欢迎提交 Issue 或 Pull Request。

````

---

# 🎯 **你下一步要做的事情**

1. **打开 GitHub → README.md → 点击编辑（✏️）**  
2. 把上面整段内容复制进去 → Save（Commit directly to main）  
3. 回到 AWS：  

```bash
git pull
````

这样 AWS 环境就与 GitHub 完全同步
