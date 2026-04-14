# -*- coding: utf-8 -*-
"""
test_logic.py — Validation des scénarios d'itinéraires
Usage: python app/test_logic.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from load_data import load_stops, load_scenarios, get_journey_stops


def run_test(origin: str, destination: str) -> None:
    print(f"\n{'='*50}")
    print(f"TEST : {origin} → {destination}")
    print("=" * 50)

    try:
        stops_df = load_stops()
        scenarios_df = load_scenarios()
    except Exception as e:
        print(f"[ERREUR] Chargement des données : {e}")
        return

    matching = scenarios_df[
        (scenarios_df["origin_name"] == origin) &
        (scenarios_df["destination_name"] == destination)
    ]

    if matching.empty:
        print("[ÉCHEC] Scénario introuvable dans scenarios.csv")
        return

    scenario = matching.iloc[0]
    print(f"[OK] Scénario : {scenario['scenario_id']}")
    print(f"     Départ       : {scenario.get('departure_stop_id', 'N/A')}")
    print(f"     Correspondance: {scenario.get('transfer_stop_id', 'N/A')}")
    print(f"     Arrivée      : {scenario.get('arrival_stop_id', 'N/A')}")
    print(f"     Lignes       : {scenario['line_ids']}")

    stops_seq = get_journey_stops(scenario, stops_df)

    if not stops_seq:
        print("[ÉCHEC] Séquence vide — vérifiez les IDs dans stops.csv")
        return

    print(f"\n[OK] {len(stops_seq)} arrêts générés :")
    for i, stop in enumerate(stops_seq):
        sid = stop.get("stop_id", "N/A")
        name = stop.get("stop_name", "Inconnu")
        if i == 0:
            prefix = "🟢 Départ"
        elif sid == str(scenario.get("transfer_stop_id", "")):
            prefix = "🔄 CORRESPONDANCE"
        elif i == len(stops_seq) - 1:
            prefix = "🔴 Arrivée"
        else:
            prefix = "│ "
        print(f"  {prefix} : {name} ({sid})")

    print(f"\n{'='*50}\n")


if __name__ == "__main__":
    run_test("Ain Diab Plage - Terminus", "Mosquée Hassan II")
    run_test("Place Mohammed V", "Quartier Habous")
    run_test("Parc de la Ligue Arabe", "Villa des Arts")
