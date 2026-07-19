import type { EmploymentTermsSummary as EmploymentTermsSummaryType } from "../types/plan";

interface EmploymentTermsSummaryProps {
  terms: EmploymentTermsSummaryType;
}

export function EmploymentTermsSummary({ terms }: EmploymentTermsSummaryProps) {
  return (
    <section className="report-section" aria-labelledby={`${terms.country}-terms-title`}>
      <h2 id={`${terms.country}-terms-title`}>{terms.country} 关键雇佣条款</h2>
      <dl className="terms-grid">
        <div>
          <dt>试用期</dt>
          <dd>{terms.probation}</dd>
        </div>
        <div>
          <dt>年假</dt>
          <dd>{terms.annual_leave}</dd>
        </div>
        <div>
          <dt>通知期</dt>
          <dd>{terms.termination_notice}</dd>
        </div>
        <div>
          <dt>工作时长</dt>
          <dd>{terms.working_hours}</dd>
        </div>
        <div>
          <dt>13 薪/奖金</dt>
          <dd>{terms.bonus}</dd>
        </div>
      </dl>
    </section>
  );
}

