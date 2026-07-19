import type { AgentRunResponse } from "../types/agent";
import type { HiringPlan } from "../types/plan";

export const singaporePlan: HiringPlan = {
  request_summary: {
    countries: ["Singapore"],
    country: "Singapore",
    role: "高级工程师",
    gross_salary: 8000,
    currency: "SGD",
    start_date: "2026-10"
  },
  cost_breakdowns: [
    {
      country: "Singapore",
      country_code: "SG",
      currency: "SGD",
      gross_salary_monthly: 8000,
      monthly: {
        base_salary: 8000,
        employer_contributions: [
          {
            name: "CPF 公积金（雇主缴纳）",
            base: 7400,
            rate: 0.17,
            monthly_amount: 1258,
            annual_amount: 15096,
            note: "缴费基数以月薪与上限孰低计算。"
          }
        ],
        employer_contributions_total: 1258,
        bonus_accrual: 666.67,
        total: 9924.67
      },
      annual: {
        base_salary: 96000,
        employer_contributions: 15096,
        bonus: 8000,
        total: 119096
      },
      bonus: {
        months_per_year: 1,
        basis: "customary",
        monthly_accrual: 666.67,
        annual_amount: 8000,
        citation: {
          source_file: "data/singapore.json",
          json_path: "thirteenth_month.notes",
          quote: "AWS 为市场普遍惯例，但非法定强制。"
        }
      }
    }
  ],
  compliance_results: [
    {
      country: "Singapore",
      country_code: "SG",
      currency: "SGD",
      overall_status: "pass",
      checks: [
        {
          item: "试用期",
          status: "pass",
          requested: "6 个月",
          required: "法律无强制上限；市场惯例 3 个月。",
          citation: {
            source_file: "data/singapore.json",
            json_path: "probation.notes",
            quote: "法律无强制上限，市场惯例 3-6 个月。"
          },
          recommendation: null
        }
      ]
    }
  ],
  employment_terms: [
    {
      country: "Singapore",
      probation: "建议 3 个月；法律无强制上限。",
      annual_leave: "建议 14 天，法定最低 7 天。",
      termination_notice: "以雇佣合同约定优先，此为法定最低标准。",
      working_hours: "标准每周 44 小时。",
      bonus: "AWS 为市场普遍惯例，但非法定强制。"
    }
  ],
  comparison: [],
  recommended_country: null,
  client_ready_summary: "在 Singapore 雇佣该岗位的月度雇主总成本约为 9924.67 SGD。",
  policy_citation_status: "complete"
};

export const vietnamConflictPlan: HiringPlan = {
  ...singaporePlan,
  request_summary: {
    countries: ["Vietnam"],
    country: "Vietnam",
    role: "工程师",
    gross_salary: 40000000,
    currency: "VND",
    start_date: null
  },
  compliance_results: [
    {
      country: "Vietnam",
      country_code: "VN",
      currency: "VND",
      overall_status: "fail",
      checks: [
        {
          item: "试用期",
          status: "fail",
          requested: "6 个月",
          required: "不超过 2 个月",
          citation: {
            source_file: "data/vietnam.json",
            json_path: "probation.notes",
            quote: "需要大专及以上学历的岗位试用期上限 60 天。"
          },
          recommendation: "将试用期调整为 2 个月以内。"
        }
      ]
    }
  ],
  client_ready_summary: "方案中存在合规冲突，需要调整后再推进雇佣。"
};

export const streamResponse: AgentRunResponse = {
  plan: singaporePlan,
  trace: [
    {
      event_type: "agent.step",
      name: "parse_hiring_terms",
      message: "已解析国家、薪资、岗位和雇佣条款。",
      tool_name: null
    }
  ]
};

