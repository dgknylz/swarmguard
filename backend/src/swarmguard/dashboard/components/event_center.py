from __future__ import annotations

import csv
import io
import json
from collections import Counter
from dataclasses import asdict, dataclass

from ...engine import SimulationFrame

EVENT_LABELS = {
    "initial_infection": "İlk bulaşma",
    "infected": "Yeni bulaşma",
    "recovered": "İyileşme",
    "add_edge": "Bağlantı eklendi",
    "remove_edge": "Bağlantı kesildi",
    "quarantine_node": "Karantina",
}

EVENT_CATEGORIES = {
    "initial_infection": "Saldırı",
    "infected": "Saldırı",
    "recovered": "Sağlık",
    "add_edge": "Savunma",
    "remove_edge": "Savunma",
    "quarantine_node": "Savunma",
}

SEVERITIES = {
    "initial_infection": "Kritik",
    "infected": "Kritik",
    "quarantine_node": "Yüksek",
    "remove_edge": "Orta",
    "add_edge": "Bilgi",
    "recovered": "Bilgi",
}


@dataclass(frozen=True, slots=True)
class EventRecord:
    event_id: str
    step: int
    event_type: str
    label: str
    category: str
    severity: str
    node_id: int
    target_node_id: int | None
    algorithm: str
    detail: str


@dataclass(frozen=True, slots=True)
class EventSummary:
    total: int
    attacks: int
    defenses: int
    recoveries: int
    affected_nodes: int


def collect_events(frames: list[SimulationFrame]) -> tuple[EventRecord, ...]:
    records: list[EventRecord] = []
    for frame in frames:
        for index, event in enumerate(frame.events):
            records.append(
                EventRecord(
                    event_id=f"t{frame.step:04d}-{index:03d}",
                    step=frame.step,
                    event_type=event.event_type,
                    label=EVENT_LABELS.get(
                        event.event_type, event.event_type.replace("_", " ").title()
                    ),
                    category=EVENT_CATEGORIES.get(event.event_type, "Sistem"),
                    severity=SEVERITIES.get(event.event_type, "Bilgi"),
                    node_id=event.node_id,
                    target_node_id=event.target_node_id,
                    algorithm=event.algorithm or "—",
                    detail=event.detail or "—",
                )
            )
    return tuple(records)


def summarize_events(events: tuple[EventRecord, ...]) -> EventSummary:
    affected = {
        node
        for event in events
        for node in (event.node_id, event.target_node_id)
        if node is not None
    }
    return EventSummary(
        total=len(events),
        attacks=sum(event.category == "Saldırı" for event in events),
        defenses=sum(event.category == "Savunma" for event in events),
        recoveries=sum(event.event_type == "recovered" for event in events),
        affected_nodes=len(affected),
    )


def filter_events(
    events: tuple[EventRecord, ...],
    *,
    categories: tuple[str, ...] = (),
    event_types: tuple[str, ...] = (),
    node_id: int | None = None,
    step_range: tuple[int, int] | None = None,
) -> tuple[EventRecord, ...]:
    filtered = events
    if categories:
        filtered = tuple(event for event in filtered if event.category in categories)
    if event_types:
        filtered = tuple(event for event in filtered if event.event_type in event_types)
    if node_id is not None:
        filtered = tuple(
            event
            for event in filtered
            if event.node_id == node_id or event.target_node_id == node_id
        )
    if step_range is not None:
        start, end = step_range
        filtered = tuple(event for event in filtered if start <= event.step <= end)
    return filtered


def export_events_json(events: tuple[EventRecord, ...]) -> bytes:
    return json.dumps([asdict(event) for event in events], ensure_ascii=False, indent=2).encode(
        "utf-8"
    )


def export_events_csv(events: tuple[EventRecord, ...]) -> bytes:
    output = io.StringIO()
    fieldnames = list(EventRecord.__dataclass_fields__)
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(asdict(event) for event in events)
    return output.getvalue().encode("utf-8-sig")


