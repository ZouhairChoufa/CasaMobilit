# -*- coding: utf-8 -*-
"""
map_utils.py — Map builders
"""
import folium
from folium.plugins import MarkerCluster
import pandas as pd
from load_data import (
    LINE_COLORS, LINE_LABELS,
    CATEGORY_FA, CATEGORY_COLOR, CATEGORY_FA_UI,
    clip_route_segment, get_journey_stops, get_journey_bbox,
)

CASA_CENTER = [33.5892, -7.6034]


# ── Shared helpers ────────────────────────────────────────────────

def _stop_color(mode: str) -> str:
    return {"tramway": "#F38230", "busway": "#0078C8"}.get(mode, "#555")


def _line_weight(mode: str) -> int:
    return 6 if mode == "tramway" else 5


def _line_dash(mode: str):
    return None if mode == "tramway" else "10 5"


def _popup_stop(s: dict) -> str:
    badge = ""
    if str(s.get("is_interchange", "FALSE")) == "TRUE":
        badge = ('<br><i class="fa fa-exchange" style="color:#F38230"></i>'
                 ' Nœud de correspondance')
    return (
        f'<div style="font-family:sans-serif;font-size:12px;min-width:160px">'
        f'<b style="color:#1A3A5C">{s["stop_name"]}</b><br>'
        f'<i class="fa fa-train" style="color:{_stop_color(s["mode"])}"></i>'
        f' Ligne <b>{s["line_id"]}</b> · {s["mode"].title()}<br>'
        f'<i class="fa fa-map-marker" style="color:#94A3B8"></i> {s["district"]}'
        f'{badge}</div>'
    )


def _popup_poi(p) -> str:
    cat   = p.get("category", "attraction")
    fa_ui = CATEGORY_FA_UI.get(cat, "fa-map-marker")
    color = CATEGORY_COLOR.get(cat, "#1565C0")
    desc  = str(p.get("short_description", ""))
    desc_s = desc[:140] + "…" if len(desc) > 140 else desc
    walk  = p.get("walking_min_from_stop", "")
    whtml = (f'<br><i class="fa fa-male" style="color:#2E7D32"></i>'
             f' <b>{walk} min</b> depuis l\'arrêt' if walk else "")
    return (
        f'<div style="font-family:sans-serif;font-size:12px;min-width:200px">'
        f'<b style="font-size:13px;color:#1A3A5C">'
        f'<i class="fa {fa_ui}" style="color:{color}"></i> {p["poi_name"]}</b><br>'
        f'<span style="background:{color};color:white;padding:1px 7px;'
        f'border-radius:10px;font-size:10px">{cat.title()}</span>'
        f' · {p.get("area", "Casablanca")}<br>'
        f'<hr style="margin:5px 0;border-color:#eee">'
        f'{desc_s}{whtml}</div>'
    )


def _get_line_coords(route_id: str, transport_geo: dict) -> list:
    for feat in transport_geo.get("features", []):
        if feat["properties"].get("route_id") == route_id:
            return feat["geometry"]["coordinates"]
    return []


# ── GENERAL MAP — full network ─────────────────────────────────────

