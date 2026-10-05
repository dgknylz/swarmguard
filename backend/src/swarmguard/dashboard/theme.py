from .design_system import design_token_css

THEME_CSS = """
<style>
    :root {
        --sg-bg: #061014;
        --sg-panel: rgba(12, 29, 35, 0.78);
        --sg-border: rgba(148, 197, 202, 0.12);
        --sg-cyan: #57e7d6;
        --sg-muted: #789097;
    }

    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(circle at 82% 6%, rgba(29, 111, 112, 0.12), transparent 32rem),
            linear-gradient(180deg, #071216 0%, var(--sg-bg) 100%);
    }

    [data-testid="stHeader"], [data-testid="stToolbar"] {
        background: transparent;
    }

    [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none; }
    [data-testid="stTopNav"] { border-bottom: 1px solid var(--sg-border); }
    [data-testid="stTopNav"] a { font-size: 0.78rem; font-weight: 700; letter-spacing: 0.025em; }

    .block-container {
        max-width: 1500px;
        padding-top: 1.2rem;
        padding-bottom: 1rem;
    }

    .sg-site-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1.5rem;
        margin-bottom: 1.6rem;
        padding: 0.9rem 1.05rem;
        border: 1px solid var(--sg-border);
        border-radius: 1rem;
        background: rgba(9, 25, 30, 0.78);
        box-shadow: 0 18px 50px rgba(0, 0, 0, 0.16);
        backdrop-filter: blur(18px);
    }

    .sg-brand {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        min-width: 0;
    }
    .sg-brand-mark {
        display: grid;
        place-items: center;
        width: 2.3rem;
        height: 2.3rem;
        border: 1px solid rgba(87, 231, 214, 0.35);
        border-radius: 0.7rem;
        color: var(--sg-cyan);
        background: rgba(87, 231, 214, 0.08);
        box-shadow: 0 0 24px rgba(87, 231, 214, 0.08);
    }
    .sg-brand-name { color: #e9f8f6; font-size: 0.86rem; font-weight: 800; letter-spacing: 0.16em; }
    .sg-brand-subtitle { color: #557078; font-size: 0.54rem; font-weight: 700; letter-spacing: 0.12em; }
    .sg-site-meta { display: flex; align-items: center; gap: 0.85rem; color: #526b72; font: 700 0.57rem monospace; letter-spacing: 0.07em; }
    .sg-scenario-chip { display: flex; align-items: center; gap: 0.42rem; padding: 0.42rem 0.6rem; border: 1px solid var(--sg-border); border-radius: 999px; color: #7f999e; }

    .sg-context-card {
        margin: 1rem 0 0.5rem;
        padding: 0.9rem;
        border: 1px solid var(--sg-border);
        border-radius: 0.8rem;
        background: rgba(255, 255, 255, 0.018);
    }
    .sg-section-label, .sg-eyebrow {
        color: #527078;
        font-size: 0.58rem;
        font-weight: 800;
        letter-spacing: 0.14em;
    }
    .sg-status-row { display: flex; align-items: center; gap: 0.45rem; margin-top: 0.65rem; color: #b9cfce; font-size: 0.74rem; }
    .sg-status-dot { display: inline-block; width: 0.43rem; height: 0.43rem; border-radius: 999px; }
    .sg-status-online { background: var(--sg-cyan); box-shadow: 0 0 10px rgba(87, 231, 214, 0.75); }
    .sg-status-idle { background: #64767d; }
    .sg-context-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.65rem; margin-top: 0.85rem; }
    .sg-context-grid div { display: flex; flex-direction: column; gap: 0.18rem; min-width: 0; }
    .sg-context-grid span { color: #4f6970; font-size: 0.52rem; font-weight: 700; letter-spacing: 0.1em; }
    .sg-context-grid strong { overflow: hidden; color: #cadbd9; font: 600 0.67rem monospace; text-overflow: ellipsis; white-space: nowrap; }

    .sg-topbar {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 1.5rem;
        margin-bottom: 1.35rem;
        padding-bottom: 1.3rem;
        border-bottom: 1px solid var(--sg-border);
    }
    .sg-topbar h1 { margin: 0.32rem 0 0.25rem; color: #ecf8f6; font-size: clamp(1.65rem, 3vw, 2.35rem); letter-spacing: -0.035em; }
    .sg-topbar p { max-width: 50rem; margin: 0; color: var(--sg-muted); font-size: 0.85rem; line-height: 1.55; }
    .sg-system-pill {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        flex: 0 0 auto;
        padding: 0.48rem 0.7rem;
        border: 1px solid var(--sg-border);
        border-radius: 999px;
        color: #718b91;
        background: rgba(255, 255, 255, 0.018);
        font-size: 0.58rem;
        font-weight: 800;
        letter-spacing: 0.1em;
    }

    .sg-footer {
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        margin-top: 2.5rem;
        padding: 1rem 0 0.25rem;
        border-top: 1px solid var(--sg-border);
        color: #41575e;
        font: 600 0.56rem monospace;
        letter-spacing: 0.08em;
    }

    [data-baseweb="tab-list"] {
        gap: 0.4rem;
        padding: 0.35rem;
        border: 1px solid var(--sg-border);
        border-radius: 0.85rem;
        background: rgba(255, 255, 255, 0.018);
    }
    [data-baseweb="tab"] {
        min-height: 2.6rem;
        border-radius: 0.6rem;
        color: #718b91;
        font-size: 0.78rem;
        font-weight: 700;
    }
    [aria-selected="true"][data-baseweb="tab"] {
        color: var(--sg-cyan);
        background: rgba(87, 231, 214, 0.08);
    }
    [data-testid="stMetric"] {
        padding: 1rem;
        border: 1px solid var(--sg-border);
        border-radius: 0.85rem;
        background: rgba(255, 255, 255, 0.018);
    }

    .sg-hero {
        display: grid;
        grid-template-columns: minmax(0, 1.2fr) minmax(320px, 0.8fr);
        gap: clamp(2rem, 5vw, 5rem);
        align-items: center;
        min-height: 32rem;
        margin-bottom: 1rem;
        padding: clamp(2rem, 4vw, 4rem);
        overflow: hidden;
        border: 1px solid var(--sg-border);
        border-radius: 1.35rem;
        background:
            linear-gradient(120deg, rgba(10, 31, 37, 0.96), rgba(6, 18, 22, 0.88)),
            radial-gradient(circle at 85% 20%, rgba(87, 231, 214, 0.12), transparent 24rem);
        box-shadow: 0 30px 90px rgba(0, 0, 0, 0.24);
    }
    .sg-hero-kicker { display: flex; align-items: center; gap: 0.55rem; color: #6f8b91; font-size: 0.61rem; font-weight: 800; letter-spacing: 0.15em; }
    .sg-hero-kicker span { width: 1.8rem; height: 1px; background: var(--sg-cyan); box-shadow: 0 0 10px rgba(87, 231, 214, 0.65); }
    .sg-hero h2 { max-width: 52rem; margin: 1.15rem 0; color: #f0faf8; font-size: clamp(2.25rem, 5.1vw, 4.6rem); line-height: 1.02; letter-spacing: -0.055em; }
    .sg-hero h2 em { color: var(--sg-cyan); font-style: normal; }
    .sg-hero-copy > p { max-width: 45rem; margin: 0; color: #7f989e; font-size: 0.93rem; line-height: 1.75; }
    .sg-hero-actions { display: flex; flex-wrap: wrap; gap: 0.7rem; margin-top: 1.65rem; }
    .sg-button { display: inline-flex; align-items: center; justify-content: center; gap: 0.6rem; min-height: 2.75rem; padding: 0.65rem 1rem; border-radius: 0.7rem; font-size: 0.75rem; font-weight: 800; letter-spacing: 0.02em; text-decoration: none !important; transition: 160ms ease; }
    .sg-button:hover { transform: translateY(-2px); }
    .sg-button-primary { color: #05201e !important; background: var(--sg-cyan); box-shadow: 0 10px 30px rgba(87, 231, 214, 0.16); }
    .sg-button-secondary { border: 1px solid var(--sg-border); color: #b2c6c5 !important; background: rgba(255, 255, 255, 0.025); }
    .sg-hero-proof { display: flex; flex-wrap: wrap; gap: 1.5rem; margin-top: 2.3rem; padding-top: 1.3rem; border-top: 1px solid var(--sg-border); }
    .sg-hero-proof div { display: flex; flex-direction: column; gap: 0.18rem; }
    .sg-hero-proof strong { color: #d9e9e7; font: 700 1rem monospace; }
    .sg-hero-proof span { color: #526b71; font-size: 0.57rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; }

    .sg-hero-visual { position: relative; min-height: 25rem; isolation: isolate; }
    .sg-hero-visual::before { position: absolute; inset: 8%; content: ""; border-radius: 50%; background: radial-gradient(circle, rgba(87, 231, 214, 0.1), transparent 62%); filter: blur(10px); }
    .sg-radar-ring { position: absolute; top: 50%; left: 50%; border: 1px solid rgba(87, 231, 214, 0.14); border-radius: 50%; transform: translate(-50%, -50%); }
    .sg-ring-one { width: 9rem; height: 9rem; }
    .sg-ring-two { width: 16rem; height: 16rem; }
    .sg-ring-three { width: 23rem; height: 23rem; border-style: dashed; }
    .sg-radar-core { position: absolute; top: 50%; left: 50%; display: grid; place-items: center; width: 4rem; height: 4rem; border: 1px solid rgba(87, 231, 214, 0.45); border-radius: 1.1rem; color: var(--sg-cyan); background: #0b2529; box-shadow: 0 0 45px rgba(87, 231, 214, 0.2); transform: translate(-50%, -50%) rotate(45deg); font-size: 1.4rem; }
    .sg-radar-core::first-letter { transform: rotate(-45deg); }
    .sg-network-node { position: absolute; width: 0.72rem; height: 0.72rem; border: 2px solid #092329; border-radius: 50%; background: var(--sg-cyan); box-shadow: 0 0 14px rgba(87, 231, 214, 0.7); z-index: 2; }
    .sg-node-one { top: 18%; left: 28%; } .sg-node-two { top: 31%; right: 12%; } .sg-node-three { bottom: 18%; right: 25%; } .sg-node-four { bottom: 25%; left: 11%; background: #fb7185; box-shadow: 0 0 14px rgba(251, 113, 133, 0.65); } .sg-node-five { top: 46%; left: 8%; }
    .sg-network-line { position: absolute; top: 50%; left: 50%; width: 9rem; height: 1px; transform-origin: left center; background: linear-gradient(90deg, rgba(87, 231, 214, 0.5), transparent); }
    .sg-line-one { transform: rotate(-42deg); } .sg-line-two { transform: rotate(23deg); width: 10rem; } .sg-line-three { transform: rotate(148deg); width: 9.5rem; }
    .sg-visual-status { position: absolute; right: 0; bottom: 0.5rem; display: flex; align-items: center; gap: 0.45rem; padding: 0.55rem 0.75rem; border: 1px solid var(--sg-border); border-radius: 999px; color: #799297; background: rgba(7, 20, 24, 0.86); font: 700 0.57rem monospace; letter-spacing: 0.08em; }

    .sg-kpi-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 0.7rem; margin: 0.8rem 0 4.5rem; }
    .sg-kpi-grid article { display: grid; gap: 0.25rem; padding: 1rem 1.1rem; border: 1px solid var(--sg-border); border-radius: 0.85rem; background: rgba(255, 255, 255, 0.018); }
    .sg-kpi-grid span, .sg-run-banner > div > span { color: #4e6970; font-size: 0.55rem; font-weight: 800; letter-spacing: 0.12em; }
    .sg-kpi-grid strong { overflow: hidden; color: #d7e8e6; font: 700 1.1rem monospace; text-overflow: ellipsis; white-space: nowrap; }
    .sg-kpi-grid small { color: #607980; font-size: 0.63rem; }

    .sg-section-heading { display: flex; align-items: flex-end; justify-content: space-between; gap: 2rem; margin-bottom: 1.3rem; }
    .sg-section-heading span { color: var(--sg-cyan); font-size: 0.58rem; font-weight: 800; letter-spacing: 0.14em; }
    .sg-section-heading h3, .sg-run-banner h3 { margin: 0.35rem 0 0; color: #e5f2f0; font-size: clamp(1.45rem, 3vw, 2.15rem); letter-spacing: -0.035em; }
    .sg-section-heading p { max-width: 34rem; margin: 0; color: #637e84; font-size: 0.77rem; line-height: 1.6; }
    .sg-section-spaced { margin-top: 4.5rem; }
    .sg-process-grid, .sg-module-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0.8rem; }
    .sg-process-grid article, .sg-module-grid a { position: relative; min-height: 13.5rem; padding: 1.35rem; border: 1px solid var(--sg-border); border-radius: 1rem; background: linear-gradient(145deg, rgba(255, 255, 255, 0.025), rgba(255, 255, 255, 0.008)); }
    .sg-process-grid article > b, .sg-module-index { position: absolute; top: 1rem; right: 1rem; color: #345058; font: 700 0.65rem monospace; }
    .sg-process-icon, .sg-module-icon { display: grid; place-items: center; width: 2.6rem; height: 2.6rem; margin-bottom: 2rem; border: 1px solid rgba(87, 231, 214, 0.2); border-radius: 0.75rem; color: var(--sg-cyan); background: rgba(87, 231, 214, 0.055); }
    .sg-process-grid h4, .sg-module-grid h4 { margin: 0 0 0.55rem; color: #dceae8; font-size: 0.93rem; }
    .sg-process-grid p, .sg-module-grid p { margin: 0; color: #617a80; font-size: 0.72rem; line-height: 1.65; }
    .sg-module-grid a { color: inherit !important; text-decoration: none !important; transition: 180ms ease; }
    .sg-module-grid a:hover { border-color: rgba(87, 231, 214, 0.27); background: rgba(87, 231, 214, 0.035); transform: translateY(-3px); }
    .sg-module-grid b { position: absolute; right: 1.35rem; bottom: 1.1rem; color: #5d817f; font-size: 0.66rem; }

    .sg-run-banner { display: grid; grid-template-columns: minmax(0, 1.3fr) auto auto; gap: 2rem; align-items: center; margin-top: 4.5rem; padding: 1.6rem; border: 1px solid rgba(87, 231, 214, 0.17); border-radius: 1rem; background: linear-gradient(110deg, rgba(87, 231, 214, 0.06), rgba(255, 255, 255, 0.012)); }
    .sg-run-banner h3 { font-size: 1.25rem; }
    .sg-run-banner p { margin: 0.35rem 0 0; color: #657e84; font-size: 0.7rem; }
    .sg-run-stats { display: flex; gap: 1.5rem; }
    .sg-run-stats div { display: flex; flex-direction: column; gap: 0.2rem; }
    .sg-run-stats span { color: #466168; font-size: 0.52rem; font-weight: 800; letter-spacing: 0.1em; }
    .sg-run-stats strong { color: #cfe0de; font: 700 0.85rem monospace; }

    .sg-scenario-summary {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.7rem;
        margin: 1rem 0;
        padding: 0.9rem;
        border: 1px solid rgba(87, 231, 214, 0.15);
        border-radius: 0.9rem;
        background: rgba(87, 231, 214, 0.025);
    }
    .sg-scenario-summary div { display: flex; flex-direction: column; gap: 0.3rem; min-width: 0; padding: 0.55rem; }
    .sg-scenario-summary span { color: #4f6d73; font-size: 0.53rem; font-weight: 800; letter-spacing: 0.11em; }
    .sg-scenario-summary strong { overflow: hidden; color: #d3e5e2; font: 700 0.8rem monospace; text-overflow: ellipsis; white-space: nowrap; }
    [data-testid="stForm"] { padding: 1.1rem !important; border-color: var(--sg-border) !important; background: rgba(255, 255, 255, 0.012); }
    [data-testid="stForm"] h4 { margin-top: 1.1rem; color: #d8e7e5; }
    [data-testid="stPills"] button { border-color: var(--sg-border); color: #6f888e; background: rgba(255, 255, 255, 0.018); }
    [data-testid="stPills"] button[aria-pressed="true"] { border-color: rgba(87, 231, 214, 0.28); color: var(--sg-cyan); background: rgba(87, 231, 214, 0.08); }
    .sg-preset-detail {
        display: grid;
        grid-template-columns: auto minmax(0, 1fr) auto;
        gap: 1rem;
        align-items: center;
        margin: 0.6rem 0 1rem;
        padding: 1rem;
        border: 1px solid var(--sg-border);
        border-radius: 0.9rem;
        background: linear-gradient(110deg, rgba(87, 231, 214, 0.04), rgba(255, 255, 255, 0.012));
    }
    .sg-preset-symbol { display: grid; place-items: center; width: 3rem; height: 3rem; border: 1px solid rgba(87, 231, 214, 0.25); border-radius: 0.8rem; color: var(--sg-cyan); background: rgba(87, 231, 214, 0.07); font-size: 1.15rem; }
    .sg-preset-detail span { color: #4f7076; font-size: 0.53rem; font-weight: 800; letter-spacing: 0.11em; }
    .sg-preset-detail h4 { margin: 0.23rem 0; color: #dbeae8; font-size: 0.92rem; }
    .sg-preset-detail p { max-width: 42rem; margin: 0; color: #688187; font-size: 0.68rem; line-height: 1.5; }
    .sg-preset-facts { display: grid; grid-template-columns: repeat(4, auto); gap: 1rem; }
    .sg-preset-facts div { display: flex; flex-direction: column; gap: 0.15rem; }
    .sg-preset-facts b { overflow: hidden; max-width: 8rem; color: #c9ddda; font: 700 0.72rem monospace; text-overflow: ellipsis; }
    .sg-preset-facts small { color: #456168; font-size: 0.48rem; font-weight: 800; letter-spacing: 0.08em; }
    .sg-live-status {
        display: grid;
        grid-template-columns: 1.2fr repeat(4, minmax(0, 1fr));
        gap: 0.7rem;
        margin: 0.8rem 0;
        padding: 0.75rem;
        border: 1px solid var(--sg-border);
        border-radius: 0.85rem;
        background: rgba(255, 255, 255, 0.016);
    }
    .sg-live-status > div { display: flex; align-items: center; gap: 0.45rem; min-width: 0; padding: 0.3rem 0.45rem; }
    .sg-live-status > div:not(:first-child) { flex-direction: column; align-items: flex-start; gap: 0.12rem; border-left: 1px solid var(--sg-border); padding-left: 0.8rem; }
    .sg-live-status b { color: #94aaa8; font: 800 0.62rem monospace; letter-spacing: 0.09em; }
    .sg-live-status span { color: #425e65; font-size: 0.49rem; font-weight: 800; letter-spacing: 0.1em; }
    .sg-live-status strong { overflow: hidden; max-width: 100%; color: #c8dcda; font: 700 0.67rem monospace; text-overflow: ellipsis; white-space: nowrap; }
    .sg-inspector-head { display: flex; align-items: center; justify-content: space-between; gap: 1rem; margin-bottom: 1rem; padding-bottom: 0.9rem; border-bottom: 1px solid var(--sg-border); }
    .sg-inspector-identity { display: flex; align-items: center; gap: 0.75rem; }
    .sg-inspector-identity > div { display: grid; place-items: center; width: 2.8rem; height: 2.8rem; border: 1px solid rgba(87, 231, 214, 0.23); border-radius: 50%; color: var(--sg-cyan); background: rgba(87, 231, 214, 0.06); font: 800 0.68rem monospace; }
    .sg-inspector-identity span { display: flex; flex-direction: column; gap: 0.18rem; }
    .sg-inspector-identity b { color: #dceae8; font-size: 0.86rem; }
    .sg-inspector-identity small { color: #456168; font-size: 0.5rem; font-weight: 800; letter-spacing: 0.1em; }
    .sg-inspector-badges { display: flex; gap: 0.4rem; }
    .sg-inspector-badges span { padding: 0.32rem 0.48rem; border: 1px solid var(--sg-border); border-radius: 999px; color: #637e84; font-size: 0.5rem; font-weight: 800; letter-spacing: 0.08em; }
    .sg-inspector-badges .sg-node-healthy { border-color: rgba(87, 231, 214, 0.2); color: var(--sg-cyan); background: rgba(87, 231, 214, 0.05); }
    .sg-inspector-badges .sg-node-infected { border-color: rgba(251, 113, 133, 0.24); color: #fb7185; background: rgba(251, 113, 133, 0.06); }
    .sg-inspector-grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 0.6rem; margin-bottom: 1rem; }
    .sg-inspector-grid > div { display: flex; flex-direction: column; gap: 0.22rem; min-width: 0; padding: 0.75rem; border: 1px solid var(--sg-border); border-radius: 0.7rem; background: rgba(255, 255, 255, 0.012); }
    .sg-inspector-grid span { color: #466168; font-size: 0.49rem; font-weight: 800; letter-spacing: 0.09em; }
    .sg-inspector-grid strong { overflow: hidden; color: #cedfdd; font: 700 0.76rem monospace; text-overflow: ellipsis; white-space: nowrap; }
    .sg-inspector-grid small { color: #546f75; font-size: 0.54rem; }
    .sg-neighbor-list { margin: 0.9rem 0 1.2rem; }
    .sg-neighbor-list > b { color: #4f6c73; font-size: 0.52rem; letter-spacing: 0.1em; }
    .sg-neighbor-list > div { display: flex; flex-wrap: wrap; gap: 0.35rem; margin-top: 0.5rem; }
    .sg-neighbor-list span { padding: 0.28rem 0.42rem; border: 1px solid var(--sg-border); border-radius: 0.45rem; color: #789094; background: rgba(255, 255, 255, 0.016); font: 600 0.56rem monospace; }
    .sg-neighbor-list em { color: #506970; font-size: 0.65rem; }
    .sg-event-hero { display: flex; align-items: flex-end; justify-content: space-between; gap: 2rem; margin: 1.4rem 0 1rem; padding: 1.3rem 1.4rem; border: 1px solid rgba(87, 231, 214, 0.16); border-radius: 1rem; background: linear-gradient(110deg, rgba(87, 231, 214, 0.055), rgba(255, 255, 255, 0.01)); }
    .sg-event-hero span { color: var(--sg-cyan); font-size: 0.55rem; font-weight: 800; letter-spacing: 0.13em; }
    .sg-event-hero h3 { margin: 0.3rem 0 0; color: #dfefed; font-size: 1.25rem; letter-spacing: -0.025em; }
    .sg-event-hero p { max-width: 34rem; margin: 0; color: #627d83; font-size: 0.72rem; line-height: 1.55; text-align: right; }
    .sg-event-detail { min-height: 16.25rem; padding: 1rem; border: 1px solid var(--sg-border); border-radius: 0.85rem; background: rgba(255, 255, 255, 0.014); }
    .sg-event-detail > span { color: #fb7185; font-size: 0.52rem; font-weight: 800; letter-spacing: 0.11em; }
    .sg-event-detail h4 { margin: 0.35rem 0 0.9rem; color: #dceae8; font-size: 1rem; }
    .sg-event-detail div { display: flex; justify-content: space-between; gap: 1rem; padding: 0.34rem 0; border-bottom: 1px solid rgba(148, 197, 202, 0.07); }
    .sg-event-detail b { color: #4d6870; font-size: 0.57rem; }
    .sg-event-detail strong { overflow: hidden; color: #b9cecb; font: 700 0.62rem monospace; text-overflow: ellipsis; white-space: nowrap; }
    .sg-event-detail p { margin: 0.8rem 0 0; color: #627d83; font-size: 0.63rem; line-height: 1.5; }
    .sg-experiment-hero { display: grid; grid-template-columns: minmax(0, 1.2fr) minmax(280px, 0.8fr); gap: 3rem; align-items: end; margin-bottom: 1rem; padding: clamp(1.5rem, 4vw, 3rem); border: 1px solid rgba(87, 231, 214, 0.16); border-radius: 1.2rem; background: linear-gradient(115deg, rgba(9, 31, 36, 0.98), rgba(8, 21, 26, 0.9)), radial-gradient(circle at 90% 0, rgba(87, 231, 214, 0.12), transparent 22rem); }
    .sg-experiment-hero span { color: var(--sg-cyan); font-size: 0.58rem; font-weight: 800; letter-spacing: 0.14em; }
    .sg-experiment-hero h2 { max-width: 42rem; margin: 0.55rem 0 0; color: #e8f4f2; font-size: clamp(1.8rem, 4vw, 3.3rem); line-height: 1.06; letter-spacing: -0.045em; }
    .sg-experiment-hero p { margin: 0; color: #718b91; font-size: 0.76rem; line-height: 1.7; }
    .sg-experiment-plan { display: grid; grid-template-columns: 1fr 1fr; gap: 0.6rem; }
    .sg-experiment-plan > div { display: flex; flex-direction: column; gap: 0.25rem; padding: 0.8rem; border: 1px solid var(--sg-border); border-radius: 0.7rem; background: rgba(255, 255, 255, 0.014); }
    .sg-experiment-plan small, .sg-result-banner small { color: #466168; font-size: 0.49rem; font-weight: 800; letter-spacing: 0.1em; }
    .sg-experiment-plan strong, .sg-result-banner strong { overflow: hidden; color: #cfe0de; font: 700 0.7rem monospace; text-overflow: ellipsis; white-space: nowrap; }
    .sg-experiment-plan article { display: flex; flex-wrap: wrap; grid-column: 1 / -1; gap: 0.35rem; padding-top: 0.25rem; }
    .sg-experiment-plan article span { padding: 0.3rem 0.45rem; border: 1px solid rgba(87, 231, 214, 0.14); border-radius: 999px; color: #779795; background: rgba(87, 231, 214, 0.035); font-size: 0.53rem; }
    .sg-experiment-empty { display: grid; justify-items: center; margin-top: 1.5rem; padding: 3.5rem 1rem; border: 1px dashed rgba(148, 197, 202, 0.16); border-radius: 1rem; text-align: center; }
    .sg-experiment-empty div { display: grid; place-items: center; width: 3.6rem; height: 3.6rem; border: 1px solid rgba(87, 231, 214, 0.2); border-radius: 1rem; color: var(--sg-cyan); background: rgba(87, 231, 214, 0.05); font-size: 1.3rem; }
    .sg-experiment-empty h3 { margin: 1rem 0 0.4rem; color: #cfe0de; font-size: 1rem; }
    .sg-experiment-empty p { max-width: 36rem; margin: 0; color: #587178; font-size: 0.68rem; line-height: 1.6; }
    .sg-result-banner { display: grid; grid-template-columns: minmax(0, 1.5fr) repeat(3, minmax(0, 0.65fr)); gap: 0.7rem; align-items: center; margin: 1.7rem 0 1rem; padding: 1rem; border: 1px solid rgba(87, 231, 214, 0.17); border-radius: 0.95rem; background: rgba(87, 231, 214, 0.03); }
    .sg-result-banner > div { display: flex; flex-direction: column; gap: 0.2rem; min-width: 0; padding: 0.4rem 0.7rem; }
    .sg-result-banner > div:not(:first-child) { border-left: 1px solid var(--sg-border); }
    .sg-result-banner span { color: var(--sg-cyan); font-size: 0.5rem; font-weight: 800; letter-spacing: 0.11em; }
    .sg-result-banner h3 { margin: 0.2rem 0 0; color: #dceae8; font-size: 1rem; }
    .sg-comparison-hero { display: grid; grid-template-columns: minmax(0, 1.15fr) minmax(280px, 0.85fr); gap: 3rem; align-items: end; margin-bottom: 1rem; padding: clamp(1.5rem, 4vw, 3rem); border: 1px solid rgba(109, 172, 255, 0.16); border-radius: 1.2rem; background: linear-gradient(115deg, rgba(10, 27, 38, 0.98), rgba(8, 21, 26, 0.9)), radial-gradient(circle at 88% 0, rgba(109, 172, 255, 0.12), transparent 22rem); }
    .sg-comparison-hero span { color: #79b8ff; font-size: 0.58rem; font-weight: 800; letter-spacing: 0.14em; }
    .sg-comparison-hero h2 { max-width: 44rem; margin: 0.55rem 0 0; color: #e8f4f2; font-size: clamp(1.8rem, 4vw, 3.15rem); line-height: 1.06; letter-spacing: -0.045em; }
    .sg-comparison-hero p { margin: 0; color: #718b91; font-size: 0.76rem; line-height: 1.7; }
    .sg-comparison-empty { display: grid; justify-items: center; margin-top: 1.2rem; padding: 4rem 1rem; border: 1px dashed rgba(121, 184, 255, 0.18); border-radius: 1rem; text-align: center; }
    .sg-comparison-empty div { display: grid; place-items: center; width: 3.6rem; height: 3.6rem; border: 1px solid rgba(121, 184, 255, 0.22); border-radius: 1rem; color: #79b8ff; background: rgba(121, 184, 255, 0.05); font-size: 1.3rem; }
    .sg-comparison-empty h3 { margin: 1rem 0 0.4rem; color: #cfe0de; font-size: 1rem; }
    .sg-comparison-empty p { max-width: 36rem; margin: 0; color: #587178; font-size: 0.68rem; line-height: 1.6; }
    .sg-report-hero { display: grid; grid-template-columns: minmax(0, 1.15fr) minmax(280px, 0.85fr); gap: 3rem; align-items: end; margin-bottom: 1rem; padding: clamp(1.5rem, 4vw, 3rem); border: 1px solid rgba(251, 191, 36, 0.15); border-radius: 1.2rem; background: linear-gradient(115deg, rgba(34, 29, 16, 0.55), rgba(8, 21, 26, 0.96)), radial-gradient(circle at 88% 0, rgba(251, 191, 36, 0.1), transparent 22rem); }
    .sg-report-hero span { color: #fbbf24; font-size: 0.58rem; font-weight: 800; letter-spacing: 0.14em; }
    .sg-report-hero h2 { max-width: 44rem; margin: 0.55rem 0 0; color: #eef3e8; font-size: clamp(1.8rem, 4vw, 3.15rem); line-height: 1.06; letter-spacing: -0.045em; }
    .sg-report-hero p { margin: 0; color: #7f908d; font-size: 0.76rem; line-height: 1.7; }
    .sg-report-preview { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; padding: 1.4rem; border: 1px solid rgba(251, 191, 36, 0.15); border-radius: 1rem; background: linear-gradient(125deg, rgba(251, 191, 36, 0.04), rgba(255, 255, 255, 0.01)); }
    .sg-report-preview > small, .sg-report-preview > h3, .sg-report-preview > p, .sg-report-preview > code { grid-column: 1 / -1; }
    .sg-report-preview small { color: #fbbf24; font-size: 0.52rem; font-weight: 800; letter-spacing: 0.12em; }
    .sg-report-preview h3 { margin: 0.1rem 0 0; color: #e4eeec; font-size: 1.25rem; }
    .sg-report-preview p { margin: -0.45rem 0 0.35rem; color: #61797f; font-size: 0.65rem; }
    .sg-report-preview div { display: flex; flex-direction: column; gap: 0.25rem; padding: 0.8rem; border: 1px solid var(--sg-border); border-radius: 0.7rem; }
    .sg-report-preview div span { color: #4b646b; font-size: 0.49rem; font-weight: 800; letter-spacing: 0.09em; }
    .sg-report-preview div strong { color: #cbdcda; font: 700 0.7rem monospace; }
    .sg-report-preview code { overflow: hidden; color: #58777b; font-size: 0.56rem; text-overflow: ellipsis; white-space: nowrap; }
    .sg-methodology-hero { display: grid; grid-template-columns: minmax(0, 1.15fr) minmax(280px, 0.85fr); gap: 3rem; align-items: end; margin-bottom: 1rem; padding: clamp(1.5rem, 4vw, 3rem); border: 1px solid rgba(167, 139, 250, 0.16); border-radius: 1.2rem; background: linear-gradient(115deg, rgba(26, 21, 43, 0.62), rgba(8, 21, 26, 0.96)), radial-gradient(circle at 88% 0, rgba(167, 139, 250, 0.12), transparent 22rem); }
    .sg-methodology-hero span { color: #b9a4ff; font-size: 0.58rem; font-weight: 800; letter-spacing: 0.14em; }
    .sg-methodology-hero h2 { max-width: 44rem; margin: 0.55rem 0 0; color: #eeeafa; font-size: clamp(1.8rem, 4vw, 3.15rem); line-height: 1.06; letter-spacing: -0.045em; }
    .sg-methodology-hero p { margin: 0; color: #7f8994; font-size: 0.76rem; line-height: 1.7; }
    .sg-research-question { margin: 0.8rem 0 1.3rem; padding: 1.2rem 1.4rem; border-left: 3px solid #a78bfa; border-radius: 0 0.8rem 0.8rem 0; background: rgba(167, 139, 250, 0.035); }
    .sg-research-question small { color: #806fc0; font-size: 0.52rem; font-weight: 800; letter-spacing: 0.12em; }
    .sg-research-question h3 { max-width: 68rem; margin: 0.4rem 0 0; color: #c9c5da; font-size: 0.9rem; font-weight: 600; line-height: 1.6; }
    .sg-method-flow { display: flex; align-items: center; gap: 0.45rem; margin: 1rem 0 2rem; overflow-x: auto; }
    .sg-method-flow div { display: flex; flex: 1 0 9rem; flex-direction: column; gap: 0.2rem; padding: 0.8rem; border: 1px solid var(--sg-border); border-radius: 0.7rem; background: rgba(255, 255, 255, 0.012); }
    .sg-method-flow b { color: #a78bfa; font: 700 0.56rem monospace; }
    .sg-method-flow span { color: #c8d7d5; font-size: 0.66rem; font-weight: 700; }
    .sg-method-flow small { color: #506970; font-size: 0.52rem; }
    .sg-method-flow i { color: #3e565d; font-style: normal; }
    .sg-method-card { min-height: 11rem; padding: 1rem; border: 1px solid var(--sg-border); border-radius: 0.85rem; background: rgba(255, 255, 255, 0.014); }
    .sg-method-card small { color: #806fc0; font: 700 0.52rem monospace; }
    .sg-method-card h4 { margin: 0.7rem 0 0.45rem; color: #d5e1df; font-size: 0.8rem; }
    .sg-method-card p { color: #637c82; font-size: 0.63rem; line-height: 1.55; }
    .sg-method-card b { color: #82969a; font-size: 0.56rem; line-height: 1.45; }
    .sg-lifecycle { display: flex; flex-wrap: wrap; align-items: center; gap: 0.55rem; margin: 0.7rem 0; }
    .sg-lifecycle span { padding: 0.55rem 0.75rem; border: 1px solid rgba(167, 139, 250, 0.18); border-radius: 0.55rem; color: #b9a4ff; background: rgba(167, 139, 250, 0.04); font: 800 0.58rem monospace; letter-spacing: 0.08em; }
    .sg-lifecycle i { color: #425960; font-style: normal; }
    .sg-about-hero { display: grid; grid-template-columns: minmax(0, 1.25fr) minmax(260px, 0.75fr); gap: 3rem; align-items: center; min-height: 29rem; padding: clamp(1.6rem, 4vw, 3.5rem); border: 1px solid rgba(87, 231, 214, 0.16); border-radius: 1.25rem; background: linear-gradient(120deg, rgba(8, 28, 33, 0.98), rgba(7, 17, 21, 0.94)), radial-gradient(circle at 85% 20%, rgba(87, 231, 214, 0.13), transparent 24rem); }
    .sg-about-copy > span { color: var(--sg-cyan); font-size: 0.58rem; font-weight: 800; letter-spacing: 0.14em; }
    .sg-about-copy h2 { max-width: 58rem; margin: 0.8rem 0 1rem; color: #edf7f5; font-size: clamp(2rem, 4.6vw, 4rem); line-height: 1.03; letter-spacing: -0.05em; }
    .sg-about-copy p { max-width: 48rem; color: #789197; font-size: 0.8rem; line-height: 1.75; }
    .sg-about-copy > div { display: flex; flex-wrap: wrap; gap: 0.65rem; margin-top: 1.4rem; }
    .sg-about-copy a, .sg-about-actions a { padding: 0.7rem 0.9rem; border: 1px solid rgba(87, 231, 214, 0.2); border-radius: 0.65rem; color: var(--sg-cyan) !important; background: rgba(87, 231, 214, 0.055); font-size: 0.65rem; font-weight: 800; text-decoration: none !important; }
    .sg-about-mark { display: grid; justify-items: center; padding: 2rem; border: 1px solid var(--sg-border); border-radius: 50%; aspect-ratio: 1; background: radial-gradient(circle, rgba(87, 231, 214, 0.08), rgba(255, 255, 255, 0.008) 62%); }
    .sg-about-mark div { color: var(--sg-cyan); font-size: 2rem; }
    .sg-about-mark strong { margin-top: auto; color: #e1efed; font: 700 clamp(2.2rem, 5vw, 4rem) monospace; }
    .sg-about-mark span { color: #5f7b80; font-size: 0.52rem; font-weight: 800; letter-spacing: 0.12em; }
    .sg-about-mark small { margin-bottom: auto; color: #456168; font: 600 0.6rem monospace; }
    .sg-about-statement { max-width: 72rem; margin: 4rem auto; text-align: center; }
    .sg-about-statement small { color: var(--sg-cyan); font-size: 0.55rem; font-weight: 800; letter-spacing: 0.14em; }
    .sg-about-statement h3 { margin: 0.6rem 0; color: #dbe9e7; font-size: clamp(1.4rem, 3vw, 2.2rem); letter-spacing: -0.03em; }
    .sg-about-statement p { color: #698288; font-size: 0.76rem; line-height: 1.75; }
    .sg-capability-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0.7rem; margin-bottom: 3.5rem; }
    .sg-capability-grid article { display: flex; align-items: center; gap: 0.75rem; padding: 1rem; border: 1px solid var(--sg-border); border-radius: 0.8rem; background: rgba(255, 255, 255, 0.014); }
    .sg-capability-grid b { color: #34565c; font: 700 0.58rem monospace; }
    .sg-capability-grid span { color: #a8bdba; font-size: 0.67rem; font-weight: 700; }
    .sg-architecture-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 0.75rem; }
    .sg-architecture-grid article { min-height: 13rem; padding: 1.1rem; border: 1px solid var(--sg-border); border-radius: 0.9rem; background: linear-gradient(145deg, rgba(255, 255, 255, 0.02), rgba(255, 255, 255, 0.007)); }
    .sg-architecture-grid small { color: #426168; font: 700 0.51rem monospace; }
    .sg-architecture-grid h4 { margin: 1.4rem 0 0.35rem; color: #d1e0de; font-size: 0.82rem; }
    .sg-architecture-grid b { color: var(--sg-cyan); font: 700 0.57rem monospace; }
    .sg-architecture-grid p { color: #60797f; font-size: 0.62rem; line-height: 1.55; }
    .sg-responsibility-note { display: grid; grid-template-columns: auto 1fr; gap: 1rem; align-items: center; margin: 3rem 0; padding: 1.2rem; border: 1px solid rgba(251, 191, 36, 0.15); border-radius: 0.9rem; background: rgba(251, 191, 36, 0.025); }
    .sg-responsibility-note > div { display: grid; place-items: center; width: 3rem; height: 3rem; border-radius: 0.75rem; color: #fbbf24; background: rgba(251, 191, 36, 0.07); }
    .sg-responsibility-note small { color: #a8872a; font-size: 0.5rem; font-weight: 800; letter-spacing: 0.1em; }
    .sg-responsibility-note h4 { margin: 0.2rem 0; color: #d9dfd5; font-size: 0.8rem; }
    .sg-responsibility-note p { margin: 0; color: #71807d; font-size: 0.63rem; line-height: 1.55; }
    .sg-about-actions { display: flex; align-items: center; justify-content: space-between; gap: 2rem; padding: 1.5rem; border: 1px solid rgba(87, 231, 214, 0.15); border-radius: 1rem; background: rgba(87, 231, 214, 0.025); }
    .sg-about-actions small { color: #527471; font-size: 0.5rem; font-weight: 800; letter-spacing: 0.1em; }
    .sg-about-actions h3 { margin: 0.25rem 0 0; color: #d7e5e3; font-size: 1rem; }
    .sg-workspace-hero { display: grid; grid-template-columns: minmax(0, 1.15fr) minmax(280px, 0.85fr); gap: 3rem; align-items: end; margin-bottom: 1rem; padding: clamp(1.5rem, 4vw, 3rem); border: 1px solid rgba(45, 212, 191, 0.16); border-radius: 1.2rem; background: linear-gradient(115deg, rgba(9, 34, 35, 0.78), rgba(8, 21, 26, 0.96)), radial-gradient(circle at 88% 0, rgba(45, 212, 191, 0.12), transparent 22rem); }
    .sg-workspace-hero span { color: #5eead4; font-size: 0.58rem; font-weight: 800; letter-spacing: 0.14em; }
    .sg-workspace-hero h2 { max-width: 46rem; margin: 0.55rem 0 0; color: #e5f4f1; font-size: clamp(1.8rem, 4vw, 3.15rem); line-height: 1.06; letter-spacing: -0.045em; }
    .sg-workspace-hero p { margin: 0; color: #78908e; font-size: 0.76rem; line-height: 1.7; }
    .sg-workspace-card { display: flex; align-items: center; justify-content: space-between; gap: 2rem; margin: 1rem 0; padding: 1.2rem; border: 1px solid rgba(45, 212, 191, 0.16); border-radius: 0.9rem; background: rgba(45, 212, 191, 0.025); }
    .sg-workspace-card small { color: #4b7c77; font-size: 0.5rem; font-weight: 800; letter-spacing: 0.1em; }
    .sg-workspace-card h3 { margin: 0.25rem 0; color: #d4e5e2; font-size: 0.9rem; }
    .sg-workspace-card p { margin: 0; color: #5f777c; font-size: 0.62rem; }
    .sg-workspace-card code { overflow: hidden; max-width: 36rem; color: #5c8985; font-size: 0.55rem; text-overflow: ellipsis; white-space: nowrap; }
    .sg-workspace-drop-hint { display: grid; justify-items: center; padding: 2.8rem 1rem; border: 1px dashed rgba(45, 212, 191, 0.2); border-radius: 1rem; text-align: center; }
    .sg-workspace-drop-hint div { display: grid; place-items: center; width: 3.2rem; height: 3.2rem; border-radius: 0.8rem; color: #5eead4; background: rgba(45, 212, 191, 0.06); font-size: 1.2rem; }
    .sg-workspace-drop-hint h4 { margin: 0.9rem 0 0.25rem; color: #c8d9d6; font-size: 0.8rem; }
    .sg-workspace-drop-hint p { margin: 0; color: #536d72; font-size: 0.6rem; }
    .sg-state { display: grid; grid-template-columns: auto minmax(0, 1fr); gap: 1rem; align-items: center; margin: 1rem 0; padding: 1.2rem; border: 1px solid var(--sg-border); border-radius: var(--sg-radius-md); background: rgba(255, 255, 255, 0.012); }
    .sg-state > div { display: grid; place-items: center; width: 3.2rem; height: 3.2rem; border-radius: 0.8rem; font-size: 1.2rem; }
    .sg-state small { font-size: 0.5rem; font-weight: 800; letter-spacing: 0.11em; }
    .sg-state h3 { margin: 0.22rem 0; color: #d8e7e5; font-size: 0.88rem; }
    .sg-state p { margin: 0; color: #647d83; font-size: 0.65rem; line-height: 1.55; }
    .sg-state b { display: block; margin-top: 0.55rem; color: #819598; font-size: 0.58rem; }
    .sg-state a { display: inline-block; margin-top: 0.7rem; color: var(--sg-cyan) !important; font-size: 0.62rem; font-weight: 800; text-decoration: none !important; }
    .sg-state-empty > div { color: var(--sg-info); background: rgba(121, 184, 255, 0.06); }
    .sg-state-empty small { color: #668fc0; }
    .sg-state-error { border-color: rgba(251, 113, 133, 0.22); background: rgba(251, 113, 133, 0.035); }
    .sg-state-error > div { color: var(--sg-danger); background: rgba(251, 113, 133, 0.08); font-weight: 900; }
    .sg-state-error small { color: var(--sg-danger); }

    /* Professional design-system foundation */
    html { color-scheme: dark; }
    body, [data-testid="stAppViewContainer"] { font-family: var(--sg-font-sans); }
    ::selection { color: #031311; background: rgba(87, 231, 214, 0.82); }
    * { scrollbar-color: rgba(87, 231, 214, 0.28) rgba(255, 255, 255, 0.025); scrollbar-width: thin; }
    a, button, input, textarea, [role="button"], [tabindex] { outline: none; }
    a:focus-visible, button:focus-visible, input:focus-visible, textarea:focus-visible,
    [role="button"]:focus-visible, [tabindex]:focus-visible {
        border-color: var(--sg-cyan) !important;
        box-shadow: var(--sg-focus) !important;
    }
    [data-testid="stTopNav"] { background: rgba(6, 16, 20, 0.9); backdrop-filter: blur(18px); }
    [data-testid="stTopNav"] a { min-height: 2.55rem; border-radius: var(--sg-radius-sm); }
    [data-testid="stTopNav"] a:hover { color: var(--sg-text); background: rgba(87, 231, 214, 0.045); }
    [data-testid="stButton"] button, [data-testid="stDownloadButton"] button,
    [data-testid="stFormSubmitButton"] button {
        min-height: 2.65rem;
        border-color: var(--sg-border-strong);
        border-radius: var(--sg-radius-sm);
        font-weight: 750;
        transition: transform 150ms ease, border-color 150ms ease, background 150ms ease, box-shadow 150ms ease;
    }
    [data-testid="stButton"] button:hover, [data-testid="stDownloadButton"] button:hover,
    [data-testid="stFormSubmitButton"] button:hover { border-color: rgba(87, 231, 214, 0.42); transform: translateY(-1px); }
    [data-testid="stButton"] button[kind="primary"], [data-testid="stFormSubmitButton"] button[kind="primary"] {
        border-color: transparent;
        color: #05201e;
        background: var(--sg-cyan);
        box-shadow: 0 10px 28px rgba(87, 231, 214, 0.13);
    }
    [data-baseweb="input"] > div, [data-baseweb="select"] > div,
    [data-baseweb="textarea"] > div, [data-testid="stFileUploaderDropzone"] {
        border-color: var(--sg-border-strong) !important;
        border-radius: var(--sg-radius-sm) !important;
        background: rgba(255, 255, 255, 0.018) !important;
    }
    [data-testid="stDataFrame"] { overflow: hidden; border: 1px solid var(--sg-border); border-radius: var(--sg-radius-md); }
    [data-testid="stMetric"] { box-shadow: inset 0 1px rgba(255, 255, 255, 0.018); transition: border-color 150ms ease, transform 150ms ease; }
    [data-testid="stMetric"]:hover { border-color: var(--sg-border-strong); transform: translateY(-1px); }
    [data-testid="stAlert"] { border-radius: var(--sg-radius-md); }
    [data-testid="stExpander"] { overflow: hidden; border-color: var(--sg-border) !important; border-radius: var(--sg-radius-md) !important; background: rgba(255, 255, 255, 0.01); }
    [data-baseweb="tab"]:focus-visible { box-shadow: inset var(--sg-focus); }
    [data-testid="stButtonGroup"] { margin-bottom: 1rem; }
    [data-testid="stButtonGroup"] > div { padding: 0.32rem; border: 1px solid var(--sg-border); border-radius: var(--sg-radius-md); background: rgba(255, 255, 255, 0.014); }
    [data-testid="stButtonGroup"] button { min-height: 2.45rem; border: 0; border-radius: var(--sg-radius-sm); color: #718b91; font-size: 0.72rem; font-weight: 750; }
    [data-testid="stButtonGroup"] button[aria-pressed="true"] { color: var(--sg-cyan); background: rgba(87, 231, 214, 0.08); box-shadow: inset 0 0 0 1px rgba(87, 231, 214, 0.11); }
    .sg-token-grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 0.6rem; }
    .sg-token-grid article { display: flex; align-items: center; gap: 0.65rem; min-width: 0; padding: 0.7rem; border: 1px solid var(--sg-border); border-radius: var(--sg-radius-sm); background: rgba(255, 255, 255, 0.012); }
    .sg-token-grid i { flex: 0 0 auto; width: 2rem; height: 2rem; border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 0.55rem; box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.16); }
    .sg-token-grid div { display: flex; min-width: 0; flex-direction: column; gap: 0.08rem; }
    .sg-token-grid b { color: #cfe0de; font-size: 0.61rem; }
    .sg-token-grid code { color: #668187; font: 600 0.52rem var(--sg-font-mono); }
    .sg-token-grid small { overflow: hidden; color: #4e686e; font-size: 0.49rem; text-overflow: ellipsis; white-space: nowrap; }
    .sg-badge-showcase { display: flex; flex-wrap: wrap; gap: 0.45rem; margin: 1rem 0; }
    .sg-badge { padding: 0.36rem 0.55rem; border: 1px solid currentColor; border-radius: var(--sg-radius-pill); font-size: 0.52rem; font-weight: 800; letter-spacing: 0.08em; }
    .sg-badge-success { color: var(--sg-success); background: rgba(110, 231, 183, 0.05); }
    .sg-badge-info { color: var(--sg-info); background: rgba(121, 184, 255, 0.05); }
    .sg-badge-warning { color: var(--sg-warning); background: rgba(251, 191, 36, 0.05); }
    .sg-badge-danger { color: var(--sg-danger); background: rgba(251, 113, 133, 0.05); }
    .sg-badge-neutral { color: var(--sg-muted); background: rgba(120, 144, 151, 0.05); }
    .sg-type-specimen { padding: 1.2rem; border: 1px solid var(--sg-border); border-radius: var(--sg-radius-md); background: var(--sg-surface); }
    .sg-type-specimen small { color: #526f76; font: 700 0.5rem var(--sg-font-mono); letter-spacing: 0.1em; }
    .sg-type-specimen h3 { margin: 0.45rem 0; color: var(--sg-text); font-size: clamp(1.3rem, 3vw, 2rem); letter-spacing: -0.035em; }
    .sg-type-specimen p { color: var(--sg-muted); font-size: 0.68rem; }
    .sg-type-specimen code { color: var(--sg-cyan); font: 600 0.62rem var(--sg-font-mono); }

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after { scroll-behavior: auto !important; animation-duration: 0.01ms !important; animation-iteration-count: 1 !important; transition-duration: 0.01ms !important; }
    }

    @media (max-width: 760px) {
        .sg-site-header { align-items: flex-start; flex-direction: column; }
        .sg-site-meta { flex-wrap: wrap; }
        .sg-topbar { flex-direction: column; }
        .sg-system-pill { align-self: flex-start; }
        .sg-footer { flex-direction: column; }
        .sg-hero { grid-template-columns: 1fr; padding: 1.4rem; }
        .sg-hero-visual { min-height: 19rem; }
        .sg-kpi-grid { grid-template-columns: 1fr 1fr; }
        .sg-section-heading { align-items: flex-start; flex-direction: column; }
        .sg-process-grid, .sg-module-grid { grid-template-columns: 1fr; }
        .sg-run-banner { grid-template-columns: 1fr; }
        .sg-run-stats { justify-content: space-between; }
        .sg-scenario-summary { grid-template-columns: 1fr 1fr; }
        .sg-preset-detail { grid-template-columns: auto 1fr; }
        .sg-preset-facts { grid-column: 1 / -1; grid-template-columns: repeat(4, 1fr); }
        .sg-live-status { grid-template-columns: 1fr 1fr; }
        .sg-live-status > div:not(:first-child) { border-left: 0; padding-left: 0.45rem; }
        .sg-inspector-head { align-items: flex-start; flex-direction: column; }
        .sg-inspector-grid { grid-template-columns: 1fr 1fr; }
        .sg-event-hero { align-items: flex-start; flex-direction: column; }
        .sg-event-hero p { text-align: left; }
        .sg-experiment-hero { grid-template-columns: 1fr; gap: 1.3rem; }
        .sg-result-banner { grid-template-columns: 1fr 1fr; }
        .sg-result-banner > div:not(:first-child) { border-left: 0; }
        .sg-comparison-hero { grid-template-columns: 1fr; gap: 1.3rem; }
        .sg-report-hero { grid-template-columns: 1fr; gap: 1.3rem; }
        .sg-report-preview { grid-template-columns: 1fr; }
        .sg-report-preview > * { grid-column: 1 !important; }
        .sg-methodology-hero { grid-template-columns: 1fr; gap: 1.3rem; }
        .sg-about-hero { grid-template-columns: 1fr; }
        .sg-about-mark { width: min(100%, 17rem); justify-self: center; }
        .sg-capability-grid { grid-template-columns: 1fr; }
        .sg-architecture-grid { grid-template-columns: 1fr; }
        .sg-about-actions { align-items: flex-start; flex-direction: column; }
        .sg-workspace-hero { grid-template-columns: 1fr; gap: 1.3rem; }
        .sg-workspace-card { align-items: flex-start; flex-direction: column; }
        .sg-workspace-card code { max-width: 100%; }
        .sg-token-grid { grid-template-columns: 1fr 1fr; }
        .sg-state { align-items: flex-start; }
    }
</style>
"""


def apply_theme(st) -> None:
    st.markdown(design_token_css(), unsafe_allow_html=True)
    st.markdown(THEME_CSS, unsafe_allow_html=True)
