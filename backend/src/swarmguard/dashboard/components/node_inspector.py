from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import networkx as nx

from ...engine import SimulationFrame


@dataclass(frozen=True)
class NodeEvent:
    step: int
    event_type: str
    role: str
    algorithm: str
    detail: str


@dataclass(frozen=True)
class NodeSnapshot:
    node_id: int
    infected: bool
    quarantined: bool
    x: float
    y: float
    degree: int
    infected_neighbor_count: int
    infected_neighbor_ratio: float
    betweenness: float
    risk: float | None
    neighbors: tuple[int, ...]
    events: tuple[NodeEvent, ...]


@lru_cache(maxsize=512)
def _network_stats(
    node_count: int,
    edges: tuple[tuple[int, int], ...],
    infected: tuple[int, ...],
    node_id: int,
) -> tuple[int, int, float, float, tuple[int, ...]]:
    graph = nx.Graph()
    graph.add_nodes_from(range(node_count))
    graph.add_edges_from(edges)
    neighbors = tuple(sorted(graph.neighbors(node_id)))
    infected_set = set(infected)
    infected_neighbors = sum(neighbor in infected_set for neighbor in neighbors)
    infected_ratio = infected_neighbors / len(neighbors) if neighbors else 0.0
    if graph.number_of_edges() == 0:
        betweenness = 0.0
    elif node_count <= 100:
        betweenness = float(nx.betweenness_centrality(graph, normalized=True)[node_id])
    else:
        betweenness = float(
            nx.betweenness_centrality(
                graph,
                k=min(40, node_count),
                normalized=True,
                seed=2025,
            )[node_id]
        )
    return len(neighbors), infected_neighbors, infected_ratio, betweenness, neighbors


def build_node_snapshot(
    frames: list[SimulationFrame], frame_index: int, node_id: int
) -> NodeSnapshot:
    frame_index = max(0, min(frame_index, len(frames) - 1))
    frame = frames[frame_index]
    if not 0 <= node_id < len(frame.positions):
        raise ValueError(f"Geçersiz İHA kimliği: {node_id}")

    degree, infected_neighbors, infected_ratio, betweenness, neighbors = _network_stats(
        len(frame.positions), frame.edges, frame.infected, node_id
    )
    report = frame.defense_report or {}
    metadata = report.get("metadata", {})
    risk_scores = metadata.get("risk_scores", {}) if isinstance(metadata, dict) else {}
    risk_value = risk_scores.get(str(node_id)) if isinstance(risk_scores, dict) else None
    risk = float(risk_value) if risk_value is not None else None

    events: list[NodeEvent] = []
    quarantined = False
    for historical_frame in frames[: frame_index + 1]:
        for event in historical_frame.events:
            if event.node_id != node_id and event.target_node_id != node_id:
                continue
            role = "kaynak" if event.node_id == node_id else "hedef"
            if event.event_type == "quarantine_node" and event.node_id == node_id:
                quarantined = True
            events.append(
                NodeEvent(
                    step=historical_frame.step,
                    event_type=event.event_type,
                    role=role,
                    algorithm=event.algorithm or "—",
                    detail=event.detail or "—",
                )
            )

    x, y = frame.positions[node_id]
    return NodeSnapshot(
        node_id=node_id,
        infected=node_id in frame.infected,
        quarantined=quarantined,
        x=float(x),
        y=float(y),
        degree=degree,
        infected_neighbor_count=infected_neighbors,
        infected_neighbor_ratio=infected_ratio,
        betweenness=betweenness,
        risk=risk,
        neighbors=neighbors,
        events=tuple(events),
    )


def render_node_inspector(
    st,
    frames: list[SimulationFrame],
    frame_index: int,
    node_id: int,
) -> None:
    snapshot = build_node_snapshot(frames, frame_index, node_id)
    health_label = "ENFEKTE" if snapshot.infected else "SAĞLIKLI"
    health_tone = "infected" if snapshot.infected else "healthy"
    quarantine_label = "KARANTİNADA" if snapshot.quarantined else "AKTİF"
    risk_label = f"{snapshot.risk:.3f}" if snapshot.risk is not None else "Hesaplanmadı"
    st.markdown(
        f"""
        <section class="sg-inspector-head">
            <div class="sg-inspector-identity"><div>U{snapshot.node_id:02d}</div><span><b>UAV-{snapshot.node_id:02d}</b><small>DÜĞÜM İNCELEME PANELİ</small></span></div>
            <div class="sg-inspector-badges"><span class="sg-node-{health_tone}">{health_label}</span><span>{quarantine_label}</span></div>
        </section>
        <section class="sg-inspector-grid">
            <div><span>KONUM</span><strong>{snapshot.x:.1f}, {snapshot.y:.1f}</strong><small>metre</small></div>
            <div><span>DERECE</span><strong>{snapshot.degree}</strong><small>komşu bağlantı</small></div>
            <div><span>ENFEKTE KOMŞU</span><strong>{snapshot.infected_neighbor_count}</strong><small>%{snapshot.infected_neighbor_ratio * 100:.1f} maruziyet</small></div>
            <div><span>BETWEENNESS</span><strong>{snapshot.betweenness:.4f}</strong><small>merkeziyet</small></div>
            <div><span>GTAD RİSKİ</span><strong>{risk_label}</strong><small>normalize skor</small></div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    risk_col, exposure_col = st.columns(2)
    with risk_col:
        st.caption("GTAD risk skoru")
        st.progress(snapshot.risk or 0.0, text=risk_label)
    with exposure_col:
        st.caption("Enfekte komşu maruziyeti")
        st.progress(
            snapshot.infected_neighbor_ratio, text=f"%{snapshot.infected_neighbor_ratio * 100:.1f}"
        )

    neighbor_html = "".join(f"<span>UAV-{neighbor:02d}</span>" for neighbor in snapshot.neighbors)
    st.markdown(
        f"""
        <div class="sg-neighbor-list"><b>KOMŞULAR · {len(snapshot.neighbors)}</b><div>{neighbor_html or "<em>Bağlı komşu yok</em>"}</div></div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("##### Düğüm olay geçmişi")
    if snapshot.events:
        st.dataframe(
            [
                {
                    "t": event.step,
                    "olay": event.event_type,
                    "rol": event.role,
                    "algoritma": event.algorithm,
                    "detay": event.detail,
                }
                for event in reversed(snapshot.events[-12:])
            ],
            width="stretch",
            hide_index=True,
        )
    else:
        st.caption("Seçili zaman aralığında bu İHA için kayıtlı olay yok.")
