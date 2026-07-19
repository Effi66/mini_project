import type { EmploymentCostBreakdown } from "../types/plan";

interface CostBreakdownTableProps {
  breakdown: EmploymentCostBreakdown;
}

export function CostBreakdownTable({ breakdown }: CostBreakdownTableProps) {
  const rows = [
    {
      name: "月基本工资",
      base: breakdown.monthly.base_salary,
      rate: null,
      monthly: breakdown.monthly.base_salary,
      annual: breakdown.annual.base_salary,
      note: "客户输入的 gross salary。"
    },
    ...breakdown.monthly.employer_contributions.map((item) => ({
      name: item.name,
      base: item.base,
      rate: item.rate,
      monthly: item.monthly_amount,
      annual: item.annual_amount,
      note: item.note
    })),
    {
      name: "13 薪/奖金分摊",
      base: breakdown.gross_salary_monthly,
      rate: null,
      monthly: breakdown.monthly.bonus_accrual,
      annual: breakdown.annual.bonus,
      note: breakdown.bonus.citation.quote
    }
  ];

  return (
    <section className="report-section" aria-labelledby={`${breakdown.country}-cost-title`}>
      <div className="section-heading">
        <div>
          <h2 id={`${breakdown.country}-cost-title`}>{breakdown.country} 成本明细</h2>
          <p>
            月度总成本 {formatMoney(breakdown.monthly.total, breakdown.currency)}，年度总成本{" "}
            {formatMoney(breakdown.annual.total, breakdown.currency)}
          </p>
        </div>
      </div>
      <div className="table-wrap">
        <table aria-label={`${breakdown.country} 成本明细`}>
          <thead>
            <tr>
              <th>项目</th>
              <th>计算基数</th>
              <th>费率</th>
              <th>月度金额</th>
              <th>年度金额</th>
              <th>说明</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.name}>
                <td>{row.name}</td>
                <td>{formatMoney(row.base, breakdown.currency)}</td>
                <td>{row.rate === null ? "一" : formatPercent(row.rate)}</td>
                <td>{formatMoney(row.monthly, breakdown.currency)}</td>
                <td>{formatMoney(row.annual, breakdown.currency)}</td>
                <td>{row.note}</td>
              </tr>
            ))}
          </tbody>
          <tfoot>
            <tr>
              <td colSpan={3}>总计</td>
              <td>{formatMoney(breakdown.monthly.total, breakdown.currency)}</td>
              <td>{formatMoney(breakdown.annual.total, breakdown.currency)}</td>
              <td>已按本地政策 fixture 和确定性代码计算。</td>
            </tr>
          </tfoot>
        </table>
      </div>
    </section>
  );
}

export function formatMoney(amount: number, currency: string): string {
  return `${currency} ${amount.toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })}`;
}

function formatPercent(rate: number): string {
  return `${(rate * 100).toFixed(2)}%`;
}

