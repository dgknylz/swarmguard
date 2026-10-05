from .base import DefenseAlgorithm, DefenseContext, DefenseDecision, DefenseObservation
from .observation import build_observation


class NoDefenseAlgorithm(DefenseAlgorithm):
    name = "none"

    def observe(self, context: DefenseContext) -> DefenseObservation:
        return build_observation(context)

    def decide(self, observation: DefenseObservation) -> DefenseDecision:
        return DefenseDecision(algorithm=self.name, step=observation.step)
