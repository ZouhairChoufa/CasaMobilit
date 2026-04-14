# -*- coding: utf-8 -*-
"""
app.py — Géoportail Smart Mobility Casablanca PoC V1
Run: streamlit run app/app.py
"""
import re
import sys
import base64
from pathlib import Path
from collections import Counter

import streamlit as st
from streamlit_folium import st_folium
from PIL import Image

_APP_DIR = Path(__file__).parent
sys.path.insert(0, str(_APP_DIR))

from load_data import (
    load_stops, load_routes, load_scenarios, load_poi,
    load_transport_geojson, find_scenario, get_poi_by_id,
    LINE_COLORS, CATEGORY_FA_UI, CATEGORY_COLOR, step_icon,
)
from map_utils import build_general_map, build_scenario_map


def get_base64_image(image_path: Path) -> str:
    return base64.b64encode(image_path.read_bytes()).decode()


def mcard(col, ico: str, val: str, lbl: str, acc: str) -> None:
    col.markdown(
        f'<div class="metric-card" style="--acc:{acc}">'
        f'<i class="fa {ico}"></i>'
        f'<div class="metric-val">{val}</div>'
        f'<div class="metric-lbl">{lbl}</div></div>',
        unsafe_allow_html=True)


logo = Image.open(_APP_DIR / "um6p_logo.png")
st.set_page_config(
    page_title="CasaMobilité — Géoportail,  STRATÉGIES DES SMART CITIES EN AFRIQUE",
    page_icon=logo,
    layout="wide",
    initial_sidebar_state="expanded",
)

