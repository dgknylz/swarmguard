from __future__ import annotations

from ...engine import SimulationFrame
from ..charts import topology_figure
from ..simulation_session import (
    PlaybackStatus,
    advance_playback,
    apply_playback_command,
    ensure_playback_state,
    seek_playback,
)
from .node_inspector import render_node_inspector

STATUS_LABELS = {
    PlaybackStatus.READY: "HAZIR",
    PlaybackStatus.RUNNING: "CANLI",
    PlaybackStatus.PAUSED: "DURAKLATILDI",
    PlaybackStatus.STOPPED: "DURDURULDU",
    PlaybackStatus.COMPLETED: "TAMAMLANDI",
}


def render_live_lab(st, frames: list[SimulationFrame]) -> None:
    playback = ensure_playback_state(st.session_state, len(frames))
    pending_navigation = st.session_state.pop("pending_event_navigation", None)
    if pending_navigation is not None:
        target_step = min(max(int(pending_navigation["step"]), 0), len(frames) - 1)
        target_node = min(max(int(pending_navigation["node_id"]), 0), len(frames[0].positions) - 1)
        seek_playback(playback, target_step, len(frames))
        playback.status = PlaybackStatus.PAUSED
        st.session_state["replay_cursor"] = target_step
        st.session_state["analysis_step"] = target_step
        st.session_state["selected_uav"] = target_node
        st.session_state["node_picker"] = target_node
    if "selected_uav" not in st.session_state:
        st.session_state["selected_uav"] = 0
    if "node_picker" not in st.session_state:
        st.session_state["node_picker"] = st.session_state["selected_uav"]

    def select_node_from_picker() -> None:
        st.session_state["selected_uav"] = int(st.session_state["node_picker"])

    title_col, node_col, mode_col = st.columns([3, 1.15, 1.15], vertical_alignment="center")
    title_col.markdown("#### Operasyon görünümü")
    title_col.caption(
        "Sürü topolojisini canlı akışta izle, duraklat veya herhangi bir simülasyon karesine dön."
    )
    node_col.selectbox(
        "İHA incele",
        options=range(len(frames[0].positions)),
        format_func=lambda node: f"UAV-{node:02d}",
        key="node_picker",
        on_change=select_node_from_picker,
    )
    presentation = mode_col.toggle("Sunum görünümü", value=False, key="lab-presentation")

    main_label = "⏸ Duraklat" if playback.status is PlaybackStatus.RUNNING else "▶ Başlat"
    main_command = "pause" if playback.status is PlaybackStatus.RUNNING else "play"
    main_col, previous_col, next_col, stop_col, restart_col, speed_col = st.columns(
        [1.35, 0.7, 0.7, 0.85, 0.85, 1.15], vertical_alignment="bottom"
    )
    if main_col.button(main_label, type="primary", width="stretch", key="lab-main"):
        apply_playback_command(playback, main_command, len(frames))
        st.session_state["replay_cursor"] = playback.index
    if previous_col.button("←", width="stretch", key="lab-previous", help="Bir kare geri"):
        apply_playback_command(playback, "previous", len(frames))
        st.session_state["replay_cursor"] = playback.index
    if next_col.button("→", width="stretch", key="lab-next", help="Bir kare ileri"):
        apply_playback_command(playback, "next", len(frames))
        st.session_state["replay_cursor"] = playback.index
    if stop_col.button("Durdur", width="stretch", key="lab-stop"):
        apply_playback_command(playback, "stop", len(frames))
        st.session_state["replay_cursor"] = playback.index
    if restart_col.button("Başa dön", width="stretch", key="lab-restart"):
        apply_playback_command(playback, "restart", len(frames))
        st.session_state["replay_cursor"] = playback.index
    playback.speed = speed_col.select_slider(
        "Akış hızı",
        options=[0.5, 1.0, 2.0, 4.0],
        value=playback.speed,
        format_func=lambda value: f"{value:g}×",
        key="lab-speed",
    )

    run_every = 1.0 / playback.speed if playback.status is PlaybackStatus.RUNNING else None

    @st.fragment(run_every=run_every, key="live-lab-stream")
    def render_stream() -> None:
        completed_now = advance_playback(playback, len(frames))
        frame = frames[playback.index]
        metrics = frame.metrics
        defense_algorithm = (
            str(frame.defense_report.get("algorithm", "none"))
            if frame.defense_report is not None
            else "initialization"
        )
        tone = "online" if playback.status is PlaybackStatus.RUNNING else "idle"
        st.markdown(
            f"""
            <section class="sg-live-status">
                <div><span class="sg-status-dot sg-status-{tone}"></span><b>{STATUS_LABELS[playback.status]}</b></div>
                <div><span>KARE</span><strong>{playback.index + 1} / {len(frames)}</strong></div>
                <div><span>ZAMAN</span><strong>t = {frame.step}</strong></div>
                <div><span>HIZ</span><strong>{playback.speed:g}×</strong></div>
                <div><span>SAVUNMA</span><strong>{defense_algorithm.upper()}</strong></div>
            </section>
            """,
            unsafe_allow_html=True,
        )

        if playback.status is PlaybackStatus.RUNNING:
            st.progress(
                playback.index / max(1, len(frames) - 1),
                text=f"Canlı akış · t = {frame.step}",
            )
        else:
            if "replay_cursor" not in st.session_state:
                st.session_state["replay_cursor"] = playback.index

            def update_cursor() -> None:
                seek_playback(playback, st.session_state["replay_cursor"], len(frames))

            st.slider(
                "Replay zaman çizgisi",
                min_value=0,
                max_value=len(frames) - 1,
                key="replay_cursor",
                on_change=update_cursor,
            )

        metric_columns = st.columns(4)
        metric_columns[0].metric(
            "Enfekte",
            f"{metrics['infected_count']} · %{float(metrics['infected_ratio']) * 100:.1f}",
        )
        metric_columns[1].metric(
            "En büyük bileşen", f"%{float(metrics['largest_component_ratio']) * 100:.1f}"
        )
        metric_columns[2].metric("Ağ verimliliği", f"{float(metrics['global_efficiency']):.3f}")
        metric_columns[3].metric("λ₂", f"{float(metrics['algebraic_connectivity']):.3f}")

        with st.container(border=True):
            chart_event = st.plotly_chart(
                topology_figure(frame),
                width="stretch",
                config={"displayModeBar": not presentation},
                key=f"live-topology-{playback.index}",
                on_select="rerun",
                selection_mode="points",
            )
        selected_node = int(st.session_state.get("selected_uav", 0))
        selected_points = chart_event.selection.points
        if selected_points:
            customdata = selected_points[0].get("customdata")
            if isinstance(customdata, (list, tuple)) and customdata:
                selected_node = int(customdata[0])
                st.session_state["selected_uav"] = selected_node
        if not presentation:
            with st.container(border=True):
                render_node_inspector(st, frames, playback.index, selected_node)
        if completed_now:
            st.rerun()

    render_stream()
