# Copilot instructions — HA-ElevenLabs-Custom-TTS

> Canonical standards live in the `dev-standards` repo on SOUNDWAVE/Gitea.
> Read by Copilot chat **and** inline suggestions. For full HA build conventions,
> see the `build-ha-component` skill in dev-standards.

## What this repo is

A **Home Assistant custom component** providing text-to-speech via the ElevenLabs
API. Domain: `elevenlabs_custom_tts`.

## Repo shape

- `custom_components/elevenlabs_custom_tts/` — `manifest.json`, `__init__.py`,
  `config_flow.py`, `const.py`, `tts.py` (the TTS platform), `services.yaml`,
  `strings.json`.
- `hacs.json`, `example_configuration.yaml`, `test_integration.py`,
  `.github/workflows/` (`release.yaml` + `validate.yaml`).

## Conventions

- Bump `manifest.json` **version** every release (semver); `domain` matches the
  folder name.
- Test: `hassfest` + HACS validation, then `pytest` with
  `pytest-homeassistant-custom-component` (`test_integration.py` is the entry).
- Deploy/test via the published release artifact into TEST1/TEST2, not host
  file-copy. Backup + auto-rollback.
- The **ElevenLabs API key is user config** (entered in the config flow) — never
  commit it or any voice IDs tied to a private account.

## Never

- Don't commit the ElevenLabs API key, HA tokens, or deploy keys — Gitea Actions
  secrets only.
