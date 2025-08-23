#!/usr/bin/env python3
"""
Quick Battle Generator
Creates random battle scenarios for testing and demonstration
"""

import sys
import os
import random

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from models import *
from battle_engine import BattleEngine, NavalBattleEngine

def generate_random_army(name_prefix: str) -> Army:
    """Generate a random army with random traits and compositions"""
    
    # Random army size
    brigade_count = random.randint(3, 8)
    
    # Random general
    general = General(
        id=f"gen_{name_prefix}",
        name=f"General {name_prefix}",
        level=random.randint(1, 3),
        trait=random.choice(GENERAL_TRAITS)
    )
    
    # Random brigades with varying types
    brigades = []
    for i in range(brigade_count):
        # Weight towards more balanced compositions
        brigade_type = random.choices(
            list(BrigadeType),
            weights=[25, 40, 35],  # Slightly favor heavy infantry
            k=1
        )[0]
        
        brigade = Brigade(
            id=f"brigade_{name_prefix}_{i}",
            type=brigade_type,
            is_mercenary=random.choice([True, False])
        )
        
        # 40% chance of enhancement
        if random.random() < 0.4:
            if brigade_type == BrigadeType.CAVALRY:
                brigade.enhancement = random.choice(list(CAVALRY_ENHANCEMENTS.values()))
            elif brigade_type == BrigadeType.HEAVY:
                brigade.enhancement = random.choice(list(HEAVY_ENHANCEMENTS.values()))
            else:  # LIGHT
                brigade.enhancement = random.choice(list(LIGHT_ENHANCEMENTS.values()))
        
        brigades.append(brigade)
    
    # Random army enhancements (up to 2)
    army_enhancements = random.sample([
        "Additional Conscripts", "Blacksmiths", "Camp Sentries", "Combat Engineers",
        "Dedicated Chefs", "Field Hospitals", "Local Maps", "Marine Detachments",
        "Siege Equipment", "Signal Companies"
    ], k=random.randint(0, 2))
    
    return Army(
        id=f"army_{name_prefix}",
        general=general,
        brigades=brigades,
        enhancements=army_enhancements
    )

def generate_random_armada(name_prefix: str) -> Armada:
    """Generate a random armada with random traits and compositions"""
    
    # Random fleet size
    ship_count = random.randint(2, 6)
    
    # Random admiral
    admiral = Admiral(
        id=f"adm_{name_prefix}",
        name=f"Admiral {name_prefix}",
        trait=random.choice(ADMIRAL_TRAITS)
    )
    
    # Random ships
    ships = []
    enhancements = ["Additional Firepower", "Additional Propulsion", "Camouflage", 
                   "Debris Netting", "Experienced Spotters", "False Flags",
                   "Marine Detachment", "Reinforced Hulls", None]
    
    for i in range(ship_count):
        ship = Ship(
            id=f"ship_{name_prefix}_{i}",
            enhancement=random.choice(enhancements),
            flag=random.choice(list(FlagType))
        )
        ships.append(ship)
    
    # Set flagship (randomly choose one)
    if ships:
        flagship = random.choice(ships)
        flagship.is_flagship = True
        admiral.flagship = flagship
    
    return Armada(
        id=f"armada_{name_prefix}",
        admiral=admiral,
        ships=ships
    )

def run_quick_battle():
    """Run a quick random land battle"""
    print("=== QUICK RANDOM BATTLE ===")
    
    # Generate random armies
    army1 = generate_random_army("Red")
    army2 = generate_random_army("Blue")
    
    # Random terrain
    terrain = random.choice(list(TerrainType))
    
    print(f"Red Army: General {army1.general.name} ({army1.general.trait.name})")
    print(f"  - {len(army1.brigades)} brigades")
    print(f"  - Level {army1.general.level} general")
    
    print(f"Blue Army: General {army2.general.name} ({army2.general.trait.name})")
    print(f"  - {len(army2.brigades)} brigades")
    print(f"  - Level {army2.general.level} general")
    
    print(f"Terrain: {terrain.value.title()}")
    
    # Run battle
    engine = BattleEngine()
    result = engine.simulate_land_battle(army1, army2, terrain)
    
    print(f"\n=== BATTLE RESULT ===")
    print(f"Winner: {result.winner}")
    print(f"Terrain: {result.terrain.value}")
    if result.casualties:
        total_red_casualties = len(result.casualties.get(army1.id, []))
        total_blue_casualties = len(result.casualties.get(army2.id, []))
        print(f"Casualties: Red {total_red_casualties}, Blue {total_blue_casualties}")
    
    if result.promoted_generals:
        print(f"Promoted Generals: {', '.join(result.promoted_generals)}")
    
    if result.captured_generals:
        print(f"Captured Generals: {', '.join(result.captured_generals)}")
    
    return result

