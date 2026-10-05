from __future__ import annotations

import hashlib
import hmac
import json
from collections.abc import Mapping, MutableMapping
from dataclasses import asdict, dataclass, fields

from ...config import AttackStrategy, DefenseStrategy, SimulationConfig
from ...engine import SimulationEvent, SimulationFrame
from ..error_states import render_empty_state
from ..simulation_session import PlaybackState, PlaybackStatus

WORKSPACE_SCHEMA = "1.0"
MAX_BUNDLE_BYTES = 25 * 1024 * 1024


@dataclass(frozen=True, slots=True)
class WorkspaceSnapshot:
    config: SimulationConfig
    frames: tuple[SimulationFrame, ...]
    experiments: tuple[dict[str, object], ...]
    selected_node: int
    analysis_step: int
    checksum: str


def _config_to_dict(config: SimulationConfig) -> dict[str, object]:
    return {
        key: value.value if hasattr(value, "value") else value
        for key, value in asdict(config).items()
    }


def _canonical_bytes(payload: dict[str, object]) -> bytes:
    return json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def encode_workspace(session_state: Mapping[str, object]) -> bytes:
    config = session_state.get("config")
    frames = session_state.get("frames")
    if (
        not isinstance(config, SimulationConfig)
        or not isinstance(frames, (list, tuple))
        or not frames
    ):
        raise ValueError("Dışa aktarmak için aktif bir simülasyon gereklidir.")
    if not all(isinstance(frame, SimulationFrame) for frame in frames):
        raise ValueError("Oturumdaki simülasyon kareleri geçersizdir.")

    payload = {
        "config": _config_to_dict(config),
        "frames": [frame.to_dict() for frame in frames],
        "experiments": list(session_state.get("experiment_history", [])),
        "context": {
            "selected_node": int(session_state.get("selected_uav", 0)),
            "analysis_step": int(session_state.get("analysis_step", len(frames) - 1)),
        },
    }
    checksum = "sha256:" + hashlib.sha256(_canonical_bytes(payload)).hexdigest()
    envelope = {
        "schema_version": WORKSPACE_SCHEMA,
        "application": {"name": "swarmguard", "version": "1.1.0"},
        "checksum": checksum,
        "payload": payload,
    }
    return json.dumps(envelope, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8")


def _parse_config(raw: object) -> SimulationConfig:
    if not isinstance(raw, dict):
        raise ValueError("Çalışma alanı senaryosu geçersizdir.")  # noqa: TRY004
    allowed = {field.name for field in fields(SimulationConfig)}
    if set(raw) != allowed:
        raise ValueError("Çalışma alanı senaryosu beklenen alanlarla eşleşmiyor.")
    values = dict(raw)
    try:
        values["attack_strategy"] = AttackStrategy(values["attack_strategy"])
        values["defense_strategy"] = DefenseStrategy(values["defense_strategy"])
        return SimulationConfig(**values)
    except (TypeError, ValueError) as exc:
        raise ValueError("Çalışma alanı senaryo değerleri geçersizdir.") from exc


def _parse_frame(raw: object, node_count: int) -> SimulationFrame:
    if not isinstance(raw, dict):
        raise ValueError("Simülasyon karesi geçersizdir.")  # noqa: TRY004
    try:
        positions = tuple((float(x), float(y)) for x, y in raw["positions"])
        edges = tuple((int(source), int(target)) for source, target in raw["edges"])
        infected = tuple(int(node) for node in raw["infected"])
        events = tuple(
            SimulationEvent(
                event_type=str(event["event_type"]),
                node_id=int(event["node_id"]),
                target_node_id=(
                    int(event["target_node_id"])
                    if event.get("target_node_id") is not None
                    else None
                ),
                algorithm=(str(event["algorithm"]) if event.get("algorithm") else None),
                detail=(str(event["detail"]) if event.get("detail") else None),
            )
            for event in raw["events"]
        )
        frame = SimulationFrame(
            step=int(raw["step"]),
            positions=positions,
            edges=edges,
            infected=infected,
            metrics={str(key): value for key, value in raw["metrics"].items()},
            events=events,
            defense_report=raw.get("defense_report"),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("Simülasyon karesi çözümlenemedi.") from exc
    if len(frame.positions) != node_count:
        raise ValueError("Simülasyon karesinin İHA sayısı senaryoyla eşleşmiyor.")
    if any(node < 0 or node >= node_count for node in frame.infected):
        raise ValueError("Simülasyon karesinde geçersiz enfekte İHA kimliği var.")
    if any(
        source < 0 or target < 0 or source >= node_count or target >= node_count
        for source, target in frame.edges
    ):
        raise ValueError("Simülasyon karesinde geçersiz bağlantı var.")
    return frame


def decode_workspace(data: bytes) -> WorkspaceSnapshot:
    if len(data) > MAX_BUNDLE_BYTES:
        raise ValueError("Çalışma alanı dosyası 25 MB sınırını aşıyor.")
    try:
        envelope = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Dosya geçerli bir UTF-8 SwarmGuard paketi değil.") from exc
    if not isinstance(envelope, dict) or envelope.get("schema_version") != WORKSPACE_SCHEMA:
        raise ValueError("Çalışma alanı şema sürümü desteklenmiyor.")
    payload = envelope.get("payload")
    if not isinstance(payload, dict):
        raise ValueError("Çalışma alanı yükü bulunamadı.")  # noqa: TRY004
    expected = "sha256:" + hashlib.sha256(_canonical_bytes(payload)).hexdigest()
    supplied = str(envelope.get("checksum", ""))
    if not hmac.compare_digest(expected, supplied):
        raise ValueError("Çalışma alanı bütünlük kontrolü başarısız.")

    config = _parse_config(payload.get("config"))
    raw_frames = payload.get("frames")
    if not isinstance(raw_frames, list) or not raw_frames:
        raise ValueError("Çalışma alanında simülasyon karesi bulunamadı.")
    frames = tuple(_parse_frame(frame, config.node_count) for frame in raw_frames)
    if len(frames) != config.steps + 1 or tuple(frame.step for frame in frames) != tuple(
        range(config.steps + 1)
    ):
        raise ValueError("Simülasyon kare dizisi senaryo adımlarıyla eşleşmiyor.")

    experiments = payload.get("experiments", [])
    if not isinstance(experiments, list) or not all(
        isinstance(item, dict) and item.get("experiment_id") for item in experiments
    ):
        raise ValueError("Deney geçmişi geçersizdir.")
    context = payload.get("context", {})
    if not isinstance(context, dict):
        raise ValueError("Çalışma alanı bağlamı geçersizdir.")  # noqa: TRY004
    selected_node = min(max(int(context.get("selected_node", 0)), 0), config.node_count - 1)
    analysis_step = min(max(int(context.get("analysis_step", 0)), 0), len(frames) - 1)
    return WorkspaceSnapshot(
        config=config,
        frames=frames,
        experiments=tuple(experiments),
        selected_node=selected_node,
        analysis_step=analysis_step,
        checksum=supplied,
    )


def apply_workspace(
    session_state: MutableMapping[str, object], snapshot: WorkspaceSnapshot
) -> None:
    session_state["config"] = snapshot.config
    session_state["frames"] = list(snapshot.frames)
    session_state["experiment_history"] = list(snapshot.experiments)
    if snapshot.experiments:
        session_state["active_experiment_id"] = snapshot.experiments[0]["experiment_id"]
    else:
        session_state.pop("active_experiment_id", None)
    session_state["selected_uav"] = snapshot.selected_node
    session_state["node_picker"] = snapshot.selected_node
    session_state["analysis_step"] = snapshot.analysis_step
    session_state["replay_cursor"] = snapshot.analysis_step
    session_state["playback"] = PlaybackState(
        status=PlaybackStatus.PAUSED,
        index=snapshot.analysis_step,
    )


def render_workspace_center(st) -> None:
    st.markdown(
        """
        <section class="sg-workspace-hero">
            <div><span>OTURUM VE VERİ PAYLAŞIMI</span><h2>Çalışmanı kaydet, taşı ve kaldığın yerden devam et.</h2></div>
            <p>Senaryoyu, simülasyon geçmişini, deneyleri ve seçili analiz bağlamını tek bir doğrulanabilir çalışma alanı paketinde sakla.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    config = st.session_state.get("config")
    frames = st.session_state.get("frames") or []
    experiments = st.session_state.get("experiment_history", [])
    if isinstance(config, SimulationConfig) and frames:
        bundle = encode_workspace(st.session_state)
        snapshot = decode_workspace(bundle)
        summary_columns = st.columns(4)
        summary_columns[0].metric("İHA", config.node_count)
        summary_columns[1].metric("Simülasyon karesi", len(frames))
        summary_columns[2].metric("Kayıtlı deney", len(experiments))
        summary_columns[3].metric("Paket boyutu", f"{len(bundle) / 1024:.1f} KB")
        st.markdown(
            f"""
            <section class="sg-workspace-card">
                <div><small>AKTİF ÇALIŞMA ALANI</small><h3>Seed {config.seed} · {config.defense_strategy.value}</h3><p>{config.node_count} İHA · {config.steps} adım · {len(experiments)} deney</p></div>
                <code>{snapshot.checksum}</code>
            </section>
            """,
            unsafe_allow_html=True,
        )
        st.download_button(
            "Çalışma alanını indir",
            data=bundle,
            file_name=f"swarmguard-workspace-seed-{config.seed}.json",
            mime="application/json",
            type="primary",
            width="stretch",
        )
    else:
        render_empty_state(
            st,
            icon="◇",
            title="Kaydedilecek çalışma alanı yok",
            message="Simülasyon sayfasında bir senaryo çalıştırdıktan sonra buraya dön.",
            action_label="Simülasyona git",
            action_href="simulation",
        )

    st.markdown("#### Çalışma alanı yükle")
    st.caption(
        "Başka bir SwarmGuard oturumundan indirilen JSON paketini seç. Dosya uygulanmadan önce "
        "şema, boyut, senaryo ve SHA-256 bütünlük kontrollerinden geçirilir."
    )
    uploaded = st.file_uploader(
        "SwarmGuard çalışma alanı",
        type=["json"],
        accept_multiple_files=False,
        label_visibility="collapsed",
    )
    if uploaded is None:
        st.markdown(
            """
            <section class="sg-workspace-drop-hint"><div>⇧</div><h4>JSON paketini buraya bırak</h4><p>Azami dosya boyutu 25 MB · Şema 1.0 · SHA-256 doğrulamalı</p></section>
            """,
            unsafe_allow_html=True,
        )
        return

    try:
        incoming = decode_workspace(uploaded.getvalue())
    except ValueError as exc:
        st.error(str(exc))
        return

    preview_columns = st.columns(4)
    preview_columns[0].metric("İHA", incoming.config.node_count)
    preview_columns[1].metric("Kare", len(incoming.frames))
    preview_columns[2].metric("Deney", len(incoming.experiments))
    preview_columns[3].metric("Seed", incoming.config.seed)
    st.success("Paket doğrulandı. Bütünlük ve şema kontrolleri başarılı.")
    st.code(incoming.checksum, language=None)
    if st.button("Bu çalışma alanını yükle", type="primary", width="stretch"):
        apply_workspace(st.session_state, incoming)
        st.toast("Çalışma alanı geri yüklendi.", icon="✅")
        st.rerun()
