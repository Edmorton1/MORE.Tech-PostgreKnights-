from typing import Any, Dict, Union

PlanNode = Dict[str, Any]

PlanType = Union[PlanNode | list[PlanNode]]