def run_quick_naval_battle():
    """Run a quick random naval battle"""
    print("\n=== QUICK RANDOM NAVAL BATTLE ===")
    
    # Generate random armadas
    armada1 = generate_random_armada("Red")
    armada2 = generate_random_armada("Blue")
    
    # Random sea terrain
    sea_terrain = random.choice(list(SeaTerrainType))
    
    print(f"Red Fleet: Admiral {armada1.admiral.name} ({armada1.admiral.trait.name})")
    print(f"  - {len(armada1.ships)} ships")
    
    print(f"Blue Fleet: Admiral {armada2.admiral.name} ({armada2.admiral.trait.name})")
    print(f"  - {len(armada2.ships)} ships")
    
    print(f"Sea Terrain: {sea_terrain.value.replace('_', ' ').title()}")
    
    # Run battle
    engine = NavalBattleEngine()
    result = engine.simulate_naval_battle(armada1, armada2, sea_terrain)
    
    print(f"\n=== NAVAL BATTLE RESULT ===")
    print(f"Winner: {result.winner}")
    if result.winner != "Inconclusive":
        red_losses = len(result.sunk_ships.get(armada1.id, []))
        blue_losses = len(result.sunk_ships.get(armada2.id, []))
        print(f"Ships Lost: Red {red_losses}, Blue {blue_losses}")
    
    return result

def run_campaign_simulation(battles: int = 5):
    """Run a series of battles simulating a campaign"""
    print(f"=== CAMPAIGN SIMULATION ({battles} battles) ===")
    
    red_wins = 0
    blue_wins = 0
    
    for i in range(battles):
        print(f"\n--- Campaign Battle {i+1} ---")
        
        if random.choice([True, False]):
            # Land battle
            result = run_quick_battle()
            if "Red" in result.winner:
                red_wins += 1
            elif "Blue" in result.winner:
                blue_wins += 1
        else:
            # Naval battle
            result = run_quick_naval_battle()
            if "Red" in result.winner:
                red_wins += 1
            elif "Blue" in result.winner:
                blue_wins += 1
    
    print(f"\n=== CAMPAIGN RESULTS ===")
    print(f"Red victories: {red_wins}")
    print(f"Blue victories: {blue_wins}")
    
    if red_wins > blue_wins:
        print("🔴 RED EMPIRE VICTORIOUS! 🔴")
    elif blue_wins > red_wins:
        print("🔵 BLUE KINGDOM TRIUMPHANT! 🔵")
    else:
        print("⚖️ CAMPAIGN ENDS IN STALEMATE ⚖️")

def main():
    """Main function with user menu"""
    while True:
        print("\n" + "="*50)
        print("QUICK BATTLE GENERATOR")
        print("="*50)
        print("1. Random Land Battle")
        print("2. Random Naval Battle")
        print("3. Campaign Simulation (5 battles)")
        print("4. Extended Campaign (10 battles)")
        print("5. Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == "1":
            run_quick_battle()
        elif choice == "2":
            run_quick_naval_battle()
        elif choice == "3":
            run_campaign_simulation(5)
        elif choice == "4":
            run_campaign_simulation(10)
        elif choice == "5":
            print("Thanks for using the Quick Battle Generator!")
            break
        else:
            print("Invalid choice. Please select 1-5.")

if __name__ == "__main__":
    main()
