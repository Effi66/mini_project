from dataclasses import dataclass
from typing import Callable

from app.tools.compliance import check_compliance
from app.tools.country_policy import get_country_policy
from app.tools.employment_cost import calculate_employment_cost


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    handler: Callable


def build_tool_registry() -> dict[str, ToolDefinition]:
    return {
        "get_country_policy": ToolDefinition(name="get_country_policy", handler=get_country_policy),
        "calculate_employment_cost": ToolDefinition(
            name="calculate_employment_cost",
            handler=calculate_employment_cost,
        ),
        "check_compliance": ToolDefinition(name="check_compliance", handler=check_compliance),
    }
