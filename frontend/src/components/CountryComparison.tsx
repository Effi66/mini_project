import { formatMoney } from "./CostBreakdownTable";
import type { ComparisonItem } from "../types/plan";

interface CountryComparisonProps {
  items: ComparisonItem[];
  recommendedCountry: string | null;
}

export function CountryComparison({ items, recommendedCountry }: CountryComparisonProps) {
  if (items.length === 0) {
    return null;
  }

  return (
    <section className="report-section" aria-labelledby="comparison-title">
      <div className="section-heading">
        <div>
          <h2 id="comparison-title">多国对比</h2>
          <p>{recommendedCountry ? `推荐优先考虑 ${recommendedCountry}。` : "按本币成本展示。"}</p>
        </div>
      </div>
      <div className="table-wrap">
        <table aria-label="多国成本与合规对比">
          <thead>
            <tr>
              <th>国家</th>
              <th>月度总成本</th>
              <th>年度总成本</th>
              <th>合规状态</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.country}>
                <td>{item.country}</td>
                <td>{formatMoney(item.monthly_total, item.currency)}</td>
                <td>{formatMoney(item.annual_total, item.currency)}</td>
                <td>{item.compliance_status === "pass" ? "Pass" : "Fail"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

