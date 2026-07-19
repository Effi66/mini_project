export type ComplianceStatus = "pass" | "fail" | "unknown";

export interface Citation {
  source_file: string;
  json_path: string;
  quote: string;
}

export interface ContributionCostItem {
  name: string;
  base: number;
  rate: number;
  monthly_amount: number;
  annual_amount: number;
  note: string;
}

export interface BonusBreakdown {
  months_per_year: number;
  basis: string;
  monthly_accrual: number;
  annual_amount: number;
  citation: Citation;
}

export interface MonthlyCostBreakdown {
  base_salary: number;
  employer_contributions: ContributionCostItem[];
  employer_contributions_total: number;
  bonus_accrual: number;
  total: number;
}

export interface AnnualCostBreakdown {
  base_salary: number;
  employer_contributions: number;
  bonus: number;
  total: number;
}

export interface EmploymentCostBreakdown {
  country: string;
  country_code: string;
  currency: string;
  gross_salary_monthly: number;
  monthly: MonthlyCostBreakdown;
  annual: AnnualCostBreakdown;
  bonus: BonusBreakdown;
}

export interface ComplianceCheck {
  item: string;
  status: ComplianceStatus;
  requested: string | null;
  required: string | null;
  citation: Citation;
  recommendation: string | null;
}

export interface ComplianceResult {
  country: string;
  country_code: string;
  currency: string;
  overall_status: "pass" | "fail";
  checks: ComplianceCheck[];
}

export interface EmploymentTermsSummary {
  country: string;
  probation: string;
  annual_leave: string;
  termination_notice: string;
  working_hours: string;
  bonus: string;
}

export interface ComparisonItem {
  country: string;
  currency: string;
  monthly_total: number;
  annual_total: number;
  compliance_status: "pass" | "fail";
}

export interface HiringRequestSummary {
  countries: string[];
  country: string;
  role: string | null;
  gross_salary: number;
  currency: string;
  start_date: string | null;
}

export interface HiringPlan {
  request_summary: HiringRequestSummary;
  cost_breakdowns: EmploymentCostBreakdown[];
  compliance_results: ComplianceResult[];
  employment_terms: EmploymentTermsSummary[];
  comparison: ComparisonItem[];
  recommended_country: string | null;
  client_ready_summary: string;
  policy_citation_status: string;
}

