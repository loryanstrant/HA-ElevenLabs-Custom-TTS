#!/usr/bin/env python3
"""Probe which ElevenLabs TTS models accept `language_code` and
`apply_text_normalization: "on"`.

For every model your API key can use for TTS, sends three tiny requests:
  baseline   - no optional params (proves the model + voice work at all)
  language   - language_code="en"
  normalize  - apply_text_normalization="on"

Each request synthesizes a two-character phrase, so a full run costs roughly
6 characters per model of your quota.

Usage:
  ELEVENLABS_API_KEY=sk_... python3 scripts/probe_model_params.py [--voice VOICE_ID] [--json out.json]

The key is read from the environment only and never printed.
Stdlib only; no extra dependencies.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

API = "https://api.elevenlabs.io"
TEXT = "Hi"
# Lowest-bitrate format keeps responses small; it doesn't change what's billed.
OUTPUT_FORMAT = "mp3_22050_32"

VARIANTS = {
    "baseline": {},
    "language": {"language_code": "en"},
    "normalize": {"apply_text_normalization": "on"},
}


def _request(key: str, method: str, path: str, body: dict | None = None):
    """Return (status, payload). payload is bytes on success, parsed JSON/text on error."""
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        API + path,
        data=data,
        method=method,
        headers={"xi-api-key": key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as err:
        raw = err.read().decode(errors="replace")
        try:
            return err.code, json.loads(raw)
        except json.JSONDecodeError:
            return err.code, raw


def _error_summary(payload) -> str:
    """Pull the one-line reason out of an ElevenLabs error body."""
    if isinstance(payload, dict):
        detail = payload.get("detail", payload)
        if isinstance(detail, dict):
            return f"{detail.get('status', '?')}: {detail.get('message', detail)}"
        return str(detail)
    return str(payload)[:200]


def _pick_voice(key: str) -> str:
    status, payload = _request(key, "GET", "/v1/voices")
    if status != 200:
        sys.exit(f"Could not list voices (HTTP {status}): {_error_summary(payload)}")
    voices = json.loads(payload)["voices"]
    if not voices:
        sys.exit("Your account has no voices; pass --voice VOICE_ID")
    # Prefer premade/cloned voices: library voices can 402 on free tiers,
    # which would make every model look broken.
    rank = {"premade": 0, "cloned": 1, "generated": 2}
    voices.sort(key=lambda v: rank.get(v.get("category"), 3))
    voice = voices[0]
    print(f"Using voice: {voice['name']} ({voice['voice_id']}, {voice.get('category')})")
    return voice["voice_id"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--voice", help="voice ID to use (default: first voice on the account)")
    parser.add_argument("--json", metavar="PATH", help="also write raw results to this file")
    args = parser.parse_args()

    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        sys.exit("Set ELEVENLABS_API_KEY in the environment")

    status, payload = _request(key, "GET", "/v1/models")
    if status != 200:
        sys.exit(f"Could not list models (HTTP {status}): {_error_summary(payload)}")
    models = [m for m in json.loads(payload) if m.get("can_do_text_to_speech")]
    print(f"Found {len(models)} TTS models")

    voice = args.voice or _pick_voice(key)
    path = f"/v1/text-to-speech/{voice}?output_format={OUTPUT_FORMAT}"

    results = []
    for model in models:
        model_id = model["model_id"]
        row = {"model_id": model_id, "name": model.get("name")}
        for variant, extra in VARIANTS.items():
            status, payload = _request(
                key, "POST", path, {"text": TEXT, "model_id": model_id, **extra}
            )
            row[variant] = (
                {"ok": True, "status": status, "bytes": len(payload)}
                if status == 200
                else {"ok": False, "status": status, "error": _error_summary(payload)}
            )
            time.sleep(0.3)  # stay well under concurrency/rate limits
        results.append(row)
        cells = "  ".join(
            f"{v}={'ok' if row[v]['ok'] else row[v]['status']}" for v in VARIANTS
        )
        print(f"  {model_id:<32} {cells}")

    print("\nErrors:")
    any_errors = False
    for row in results:
        if not row["baseline"]["ok"]:
            # The model doesn't work at all with this voice/plan, so the
            # other variants failing tells us nothing about the params.
            any_errors = True
            print(f"  {row['model_id']} unusable (baseline HTTP {row['baseline']['status']} - {row['baseline']['error']})")
            continue
        for variant in VARIANTS:
            if not row[variant]["ok"]:
                any_errors = True
                print(f"  {row['model_id']} [{variant}] HTTP {row[variant]['status']} - {row[variant]['error']}")
    if not any_errors:
        print("  none: every model accepted every variant")

    if args.json:
        with open(args.json, "w") as fh:
            json.dump(results, fh, indent=2)
        print(f"\nRaw results written to {args.json}")


if __name__ == "__main__":
    main()
