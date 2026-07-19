# Initial Global Employment Agent 任务清单

## Git Node 1: 文档和 OpenSpec 基线

- [x] 创建 `docs/agent.md`，沉淀长期 Agent 开发守则。
- [x] 创建 `docs/openspec/config.yaml`。
- [x] 创建源事实规格 `docs/openspec/specs/global-employment-agent/spec.md`。
- [x] 创建初始变更提案 `docs/openspec/changes/initial-global-employment-agent/proposal.md`。
- [x] 创建初始变更设计 `docs/openspec/changes/initial-global-employment-agent/design.md`。
- [x] 创建实现任务清单 `docs/openspec/changes/initial-global-employment-agent/tasks.md`。
- [x] 提交节点：`git add desc.md data docs && git commit -m "docs: add project spec baseline"`

## Git Node 2: Backend 骨架和 Policy Repository

- [x] 创建 `backend/pyproject.toml`，包含 FastAPI、Uvicorn、Pydantic、pytest 和 Ruff 依赖。
- [x] 创建 `backend/app/main.py`，包含 FastAPI app 构造和 health route。
- [x] 创建 `backend/app/core/config.py`，配置 data directory 和 agent mode。
- [x] 创建 `backend/app/core/errors.py`，定义 typed domain exceptions。
- [x] 创建 `backend/app/models/policy.py`，定义 policy fixture 的 Pydantic models。
- [x] 创建 `backend/app/domain/policy_repository.py`，加载 `data/*.json` 并解析国家别名。
- [x] 创建 `backend/app/domain/citations.py`，构造 citation 对象。
- [x] 创建 `backend/app/api/routes_countries.py`，提供 `GET /api/countries` 和 `GET /api/policies/{country}`。
- [x] 创建 `backend/tests/test_policy_repository.py`。
- [x] 运行 `pytest backend/tests/test_policy_repository.py -v`。
- [x] 提交节点：`git add .gitignore backend docs && git commit -m "feat: add policy repository"`

## Git Node 3: Cost Calculator

- [x] 创建 `backend/app/domain/cost_calculator.py`。
- [x] 创建 `backend/app/tools/employment_cost.py`。
- [x] 在 `backend/app/models/response.py` 中创建成本明细 response models。
- [x] 实现缴费上限处理。
- [x] 实现月度和年度总成本。
- [x] 使用 normalized fixture values 实现法定和市场惯例奖金分摊。
- [x] 创建 `backend/tests/test_cost_calculator.py`。
- [x] 运行 `pytest backend/tests/test_cost_calculator.py -v`。
- [x] 提交节点：`git add backend docs && git commit -m "feat: calculate employment cost"`

## Git Node 4: Compliance Checker

- [x] 创建 `backend/app/domain/compliance_checker.py`。
- [x] 创建 `backend/app/tools/compliance.py`。
- [x] 在 `backend/app/models/request.py` 中创建结构化 hiring terms request models。
- [x] 实现最低工资检查。
- [x] 实现试用期检查。
- [x] 实现年假检查。
- [x] 实现工作时长检查。
- [x] 实现解雇通知期检查。
- [x] 实现法定 13 薪检查。
- [x] 创建 `backend/tests/test_compliance_checker.py`。
- [x] 运行 `pytest backend/tests/test_compliance_checker.py -v`。
- [x] 提交节点：`git add backend docs && git commit -m "feat: check employment compliance"`

## Git Node 5: Agent Orchestration 和 API Contracts

- [x] 创建 `backend/app/agent/schemas.py`，定义 agent terms、events、tool traces 和 final plan。
- [x] 创建 `backend/app/agent/events.py`，负责构造 event。
- [x] 创建 `backend/app/tools/country_policy.py`。
- [x] 创建 `backend/app/tools/registry.py`。
- [x] 创建 `backend/app/agent/orchestrator.py`。
- [x] 实现 deterministic parser，覆盖支持的 demo prompts。
- [x] 在 `AGENT_MODE=llm` 下保留可选 LLM-backed parsing 的模式开关和 API 边界。
- [x] 实现单国编排。
- [x] 实现多国编排。
- [x] 确保最终方案中的每个政策结论都有 citation 或 `unknown` 状态。
- [x] 创建 `backend/app/api/routes_agent.py`，提供 `POST /api/agent/hire`。
- [x] 创建 `backend/tests/test_agent_orchestrator.py`。
- [x] 运行 `pytest backend/tests/test_agent_orchestrator.py -v`。
- [x] 提交节点：`git add backend docs && git commit -m "feat: orchestrate hiring agent"`

