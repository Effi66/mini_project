from pydantic import BaseModel


class HiringTerms(BaseModel):
    gross_salary: float | None = None
    probation_months: float | None = None
    annual_leave_days: float | None = None
    working_hours_per_week: float | None = None
    notice_days: float | None = None
    include_13th_month: bool | None = None

