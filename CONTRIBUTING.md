# Contributing to CasaMobilité

Thank you for your interest in contributing! Here's how to get started.

---

## Development Setup

```bash
git clone https://github.com/ZouhairChoufa/CasaMobilit.git
cd CasaMobilit
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
streamlit run app/app.py
```

---

## Branch Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Stable, production-ready |
| `feature/*` | New features |
| `fix/*` | Bug fixes |
| `data/*` | Data updates only |

```bash
git checkout -b feature/my-feature
```

---

## Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add real-time bus tracking
fix: correct NaN transfer stop handling
data: update stops.csv with new T3 stations
docs: improve README installation steps
chore: bump streamlit to 1.35
refactor: extract map legend to helper function
```

---

## Pull Request Checklist

- [ ] `python app/test_logic.py` passes for all 3 scenarios
- [ ] No new dependencies added without updating `requirements.txt`
- [ ] Data files validated in QGIS if geographic changes were made
- [ ] `CHANGELOG.md` updated under `[Unreleased]`

---

## Data Contributions

If you're adding or correcting transport/POI data:

- `stops.csv` — must include `stop_id`, `stop_name`, `line_id`, `seq`, `latitude`, `longitude`, `mode`, `district`
- `poi_clean.csv` — must use `;` separator and include `poi_id`, `poi_name`, `category`, `latitude`, `longitude`
- Validate coordinates against OSM before submitting

---

## Reporting Issues

Open a GitHub Issue with:
1. Steps to reproduce
2. Expected vs actual behaviour
3. Python version and OS
