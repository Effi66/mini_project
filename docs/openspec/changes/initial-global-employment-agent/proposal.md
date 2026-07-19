# Initial Global Employment Agent 提案

## 摘要

构建 Global Employment Agent 的第一版完整产品形态：使用 FastAPI、确定性政策工具、React、TypeScript、SSE trace streaming 和 Docker Compose。

## 背景动机

本项目需要展示一个能够回答全球雇佣问题的 Agent，但政策和算术不能依赖模型自身知识。最稳妥的实现方式是 source-backed agent：所有政策结论可追溯，所有成本计算可复现，最终方案对客户有直接使用价值。

## 变更内容

创建一个全栈应用，包括：

- FastAPI backend。
- 基于 `data/*.json` 的 policy repository。
- 三个必做工具：
  - `get_country_policy(country)`
  - `calculate_employment_cost(country, gross_salary)`
  - `check_compliance(country, terms)`
- 一个显式 agent orchestrator，用于产出步骤事件。
- 一个 React + TypeScript frontend，用于展示请求表单、Agent timeline、成本表、合规检查和关键雇佣条款。
- Docker Compose 和 README，支持一条命令启动。

## 不在本轮范围内

- 正式法律意见。
- 实时政府政策查询。
- 汇率换算。
- 薪资发放。
- 用户账号。
- 持久化雇佣历史。
- PDF 导出。
- 第一轮开发中完整实现 MCP server。

## 成功标准

- 用户可以用中文或英文提交雇佣请求。
- 后端至少能为一个支持国家返回结构化雇佣方案。
- 成本总额由代码计算，并有测试覆盖。
- 合规冲突使用 pass/fail 状态、citation 和替代建议明确展示。
- 前端将最终方案展示为客户可读报告，而不是 JSON dump。
- `docker compose up --build` 可以启动项目。
- README 明确说明政策来源边界和确定性计算边界。
- Git 历史包含 `docs/agent.md` 中列出的关键开发节点。

