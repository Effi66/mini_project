import { CheckCircle2, LoaderCircle, Wrench } from "lucide-react";

import type { AgentStreamEvent } from "../types/agent";

interface AgentTimelineProps {
  events: AgentStreamEvent[];
  isLoading: boolean;
}

export function AgentTimeline({ events, isLoading }: AgentTimelineProps) {
  return (
    <section className="timeline-section" aria-labelledby="timeline-title">
      <div className="section-heading">
        <div>
          <h2 id="timeline-title">Agent 执行步骤</h2>
          <p>每一步来自后端 trace 或工具调用事件。</p>
        </div>
        {isLoading ? <LoaderCircle className="spin" aria-hidden="true" size={20} /> : null}
      </div>
      {events.length === 0 ? (
        <p className="muted">提交请求后会在这里看到 Agent 的执行流。</p>
      ) : (
        <ol className="timeline">
          {events.map((event, index) => (
            <li key={`${event.event}-${index}`}>
              {event.event.startsWith("tool.") ? (
                <Wrench aria-hidden="true" size={16} />
              ) : (
                <CheckCircle2 aria-hidden="true" size={16} />
              )}
              <div>
                <span>{event.event}</span>
                <p>{messageForEvent(event)}</p>
              </div>
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}

function messageForEvent(event: AgentStreamEvent): string {
  if (event.event === "agent.completed") {
    return "雇佣方案已生成。";
  }
  if (event.event === "agent.error") {
    return event.data.detail;
  }
  return event.data.message;
}

