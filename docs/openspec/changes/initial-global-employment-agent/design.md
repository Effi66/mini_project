# Initial Global Employment Agent 设计

## 架构

应用分为 FastAPI backend 和 React frontend。Backend 负责所有政策查询、成本计算、合规检查和 Agent 编排。Frontend 负责用户输入、执行进度可视化，以及最终雇佣方案的客户可读渲染。

```text
React Frontend
  -> FastAPI API/SSE routes
    -> Agent Orchestrator
      -> get_country_policy
      -> calculate_employment_cost
      -> check_compliance
    -> Policy Repository
      -> data/*.json
```

## Backend 结构

```text
backend/
  app/
    main.py
    api/
      routes_agent.py
      routes_countries.py
    agent/
      orchestrator.py
      events.py
      schemas.py
    tools/
      country_policy.py
      employment_cost.py
      compliance.py
      registry.py
    domain/
      policy_repository.py
      cost_calculator.py
      compliance_checker.py
      citations.py
      normalizer.py
    models/
      policy.py
      request.py
      response.py
    core/
      config.py
      errors.py
  tests/
```

## Frontend 结构

```text
frontend/
  src/
    app/
      App.tsx
      api.ts
    components/
      HiringRequestForm.tsx
      AgentTimeline.tsx
      CostBreakdownTable.tsx
      ComplianceChecklist.tsx
      EmploymentTermsSummary.tsx
      CountryComparison.tsx
      EmptyState.tsx
      ErrorState.tsx
    types/
      agent.ts
      plan.ts
    styles/
      globals.css
```

## 数据边界

Policy repository 只加载 `data/` 下的本地文件。Backend 返回的每个政策结论都必须指向具体 source file、JSON path 和 quote。如果某个 policy fixture 没有足够信息支撑结论，应用返回 `unknown`。

## Agent Loop

Orchestrator 执行以下阶段：

1. 接收用户请求。
2. 解析结构化雇佣条款。
3. 解析目标国家。
4. 为每个目标国家调用 `get_country_policy`。
5. 为每个目标国家和薪资调用 `calculate_employment_cost`。
6. 为每个目标国家和用户请求条款调用 `check_compliance`。
7. 为失败检查项生成合规替代建议。
8. 组合最终客户可读方案。
9. 返回方案和 trace。

Deterministic fallback mode 使用规则解析演示 prompt。LLM-backed mode 可以解析和组织语言，但不能计算总额，也不能脱离工具输出判断合规。

## 成本计算

对每个雇主缴费项目：

```text
base = gross_salary if monthly_salary_cap is null else min(gross_salary, monthly_salary_cap)
monthly_amount = base * rate
annual_amount = monthly_amount * 12
```

奖金分摊：

```text
monthly_bonus_accrual = gross_salary * bonus_months_per_year / 12
annual_bonus = gross_salary * bonus_months_per_year
```

总成本：

```text
monthly_total = gross_salary + sum(monthly_contributions) + monthly_bonus_accrual
annual_total = monthly_total * 12
```

## 合规检查

Compliance checker 检查：

- 最低工资。
- 试用期。
- 年假。
- 工作时长。
- 解雇通知期。
- 法定 13 薪或强制奖金要求。

每个结果包含：

- 检查项名称。
- 用户请求值。
- 法定要求或推荐值。
- 状态：`pass`、`fail` 或 `unknown`。
- Citation。
- 失败项的替代建议。

## API 设计

```text
GET /api/countries
POST /api/agent/hire
POST /api/agent/hire/stream
GET /api/policies/{country}
POST /api/tools/calculate-cost
POST /api/tools/check-compliance
```

Stream endpoint 发送 Server-Sent Events：

```text
agent.started
agent.step
tool.called
tool.completed
agent.completed
agent.error
```

## Frontend 设计

第一屏就是可用应用，不做营销 landing page。页面包括：

- 自然语言雇佣请求表单。
- 示例 prompt。
- Agent 执行 timeline。
- 最终报告区域：
  - 请求摘要
  - 成本明细表
  - 合规检查列表
  - 关键雇佣条款
  - 多国请求时的对比表

UI 应该是克制、专业的 B2B operations tool 风格。避免营销页布局，也避免把 raw JSON 作为主要体验。

## 测试策略

Backend tests 覆盖：

- 国家别名解析。
- Policy fixture 加载。
- 缴费上限。
- 奖金分摊。
- 合规 `pass`、`fail`、`unknown` 结果。
- Citation 存在性。
- Agent trace 顺序。

Frontend tests 覆盖：

- 表单提交。
- Timeline 更新。
- 成本表渲染。
- 合规失败项渲染。
- 错误状态渲染。

## 运行方式

项目使用以下命令运行：

```bash
docker compose up --build
```

Backend 支持：

```text
AGENT_MODE=deterministic
AGENT_MODE=llm
```

如果没有 LLM API Key，默认使用 deterministic mode 作为演示模式。

