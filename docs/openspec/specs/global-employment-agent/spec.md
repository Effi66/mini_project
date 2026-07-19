# Global Employment Agent 规格

## 目标

Global Employment Agent 将自然语言雇佣请求转换为结构化、客户可读的雇佣方案。系统必须结合 agentic orchestration、确定性政策查询、成本计算、合规检查和 citation-backed presentation。

## 范围

系统支持 `data/*.json` 中已有本地政策 fixture 对应的国家：

- Singapore
- Vietnam
- Indonesia
- Philippines
- Japan

系统不做实时法律检索、实时政策更新、汇率换算、薪资发放、报税、社保申报或正式法律意见。

## Requirements

### Requirement: 自然语言雇佣请求

系统必须接受客户的自然语言雇佣请求，并提取结构化雇佣条款。

#### Scenario: 单国请求

- 前提：用户输入 `我想在新加坡雇一名月薪 8000 SGD 的高级工程师，10 月入职`
- 当：Agent 处理该请求
- 则：解析结果包含国家 `Singapore`、月度 gross salary `8000`、币种 `SGD`、岗位 `高级工程师` 和入职月份 `10`

#### Scenario: 可选条款缺失

- 前提：用户没有填写试用期、年假、通知期和工作时长
- 当：Agent 生成方案
- 则：系统基于本地政策数据推荐合规默认条款
- 并且：不得把用户未填写的可选条款标记为失败

### Requirement: 政策来源控制

系统的所有雇佣政策结论都必须来自本地政策文件。

#### Scenario: 有数据支撑的政策结论

- 前提：某个合规结果提到 Vietnam 的试用期限制
- 当：系统返回该结果
- 则：结果包含指向 `data/vietnam.json` 和相关 JSON path 的 citation

#### Scenario: 本地数据不支持的政策结论

- 前提：用户询问的政策主题未被本地数据覆盖
- 当：Agent 生成响应
- 则：响应将该主题标记为 `unknown` 或要求用户补充信息
- 并且：不得使用模型自身知识补齐缺失内容

### Requirement: 国家政策工具

后端必须提供 `get_country_policy(country)` 工具。

#### Scenario: 国家查询成功

- 前提：输入国家是 `SG`、`Singapore` 或 `新加坡`
- 当：工具运行
- 则：返回 Singapore 政策 fixture、标准化国家元数据和政策 citation

#### Scenario: 国家查询失败

- 前提：输入国家不在支持范围内
- 当：工具运行
- 则：返回结构化错误和支持国家列表

### Requirement: 雇佣成本工具

后端必须提供 `calculate_employment_cost(country, gross_salary)` 工具。

#### Scenario: 缴费上限生效

- 前提：Singapore 月度 gross salary 为 `8000`
- 当：系统计算成本
- 则：CPF 雇主缴费用 `7400` 作为计算基数
- 并且：SDL 用 `4500` 作为计算基数
- 并且：输出包含基本工资、每个雇主缴费项目、奖金分摊、月度总成本和年度总成本

#### Scenario: 计算由代码确定性完成

- 前提：任意支持国家和 gross salary
- 当：系统计算成本
- 则：所有算术都在应用代码中完成
- 并且：LLM 不计算任何总额

### Requirement: 合规检查工具

后端必须提供 `check_compliance(country, terms)` 工具。

#### Scenario: 试用期违规

- 前提：国家是 Vietnam
- 并且：用户请求试用期为 `6` 个月
- 当：系统检查合规
- 则：试用期检查返回 `fail`
- 并且：结果引用 Vietnam 试用期政策原文
- 并且：建议将普通专业岗位试用期调整到不超过 `2` 个月

#### Scenario: 遗漏法定 13 薪或强制奖金

- 前提：某国家政策数据包含法定 13 薪或类似强制奖金
- 并且：用户明确要求不发放
- 当：系统检查合规
- 则：结果返回 `fail`
- 并且：建议纳入该法定支付

### Requirement: Agentic Loop

后端必须实现显式 Agent loop，用于编排解析、政策查询、成本计算、合规检查和方案生成。

#### Scenario: 可查看 tool trace

- 前提：Agent 正在处理一条雇佣请求
- 当：系统返回最终响应
- 则：响应包含有序 Agent steps 和 tool-call trace data

#### Scenario: 合规冲突处理

- 前提：用户请求与当地规则冲突
- 当：Agent 生成最终方案
- 则：方案明确标出冲突
- 并且：提供合规替代方案
- 并且：不得隐藏失败检查项

### Requirement: 客户可读前端

前端必须展示 Agent 执行 trace 和最终雇佣方案，并保证最终方案客户可读。

#### Scenario: 成本展示

- 前提：后端返回成本明细
- 当：前端渲染方案
- 则：使用表格展示成本项目、计算基数、费率、月度金额、年度金额和说明

#### Scenario: 合规展示

- 前提：后端返回合规检查
- 当：前端渲染方案
- 则：`pass` 和 `fail` 状态视觉上可区分
- 并且：每个基于政策的检查项都能查看 citation 原文

### Requirement: 一条命令运行

项目必须提供一条命令的本地运行方式。

#### Scenario: Docker Compose 启动

- 前提：本机已安装 Docker
- 当：用户运行 `docker compose up --build`
- 则：backend 和 frontend 都能启动
- 并且：用户可以在浏览器访问 frontend

### Requirement: 多国对比

系统应支持对多个支持国家的雇佣成本和合规结果进行比较。

#### Scenario: 对比 Singapore 和 Vietnam

- 前提：用户要求对比在 Singapore 和 Vietnam 雇佣同一岗位
- 当：Agent 处理请求
- 则：分别为两个国家调用政策、成本和合规工具
- 并且：返回包含月度成本、年度成本、合规状态和推荐结论的对比表