def build_general_map(transport_geo, stops_df, poi_df,
                      show_stops=True, show_poi=True):
    m = folium.Map(location=CASA_CENTER, zoom_start=12,
                   tiles="OpenStreetMap", prefer_canvas=True)

    # All lines
    line_fg = folium.FeatureGroup(name="Lignes", show=True)
    for feat in transport_geo.get("features", []):
        p  = feat["properties"]
        ll = [[c[1], c[0]] for c in feat["geometry"]["coordinates"]]
        lid   = p.get("route_id", "")
        color = LINE_COLORS.get(lid, "#888")
        mode  = p.get("mode", "")
        folium.PolyLine(ll, color="white",
                        weight=_line_weight(mode) + 4, opacity=0.45).add_to(line_fg)
        folium.PolyLine(ll, color=color,
                        weight=_line_weight(mode), opacity=1.0,
                        smooth_factor=1, dash_array=_line_dash(mode),
                        tooltip=LINE_LABELS.get(lid, lid)).add_to(line_fg)
    line_fg.add_to(m)

    # Stops
    if show_stops:
        stop_fg = folium.FeatureGroup(name="Arrêts", show=True)
        for _, s in stops_df.iterrows():
            ichange = str(s.get("is_interchange", "FALSE")) == "TRUE"
            color   = _stop_color(s["mode"])
            folium.CircleMarker(
                [s["latitude"], s["longitude"]],
                radius=7 if ichange else 4,
                color=color, fill=True, fill_color="white",
                fill_opacity=1.0, weight=2.5,
                tooltip=s["stop_name"],
                popup=folium.Popup(_popup_stop(dict(s)), max_width=230),
            ).add_to(stop_fg)
            if ichange:
                folium.CircleMarker(
                    [s["latitude"], s["longitude"]],
                    radius=11, color=color,
                    fill=False, weight=1.5, opacity=0.4,
                ).add_to(stop_fg)
        stop_fg.add_to(m)

    # POI
    if show_poi:
        poi_fg  = folium.FeatureGroup(name="POI", show=True)
        cluster = MarkerCluster(
            options={"maxClusterRadius": 40, "disableClusteringAtZoom": 14}
        ).add_to(poi_fg)
        for _, p in poi_df.iterrows():
            cat = p.get("category", "attraction")
            fa_name, fa_col = CATEGORY_FA.get(cat, ("map-marker", "blue"))
            folium.Marker(
                [p["latitude"], p["longitude"]],
                tooltip=p["poi_name"],
                popup=folium.Popup(_popup_poi(p), max_width=260),
                icon=folium.Icon(color=fa_col, icon=fa_name, prefix="fa"),
            ).add_to(cluster)
        poi_fg.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)

    legend = """
            <div style='position:fixed;bottom:28px;left:12px;z-index:9999;background:var(--background-color);
                        padding:13px 17px;border-radius:10px;
                        box-shadow:0 3px 14px rgba(0,0,0,0.22);font-family:sans-serif;
                        font-size:12px;line-height:2.0;min-width:240px;
                        border-left:4px solid #F38230'>
                <b style='font-size:13px;color:#1A3A5C'>
                    <i class='fa fa-map'></i>&nbsp;Réseau</b><br>
                <span style='color:#F38230;font-weight:900'>━━</span> T1 Tramway · Sidi Moumen ↔ Lissasfa<br>
                <span style='color:#FFDB2F;font-weight:900'>━━</span> T2 Tramway · Aïn Diab ↔ Sidi Bernoussi<br>
                <span style='color:#A0522D;font-weight:900'>╌╌</span> T3 Busway · Casa Port ↔ Hay El Wahda<br>
                <span style='color:#0078C8;font-weight:900'>╌╌</span> T4 Busway · Ligue Arabe ↔ M. Erradi<br>
                <span style='color:#2E7D32;font-weight:900'>╌╌</span> BW1 / BW2 Busway
                <hr style='margin:6px 0'>
                <i class='fa fa-circle' style='color:#F38230'></i> Arrêt &nbsp;
                <i class='fa fa-circle-o' style='color:#F38230'></i> Correspondance &nbsp;
                <i class='fa fa-map-marker' style='color:#1565C0'></i> POI
            </div>"""
    m.get_root().html.add_child(folium.Element(legend))
    return m


# ── SCENARIO MAP — shows ONLY the journey segment ─────────────────

