## mini project 
构建一个「全球雇佣数字员工」：客户用自然语言提出雇佣需求（例如"我想在新加坡雇一名月薪 8000 SGD 的高级工程师，10 月入职"），Agent 自动产出完整的雇佣方案。

我们提供的数据（5 个国家的规则文件，markdown/JSON）：每国包含雇主社保/公积金费率、13 薪或年终奖惯例、法定年假、试用期上限、解雇通知期、个税概要、货币。数据可以是简化的模拟数据，但 Agent 的所有结论必须来自这些文件，不允许用模型自身知识回答政策问题。

### 必做

后端（Python/FastAPI 或 Node）：实现 Agentic Loop，至少三个工具——
get_country_policy(country)：查询国家雇佣规则
calculate_employment_cost(country, gross_salary)：计算雇主月度/年度总成本（工资 + 雇主缴纳部分 + 13薪分摊等），计算必须在代码里做，不能让 LLM 算
check_compliance(country, terms)：校验客户要求是否违规（如试用期 6 个月但该国上限 3 个月）
处理含合规冲突的请求：如客户要求违反当地规定，方案中必须标出冲突并给出合规替代建议。
输出结构化雇佣方案：成本明细表（分项列出）、合规检查结果（逐项 pass/fail + 引用规则原文）、关键雇佣条款摘要。
前端（React + TypeScript）：展示 Agent 执行步骤流 + 最终方案（成本明细要像给客户看的，不是 JSON dump）。
README + 一条命令可跑（docker compose 或脚本），保留真实 git 提交历史。

### 加分（选做）

工具层封装成 MCP Server
Agent 步骤 SSE 流式输出
支持多国对比（"在新加坡和越南雇同样的人，哪个成本低？"——考多轮工具调用编排）
政策文件用 RAG 检索而非整文件塞 prompt，并说明理由
工具失败的重试/降级处理