# Agent 开发指南

本文档沉淀 Global Employment Agent 的长期核心要求。后续写后端、前端、测试、README 或 OpenSpec 变更前，都应先对齐这里的规则。

## 产品目标

构建一个面向客户的 Global Employment Agent。用户用自然语言提出跨国雇佣需求后，系统基于 `data/*.json` 中的本地政策数据，生成结构化、可审计、客户可读的雇佣方案。

Agent 必须帮助客户理解：

- 雇主月度和年度总成本是多少。
- 当地雇佣要求中哪些通过、哪些失败。
- 用户请求中哪些条款需要合规替代方案。
- 每个政策结论来自哪个本地政策文件。
- 推荐的关键雇佣条款是什么。

## 不可妥协的规则

1. 政策结论只能来自本地政策文件。
   - 不允许用模型自身知识回答雇佣政策问题。
   - 不允许编造 `data/*.json` 中不存在的规则。
   - 如果本地数据不足以支持某个结论，返回 `unknown` 或要求用户补充信息。

2. 成本计算必须由确定性代码完成。
   - LLM 绝不能计算雇主缴费、月度总额、年度总额、缴费上限、奖金分摊。
   - 成本计算器必须展示每个项目的计算基数、费率和金额。

3. 合规检查必须结构化。
   - 每个检查项必须返回 `pass`、`fail` 或 `unknown`。
   - 每个基于政策的检查项必须包含 citation，至少包括来源文件、JSON 路径和原文引用。
   - 失败项必须给出合规替代建议。

4. Agent 必须暴露执行过程。
   - 前端必须展示 Agent 执行步骤流或 trace。
   - 后端必须在最终响应中保留 tool-call trace。

5. 最终方案必须对客户可读。
   - 不允许把 raw JSON dump 当作最终用户体验。
   - 成本明细应以表格展示。
   - 合规结果应清晰、可扫读，并能查看引用来源。

6. 项目必须一条命令可运行。
   - 优先使用 `docker compose up --build`。
   - 必须提供 deterministic fallback mode，保证没有 LLM API Key 时仍能演示。

7. 保留真实 Git 历史。
   - 每完成一个有意义的开发节点后停止，并提醒用户提交。
   - 推荐提交节点见 `docs/openspec/changes/initial-global-employment-agent/tasks.md`。

## 支持国家

当前项目支持 `data/` 下 5 个政策 fixture：

- Singapore: `data/singapore.json`
- Vietnam: `data/vietnam.json`
- Indonesia: `data/indonesia.json`
- Philippines: `data/philippines.json`
- Japan: `data/japan.json`

国家查询应尽量支持国家英文名、国家代码和常见中文名。

## 必做工具

后端 Agent 至少必须编排以下工具。

### `get_country_policy(country)`

加载并摘要某个支持国家的雇佣政策。

必要行为：

- 支持 `SG`、`Singapore`、`新加坡` 等别名解析。
- 返回结构化政策 section，不能只返回自由文本。
- 为后续阶段会使用的政策文本提供 citation。
- 不支持的国家必须 fail closed，并返回可解释错误。

### `calculate_employment_cost(country, gross_salary)`

计算雇主月度和年度总成本。

必要行为：

- 从本地政策数据读取雇主缴费费率和缴费上限。
- 对每个雇主缴费项目计算：
  - 计算基数
  - 费率
  - 月度金额
  - 年度金额
- 成本中必须包含工资、雇主缴费、13 薪或年终奖分摊。
- 必要时区分法定成本和市场推荐预算。
- 展示金额保留两位小数，API 响应中保留数值字段。

### `check_compliance(country, terms)`

根据本地政策数据校验用户请求的雇佣条款。

必要行为：

- 至少检查：
  - 最低工资
  - 试用期
  - 年假
  - 工作时长
  - 解雇通知期
  - 法定 13 薪或强制奖金要求
- 返回逐项 `pass`、`fail` 或 `unknown`。
- 包含来源 citation。
- 对失败项给出合规替代建议。

## Agent 边界

LLM 可以做：

- 将用户自然语言请求解析为结构化雇佣条款。
- 判断应该调用哪些已支持工具。
- 将工具输出组织成客户可读语言。
- 把合规替代建议改写得更自然。

LLM 不可以做：

- 执行雇主成本算术。
- 基于自身知识判断合规。
- 创建没有 citation 的政策结论。
- 隐藏失败的合规检查。

## 推荐技术栈

- Backend: Python, FastAPI, Pydantic, pytest。
- Agent loop: 显式 orchestrator，可选 OpenAI tool calling。
- Frontend: React, TypeScript, Vite。
- Streaming: 使用 Server-Sent Events 展示 Agent 步骤。
- Runtime: Docker Compose。
- Tests: 后端使用 pytest，前端使用 Vitest 和 React Testing Library。

## 开发节点

每完成以下任一节点后，停止并提醒用户提交：

1. 文档和 OpenSpec 基线。
2. Backend 项目骨架和 policy repository。
3. Cost calculator 和测试。
4. Compliance checker 和测试。
5. Agent orchestration 和 API contracts。
6. SSE trace streaming。
7. React UI，包括请求、trace、成本、合规和条款展示。
8. Docker Compose 和 README。
9. 最终验证。