_CSS_PATH = Path(__file__).parent / "style.css"
_css = _CSS_PATH.read_text(encoding="utf-8")
st.markdown(
    '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">',
    unsafe_allow_html=True,
)
st.markdown(f"<style>{_css}</style>", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────
stops_df      = load_stops()
routes_df     = load_routes()
scenarios_df  = load_scenarios()
poi_df        = load_poi()
transport_geo = load_transport_geojson()

# ── SIDEBAR ───────────────────────────────────────────────────────
with st.sidebar:
    img_base64 = get_base64_image(_APP_DIR / "um6p_logo.png")

    st.markdown(
        f"""
        <div style="text-align: center; margin-bottom: 10px;">
            <a href="." target="_self" style="text-decoration: none; color: inherit; display: inline-block; cursor: pointer;">
                <img src="data:image/png;base64,{img_base64}" style="width: 55%; margin: 0 auto 10px auto; display: block;">
                <div style="font-size: 22px; font-weight: 800; color: var(--text-color);">CasaMobilité</div>
                <div style="font-size: 11px; color: #2563EB; font-weight: 700; margin-top: 3px;">
                    Géoportail Smart Mobility<br>STRATÉGIES DES SMART CITIES EN AFRIQUE
                </div>
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # La ligne de séparation grise
    st.markdown("<hr style='border-color:var(--secondary-background-color);margin:0px 0 10px'>", unsafe_allow_html=True)
    
    

    ORIGINS = ["Ain Diab Plage - Terminus", "Casa Port - Terminus", "Place Mohammed V", 
            "Parc de la Ligue Arabe", "Casa Voyageurs", "Sidi Moumen", "Sidi Maârouf"]
    origin = st.selectbox("Point de départ", ORIGINS, format_func=lambda x: f"▶  {x}")

    sc_dests  = scenarios_df["destination_name"].tolist() if not scenarios_df.empty else []
    all_dests = sc_dests + [n for n in poi_df["poi_name"].tolist() if n not in sc_dests]
    destination = st.selectbox("Destination touristique", all_dests, format_func=lambda x: f"★  {x}")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    go = st.button("  Voir l'itinéraire  ›", use_container_width=True)

    st.markdown("<hr style='border-color:var(--secondary-background-color);margin:14px 0'>", unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:12px;font-weight:700;color:#2563EB;margin-bottom:8px">'
        '<i class="fa fa-th-large"></i>&nbsp; COUCHES CARTE</div>',
        unsafe_allow_html=True,
    )
    show_stops = st.checkbox("Afficher les arrêts", value=True)
    show_poi   = st.checkbox("Afficher les POI",    value=True)

    st.markdown("<hr style='border-color:var(--secondary-background-color);margin:14px 0'>", unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:12px;font-weight:700;color:#2563EB;margin-bottom:10px">'
        '<i class="fa fa-bar-chart"></i>&nbsp; RÉSEAU EN CHIFFRES</div>',
        unsafe_allow_html=True,
    )
    for ico, col, txt in [
        ("fa-train",      "#F38230", f"{len(stops_df[stops_df['mode']=='tramway'])} arrêts tramway"),
        ("fa-bus",        "#0078C8", f"{len(stops_df[stops_df['mode']=='busway'])} arrêts busway"),
        ("fa-map-marker", "#F38230", f"{len(poi_df)} points d'intérêt"),
        ("fa-road",       "#27ae60", f"{len(routes_df)} lignes actives"),
        ("fa-bullseye",   "#e67e22", f"{len(scenarios_df)} scénarios V1"),
    ]:
        st.markdown(
            f'<div class="stat-row">'
            f'<i class="fa {ico}" style="color:{col};width:16px;text-align:center"></i>'
            f'<span>{txt}</span></div>',
            unsafe_allow_html=True,
        )
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:10px;color:var(--text-color);opacity:0.6;text-align:center;line-height:1.7">'
        '<i class="fa fa-database"></i> Source : OSM Casatramway + Casabusway<br>'
        '<i class="fa fa-graduation-cap"></i>STRATÉGIES DES SMART CITIES EN AFRIQUE · 2026</div>',
        unsafe_allow_html=True,
    )

# ── HEADER ────────────────────────────────────────────────────────
st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
col_logo, col_texte = st.columns([1, 7])

with col_logo:
    # L'image est remplacée par l'icône Font Awesome
    st.markdown(
        '<div style="text-align:center; margin-top: 5px;">'
        '<i class="fa fa-map" style="font-size: 55px; color: #F38230;"></i>'        '</div>',
        unsafe_allow_html=True
    )

with col_texte:
    st.markdown(
        '<div>'
        '<div style="font-size:26px;font-weight:800;color:var(--text-color);line-height:1.5; padding-top:5px;">'
        'CasaMobilité — Géoportail</div>'
        '<div style="font-size:16px;color:#2563EB;font-weight:700;margin-top:2px;text-transform:uppercase;">'
        'STRATÉGIES DES SMART CITIES EN AFRIQUE</div>'
        '<div style="font-size:13px;color:var(--text-color);opacity:0.7;margin-top:8px">'
        '<i class="fa fa-train"></i>&nbsp;Transport public'
        '&nbsp;·&nbsp;<i class="fa fa-map-marker"></i>&nbsp;Points d\'intérêt touristiques'
        '&nbsp;·&nbsp;<i class="fa fa-road"></i>&nbsp;Itinéraires urbains'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)
# ── SCENARIO RESULT ───────────────────────────────────────────────
if go:
    scenario = find_scenario(scenarios_df, origin, destination)

    if scenario is not None:
        st.markdown(
            '<div class="sec-hdr"><i class="fa fa-road" style="color:#F38230"></i>'
            '&nbsp;Votre itinéraire</div>', unsafe_allow_html=True)

        # Metrics
        c1, c2, c3, c4 = st.columns(4)
        mcard(c1,"fa-clock-o", f"{scenario.get('estimated_time_min', '?')} min","Durée totale","#F38230")
        mcard(c2,"fa-tag",     f"{scenario.get('estimated_cost_mad', '?')} MAD","Coût total","#27ae60")
        mcard(c3,"fa-exchange",f"{scenario.get('correspondences', '?')}","Correspondance(s)","#e67e22")
        mcard(c4,"fa-male",    f"{scenario.get('walking_distance_m', '?')} m","Marche totale","#8e44ad")

        # Mode pills
        st.markdown(
            '<div style="font-weight:700;font-size:13px;color:var(--text-color);margin:14px 0 6px">'
            '<i class="fa fa-ticket" style="color:#F38230"></i>&nbsp;Modes de transport :</div>',
            unsafe_allow_html=True)
        pills = ""
        modes_string = str(scenario.get("mode_used", scenario.get("modes_used", "")))
        for mode in [m.strip() for m in modes_string.split(",")]:
            if mode=="tramway":
                pills += '<span class="pill pill-tramway"><i class="fa fa-train"></i>&nbsp;Tramway</span> '
            elif mode=="busway":
                pills += '<span class="pill pill-busway"><i class="fa fa-bus"></i>&nbsp;Busway</span> '
            elif mode=="marche":
                pills += '<span class="pill pill-marche"><i class="fa fa-male"></i>&nbsp;Marche</span> '
        for line in [l.strip() for l in str(scenario.get("line_ids", "")).split(",")]:
            c = LINE_COLORS.get(line,"#555")
            pills += (f'<span class="route-badge" style="background:{c}">'
                      f'<i class="fa fa-ticket"></i>&nbsp;Ligne {line}</span>')
        st.markdown(pills, unsafe_allow_html=True)

        # Steps
        st.markdown(
            '<div class="sec-hdr" style="margin-top:20px">'
            '<i class="fa fa-list-ol" style="color:#2563EB"></i>'
            '&nbsp;Étapes du trajet</div>', unsafe_allow_html=True)
        steps = [s.strip().rstrip(".") for s in
                 re.split(r"\s*\d+\.\s+", str(scenario.get("instructions", ""))) if s.strip()]
        for i, step in enumerate(steps, 1):
            ico = step_icon(step)
            st.markdown(
                f'<div class="step">'
                f'<div class="step-num">{i}</div>'
                f'<div class="step-ico"><i class="fa {ico}"></i></div>'
                f'<div class="step-txt">{step}.</div></div>',
                unsafe_allow_html=True)

        # Scenario map
        st.markdown(
            '<div class="sec-hdr"><i class="fa fa-map" style="color:#F38230"></i>'
            "&nbsp;Carte de l'itinéraire</div>", unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:12px;color:var(--text-color);opacity:0.8;margin-bottom:8px">'
            '<i class="fa fa-play" style="color:#27ae60"></i> Départ&nbsp;&nbsp;'
            '<i class="fa fa-exchange" style="color:#e67e22"></i> Correspondance&nbsp;&nbsp;'
            '<i class="fa fa-flag-checkered" style="color:#2980b9"></i> Arrivée&nbsp;&nbsp;'
            '<i class="fa fa-star" style="color:#c0392b"></i> Destination&nbsp;&nbsp;'
            '<span style="color:#27ae60;font-weight:700">- - -</span> Marche'
            '</div>', unsafe_allow_html=True)
        sc_map = build_scenario_map(scenario, stops_df, poi_df, transport_geo)
        st_folium(sc_map, width=None, height=480, returned_objects=[])

        # POI detail
        poi_id_to_find = scenario.get("destination_id", scenario.get("destination_poi_id", ""))
        poi_row = get_poi_by_id(poi_df, poi_id_to_find)
        
        if poi_row is not None:
            cat   = poi_row.get("category","attraction")
            fa_ui = CATEGORY_FA_UI.get(cat,"fa-map-marker")
            color = CATEGORY_COLOR.get(cat,"#1565C0")
            near  = stops_df[stops_df["stop_id"]==str(poi_row.get("nearest_stop_id",""))]
            stop_nm = near.iloc[0]["stop_name"] if not near.empty else "—"
            line_nm = near.iloc[0]["line_id"]   if not near.empty else "—"

            st.markdown(
                '<div class="sec-hdr"><i class="fa fa-info-circle" style="color:#F38230"></i>'
                '&nbsp;Fiche du site</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="poi-card" style="border-top-color:{color}">'
                f'<h3 style="margin:0 0 10px;color:var(--text-color);font-size:19px">'
                f'<i class="fa {fa_ui}" style="color:{color}"></i>&nbsp;{poi_row["poi_name"]}'
                f'</h3>'
                f'<div style="margin-bottom:12px">'
                f'<span class="poi-badge" style="background:{color}"><i class="fa fa-tag"></i>&nbsp;{cat.title()}</span>'
                f'<span class="poi-badge" style="background:var(--secondary-background-color);color:var(--text-color) !important"><i class="fa fa-map-marker"></i>&nbsp;{poi_row.get("area","Casablanca")}</span>'
                f'<span class="poi-badge" style="background:#0078C8"><i class="fa fa-train"></i>&nbsp;Ligne {line_nm} · {stop_nm}</span>'
                f'<span class="poi-badge" style="background:#2E7D32"><i class="fa fa-male"></i>&nbsp;{poi_row.get("walking_min_from_stop","?")} min à pied</span>'
                f'</div>'
                f'<hr style="border-color:var(--secondary-background-color);margin:12px 0">'
                f'<p style="color:var(--text-color);opacity:0.9;font-size:14px;line-height:1.75;margin:0">'
                f'{poi_row.get("short_description","Description non disponible.")}</p>'
                f'<div style="margin-top:14px;font-size:11px;color:var(--text-color);opacity:0.6">'
                f'<i class="fa fa-globe"></i> Coordonnées : {float(poi_row["latitude"]):.4f}°N, {float(poi_row["longitude"]):.4f}°W'
                f'&nbsp;|&nbsp;<i class="fa fa-database"></i> Source : {poi_row.get("source","")}'
                f'</div></div>',
                unsafe_allow_html=True)

    else:
        sc_list = "".join(
            f'<li><i class="fa fa-arrow-right" style="color:#F38230"></i>&nbsp;'
            f'<b>{r["origin_name"]}</b> → <b>{r["destination_name"]}</b></li>'
            for _, r in scenarios_df.iterrows())
        st.markdown(
            f'<div class="no-route">'
            f'<b><i class="fa fa-exclamation-triangle"></i>&nbsp;'
            f'Itinéraire non disponible en V1</b><br><br>'
            f'Le trajet <b>{origin} → {destination}</b> n\'est pas encore préconfiguré.<br>'
            f'<b><i class="fa fa-check-circle" style="color:#27ae60"></i>'
            f' Scénarios disponibles :</b><ul style="margin:6px 0 0 16px">{sc_list}</ul>'
            f'</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        gen_map = build_general_map(transport_geo, stops_df, poi_df, show_stops, show_poi)
        st_folium(gen_map, width=None, height=520, returned_objects=[])

# ── DEFAULT STATE ─────────────────────────────────────────────────
else:
    tab_map, tab_poi, tab_lines, tab_sc = st.tabs([
        "Carte du réseau", "Points d'intérêt",
        "Lignes & Horaires", "Scénarios"
    ])

    with tab_map:
        badges = "".join(
            f'<span class="route-badge" style="background:{c};margin-right:4px">'
            f'<i class="fa fa-circle" style="font-size:8px"></i>&nbsp;{lid}</span>'
            for lid,c in LINE_COLORS.items())
        st.markdown(
            f'<div style="margin-bottom:8px;font-size:13px;color:var(--text-color);opacity:0.8">'
            f'<i class="fa fa-info-circle" style="color:#2563EB"></i>'
            f'&nbsp;Réseau complet — {len(stops_df)} arrêts · {len(poi_df)} POI</div>'
            f'<div style="margin-bottom:10px">{badges}</div>', unsafe_allow_html=True)
        gen_map = build_general_map(transport_geo, stops_df, poi_df, show_stops, show_poi)
        st_folium(gen_map, width=None, height=530, returned_objects=[])

    with tab_poi:
        cats = Counter(poi_df["category"].tolist())
        ca, cb = st.columns([2,1])
        with ca:
            st.markdown(
                f'<div style="font-size:14px;color:var(--text-color);opacity:0.9">'
                f'<i class="fa fa-map-marker" style="color:#F38230"></i>&nbsp;'
                f'<b>{len(poi_df)} points d\'intérêt</b> répertoriés</div>',
                unsafe_allow_html=True)
        with cb:
            cat_f = st.selectbox("Catégorie",["Toutes"]+sorted(cats.keys()),label_visibility="collapsed")
        filtered = poi_df if cat_f=="Toutes" else poi_df[poi_df["category"]==cat_f]
        
        for _, p in filtered.iterrows():
            cat   = p.get("category","attraction")
            fa_ui = CATEGORY_FA_UI.get(cat,"fa-map-marker")
            color = CATEGORY_COLOR.get(cat,"#1565C0")
            near  = stops_df[stops_df["stop_id"]==str(p.get("nearest_stop_id",""))]
            stop_txt = (f"Ligne {near.iloc[0]['line_id']} · {near.iloc[0]['stop_name']}"
                        if not near.empty else "—")
            
            with st.expander(f"{p['poi_name']}  —  {p.get('area','Casablanca')}"):
                c1, c2 = st.columns([2,1])
                with c1:
                    html_poi1 = (
                        f'<div style="font-size:13px;color:var(--text-color);opacity:0.9;line-height:1.7">'
                        f'<i class="fa fa-align-left" style="color:var(--text-color);opacity:0.5"></i>&nbsp;'
                        f'{p.get("short_description","—")}</div>'
                    )
                    st.markdown(html_poi1, unsafe_allow_html=True)
                with c2:
                    html_poi2 = (
                        f'<div style="font-size:12px;line-height:2.0;color:var(--text-color);opacity:0.8">'
                        f'<span class="poi-badge" style="background:{color}">'
                        f'<i class="fa {fa_ui}"></i>&nbsp;{cat.title()}</span><br>'
                        f'<i class="fa fa-map-marker" style="color:var(--text-color);opacity:0.5"></i>&nbsp;{p.get("area","—")}<br>'
                        f'<i class="fa fa-train" style="color:#0078C8"></i>&nbsp;{stop_txt}<br>'
                        f'<i class="fa fa-male" style="color:#2E7D32"></i>&nbsp;'
                        f'{p.get("walking_min_from_stop","?")} min à pied</div>'
                    )
                    st.markdown(html_poi2, unsafe_allow_html=True)

    with tab_lines:
        st.markdown('<div class="sec-hdr"><i class="fa fa-calendar" style="color:#F38230"></i>'
                    '&nbsp;Lignes et horaires officiels</div>', unsafe_allow_html=True)
        for _, r in routes_df.iterrows():
            c = LINE_COLORS.get(r["route_id"],"#888")
            m_ico = "fa-train" if r["mode"]=="tramway" else "fa-bus"
            
            with st.expander(f"Ligne {r['route_id']} — {r['route_name']}"):
                c1, c2, c3 = st.columns(3)
                
                with c1:
                    html_c1 = (
                        f'<div style="font-size:13px;line-height:2.2;color:var(--text-color);opacity:0.9">'
                        f'<i class="fa fa-building" style="color:{c}"></i>&nbsp;<b>Opérateur :</b> {r["operator"]}<br>'
                        f'<i class="fa {m_ico}" style="color:{c}"></i>&nbsp;<b>Mode :</b> {r["mode"].title()}<br>'
                        f'<i class="fa fa-flag" style="color:{c}"></i>&nbsp;<b>Terminus A :</b> {r["terminal_a"]}<br>'
                        f'<i class="fa fa-flag-checkered" style="color:{c}"></i>&nbsp;<b>Terminus B :</b> {r["terminal_b"]}'
                        f'</div>'
                    )
                    st.markdown(html_c1, unsafe_allow_html=True)
                
                with c2:
                    html_c2 = (
                        f'<div style="font-size:13px;line-height:2.2;color:var(--text-color);opacity:0.9">'
                        f'<i class="fa fa-clock-o" style="color:{c}"></i>&nbsp;<b>1er départ A :</b> {r["first_departure_a"]}<br>'
                        f'<i class="fa fa-clock-o" style="color:{c}"></i>&nbsp;<b>Dernier A :</b> {r["last_departure_a"]}<br>'
                        f'<i class="fa fa-clock-o" style="color:{c}"></i>&nbsp;<b>1er départ B :</b> {r["first_departure_b"]}<br>'
                        f'<i class="fa fa-clock-o" style="color:{c}"></i>&nbsp;<b>Dernier B :</b> {r["last_departure_b"]}'
                        f'</div>'
                    )
                    st.markdown(html_c2, unsafe_allow_html=True)
                
                with c3:
                    html_c3 = (
                        f'<div style="font-size:13px;line-height:2.2;color:var(--text-color);opacity:0.9">'
                        f'<i class="fa fa-bolt" style="color:#F38230"></i>&nbsp;<b>Pointe :</b> {r["peak_frequency_min"]} min<br>'
                        f'<i class="fa fa-clock-o" style="color:#e67e22"></i>&nbsp;<b>Normale :</b> {r["offpeak_frequency_min"]} min<br>'
                        f'<i class="fa fa-calendar" style="color:#8e44ad"></i>&nbsp;<b>Weekend :</b> {r["weekend_frequency_min"]} min<br>'
                        f'<i class="fa fa-tag" style="color:#27ae60"></i>&nbsp;<b>Tarif :</b> {r["fare_mad"]} MAD'
                        f'</div>'
                    )
                    st.markdown(html_c3, unsafe_allow_html=True)
                    
                html_caption = f'<p style="font-size: 0.8rem; color: #888;"><i class="fa fa-file"></i> Source : {r["source"]}</p>'
                st.markdown(html_caption, unsafe_allow_html=True)

    with tab_sc:
        st.markdown('<div class="sec-hdr"><i class="fa fa-map-signs" style="color:#F38230"></i>'
                    '&nbsp;Scénarios de démonstration V1</div>', unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:13px;color:var(--text-color);opacity:0.7;margin-bottom:16px">'
            '<i class="fa fa-info-circle" style="color:#2563EB"></i>'
            '&nbsp;Sélectionnez un trajet dans la barre latérale.</div>',
            unsafe_allow_html=True)
        for _, sc in scenarios_df.iterrows():
            lines = [l.strip() for l in str(sc["line_ids"]).split(",")]
            c     = LINE_COLORS.get(lines[0],"#F38230")
            bdgs  = "".join(
                f'<span class="route-badge" style="background:{LINE_COLORS.get(l,"#555")}">'
                f'<i class="fa fa-train"></i>&nbsp;{l}</span>' for l in lines)
            st.markdown(
                f'<div class="sc-card" style="--sc-col:{c}">'
                f'<div style="font-size:10px;font-weight:700;color:var(--text-color);opacity:0.6;'
                f'text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">'
                f'<i class="fa fa-bullseye" style="color:{c}"></i>&nbsp;{sc.get("scenario_id", "")}</div>'
                f'<div style="font-size:17px;font-weight:700;color:var(--text-color);margin-bottom:6px">'
                f'<i class="fa fa-map-marker" style="color:#27ae60"></i>&nbsp;{sc.get("origin_name", "")}'
                f'&nbsp;<i class="fa fa-long-arrow-right" style="color:var(--text-color);opacity:0.5"></i>&nbsp;'
                f'<i class="fa fa-star" style="color:{c}"></i>&nbsp;{sc.get("destination_name", "")}'
                f'</div><div style="margin-bottom:8px">{bdgs}</div>'
                f'<div class="sc-meta">'
                f'<span><i class="fa fa-clock-o" style="color:{c}"></i>&nbsp;<b>{sc.get("estimated_time_min", "?")} min</b></span>'
                f'<span><i class="fa fa-tag" style="color:#27ae60"></i>&nbsp;<b>{sc.get("estimated_cost_mad", "?")} MAD</b></span>'
                f'<span><i class="fa fa-exchange" style="color:#e67e22"></i>&nbsp;{sc.get("correspondences", "?")} correspondance(s)</span>'
                f'<span><i class="fa fa-male" style="color:#8e44ad"></i>&nbsp;{sc.get("walking_distance_m", "?")} m</span>'
                f'</div></div>', unsafe_allow_html=True)