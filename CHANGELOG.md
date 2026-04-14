# Changelog

All notable changes to CasaMobilité are documented here.  
Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)  
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html)

---

## [1.1.0] — 2025-07-xx

### Fixed
- `get_journey_stops`: `transfer_stop_id` NaN cell was cast to string `"nan"` (truthy), triggering wrong 2-line branch
- `get_journey_bbox`: `min([])`/`max([])` crash when stop sequence is empty — now returns Casablanca default bbox
- `step_icon`: hardcoded distance strings (`"550m"`, `"350m"`) replaced with generic digit+`m` pattern
- `app.py`: hardcoded `"app/um6p_logo.png"` path replaced with `Path(__file__).parent` — fixes crash when running from any directory

### Changed
- `requirements.txt`: added missing `Pillow>=10.0.0` (used in `app.py` but was absent — broke fresh installs)
- `load_data.py`: split `import pandas as pd, json, streamlit as st` into separate lines (PEP 8)
- `app.py`: moved `mcard()` helper from inside `if go:` block to module level
- `test_logic.py`: now tests all 3 scenarios (SC01, SC02, SC03) instead of only SC01
- `.streamlit/config.toml`: added brand theme colors and server config (was empty)

### Added
- `LICENSE` (MIT)
- `CHANGELOG.md`
- `CONTRIBUTING.md`
- `.env.example`
- UTF-8 encoding declarations (`# -*- coding: utf-8 -*-`) in all Python files

---

## [1.0.0] — 2025-06-xx — Initial Release

### Added
- Interactive map of Casablanca public transport network (T1, T2, T3, T4, BW1, BW2)
- 91 categorised tourist points of interest
- 3 pre-configured journey scenarios (SC01, SC02, SC03)
- Automatic route segment clipping between stops
- Light/dark theme support
- GitHub Codespaces devcontainer configuration
