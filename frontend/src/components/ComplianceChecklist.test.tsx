import { render, screen } from "@testing-library/react";

import { ComplianceChecklist } from "./ComplianceChecklist";
import { vietnamConflictPlan } from "../test/fixtures";

test("renders failed compliance checks with recommendation and citation", () => {
  render(<ComplianceChecklist result={vietnamConflictPlan.compliance_results[0]} />);

  expect(screen.getByText("Vietnam 合规检查")).toBeInTheDocument();
  expect(screen.getAllByText("Fail").length).toBeGreaterThan(0);
  expect(screen.getByText("试用期")).toBeInTheDocument();
  expect(screen.getByText("将试用期调整为 2 个月以内。")).toBeInTheDocument();
  expect(screen.getByText("data/vietnam.json · probation.notes")).toBeInTheDocument();
  expect(screen.getByText("需要大专及以上学历的岗位试用期上限 60 天。")).toBeInTheDocument();
});
