import pytest

from swarmguard.sis import infection_probability


@pytest.mark.parametrize(
    ("beta", "infected_neighbors", "expected"),
    [
        (0.2, 0, 0.0),
        (0.2, 1, 0.2),
        (0.2, 2, 0.36),
        (1.0, 5, 1.0),
    ],
)
def test_infection_probability(beta: float, infected_neighbors: int, expected: float) -> None:
    assert infection_probability(beta, infected_neighbors) == pytest.approx(expected)
