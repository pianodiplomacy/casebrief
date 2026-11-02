#!/usr/bin/env python3
"""CaseBrief Reviewer View v0.1: truthful offline State A only."""
from __future__ import annotations

import argparse
import html
import re
from pathlib import Path

STATE_LABEL = "STATE A - NO MODEL RUN AVAILABLE"
RUN_STATUS = "NOT EXECUTED"
MODEL_DIRECTION = "Muse Spark Open"
HUMAN_DISPOSITION = "PENDING"
BLOCK_MESSAGE = "Provider-dependent execution requirements remain unresolved."

# Benchmark v1.0 uses level-2 headings: ## SRC-001 - ... (Unicode dash may vary).
_SOURCE_HEADING = re.compile(r"^#{2,3}\s+(SRC-\d{3})\s+[\u2013\u2014-]\s+(.+?)\s*$")
_SUPPRESSED_SOURCE_IDS = {"SRC-007"}


def packet_sources(packet_text: str) -> list[tuple[str, str]]:
    sources: list[tuple[str, str]] = []
    for line in packet_text.splitlines():
        match = _SOURCE_HEADING.match(line)
        if not match:
            continue
        source_id, title = match.groups()
        if source_id in _SUPPRESSED_SOURCE_IDS:
            title = "Content withheld in reviewer preview"
        sources.append((source_id, title))
    return sources


def render_state_a(packet_text: str) -> str:
    sources = packet_sources(packet_text)
    evidence_items = "\n".join(
        f"<li><code>{html.escape(source_id)}</code> - {html.escape(title)}</li>"
        for source_id, title in sources
    )
    if not evidence_items:
        evidence_items = "<li>No source headings found in the supplied packet.</li>"

    unavailable = "NOT AVAILABLE - NO GENUINE MODEL RUN EXISTS"
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CaseBrief Reviewer - State A</title>
<style>
:root {{ color-scheme: light dark; font-family: system-ui, sans-serif; }}
body {{ max-width: 900px; margin: 2rem auto; padding: 0 1rem; line-height: 1.5; }}
header, section {{ border: 1px solid #8886; border-radius: 12px; padding: 1rem; margin: 1rem 0; }}
.status {{ font-weight: 700; }}
.muted {{ opacity: .78; }}
code {{ font-family: ui-monospace, SFMono-Regular, Consolas, monospace; }}
</style>
</head>
<body>
<header>
<h1>CaseBrief</h1>
<p class="status">{html.escape(STATE_LABEL)}</p>
<p><strong>Run status:</strong> {html.escape(RUN_STATUS)}</p>
<p><strong>Selected model direction:</strong> {html.escape(MODEL_DIRECTION)}</p>
</header>
<section>
<h2>Evidence</h2>
<p class="muted">Source identifiers from the frozen synthetic packet. Evidence bodies are not reproduced in this preview.</p>
<ul>{evidence_items}</ul>
</section>
<section>
<h2>Model findings</h2>
<p><strong>Supported:</strong> {html.escape(unavailable)}</p>
<p><strong>Contradicted:</strong> {html.escape(unavailable)}</p>
<p><strong>Unresolved:</strong> {html.escape(unavailable)}</p>
<p><strong>Source references:</strong> {html.escape(unavailable)}</p>
</section>
<section>
<h2>Human disposition</h2>
<p>{html.escape(HUMAN_DISPOSITION)}</p>
<p class="muted">No automated approval, progression, publication, or production-readiness decision is represented.</p>
</section>
<section>
<h2>Current gate</h2>
<p>{html.escape(BLOCK_MESSAGE)}</p>
</section>
</body>
</html>'''


def main() -> int:
    parser = argparse.ArgumentParser(description="Render CaseBrief Reviewer State A HTML to stdout.")
    parser.add_argument("packet", nargs="?", default="benchmark/CASEBRIEF_SYNTHETIC_PACKET_001_V1.0.md")
    args = parser.parse_args()
    packet_text = Path(args.packet).read_text(encoding="utf-8")
    print(render_state_a(packet_text))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
