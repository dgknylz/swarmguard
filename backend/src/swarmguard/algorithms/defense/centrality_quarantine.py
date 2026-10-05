from .base import (
    DefenseAction,
    DefenseAlgorithm,
    DefenseContext,
    DefenseDecision,
    DefenseObservation,
)
from .observation import build_observation


class CentralityQuarantineAlgorithm(DefenseAlgorithm):
    name = "centrality_quarantine"

    def __init__(self, budget: int):
        self.budget = budget

    def observe(self, context: DefenseContext) -> DefenseObservation:
        return build_observation(context)

    def decide(self, observation: DefenseObservation) -> DefenseDecision:
        degrees = dict(observation.degrees)
        betweenness = dict(observation.betweenness)
        max_degree = max(degrees.values(), default=1) or 1
        max_betweenness = max(betweenness.values(), default=1.0) or 1.0
        ranked = sorted(
            (
                (
                    0.55 * degrees[node] / max_degree + 0.45 * betweenness[node] / max_betweenness,
                    node,
                )
                for node in observation.infected
                if degrees.get(node, 0) > 0
            ),
            key=lambda item: (-item[0], item[1]),
        )
        selected = ranked[: self.budget]
        return DefenseDecision(
            algorithm=self.name,
            step=observation.step,
            actions=tuple(
                DefenseAction("quarantine_node", node, reason=f"merkeziyet={score:.4f}")
                for score, node in selected
            ),
            metadata={"quarantined_nodes": [node for _, node in selected]},
        )
