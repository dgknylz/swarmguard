from .base import (
    DefenseAction,
    DefenseAlgorithm,
    DefenseContext,
    DefenseDecision,
    DefenseObservation,
)
from .gtad_candidates import (
    ScoreWeights,
    generate_link_candidates,
    score_link_candidates,
    select_feasible_candidates,
)
from .observation import build_observation


class GtadRiskAlgorithm(DefenseAlgorithm):
    """Risk-aware, multi-objective and constraint-aware topology adaptation."""

    name = "gtad_risk"

    def __init__(
        self,
        budget: int = 0,
        range_multiplier: float = 1.5,
        maximum_degree: int = 8,
        weights: ScoreWeights | None = None,
    ) -> None:
        self.budget = budget
        self.range_multiplier = range_multiplier
        self.maximum_degree = maximum_degree
        self.weights = weights or ScoreWeights()

    def observe(self, context: DefenseContext) -> DefenseObservation:
        return build_observation(context, include_risk=True)

    def decide(self, observation: DefenseObservation) -> DefenseDecision:
        ranked = sorted(observation.risk_scores, key=lambda item: (-item[1], item[0]))
        maximum_range = observation.communication_range * self.range_multiplier
        generated = generate_link_candidates(observation)
        scored = score_link_candidates(
            observation,
            generated,
            maximum_range=maximum_range,
            weights=self.weights,
        )
        selection = select_feasible_candidates(
            observation,
            scored,
            maximum_range=maximum_range,
            maximum_degree=self.maximum_degree,
            budget=self.budget,
        )
        selected_links = [
            {
                "source": candidate.source,
                "target": candidate.target,
                "score": candidate.total_score,
                "connectivity_gain": candidate.connectivity_gain,
                "safety_score": candidate.safety_score,
                "distance_score": candidate.distance_score,
                "distance": round(candidate.distance, 3),
            }
            for candidate in selection.selected
        ]
        return DefenseDecision(
            algorithm=self.name,
            step=observation.step,
            actions=tuple(
                DefenseAction(
                    "add_edge",
                    candidate.source,
                    candidate.target,
                    (
                        f"GTAD skor={candidate.total_score:.4f}; "
                        f"bağlantı={candidate.connectivity_gain:.4f}; "
                        f"güvenlik={candidate.safety_score:.4f}; "
                        f"mesafe={candidate.distance_score:.4f}"
                    ),
                )
                for candidate in selection.selected
            ),
            metadata={
                "risk_scores": {str(node): score for node, score in observation.risk_scores},
                "highest_risk_nodes": [node for node, _ in ranked[:5]],
                "max_risk": ranked[0][1] if ranked else 0.0,
                "candidate_count": len(generated),
                "feasible_candidate_count": (len(selection.selected) + selection.budget_rejected),
                "selected_candidate_count": len(selection.selected),
                "range_rejected_count": selection.range_rejected,
                "degree_rejected_count": selection.degree_rejected,
                "budget_rejected_count": selection.budget_rejected,
                "selected_links": selected_links,
                "score_weights": self.weights.to_dict(),
                "constraints": {
                    "maximum_range": round(maximum_range, 3),
                    "maximum_degree": self.maximum_degree,
                    "budget": self.budget,
                },
            },
        )
