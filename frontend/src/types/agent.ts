import type { HiringPlan } from "./plan";

export interface AgentTraceStep {
  event_type: string;
  name: string;
  message: string;
  tool_name: string | null;
}

export interface AgentRunResponse {
  plan: HiringPlan;
  trace: AgentTraceStep[];
}

export type AgentStreamEvent =
  | {
      event: "agent.started";
      data: { message: string };
    }
  | {
      event: "agent.step";
      data: { step: string; message: string };
    }
  | {
      event: "tool.called" | "tool.completed";
      data: { tool: string; message: string };
    }
  | {
      event: "agent.completed";
      data: { plan: HiringPlan };
    }
  | {
      event: "agent.error";
      data: { detail: string };
    };

