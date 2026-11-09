"""Spectral graph quantities behind the SwarmGuard theorems and the spectral defense.

Notation matches the Teori page: ``A`` is the adjacency matrix with largest eigenvalue
``λ₁`` (spectral radius) and unit Perron vector ``u``; ``L = D - A`` is the Laplacian with
algebraic connectivity ``λ₂`` and unit Fiedler vector ``v`` (orthogonal to the all-ones
vector).
"""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]

_ZERO = 1e-9


def adjacency_from_edges(node_count: int, edges: Iterable[tuple[int, int]]) -> FloatArray:
    matrix = np.zeros((node_count, node_count))
    for source, target in edges:
        if source != target:
            matrix[source, target] = matrix[target, source] = 1.0
    return matrix


def spectral_radius(adjacency: FloatArray) -> float:
    """λ₁(A); non-negative for every symmetric non-negative matrix with zero trace."""
    if adjacency.size == 0:
        return 0.0
    return float(max(np.linalg.eigvalsh(adjacency)[-1], 0.0))


def perron_pair(adjacency: FloatArray) -> tuple[float, FloatArray]:
    """Return ``(λ₁, u)`` with ``u`` the non-negative unit Perron vector.

    When several components share λ₁ the eigenspace is spanned by their Perron
    vectors, each of constant sign, so the absolute value is still an eigenvector.
    """
    node_count = adjacency.shape[0]
    if node_count == 0:
        return 0.0, np.zeros(0)
    values, vectors = np.linalg.eigh(adjacency)
    radius = float(max(values[-1], 0.0))
    if radius <= _ZERO:
        return 0.0, np.full(node_count, 1.0 / np.sqrt(node_count))
    vector = np.abs(vectors[:, -1])
    return radius, vector / np.linalg.norm(vector)


def laplacian(adjacency: FloatArray) -> FloatArray:
    return np.diag(adjacency.sum(axis=1)) - adjacency


def fiedler_pair(adjacency: FloatArray) -> tuple[float, FloatArray]:
    """Return ``(λ₂, v)`` with ``v ⟂ 1`` and ``vᵀLv = λ₂``.

    For a disconnected graph λ₂ = 0 and ``v`` is a unit vector of the Laplacian null
    space orthogonal to the all-ones vector (it separates the components).
    """
    node_count = adjacency.shape[0]
    if node_count < 2:
        return 0.0, np.zeros(node_count)
    values, vectors = np.linalg.eigh(laplacian(adjacency))
    if values[1] > _ZERO:
        vector = vectors[:, 1] - vectors[:, 1].mean()
        return float(values[1]), vector / np.linalg.norm(vector)

    null_space = vectors[:, values <= _ZERO]
    centered = null_space - null_space.mean(axis=0)
    norms = np.linalg.norm(centered, axis=0)
    best = int(np.argmax(norms))
    if norms[best] <= _ZERO:
        return 0.0, np.zeros(node_count)
    return 0.0, centered[:, best] / norms[best]


def connected_components(adjacency: FloatArray) -> list[list[int]]:
    """Components ordered by decreasing size, ties broken by the smallest node id."""
    node_count = adjacency.shape[0]
    seen = np.zeros(node_count, dtype=bool)
    components: list[list[int]] = []
    for start in range(node_count):
        if seen[start]:
            continue
        stack = [start]
        seen[start] = True
        members = []
        while stack:
            node = stack.pop()
            members.append(node)
            for neighbor in np.flatnonzero(adjacency[node]):
                if not seen[neighbor]:
                    seen[neighbor] = True
                    stack.append(int(neighbor))
        components.append(sorted(members))
    return sorted(components, key=lambda members: (-len(members), members[0]))
