"""
load_data.py — Data layer + route clipping
Source of truth: OSM arete_casatramway_casabusway.geojson
"""
import math
import pandas as pd, json, streamlit as st
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

# ── Loaders ───────────────────────────────────────────────────────

@st.cache_data
def load_stops() -> pd.DataFrame:
    # Lecture avec des virgules (sep=",") et encodage standard (utf-8)
    df = pd.read_csv(DATA_DIR / "stops.csv", sep=",", encoding="utf-8")
    df["latitude"]  = df["latitude"].astype(float)
    df["longitude"] = df["longitude"].astype(float)
    df["seq"]       = df["seq"].astype(int)
    return df

@st.cache_data
def load_routes() -> pd.DataFrame:
    # Fichier classique en UTF-8
    return pd.read_csv(DATA_DIR / "routes.csv", encoding="utf-8")

@st.cache_data
def load_scenarios() -> pd.DataFrame:
    # Fichier classique en UTF-8
    return pd.read_csv(DATA_DIR / "scenarios.csv", encoding="utf-8")

@st.cache_data
def load_poi() -> pd.DataFrame:
    file_path = DATA_DIR / "poi_clean.csv"
    
    # L'utilisation de sep=None et engine='python' permet à Pandas 
    # de deviner automatiquement si le fichier utilise des virgules ou des points-virgules
    try:
        df = pd.read_csv(file_path, sep=None, engine='python', encoding='utf-8')
    except UnicodeDecodeError:
        # Si UTF-8 échoue, on tente l'encodage Windows/Excel classique
        df = pd.read_csv(file_path, sep=None, engine='python', encoding='latin1')
        
    # Nettoyage de sécurité pour garantir que les coordonnées sont bien des nombres
    # (Remplace aussi les virgules décimales par des points si nécessaire)
    if "latitude" in df.columns and "longitude" in df.columns:
        df["latitude"] = pd.to_numeric(df["latitude"].astype(str).str.replace(',', '.'), errors='coerce')
        df["longitude"] = pd.to_numeric(df["longitude"].astype(str).str.replace(',', '.'), errors='coerce')
        
        # Supprime les lignes fantômes ou vides
        df = df.dropna(subset=["latitude", "longitude"])
        
    return df

@st.cache_data
def load_transport_geojson() -> dict:
    # Fichier JSON standard en UTF-8
    with open(DATA_DIR / "transport.geojson", encoding="utf-8") as f:
        return json.load(f)


# ── Geometry helpers ──────────────────────────────────────────────

def _haversine_m(lat1, lon1, lat2, lon2) -> float:
    R = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a  = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def _snap_idx(lat: float, lon: float, coords: list) -> int:
    best_i, best_d = 0, float('inf')
    for i, (clon, clat) in enumerate(coords):
        d = _haversine_m(lat, lon, clat, clon)
        if d < best_d:
            best_d = d
            best_i = i
    return best_i

def clip_route_segment(line_coords: list, stop_a: dict, stop_b: dict) -> list:
    lat_a, lon_a = float(stop_a['latitude']), float(stop_a['longitude'])
    lat_b, lon_b = float(stop_b['latitude']), float(stop_b['longitude'])

    ia = _snap_idx(lat_a, lon_a, line_coords)
    ib = _snap_idx(lat_b, lon_b, line_coords)

    lo, hi = min(ia, ib), max(ia, ib)
    clipped = line_coords[lo : hi + 1]

    if len(clipped) < 2:
        clipped = [[lon_a, lat_a], [lon_b, lat_b]]

    if ia > ib:
        clipped = list(reversed(clipped))

    return clipped

def get_journey_bbox(stops_list: list, poi=None) -> dict:
    lats = [float(s['latitude'])  for s in stops_list]
    lons = [float(s['longitude']) for s in stops_list]
    if poi is not None:
        lats.append(float(poi['latitude']))
        lons.append(float(poi['longitude']))
    if not lats:
        return {'min_lat': 33.5, 'max_lat': 33.6, 'min_lon': -7.7, 'max_lon': -7.5}
    pad = 0.005
    return {
        'min_lat': min(lats) - pad,
        'max_lat': max(lats) + pad,
        'min_lon': min(lons) - pad,
        'max_lon': max(lons) + pad,
    }


# ── Scenario helpers ──────────────────────────────────────────────

def find_scenario(df: pd.DataFrame, origin: str, destination: str):
    m = ((df["origin_name"] == origin) &
         (df["destination_name"] == destination) &
         (df["status"] == "validated"))
    r = df[m]
    return None if r.empty else r.iloc[0]

