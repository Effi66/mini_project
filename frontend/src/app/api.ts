import type { AgentStreamEvent } from "../types/agent";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

export async function streamHiringPlan(
  message: string,
  onEvent: (event: AgentStreamEvent) => void
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/agent/hire/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ message })
  });

  if (!response.ok) {
    throw new Error(`请求失败：${response.status}`);
  }
  if (!response.body) {
    throw new Error("浏览器不支持流式响应。");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }
    buffer += decoder.decode(value, { stream: true });
    buffer = emitCompleteEvents(buffer, onEvent);
  }

  buffer += decoder.decode();
  emitCompleteEvents(`${buffer}\n\n`, onEvent);
}

function emitCompleteEvents(
  buffer: string,
  onEvent: (event: AgentStreamEvent) => void
): string {
  const chunks = buffer.split(/\n\n/);
  const remaining = chunks.pop() ?? "";

  for (const chunk of chunks) {
    const event = parseSseChunk(chunk);
    if (event) {
      onEvent(event);
    }
  }
  return remaining;
}

export function parseSseChunk(chunk: string): AgentStreamEvent | null {
  const eventLine = chunk.split("\n").find((line) => line.startsWith("event: "));
  const dataLine = chunk.split("\n").find((line) => line.startsWith("data: "));
  if (!eventLine || !dataLine) {
    return null;
  }

  return {
    event: eventLine.replace("event: ", ""),
    data: JSON.parse(dataLine.replace("data: ", ""))
  } as AgentStreamEvent;
}
