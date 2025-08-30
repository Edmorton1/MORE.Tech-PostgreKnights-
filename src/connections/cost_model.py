class CostModel:
    """
    Модель для вычисления "стоимости" или "веса" узлов в плане выполнения запроса.
    """
    def __init__(self, high_cost_threshold=10000.0, high_rows_threshold=10000):
        self.high_cost_threshold = high_cost_threshold
        self.high_rows_threshold = high_rows_threshold

    def calculate_node_cost(self, node: dict) -> dict:
        node_type = node.get("Node Type")
        total_cost = node.get("Total Cost", 0)
        plan_rows = node.get("Plan Rows", 0)

        cost_impact = 0
        rows_impact = 0

        if total_cost > self.high_cost_threshold:
            cost_impact = 10
        if plan_rows > self.high_rows_threshold:
            rows_impact = 5

        if node_type == "Seq Scan":
            cost_impact += 15
        elif node_type == "Nested Loop":
            cost_impact += 10
        elif node_type == "Sort":
            cost_impact += 8

        node_score = cost_impact + rows_impact

        return {
            "node_type": node_type,
            "score": node_score,
            "cost_impact": cost_impact,
            "rows_impact": rows_impact,
            "details": f"Оценка узла '{node_type}' (cost={total_cost}, rows={plan_rows})."
        }

    def calculate_plan_score(self, plan: dict) -> int:
        total_score = 0
        total_score += self.calculate_node_cost(plan)["score"]
        for subplan in plan.get("Plans", []):
            total_score += self.calculate_plan_score(subplan)
        return total_score