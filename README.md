# Global Employment Agent

Global Employment Agent 是一个面向客户的全球雇佣方案生成器。用户用自然语言描述雇佣需求，系统基于本地政策 fixture 生成结构化雇佣方案，包括雇主成本、合规检查、政策引用和关键雇佣条款。

当前支持国家来自 `data/*.json`：

- Singapore
- Vietnam
- Indonesia
- Philippines
- Japan

## 一条命令运行

先复制环境变量示例：

```bash
cp .env.example .env
```

Windows PowerShell 可使用：

```powershell
Copy-Item .env.example .env
```

启动项目：

```bash
docker compose up --build
```

访问前端：

```text
http://localhost:5173
```

后端健康检查：

```text
http://localhost:8000/health
```

## 本地开发运行

Backend：

```bash
cd backend
python -m pip install -e .[dev]
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Frontend：

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Frontend 本地开发通过 Vite proxy 将 `/api` 转发到 `http://localhost:8000`。Docker Compose 中会将该 proxy 指向 `http://backend:8000`。

## Agent 边界

LLM 可以做：

- 解析用户自然语言请求。
- 决定调用哪些工具。
- 组织客户可读表达。

LLM 不可以做：

- 计算雇主成本。
- 基于自身知识判断政策合规。
- 生成没有 citation 的政策结论。

当前 `AGENT_MODE=deterministic` 是默认演示模式，可以在没有 LLM API Key 的情况下运行。`AGENT_MODE=llm` 当前保留模式边界，后续可接入真实 LLM tool-calling。

## 政策来源边界

所有政策结论只能来自 `data/*.json`。如果本地 fixture 没有覆盖某个政策主题，系统应返回 `unknown` 或要求用户补充信息，不允许用模型自身知识补齐。

每个基于政策的合规检查都包含：

- `source_file`
- `json_path`
- `quote`

## 成本计算边界

雇主成本由 backend 的确定性代码计算。计算包括：

- 月基本工资
- 雇主缴费
- 缴费上限
- 13 薪或奖金分摊
- 月度总成本
- 年度总成本

年度总成本按年度组成项相加，避免用展示层月度金额乘以 12 导致四舍五入漂移。

## 为什么先用结构化检索，而不是 vector RAG

当前政策数据是 5 个结构化 JSON fixture，字段已经包含雇主缴费、13 薪、年假、试用期、通知期、最低工资、个税概要、货币等信息。

因此本项目优先使用结构化 policy repository：

- 字段路径稳定，citation 可以精确到 JSON path。
- 合规检查和成本计算需要确定性字段，不适合从向量相似度结果中猜。
- fixture 体量很小，引入 vector RAG 会增加复杂度和引用错位风险。

如果未来政策文件扩展为长篇法规文本，可以增加 `retrieve_policy_sections(country, query)` 或 vector RAG 层，但计算和合规判断仍应由确定性工具完成。

## API

国家和政策：

```text
GET /api/countries
GET /api/policies/{country}
```

Agent：

```text
POST /api/agent/hire
POST /api/agent/hire/stream
```

SSE event 类型：

```text
agent.started
agent.step
tool.called
tool.completed
agent.completed
agent.error
```

## 测试

Backend：

```bash
python -m pytest backend/tests -v
```

Frontend：

```bash
cd frontend
npm test -- --run
npm run build
```

Docker Compose 配置检查：

```bash
docker compose config
```

## Git 开发节点

本项目按 OpenSpec 任务节点开发，每个节点单独提交，保留真实 Git 历史。任务清单见：

```text
docs/openspec/changes/initial-global-employment-agent/tasks.md
```
