import { CheckCircle2, HelpCircle, XCircle } from "lucide-react";

import type { ComplianceCheck, ComplianceResult } from "../types/plan";

interface ComplianceChecklistProps {
  result: ComplianceResult;
}

export function ComplianceChecklist({ result }: ComplianceChecklistProps) {
  return (
    <section className="report-section" aria-labelledby={`${result.country}-compliance-title`}>
      <div className="section-heading">
        <div>
          <h2 id={`${result.country}-compliance-title`}>{result.country} 合规检查</h2>
          <p>逐项展示 pass/fail/unknown、政策原文和替代建议。</p>
        </div>
        <span className={`status-pill ${result.overall_status}`}>
          {result.overall_status === "pass" ? "Pass" : "Fail"}
        </span>
      </div>
      <div className="check-list">
        {result.checks.map((check) => (
          <ComplianceRow key={`${result.country}-${check.item}`} check={check} />
        ))}
      </div>
    </section>
  );
}

function ComplianceRow({ check }: { check: ComplianceCheck }) {
  const Icon = check.status === "pass" ? CheckCircle2 : check.status === "fail" ? XCircle : HelpCircle;
  return (
    <article className={`check-row ${check.status}`}>
      <div className="check-title">
        <Icon aria-hidden="true" size={18} />
        <strong>{check.item}</strong>
        <span>{labelForStatus(check.status)}</span>
      </div>
      <dl>
        <div>
          <dt>客户要求</dt>
          <dd>{check.requested ?? "未提供"}</dd>
        </div>
        <div>
          <dt>当地规则</dt>
          <dd>{check.required ?? "需依据方案建议确认"}</dd>
        </div>
      </dl>
      {check.recommendation ? <p className="recommendation">{check.recommendation}</p> : null}
      <details>
        <summary>{`${check.citation.source_file} · ${check.citation.json_path}`}</summary>
        <p>{check.citation.quote}</p>
      </details>
    </article>
  );
}

function labelForStatus(status: ComplianceCheck["status"]): string {
  if (status === "pass") {
    return "Pass";
  }
  if (status === "fail") {
    return "Fail";
  }
  return "Unknown";
}