def render_event_center(st, frames: list[SimulationFrame]) -> None:
    import pandas as pd

    events = collect_events(frames)
    summary = summarize_events(events)
    st.markdown(
        """
        <section class="sg-event-hero">
            <div><span>OLAY VE SALDIRI MERKEZİ</span><h3>Operasyon geçmişinin tamamı</h3></div>
            <p>Bulaşma, iyileşme ve savunma müdahalelerini tek zaman çizelgesinde araştır.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    metric_columns = st.columns(5)
    metric_columns[0].metric("Toplam olay", summary.total)
    metric_columns[1].metric("Saldırı", summary.attacks)
    metric_columns[2].metric("Savunma", summary.defenses)
    metric_columns[3].metric("İyileşme", summary.recoveries)
    metric_columns[4].metric("Etkilenen İHA", summary.affected_nodes)

    if not events:
        st.info("Bu simülasyonda henüz kayıtlı olay bulunmuyor.")
        return

    max_step = max(frame.step for frame in frames)
    filter_columns = st.columns([1.35, 1.5, 1, 1.35])
    categories = filter_columns[0].multiselect(
        "Kategori",
        options=sorted({event.category for event in events}),
        placeholder="Tümü",
        key="event-categories",
    )
    event_types = filter_columns[1].multiselect(
        "Olay türü",
        options=sorted({event.event_type for event in events}),
        format_func=lambda value: EVENT_LABELS.get(value, value),
        placeholder="Tümü",
        key="event-types",
    )
    node_choice = filter_columns[2].selectbox(
        "İHA",
        options=[None, *range(len(frames[0].positions))],
        format_func=lambda value: "Tümü" if value is None else f"UAV-{value:02d}",
        key="event-node",
    )
    step_range = filter_columns[3].slider(
        "Zaman aralığı",
        min_value=0,
        max_value=max_step,
        value=(0, max_step),
        key="event-step-range",
    )
    filtered = filter_events(
        events,
        categories=tuple(categories),
        event_types=tuple(event_types),
        node_id=node_choice,
        step_range=step_range,
    )

    chart_column, detail_column = st.columns([1.65, 1], vertical_alignment="top")
    with chart_column:
        st.markdown("##### Zaman çizelgesi")
        counts = Counter((event.step, event.category) for event in filtered)
        timeline = pd.DataFrame(
            [
                {"adım": step, "kategori": category, "olay": count}
                for (step, category), count in sorted(counts.items())
            ]
        )
        if timeline.empty:
            st.info("Seçili filtrelerle eşleşen olay yok.")
        else:
            st.bar_chart(timeline, x="adım", y="olay", color="kategori", height=260)

    with detail_column:
        st.markdown("##### Olay ayrıntısı")
        if filtered:
            selected_id = st.selectbox(
                "Kayıt",
                options=[event.event_id for event in reversed(filtered)],
                format_func=lambda event_id: next(
                    f"t={event.step} · {event.label} · UAV-{event.node_id:02d}"
                    for event in filtered
                    if event.event_id == event_id
                ),
                label_visibility="collapsed",
                key="event-detail",
            )
            selected = next(event for event in filtered if event.event_id == selected_id)
            target = (
                "—" if selected.target_node_id is None else f"UAV-{selected.target_node_id:02d}"
            )
            st.markdown(
                f"""
                <article class="sg-event-detail">
                    <span>{selected.category.upper()} · {selected.severity.upper()}</span>
                    <h4>{selected.label}</h4>
                    <div><b>Kaynak</b><strong>UAV-{selected.node_id:02d}</strong></div>
                    <div><b>Hedef</b><strong>{target}</strong></div>
                    <div><b>Zaman</b><strong>t = {selected.step}</strong></div>
                    <div><b>Algoritma</b><strong>{selected.algorithm}</strong></div>
                    <p>{selected.detail}</p>
                </article>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Canlı ağda aç", width="stretch", key="event-open-frame"):
                st.session_state["pending_event_navigation"] = {
                    "step": selected.step,
                    "node_id": selected.node_id,
                }
                st.rerun()

    st.markdown(f"##### Olay kayıtları · {len(filtered)} sonuç")
    rows = [
        {
            "zaman": event.step,
            "kategori": event.category,
            "önem": event.severity,
            "olay": event.label,
            "kaynak": f"UAV-{event.node_id:02d}",
            "hedef": "—" if event.target_node_id is None else f"UAV-{event.target_node_id:02d}",
            "algoritma": event.algorithm,
            "detay": event.detail,
        }
        for event in reversed(filtered)
    ]
    st.dataframe(rows, width="stretch", hide_index=True, height=360)

    csv_column, json_column, note_column = st.columns([1, 1, 3], vertical_alignment="center")
    csv_column.download_button(
        "CSV indir",
        data=export_events_csv(filtered),
        file_name="swarmguard-events.csv",
        mime="text/csv",
        width="stretch",
    )
    json_column.download_button(
        "JSON indir",
        data=export_events_json(filtered),
        file_name="swarmguard-events.json",
        mime="application/json",
        width="stretch",
    )
    note_column.caption("Dışa aktarılan dosya ekrandaki aktif filtreleri korur.")