def get_stop_by_id(df: pd.DataFrame, sid: str):
    r = df[df["stop_id"] == sid]
    return None if r.empty else r.iloc[0]

def get_poi_by_id(df: pd.DataFrame, pid: str):
    r = df[df["poi_id"] == pid]
    return None if r.empty else r.iloc[0]

def get_journey_stops(scenario: pd.Series, stops_df: pd.DataFrame) -> list:
    lines   = [l.strip() for l in str(scenario["line_ids"]).split(",")]
    dep_id  = str(scenario["departure_stop_id"]).strip()
    arr_id  = str(scenario["arrival_stop_id"]).strip()
    
    # ID de descente de la ligne 1
    raw_tf  = scenario.get("transfer_stop_id", "")
    tf_id   = "" if pd.isna(raw_tf) else str(raw_tf).strip()
    
    # NOUVEAU : ID de montée de la ligne 2 (s'il existe, sinon on garde l'ancien)
    raw_tf2 = scenario.get("debut_transfer_id", raw_tf)
    tf_id2  = tf_id if pd.isna(raw_tf2) else str(raw_tf2).strip()

    result  = []

    def _segment(line_id, from_id, to_id):
        line_stops = (stops_df[stops_df["line_id"] == line_id]
                      .sort_values("seq")
                      .to_dict("records"))
        f_seq = next((int(s["seq"]) for s in line_stops if s["stop_id"] == from_id), None)
        t_seq = next((int(s["seq"]) for s in line_stops if s["stop_id"] == to_id),   None)
        if f_seq is None or t_seq is None:
            return []
        lo, hi = min(f_seq, t_seq), max(f_seq, t_seq)
        seg = [s for s in line_stops if lo <= int(s["seq"]) <= hi]
        return seg if f_seq <= t_seq else list(reversed(seg))

    if len(lines) == 1:
        result = _segment(lines[0], dep_id, arr_id)
    elif len(lines) == 2 and tf_id:
        seg1 = _segment(lines[0], dep_id, tf_id)
        # NOUVEAU : On utilise tf_id2 pour calculer la ligne 2 !
        seg2 = _segment(lines[1], tf_id2, arr_id) 
        result = seg1 + seg2

    return result


# ── UI constants ──────────────────────────────────────────────────

LINE_COLORS = {
    "T1": "#F38230", "T2": "#FFDB2F", "T3": "#A0522D",
    "T4": "#0078C8", "BW1": "#2E7D32", "BW2": "#388E3C",
}
LINE_LABELS = {
    "T1":  "Tramway T1 · Sidi Moumen ↔ Lissasfa",
    "T2":  "Tramway T2 · Aïn Diab ↔ Sidi Bernoussi",
    "T3":  "Busway T3 · Casa Port ↔ Hay El Wahda",
    "T4":  "Busway T4 · Ligue Arabe ↔ M. Erradi",
    "BW1": "Busway BW1 · Salmia 2 ↔ Omar El Khayam",
    "BW2": "Busway BW2 · Ouled Azzouz ↔ Oulmès",
}

CATEGORY_FA = {
    "museum":     ("university",   "darkred"),
    "historic":   ("fort-awesome", "cadetblue"),
    "mosque":     ("moon-o",       "green"),
    "theatre":    ("music",        "purple"),
    "arts_centre":("paint-brush",  "orange"),
    "attraction": ("map-marker",   "blue"),
    "hotel":      ("bed",          "gray"),
    "viewpoint":  ("eye",          "darkblue"),
}
CATEGORY_FA_UI = {
    "museum":     "fa-university",
    "historic":   "fa-fort-awesome",
    "mosque":     "fa-moon-o",
    "theatre":    "fa-music",
    "arts_centre":"fa-paint-brush",
    "attraction": "fa-map-marker",
    "hotel":      "fa-bed",
    "viewpoint":  "fa-eye",
}
CATEGORY_COLOR = {
    "museum":     "#8B0000",
    "historic":   "#5F9EA0",
    "mosque":     "#2E8B57",
    "theatre":    "#9932CC",
    "arts_centre":"#FF8C00",
    "attraction": "#1565C0",
    "hotel":      "#607D8B",
    "viewpoint":  "#00838F",
}

def step_icon(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ["prendre", "tramway", "busway", "t1", "t2", "t3", "t4", "bw"]):
        return "fa-train"
    if any(k in t for k in ["marcher", "marche", "à pied"]) or ("m" in t and any(c.isdigit() for c in t)):
        return "fa-male"
    if "descendre" in t:
        return "fa-sign-out"
    if "correspondance" in t:
        return "fa-exchange"
    return "fa-info-circle"