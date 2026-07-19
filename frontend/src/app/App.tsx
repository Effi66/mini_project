import { useState } from "react";

import { streamHiringPlan } from "./api";
import { AgentTimeline } from "../components/AgentTimeline";
import { ComplianceChecklist } from "../components/ComplianceChecklist";
import { CostBreakdownTable } from "../components/CostBreakdownTable";
import { CountryComparison } from "../components/CountryComparison";
import { EmploymentTermsSummary } from "../components/EmploymentTermsSummary";
import { EmptyState } from "../components/EmptyState";
import { ErrorState } from "../components/ErrorState";
import { HiringRequestForm } from "../components/HiringRequestForm";
import type { AgentStreamEvent } from "../types/agent";
import type { HiringPlan } from "../types/plan";
import "../styles/globals.css";

const initialPrompt = "我想在新加坡雇一名月薪 8000 SGD 的高级工程师，10 月入职";

export default function App() {
  const [message, setMessage] = useState(initialPrompt);
  const [events, setEvents] = useState<AgentStreamEvent[]>([]);
  const [plan, setPlan] = useState<HiringPlan | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit() {
    setIsLoading(true);
    setError(null);
    setPlan(null);
    setEvents([]);

    try {
      await streamHiringPlan(message, (event) => {
        setEvents((current) => [...current, event]);
        if (event.event === "agent.completed") {
          setPlan(event.data.plan);
        }
        if (event.event === "agent.error") {
          setError(event.data.detail);
        }
      });
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "请求失败。");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <HiringRequestForm
        value={message}
        isLoading={isLoading}
        onChange={setMessage}
        onSubmit={handleSubmit}
      />
      <div className="workspace-grid">
        <AgentTimeline events={events} isLoading={isLoading} />
        <section className="plan-surface" aria-label="最终雇佣方案">
          {error ? <ErrorState message={error} /> : null}
          {!plan && !error ? <EmptyState /> : null}
          {plan ? <HiringPlanReport plan={plan} /> : null}
        </section>
      </div>
    </main>
  );
}

function HiringPlanReport({ plan }: { plan: HiringPlan }) {
  return (
    <div className="report-stack">
      <section className="summary-band" aria-label="方案摘要">
        <div>
          <p className="eyebrow">方案摘要</p>
          <h2>{plan.request_summary.country}</h2>
        </div>
        <p>{plan.client_ready_summary}</p>
      </section>
      <CountryComparison items={plan.comparison} recommendedCountry={plan.recommended_country} />
      {plan.cost_breakdowns.map((breakdown) => (
        <CostBreakdownTable key={breakdown.country} breakdown={breakdown} />
      ))}
      {plan.compliance_results.map((result) => (
        <ComplianceChecklist key={result.country} result={result} />
      ))}
      {plan.employment_terms.map((terms) => (
        <EmploymentTermsSummary key={terms.country} terms={terms} />
      ))}
    </div>
  );
}