def build_scenario_map(scenario, stops_df, poi_df, transport_geo):
    """
    FILTERED: draws ONLY the clipped route segments used in this journey.
    - One coloured PolyLine per line used (clipped between dep/transfer/arr stops)
    - Green dashed line for walking (arrival stop → POI)
    - Markers: green=dep, orange=transfer, blue=arr, red=POI
    - Auto-zooms to fit the journey
    """
    dep_id = str(scenario.get("departure_stop_id", scenario.get("origine_stop_id", ""))).strip()
    arr_id = str(scenario.get("arrival_stop_id", scenario.get("destination_id", ""))).strip()
    
    # ID de descente
    raw_tf  = scenario.get("transfer_stop_id", scenario.get("transfer_id", ""))
    tf_id   = "" if pd.isna(raw_tf) else str(raw_tf).strip()
    
    # ID de montée (si inexistant, prend la valeur de tf_id)
    raw_tf2 = scenario.get("debut_transfer_id", tf_id)
    tf_id2  = tf_id if pd.isna(raw_tf2) else str(raw_tf2).strip()
    
    lines  = [l.strip() for l in str(scenario["line_ids"]).split(",")]

    dep_row = stops_df[stops_df["stop_id"] == dep_id]
    arr_row = stops_df[stops_df["stop_id"] == arr_id]
    poi_row = poi_df[poi_df["poi_id"] == scenario.get("destination_poi_id", scenario.get("destination_id", ""))]
    
    tf_row  = stops_df[stops_df["stop_id"] == tf_id] if tf_id and tf_id != "nan" else None
    tf_row2 = stops_df[stops_df["stop_id"] == tf_id2] if tf_id2 and tf_id2 != "nan" else tf_row

    # ── Auto-zoom: fit to journey bbox ───────────────────────────
    journey_stops = get_journey_stops(scenario, stops_df)
    poi_for_bbox  = poi_row.iloc[0] if not poi_row.empty else None
    bbox = get_journey_bbox(journey_stops, poi_for_bbox)

    center_lat = (bbox["min_lat"] + bbox["max_lat"]) / 2
    center_lon = (bbox["min_lon"] + bbox["max_lon"]) / 2
    span = max(bbox["max_lat"] - bbox["min_lat"],
            bbox["max_lon"] - bbox["min_lon"])
    zoom = 13 if span < 0.04 else (12 if span < 0.08 else 11)

    m = folium.Map(location=[center_lat, center_lon],
                zoom_start=zoom, tiles="OpenStreetMap",
                prefer_canvas=True)

    # ── Draw clipped route segment(s) ───────────────────────────
    color1 = LINE_COLORS.get(lines[0], "#888")
    mode1  = (stops_df[stops_df["line_id"] == lines[0]]["mode"].iloc[0]
                if not stops_df[stops_df["line_id"] == lines[0]].empty else "tramway")

    if len(lines) == 1:
        # Single line: dep → arr
        line_coords = _get_line_coords(lines[0], transport_geo)
        if line_coords and not dep_row.empty and not arr_row.empty:
            seg = clip_route_segment(line_coords, dep_row.iloc[0], arr_row.iloc[0])
            latlons = [[c[1], c[0]] for c in seg]
            # Shadow
            folium.PolyLine(latlons, color="white",
                            weight=_line_weight(mode1) + 6, opacity=0.6).add_to(m)
            # Route
            folium.PolyLine(latlons, color=color1,
                            weight=_line_weight(mode1) + 2, opacity=1.0,
                            dash_array=_line_dash(mode1),
                            tooltip=LINE_LABELS.get(lines[0], lines[0])).add_to(m)
        else:
            # Fallback: straight line dep → arr
            if not dep_row.empty and not arr_row.empty:
                d, a = dep_row.iloc[0], arr_row.iloc[0]
                folium.PolyLine(
                    [[d["latitude"], d["longitude"]], [a["latitude"], a["longitude"]]],
                    color=color1, weight=5, opacity=0.9,
                    dash_array=_line_dash(mode1),
                    tooltip=LINE_LABELS.get(lines[0], lines[0])
                ).add_to(m)

    elif len(lines) == 2 and tf_id and tf_id != "nan":
        # Two lines: dep → transfer (line1), transfer2 → arr (line2)
        color2 = LINE_COLORS.get(lines[1], "#888")
        mode2  = (stops_df[stops_df["line_id"] == lines[1]]["mode"].iloc[0]
                   if not stops_df[stops_df["line_id"] == lines[1]].empty else "tramway")

        if tf_row is not None and not tf_row.empty:
            tf_s = tf_row.iloc[0]

            # Segment 1: dep → transfer on line[0]
            lc1 = _get_line_coords(lines[0], transport_geo)
            if lc1 and not dep_row.empty:
                seg1 = clip_route_segment(lc1, dep_row.iloc[0], tf_s)
                ll1  = [[c[1], c[0]] for c in seg1]
                folium.PolyLine(ll1, color="white",
                                weight=_line_weight(mode1) + 6, opacity=0.6).add_to(m)
                folium.PolyLine(ll1, color=color1,
                                weight=_line_weight(mode1) + 2, opacity=1.0,
                                dash_array=_line_dash(mode1),
                                tooltip=f"{LINE_LABELS.get(lines[0],lines[0])} (partie 1)").add_to(m)

            # Segment 2: transfer2 → arr on line[1]
            if tf_row2 is not None and not tf_row2.empty:
                tf_s2 = tf_row2.iloc[0]
                lc2 = _get_line_coords(lines[1], transport_geo)
                if lc2 and not arr_row.empty:
                    seg2 = clip_route_segment(lc2, tf_s2, arr_row.iloc[0])
                    ll2  = [[c[1], c[0]] for c in seg2]
                    folium.PolyLine(ll2, color="white",
                                    weight=_line_weight(mode2) + 6, opacity=0.6).add_to(m)
                    folium.PolyLine(ll2, color=color2,
                                    weight=_line_weight(mode2) + 2, opacity=1.0,
                                    dash_array=_line_dash(mode2),
                                    tooltip=f"{LINE_LABELS.get(lines[1],lines[1])} (partie 2)").add_to(m)

    # ── Journey stops (intermediate only, small circles) ─────────
    special_ids = {dep_id, arr_id, tf_id, tf_id2}
    for s in journey_stops:
        if s["stop_id"] in special_ids:
            continue
        color = _stop_color(s["mode"])
        folium.CircleMarker(
            [s["latitude"], s["longitude"]],
            radius=5, color=color,
            fill=True, fill_color="white",
            fill_opacity=1.0, weight=2.5,
            tooltip=s["stop_name"],
            popup=folium.Popup(_popup_stop(s), max_width=220),
        ).add_to(m)

    # ── Departure marker — green ──────────────────────────────────
    if not dep_row.empty:
        s = dep_row.iloc[0]
        folium.Marker(
            [s["latitude"], s["longitude"]],
            tooltip=f'DÉPART : {s["stop_name"]}',
            popup=folium.Popup(
                f'<div style="font-size:12px">'
                f'<b style="color:#27ae60"><i class="fa fa-play"></i> Point de départ</b><br>'
                f'<b>{s["stop_name"]}</b><br>'
                f'Ligne {s["line_id"]} · {s["district"]}</div>',
                max_width=200),
            icon=folium.Icon(color="green", icon="play", prefix="fa"),
        ).add_to(m)

    # ── Transfer marker — orange (Descente) ────────────────────────
    if tf_row is not None and not tf_row.empty:
        s = tf_row.iloc[0]
        folium.Marker(
            [s["latitude"], s["longitude"]],
            tooltip=f'CORRESPONDANCE (Descente) : {s["stop_name"]}',
            popup=folium.Popup(
                f'<div style="font-size:12px">'
                f'<b style="color:#e67e22"><i class="fa fa-exchange"></i> Correspondance</b><br>'
                f'<b>{s["stop_name"]}</b><br>{s["district"]}</div>',
                max_width=200),
            icon=folium.Icon(color="orange", icon="exchange", prefix="fa"),
        ).add_to(m)

    # ── Transfer marker — orange (Montée si différente) ────────────
    if tf_row2 is not None and not tf_row2.empty and tf_id != tf_id2:
        s2 = tf_row2.iloc[0]
        folium.Marker(
            [s2["latitude"], s2["longitude"]],
            tooltip=f'CORRESPONDANCE (Montée) : {s2["stop_name"]}',
            popup=folium.Popup(
                f'<div style="font-size:12px">'
                f'<b style="color:#e67e22"><i class="fa fa-exchange"></i> Correspondance</b><br>'
                f'<b>{s2["stop_name"]}</b><br>{s2["district"]}</div>',
                max_width=200),
            icon=folium.Icon(color="orange", icon="exchange", prefix="fa"),
        ).add_to(m)

    # ── Arrival marker — blue ─────────────────────────────────────
    if not arr_row.empty:
        s = arr_row.iloc[0]
        folium.Marker(
            [s["latitude"], s["longitude"]],
            tooltip=f'ARRIVÉE : {s["stop_name"]}',
            popup=folium.Popup(
                f'<div style="font-size:12px">'
                f'<b style="color:#2980b9"><i class="fa fa-flag-checkered"></i> Arrêt d\'arrivée</b><br>'
                f'<b>{s["stop_name"]}</b><br>'
                f'Ligne {s["line_id"]} · {s["district"]}</div>',
                max_width=200),
            icon=folium.Icon(color="blue", icon="flag-checkered", prefix="fa"),
        ).add_to(m)

    # ── Destination POI — red + walking line ─────────────────────
    if not poi_row.empty:
        p   = poi_row.iloc[0]
        cat = p.get("category", "attraction")
        fa_name, _ = CATEGORY_FA.get(cat, ("map-marker", "red"))
        folium.Marker(
            [p["latitude"], p["longitude"]],
            tooltip=p["poi_name"],
            popup=folium.Popup(_popup_poi(p), max_width=270),
            icon=folium.Icon(color="red", icon=fa_name, prefix="fa"),
        ).add_to(m)

        # Walking dashed line: arr_stop → POI
        if not arr_row.empty:
            arr_s = arr_row.iloc[0]
            arr_lat, arr_lon = float(arr_s["latitude"]), float(arr_s["longitude"])
            poi_lat, poi_lon = float(p["latitude"]), float(p["longitude"])

            folium.PolyLine(
                [[arr_lat, arr_lon], [poi_lat, poi_lon]],
                color="#27ae60", weight=3, opacity=0.9,
                dash_array="6 10",
                tooltip=f'Marche ~{scenario.get("walking_distance_m", "???")} m à pied',
            ).add_to(m)

            # Walking icon at midpoint
            mid_lat = (arr_lat + poi_lat) / 2
            mid_lon = (arr_lon + poi_lon) / 2
            folium.Marker(
                [mid_lat, mid_lon],
                icon=folium.DivIcon(
                    html='<div style="font-size:20px;filter:drop-shadow(1px 1px 2px rgba(0,0,0,.4))">🚶</div>',
                    icon_size=(28, 28), icon_anchor=(14, 14),
                ),
                tooltip=f'{scenario.get("walking_distance_m", "???")} m à pied',
            ).add_to(m)

    # ── Info overlay (top-right corner) ──────────────────────────
    c = LINE_COLORS.get(lines[0], "#F38230")
    info_html = f"""
    <div style='position:fixed;top:76px;right:14px;z-index:9999;background:white;
                padding:14px 18px;border-radius:10px;font-family:sans-serif;
                box-shadow:0 3px 14px rgba(0,0,0,0.22);font-size:12px;
                max-width:215px;border-top:4px solid {c}'>
    <b style='font-size:13px;color:#1A3A5C'>
        <i class='fa fa-map-signs' style='color:{c}'></i>&nbsp;{scenario['scenario_id']}
    </b><br>
    <span style='color:#64748B;font-size:11px;line-height:1.7'>
        <i class='fa fa-map-marker' style='color:#27ae60'></i> {scenario['origin_name']}<br>
        <i class='fa fa-arrow-down' style='color:#ccc'></i><br>
        <i class='fa fa-star' style='color:{c}'></i> {scenario['destination_name']}
    </span>
    <hr style='margin:8px 0;border-color:#eee'>
    <table style='width:100%;font-size:12px;border-collapse:collapse'>
        <tr>
        <td><i class='fa fa-clock-o' style='color:{c}'></i></td>
        <td><b>{scenario.get('estimated_time_min', '?')} min</b></td>
        <td><i class='fa fa-tag' style='color:#27ae60'></i></td>
        <td><b>{scenario.get('estimated_cost_mad', '?')} MAD</b></td>
        </tr>
        <tr>
        <td><i class='fa fa-exchange' style='color:#e67e22'></i></td>
        <td>{scenario.get('correspondences', '?')} corresp.</td>
        <td><i class='fa fa-male' style='color:#8e44ad'></i></td>
        <td>{scenario.get('walking_distance_m', '?')} m</td>
        </tr>
        <tr><td colspan='4' style='padding-top:5px'>
        <i class='fa fa-train' style='color:{c}'></i>
        Ligne(s) : <b>{scenario['line_ids']}</b>
        </td></tr>
    </table>
    </div>"""
    m.get_root().html.add_child(folium.Element(info_html))
    return m