import sys
from pathlib import Path

# Ajouter le dossier parent au chemin d'importation pour pouvoir importer load_data
sys.path.insert(0, str(Path(__file__).parent))

from load_data import (
    load_stops, load_scenarios, load_transport_geojson,
    get_journey_stops
)

def run_terminal_test():
    print("\n" + "="*50)
    print("TEST DU SCÉNARIO SC01")
    print("="*50)

    # 1. Chargement des données
    print("[1] Chargement des données...")
    try:
        print("  -> Chargement des stations (stops)...")
        stops_df = load_stops()
        print("===============")
        print("  -> Chargement des scénarios...")
        scenarios_df = load_scenarios()
        print("  -> Chargement de transport.geojson...")
        transport_geo = load_transport_geojson()
        print("Données chargées avec succès.")
    except Exception as e:
        print(f"Erreur lors du chargement des données: {e}")
        return

    # 2. Configuration du SC01
    # Noms exacts extraits de votre fichier scenarios.csv
    TEST_ORIGIN = "Ain Diab Plage - Terminus"
    TEST_DESTINATION = "Mosquée Hassan II"
    
    print(f"\n[2] Recherche de l'itinéraire : '{TEST_ORIGIN}' ➔ '{TEST_DESTINATION}'...")
    
    matching_scenarios = scenarios_df[
        (scenarios_df["origin_name"] == TEST_ORIGIN) & 
        (scenarios_df["destination_name"] == TEST_DESTINATION)
    ]
    
    if matching_scenarios.empty:
        print("Scénario introuvable. Vérifiez les noms dans votre fichier CSV.")
        return

    scenario = matching_scenarios.iloc[0]
    print(f"Scénario trouvé : {scenario['scenario_id']}")
    print(f" --> Départ : {scenario.get('departure_stop_id', 'N/A')} | Correspondance : {scenario.get('transfer_stop_id', 'N/A')} | Arrivée : {scenario.get('arrival_stop_id', 'N/A')}")
    print(f" ----- Lignes utilisées : {scenario['line_ids']}")

    # 3. Test Séquence d'arrêts (Stops)
    print("\n[3] Test du calcul de la séquence d'arrêts...")
    
    stops_sequence = get_journey_stops(scenario, stops_df)
    
    if not stops_sequence:
        print("ÉCHEC : La séquence est vide. Vérifiez que les IDs existent dans stops.csv (ou stops.geojson).")
    else:
        print(f"SUCCÈS : {len(stops_sequence)} arrêts générés.")
        print("  --- Trajet détaillé ---")
        
        for i, stop in enumerate(stops_sequence):
            stop_id = stop.get('stop_id', 'N/A')
            stop_name = stop.get('stop_name', 'Inconnu')
            
            # Si c'est le départ
            if i == 0:
                print(f"  🟢 Départ : {stop_name} ({stop_id})")
            # Si c'est la station où l'on fait le transfert
            elif stop_id == scenario.get('transfer_stop_id'):
                print(f"  🔄 CORRESPONDANCE : {stop_name} ({stop_id})")
            # Si c'est l'arrivée (le dernier arrêt de la liste)
            elif i == len(stops_sequence) - 1:
                print(f"  🔴 Arrivée : {stop_name} ({stop_id})")
            # Pour les autres arrêts normaux
            else:
                print(f"  │  {stop_name} ({stop_id})")

    print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    run_terminal_test()