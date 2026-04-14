# CasaMobilité — Géoportail Smart Mobility Casablanca

> Proof of Concept V1 — PFE Smart City 2025  
> Géoportail frugal d'intégration des données de transport public et des points d'intérêt touristiques à Casablanca.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red?logo=streamlit)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Description

CasaMobilité est une application web interactive permettant de visualiser le réseau de transport public de Casablanca (tramway + busway) et les points d'intérêt touristiques, avec des itinéraires préconfigurés.

**Fonctionnalités principales :**
- Carte interactive du réseau complet (T1, T2, T3, T4, BW1, BW2)
- 91 points d'intérêt touristiques catégorisés
- 3 scénarios d'itinéraires avec étapes détaillées
- Calcul automatique du segment de route entre deux arrêts
- Interface responsive avec thème clair/sombre

---

## Installation

### Prérequis
- Python 3.10 ou supérieur
- pip

### 1. Cloner le dépôt
```bash
git clone https://github.com/ZouhairChoufa/CasaMobilit.git
cd CasaMobilit
```

### 2. Créer un environnement virtuel
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Lancer l'application
```bash
streamlit run app/app.py
```

L'application s'ouvre sur **http://localhost:8501**

---

## ☁️ Lancer dans GitHub Codespaces

Ce projet inclut une configuration `.devcontainer` prête à l'emploi.  
Cliquez sur **Code → Open with Codespaces** depuis GitHub — l'application démarre automatiquement.

---

## 🗂️ Structure du projet

```
geoportal/
├── .devcontainer/
│   └── devcontainer.json       # Config GitHub Codespaces
├── .streamlit/
│   └── config.toml             # Thème Streamlit + couleurs de marque
├── app/
│   ├── app.py                  # Point d'entrée principal
│   ├── load_data.py            # Chargement des données + helpers géométriques
│   ├── map_utils.py            # Constructeurs de cartes Folium
│   ├── style.css               # Styles personnalisés
│   ├── test_logic.py           # Tests de validation des 3 scénarios
│   └── um6p_logo.png           # Logo de l'application
├── data/
│   ├── stops.csv               # 65 arrêts tramway et busway
│   ├── routes.csv              # 6 lignes avec horaires officiels
│   ├── scenarios.csv           # 3 itinéraires préconfigurés
│   ├── poi_clean.csv           # 91 points d'intérêt touristiques
│   ├── transport.geojson       # Tracés géographiques des lignes
│   ├── stops.geojson           # Arrêts en points géographiques
│   └── poi_clean.geojson       # POI en points géographiques
├── .env.example                # Variables d'environnement (modèle)
├── .gitignore
├── CHANGELOG.md                # Historique des versions
├── CONTRIBUTING.md             # Guide de contribution
├── LICENSE                     # Licence MIT
├── requirements.txt
└── README.md
```

---

## 📊 Données

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

## 🗺️ Scénarios disponibles (V1)

| ID | Origine | Destination | Lignes | Durée | Coût |
|----|---------|-------------|--------|-------|------|
| SC01 | Ain Diab Plage - Terminus | Mosquée Hassan II | T1 + T2 | 28 min | 6 MAD |
| SC02 | Place Mohammed V | Quartier Habous | T3 | 20 min | 6 MAD |
| SC03 | Parc de la Ligue Arabe | Villa des Arts | T4 | 18 min | 6 MAD |

---

## 🛠️ Stack technique

| Technologie | Rôle |
|-------------|------|
| Python 3.10+ | Langage principal |
| Streamlit | Interface web |
| Folium + streamlit-folium | Cartes interactives |
| Pandas | Traitement des données |
| OpenStreetMap | Fond de carte |
| QGIS | Validation cartographique |

---

## 🧪 Tests

Pour valider la logique des scénarios en ligne de commande :

```bash
python app/test_logic.py
```

---

## 📦 Périmètre V1

- ✅ Tramway T1, T2
- ✅ Busway T3, T4, BW1, BW2
- ✅ 91 POI touristiques
- ✅ 3 scénarios d'itinéraires
- ❌ Taxis et VTC (hors périmètre)
- ❌ Géolocalisation temps réel
- ❌ Authentification utilisateur

---

## 🤝 Contribution

Les contributions sont les bienvenues pour la V2 !

Consultez [CONTRIBUTING.md](CONTRIBUTING.md) pour les détails complets.

1. Forkez le dépôt
2. Créez une branche : `git checkout -b feature/ma-fonctionnalite`
3. Committez vos changements : `git commit -m "feat: ajout de ma fonctionnalité"`
4. Poussez : `git push origin feature/ma-fonctionnalite`
5. Ouvrez une Pull Request

---

## 📄 Licence

Ce projet est sous licence [MIT](LICENSE).

---

*PFE — Conception et prototypage d'un géoportail frugal — STRATÉGIES DES SMART CITIES EN AFRIQUE · Casablanca 2025*