## Git Node 6: SSE Trace Streaming

- [x] 在 `backend/app/api/routes_agent.py` 中添加 SSE event generator。
- [x] 发送 `agent.started`。
- [x] 发送 `agent.step`。
- [x] 发送 `tool.called`。
- [x] 发送 `tool.completed`。
- [x] 发送 `agent.completed`。
- [x] 对结构化失败发送 `agent.error`。
- [x] 添加 backend tests，验证 event 顺序。
- [x] 运行 `pytest backend/tests/test_agent_orchestrator.py -v`。
- [x] 提交节点：`git add backend docs && git commit -m "feat: stream agent trace events"`

## Git Node 7: React Frontend

- [x] 在 `frontend/` 下创建 Vite React TypeScript 项目。
- [x] 创建 `frontend/src/types/agent.ts`。
- [x] 创建 `frontend/src/types/plan.ts`。
- [x] 创建 `frontend/src/app/api.ts`。
- [x] 创建 `frontend/src/components/HiringRequestForm.tsx`。
- [x] 创建 `frontend/src/components/AgentTimeline.tsx`。
- [x] 创建 `frontend/src/components/CostBreakdownTable.tsx`。
- [x] 创建 `frontend/src/components/ComplianceChecklist.tsx`。
- [x] 创建 `frontend/src/components/EmploymentTermsSummary.tsx`。
- [x] 创建 `frontend/src/components/CountryComparison.tsx`。
- [x] 创建 `frontend/src/components/EmptyState.tsx`。
- [x] 创建 `frontend/src/components/ErrorState.tsx`。
- [x] 创建 `frontend/src/styles/globals.css`。
- [x] 在 `frontend/src/app/App.tsx` 中串联完整应用。
- [x] 添加 Singapore、Vietnam 合规冲突、Singapore/Vietnam 对比三个示例 prompt。
- [x] 添加 frontend tests，覆盖成本表和合规结果渲染。
- [x] 运行 `npm test -- --run`。
- [x] 提交节点：`git add frontend docs && git commit -m "feat: build employment agent UI"`

## Git Node 8: Docker Compose 和 README

- [x] 创建 `backend/Dockerfile`。
- [x] 创建 `frontend/Dockerfile`。
- [x] 创建根目录 `docker-compose.yml`。
- [x] 创建根目录 `.env.example`。
- [x] 创建或更新 `README.md`。
- [x] 文档说明一条命令启动：`docker compose up --build`。
- [x] 文档说明 `AGENT_MODE=deterministic` 和 `AGENT_MODE=llm`。
- [x] 文档说明政策来源边界。
- [x] 文档说明确定性成本计算边界。
- [x] 文档说明当前 fixture 规模下先使用结构化政策检索，而不是 vector RAG 的原因。
- [x] 运行 `docker compose config`。
- [ ] 提交节点：`git add .env.example README.md docker-compose.yml backend frontend docs && git commit -m "docs: add one-command runtime"`

## Git Node 9: 最终验证

- [ ] 运行 backend tests。
- [ ] 运行 frontend tests。
- [ ] 运行 Docker Compose startup。
- [ ] 手动验证 Singapore happy path。
- [ ] 手动验证 Vietnam compliance-conflict path。
- [ ] 手动验证 Singapore/Vietnam comparison path。
- [ ] 检查最终 UI 是否客户可读。
- [ ] 检查最终 API 输出是否覆盖 citation。
- [ ] 提交节点：`git add . && git commit -m "test: verify global employment agent"`
