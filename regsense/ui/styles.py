"""Design tokens and CSS shared across every UI module."""

NAVY = "#0B2545"
STEEL = "#3E5C76"
AMBER = "#C77D22"
RED = "#B3261E"
GREEN = "#1E6B3E"
BG = "#F7F8FA"

CSS = f"""
<style>
.rs-badge {{
    display: inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
}}
.rs-covered {{ background: #E3F2E9; color: {GREEN}; }}
.rs-partial {{ background: #FBEBD8; color: {AMBER}; }}
.rs-missing {{ background: #FBE7E6; color: {RED}; }}
.rs-open {{ background: #EAEFF5; color: {STEEL}; }}
.rs-closed {{ background: #E3F2E9; color: {GREEN}; }}
.rs-escalated {{ background: #FBE7E6; color: {RED}; }}
.rs-card {{
    background: white;
    border: 1px solid #E3E6EA;
    border-radius: 10px;
    padding: 16px 18px;
    margin-bottom: 10px;
}}
</style>
"""


def badge(text: str, css_class: str) -> str:
    return f'<span class="rs-badge {css_class}">{text}</span>'
