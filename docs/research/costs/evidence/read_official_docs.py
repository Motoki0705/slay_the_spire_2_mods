#!/usr/bin/env python3
"""Read public documentation only; never submits a generation or uploads media.

BytePlus embeds document JSON in its server response. The generic browser text
reader omits that body, so read curDoc.MDContent and retain only hashes, dates,
selected numeric facts, and source locations. Do not archive complete articles.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import urllib.request
from datetime import datetime, timezone

OUT = Path(__file__).resolve().parent
SOURCES = {
    "minimax_price": "https://platform.minimax.io/docs/pricing/overview.md",
    "minimax_create": "https://platform.minimax.io/docs/api-reference/video-generation-v2-create.md",
    "minimax_guide": "https://platform.minimax.io/docs/guides/video-generation.md",
    "minimax_hailuo": "https://hailuoai.video/tools/minimax-h3",
    "byteplus_price": "https://docs.byteplus.com/en/docs/modelark/model-pricing",
    "byteplus_specs": "https://docs.byteplus.com/en/docs/modelark/seedance-2-5",
    "byteplus_tutorial": "https://docs.byteplus.com/en/docs/modelark/video-generation-tutorial",
    "dreamina_plans": "https://dreamina.capcut.com/seedance/seedance-2-5-pricing-2026",
    "bytedance_launch": "https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5",
}


def read_public(url: str) -> tuple[dict, str]:
    with urllib.request.urlopen(url, timeout=45) as response:
        raw = response.read()
        meta = {
            "requested_url": url,
            "final_url": response.url,
            "read_at_utc": datetime.now(timezone.utc).isoformat(),
            "http_status": response.status,
            "bytes": len(raw),
            "response_sha256": hashlib.sha256(raw).hexdigest(),
        }
    body = raw.decode("utf-8")
    if "docs.byteplus.com" in url:
        match = re.search(r"window\._ROUTER_DATA = (.*?)</script>", body, re.S)
        if not match:
            raise ValueError(f"Missing documented server body: {url}")
        routes = json.loads(match.group(1).rstrip(";\n "))["loaderData"]
        docs = [v["curDoc"] for v in routes.values()
                if isinstance(v, dict) and isinstance(v.get("curDoc"), dict)]
        doc = docs[-1]
        body = doc["MDContent"].replace("\\-", "-")
        meta.update({
            "document_title": doc["Title"],
            "document_updated_utc": doc["UpdatedTime"],
            "document_body_sha256": hashlib.sha256(body.encode()).hexdigest(),
            "read_mechanism": "public HTML > window._ROUTER_DATA > curDoc.MDContent",
        })
    return meta, body


def main() -> None:
    metadata = {}
    bodies = {}
    for key, url in SOURCES.items():
        meta, body = read_public(url)
        metadata[key] = meta
        bodies[key] = body

    # Fail visibly if the official rows change, instead of silently assuming an
    # older model price. Only the requested model's numeric facts are retained.
    h3_line = [line for line in bodies["minimax_price"].splitlines()
               if "MiniMax-H3" in line and "MiniMax-H3-Max" not in line
               and "Regeneration" not in line and "/ second" in line]
    assert any("$0.08" in line and "768P" in line for line in h3_line)
    assert any("$0.13" in line and "2K" in line for line in h3_line)
    bp_lines = bodies["byteplus_price"].splitlines()
    bp_row = next(line for line in bp_lines if line.startswith("|dreamina-seedance-2-5-260628"))
    assert all(rate in bp_row for rate in ["10.70", "6.40", "11.7", "7.0"])
    assert "1024" in bodies["byteplus_price"]
    assert "834×1112" in bodies["byteplus_specs"]
    assert "1920×1080" in bodies["byteplus_specs"]
    metadata["byteplus_price"]["fact_locations"] = {
        "price_row_line": bp_lines.index(bp_row) + 1,
        "price_section_anchor": "28d5ad67",
        "examples_section_anchor": "sd25_price",
        "token_formula_line": next(i + 1 for i, x in enumerate(bp_lines)
                                    if "Estimated token consumption =" in x),
    }
    metadata["byteplus_specs"]["fact_locations"] = {
        "model_id": "Model capabilities table",
        "duration_anchor": "2.5_duration",
        "resolution_anchor": "2.5_resolution",
        "pixel_dimensions_anchor": "2.5_ratio",
        "draft_anchor": "2.5_draft_mode",
    }
    (OUT / "source-reads.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"public_documents_read": len(metadata),
                      "price_row_checks": "passed",
                      "output": str(OUT / "source-reads.json")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
