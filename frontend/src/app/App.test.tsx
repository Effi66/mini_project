import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import App from "./App";
import { streamResponse } from "../test/fixtures";

function buildSseBody(): string {
  return [
    'event: agent.started\ndata: {"message":"开始处理雇佣需求。"}\n\n',
    'event: agent.step\ndata: {"step":"parse_hiring_terms","message":"已解析国家、薪资、岗位和雇佣条款。"}\n\n',
    `event: agent.completed\ndata: ${JSON.stringify({ plan: streamResponse.plan })}\n\n`
  ].join("");
}

test("submits a hiring request and renders timeline plus final plan", async () => {
  const user = userEvent.setup();
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: true,
      body: new Response(buildSseBody()).body
    })
  );

  render(<App />);

  await user.click(screen.getByRole("button", { name: "使用新加坡示例" }));
  await user.click(screen.getByRole("button", { name: "生成雇佣方案" }));

  await waitFor(() => {
    expect(screen.getByText("开始处理雇佣需求。")).toBeInTheDocument();
  });
  expect(screen.getByText("已解析国家、薪资、岗位和雇佣条款。")).toBeInTheDocument();
  expect(screen.getByText("Singapore")).toBeInTheDocument();
  expect(screen.getByText("SGD 119,096.00")).toBeInTheDocument();
});

