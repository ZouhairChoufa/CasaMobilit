# 🗺️ CasaMobilité — Géoportail Smart Mobility Casablanca

**Proof of Concept V1 — PFE Smart City 2025**

Géoportail frugal d'intégration des données de transport public et des points d'intérêt touristiques à Casablanca.

---

## Installation

### 1. Prérequis
- Python 3.10 ou supérieur
- pip

### 2. Cloner / décompresser le projet
```
casablanca-geoportal/
├── app/
│   ├── app.py
│   ├── load_data.py
│   └── map_utils.py
├── data/
│   ├── stops.csv
│   ├── routes.csv
│   ├── scenarios.csv
│   ├── poi_clean.csv
│   ├── transport.geojson
│   ├── stops.geojson
│   └── poi_clean.geojson
├── requirements.txt
└── README.md
```

### 3. Créer un environnement virtuel (recommandé)
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 4. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 5. Lancer l'application
```bash
streamlit run app/app.py
```

L'application s'ouvre automatiquement sur **http://localhost:8501**

---

## Scénarios disponibles (V1)

| ID | Origine | Destination | Lignes | Durée | Coût |
|----|---------|-------------|--------|-------|------|
| SC01 | Casa Port | Mosquée Hassan II | T1 + T2 | 28 min | 6 MAD |
| SC02 | Place Mohammed V | Quartier Habous | T3 | 20 min | 6 MAD |
| SC03 | Parc de la Ligue Arabe | Villa des Arts | T4 | 18 min | 6 MAD |

---

## Données

| Fichier | Description | Source |
|---------|-------------|--------|
| `stops.csv` | 65 arrêts tramway et busway | casatramway.ma + OSM |
| `routes.csv` | 6 lignes avec horaires officiels | casatramway.ma (PDFs) |
| `scenarios.csv` | 3 itinéraires préconfigurés | Manuel + validation QGIS |
| `poi_clean.csv` | 91 points d'intérêt touristiques | OpenStreetMap via Overpass |
| `transport.geojson` | Tracés géographiques des lignes | OSM + casatramway.ma |
| `stops.geojson` | Arrêts en points géographiques | OSM + casatramway.ma |
| `poi_clean.geojson` | POI en points géographiques | OpenStreetMap |

---

## Stack technique
- **Python** — langage principal
- **Streamlit** — interface web
- **Folium + streamlit-folium** — cartes interactives
- **Pandas** — traitement des données
- **QGIS** — validation cartographique
- **OpenStreetMap** — fond de carte

---

## Périmètre V1
- ✅ Tramway T1, T2
- ✅ Busway T3, T4, Bw1, Bw2
- ✅ 91 POI touristiques
- ✅ 3 scénarios d'itinéraires
- ❌ Taxis et VTC (hors périmètre)
- ❌ Géolocalisation temps réel
- ❌ Authentification utilisateur

---

*PFE — Conception et prototypage d'un géoportail frugal — Casablanca 2025*
