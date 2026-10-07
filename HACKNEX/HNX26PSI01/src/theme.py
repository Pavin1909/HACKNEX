import streamlit as st


CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Rajdhani:wght@500;600;700&display=swap');

:root {
    --bg: #090612;
    --bg-2: #100B1C;
    --panel: #161025;
    --panel-light: #1D1530;
    --purple: #8B5CF6;
    --purple-bright: #A855F7;
    --purple-deep: #5B21B6;
    --gold: #F5C451;
    --gold-bright: #FFD76A;
    --gold-dark: #9A7625;
    --text: #F8F5FF;
    --text-soft: #B8AFCB;
    --text-muted: #756B88;
    --success: #4ADE80;
    --warning: #FACC15;
    --error: #FB7185;
    --border: rgba(245,196,81,0.18);
    --purple-glow: rgba(139,92,246,0.30);
    --gold-glow: rgba(245,196,81,0.25);
}

html, body, [data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at top left, rgba(139,92,246,0.18), transparent 28%),
                radial-gradient(circle at bottom right, rgba(245,196,81,0.12), transparent 22%),
                linear-gradient(135deg, #090612 0%, #100B1C 45%, #090612 100%);
    color: var(--text);
    font-family: 'Inter', sans-serif;
}

body::before {
    content: "";
    position: fixed;
    inset: 0;
    background-image: linear-gradient(rgba(139,92,246,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(245,196,81,0.04) 1px, transparent 1px);
    background-size: 32px 32px;
    mask-image: radial-gradient(circle at center, black 42%, transparent 100%);
    opacity: 0.35;
    pointer-events: none;
}

[data-testid="stSidebar"] {
    background: rgba(16, 11, 28, 0.9);
    border-right: 1px solid var(--border);
    backdrop-filter: blur(18px);
}

.block-container {
    padding-top: 1.1rem;
    padding-bottom: 2rem;
    max-width: 1600px;
}

section[data-testid="stSidebar"] .stMarkdownContainer {
    color: var(--text-soft);
}

h1, h2, h3, h4, .display-heading, .section-kicker {
    font-family: 'Rajdhani', 'Inter', sans-serif;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

h1, h2, h3, h4 {
    margin: 0 0 0.5rem 0;
    color: var(--text);
}

p, div, span, label, .stTextInput, .stTextArea, .stSelectbox {
    color: var(--text);
}

.hud-shell {
    position: relative;
    padding: 0.4rem 0 1.5rem 0;
}

.hud-topbar {
    background: rgba(22, 16, 37, 0.72);
    border: 1px solid var(--border);
    box-shadow: inset 0 0 0 1px rgba(139,92,246,0.12), 0 20px 40px rgba(4, 2, 10, 0.32);
    border-radius: 18px;
    padding: 0.6rem 0.9rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(10px);
}

.logo-lockup {
    display: inline-flex;
    align-items: center;
    gap: 0.75rem;
    min-width: 180px;
}

.logo-mark {
    width: 18px;
    height: 18px;
    display: inline-block;
    background: linear-gradient(135deg, var(--gold) 0%, var(--gold-bright) 45%, var(--gold-dark) 100%);
    border: 1px solid rgba(255,255,255,0.35);
    transform: rotate(45deg);
    box-shadow: 0 0 14px rgba(245,196,81,0.45);
}

.brand-title {
    font-family: 'Rajdhani', 'Inter', sans-serif;
    font-weight: 700;
    font-size: 1.45rem;
    letter-spacing: 0.14em;
    color: var(--text);
}

.brand-subtitle {
    font-size: 0.62rem;
    color: var(--text-muted);
    letter-spacing: 0.24em;
    text-transform: uppercase;
    margin-top: 0.12rem;
}

.top-nav {
    display: flex;
    gap: 0.5rem;
    justify-content: center;
    flex-wrap: wrap;
}

.top-nav .nav-chip {
    padding: 0.5rem 0.9rem;
    border-radius: 12px;
    border: 1px solid transparent;
    background: transparent;
    color: var(--text-soft);
    font-size: 0.72rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    transition: all 0.2s ease;
}

.top-nav .nav-chip.active {
    background: linear-gradient(180deg, rgba(139,92,246,0.16), rgba(139,92,246,0.08));
    border-color: rgba(245,196,81,0.3);
    color: var(--text);
    box-shadow: inset 0 0 0 1px rgba(245,196,81,0.18), 0 0 18px rgba(139,92,246,0.22);
}

.status-panel {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 0.75rem;
    color: var(--text-soft);
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
    background: var(--success);
    box-shadow: 0 0 10px rgba(74,222,128,0.8);
}

.sidebar-section {
    padding: 0.2rem 0 0.4rem 0;
}

.side-label {
    font-size: 0.62rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.6rem;
    margin-top: 0.5rem;
}

.sidebar-nav-item {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    width: 100%;
    padding: 0.7rem 0.8rem;
    border-radius: 12px;
    border: 1px solid transparent;
    color: var(--text-soft);
    background: transparent;
    margin-bottom: 0.4rem;
    font-size: 0.82rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

.sidebar-nav-item.active {
    background: linear-gradient(90deg, rgba(139,92,246,0.16) 0%, rgba(255,255,255,0.02) 100%);
    border-left: 2px solid var(--gold);
    color: var(--text);
    box-shadow: inset 0 0 0 1px rgba(245,196,81,0.18), 0 0 20px rgba(139,92,246,0.12);
}

.sidebar-icon {
    width: 8px;
    height: 8px;
    display: inline-block;
    border-radius: 2px;
    background: var(--gold);
    box-shadow: 0 0 10px rgba(245,196,81,0.5);
}

.hud-panel {
    background: linear-gradient(180deg, rgba(29, 21, 48, 0.92), rgba(22,16,37,0.92));
    border: 1px solid var(--border);
    border-radius: 20px;
    box-shadow: inset 0 0 0 1px rgba(245,196,81,0.08), 0 10px 26px rgba(0,0,0,0.2);
    overflow: hidden;
}

.hero-panel {
    padding: 1.3rem 1.4rem;
    background: linear-gradient(135deg, rgba(91,33,182,0.26), rgba(22,16,37,0.9) 42%, rgba(13,10,21,0.96));
    position: relative;
}

.hero-panel::before {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(120deg, transparent 16%, rgba(245,196,81,0.08), transparent 68%);
    pointer-events: none;
}

.section-kicker {
    font-size: 0.72rem;
    color: var(--gold);
    letter-spacing: 0.22em;
    margin-bottom: 0.55rem;
    text-transform: uppercase;
}

.hero-title {
    font-family: 'Rajdhani', 'Inter', sans-serif;
    font-size: clamp(2.2rem, 4vw, 4rem);
    line-height: 0.9;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin: 0;
    color: var(--text);
}

.hero-title .accent {
    background: linear-gradient(90deg, var(--gold-bright), #f6d68a 35%, #fff 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}

.hero-copy {
    margin-top: 0.8rem;
    max-width: 760px;
    color: var(--text-soft);
    font-size: 1rem;
}

.tag-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem;
    margin-top: 1rem;
}

.tag {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.38rem 0.7rem;
    border-radius: 999px;
    background: rgba(139,92,246,0.12);
    border: 1px solid rgba(139,92,246,0.28);
    color: var(--text-soft);
    font-size: 0.7rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

.tag::before {
    content: "";
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--gold);
    box-shadow: 0 0 8px rgba(245,196,81,0.6);
}

.metric-card {
    background: linear-gradient(180deg, rgba(22,16,37,0.95), rgba(16,11,28,0.95));
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1rem 1rem 0.8rem 1rem;
    min-height: 120px;
    box-shadow: inset 0 0 0 1px rgba(139,92,246,0.08);
}

.metric-label {
    color: var(--text-muted);
    font-size: 0.68rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
}

.metric-value {
    color: var(--gold-bright);
    font-weight: 800;
    font-size: clamp(1.8rem, 2.2vw, 2.5rem);
    line-height: 1.1;
    margin-top: 0.5rem;
    font-family: 'Rajdhani', sans-serif;
}

.metric-foot {
    margin-top: 0.35rem;
    font-size: 0.72rem;
    color: var(--text-soft);
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

.document-card, .evidence-card, .source-card, .chat-bubble {
    background: linear-gradient(180deg, rgba(22,16,37,0.96), rgba(16,11,28,0.98));
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1rem 1rem 0.9rem 1rem;
    box-shadow: inset 0 0 0 1px rgba(139,92,246,0.08);
}

.document-card:hover, .evidence-card:hover {
    box-shadow: 0 0 0 1px rgba(245,196,81,0.12), 0 0 22px rgba(139,92,246,0.18);
    border-color: rgba(245,196,81,0.28);
}

.card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.8rem;
    margin-bottom: 0.9rem;
}

.card-title {
    font-size: 0.92rem;
    font-weight: 700;
    color: var(--text);
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

.status-badge {
    font-size: 0.64rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 0.38rem 0.52rem;
    border-radius: 999px;
    background: rgba(74,222,128,0.12);
    border: 1px solid rgba(74,222,128,0.22);
    color: var(--success);
}

.muted-note {
    color: var(--text-muted);
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.primary-button, .stButton > button {
    background: linear-gradient(180deg, rgba(139,92,246,0.2), rgba(68,41,110,0.18));
    border: 1px solid rgba(245,196,81,0.5) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    box-shadow: 0 0 18px rgba(139,92,246,0.18);
}

.primary-button:hover, .stButton > button:hover {
    border-color: rgba(245,196,81,0.75) !important;
    box-shadow: 0 0 20px rgba(245,196,81,0.24);
}

.secondary-button {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(139,92,246,0.36);
    border-radius: 12px;
    color: var(--text-soft);
    padding: 0.7rem 0.9rem;
}

.answer-panel {
    padding: 1.2rem;
    margin-top: 1rem;
    background: linear-gradient(135deg, rgba(91,33,182,0.14), rgba(16,11,28,0.9));
}

.answer-panel strong {
    color: var(--gold-bright);
}

.evidence-block {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 0.75rem;
}

.evidence-pill {
    display: inline-flex;
    align-items: center;
    padding: 0.35rem 0.65rem;
    border-radius: 999px;
    background: rgba(245,196,81,0.08);
    border: 1px solid rgba(245,196,81,0.18);
    color: var(--gold-bright);
    font-size: 0.7rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.empty-state {
    background: rgba(255,255,255,0.02);
    border: 1px dashed rgba(139,92,246,0.35);
    border-radius: 16px;
    padding: 1.2rem;
    color: var(--text-soft);
}

.chat-bubble.user {
    border-color: rgba(139,92,246,0.22);
    background: rgba(139,92,246,0.08);
}

.chat-bubble.assistant {
    border-color: rgba(245,196,81,0.18);
    background: rgba(245,196,81,0.06);
}

.chat-role {
    font-size: 0.68rem;
    letter-spacing: 0.14em;
    color: var(--text-muted);
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}

.stTextInput input, .stTextArea textarea {
    background: rgba(19,14,29,0.96) !important;
    color: var(--text) !important;
    border: 1px solid rgba(245,196,81,0.18) !important;
    border-radius: 14px !important;
}

.stSelectbox > div > div {
    background: rgba(19,14,29,0.96) !important;
    border: 1px solid rgba(245,196,81,0.18) !important;
    border-radius: 14px !important;
}

[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    background: rgba(22,16,37,0.7);
}

[data-testid="stExpanderSummary"] {
    font-size: 0.78rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-soft);
}

@media (max-width: 1200px) {
    .top-nav {
        justify-content: flex-start;
    }
}
</style>
"""


def render_doculens_theme():
    st.markdown(CSS, unsafe_allow_html=True)
