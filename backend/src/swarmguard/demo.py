from __future__ import annotations

from .config import SimulationConfig
from .engine import SimulationEngine


def main() -> None:
    config = SimulationConfig(steps=20, seed=42)
    frames = SimulationEngine(config).run()

    print("step infected edges gcc efficiency lambda_2")
    for frame in frames:
        metrics = frame.metrics
        print(
            f"{frame.step:>4} "
            f"{metrics['infected_count']:>8} "
            f"{metrics['edge_count']:>5} "
            f"{metrics['largest_component_ratio']:.3f} "
            f"{metrics['global_efficiency']:.3f} "
            f"{metrics['algebraic_connectivity']:.3f}"
        )


if __name__ == "__main__":
    main()
