import { render, screen } from "@testing-library/react";

import { CostBreakdownTable } from "./CostBreakdownTable";
import { singaporePlan } from "../test/fixtures";

test("renders cost breakdown as a client-readable table", () => {
  render(<CostBreakdownTable breakdown={singaporePlan.cost_breakdowns[0]} />);

  expect(screen.getByRole("table", { name: "Singapore 成本明细" })).toBeInTheDocument();
  expect(screen.getByText("CPF 公积金（雇主缴纳）")).toBeInTheDocument();
  expect(screen.getByText("SGD 7,400.00")).toBeInTheDocument();
  expect(screen.getByText("17.00%")).toBeInTheDocument();
  expect(screen.getByText("SGD 1,258.00")).toBeInTheDocument();
  expect(screen.getByText("SGD 119,096.00")).toBeInTheDocument();
});

