"""Translations must ship as translations/en.json, not just strings.json."""

import json
from pathlib import Path

COMPONENT = Path(__file__).parent.parent / "custom_components" / "elevenlabs_custom_tts"


def test_english_translations_match_strings() -> None:
    """Home Assistant loads <integration>/translations/<lang>.json at runtime.

    strings.json is only an authoring file for core's build pipeline, so a custom
    integration that ships it alone renders raw keys ("invalid_api_key") in every
    dialog. Keep the two in sync.
    """
    strings = json.loads((COMPONENT / "strings.json").read_text())
    english = json.loads((COMPONENT / "translations" / "en.json").read_text())
    assert english == strings
