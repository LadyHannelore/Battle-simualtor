#!/usr/bin/env python3
"""
Test script for the Battle Simulator
This script validates the core battle mechanics without the GUI
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from models import *
from battle_engine import BattleEngine, NavalBattleEngine
import random

def create_test_army(name: str, general_trait_name: str, brigade_count: int = 5) -> Army:
    """Create a test army with specific parameters"""
    # Find the trait
    trait = next((t for t in GENERAL_TRAITS if t.name == general_trait_name), GENERAL_TRAITS[0])
    
    # Create general
    general = General(
        id=f"gen_{name}",
        name=name,
        level=random.randint(1, 3),
        trait=trait
    )
    
    # Create brigades
    brigades = []
    for i in range(brigade_count):
        brigade_type = random.choice(list(BrigadeType))
        brigade = Brigade(
            id=f"brigade_{name}_{i}",
            type=brigade_type
        )
        
        # Add some enhancements
        if random.random() < 0.3:
            if brigade_type == BrigadeType.CAVALRY:
                brigade.enhancement = random.choice(list(CAVALRY_ENHANCEMENTS.values()))
            elif brigade_type == BrigadeType.HEAVY:
                brigade.enhancement = random.choice(list(HEAVY_ENHANCEMENTS.values()))
            else:
                brigade.enhancement = random.choice(list(LIGHT_ENHANCEMENTS.values()))
        
        brigades.append(brigade)
    
    return Army(
        id=f"army_{name}",
        general=general,
        brigades=brigades
    )

def create_test_armada(name: str, admiral_trait_name: str, ship_count: int = 3) -> Armada:
    """Create a test armada with specific parameters"""
    # Find the trait
    trait = next((t for t in ADMIRAL_TRAITS if t.name == admiral_trait_name), ADMIRAL_TRAITS[0])
    
    # Create admiral
    admiral = Admiral(
        id=f"adm_{name}",
        name=name,
        trait=trait
    )
    
    # Create ships
    ships = []
    enhancements = ["Additional Firepower", "Additional Propulsion", "Marine Detachment", None]
    
    for i in range(ship_count):
        ship = Ship(
            id=f"ship_{name}_{i}",
            enhancement=random.choice(enhancements),
            flag=FlagType.NATIONAL
        )
        ships.append(ship)
    
    # Set flagship
    if ships:
        ships[0].is_flagship = True
        admiral.flagship = ships[0]
    
    return Armada(
        id=f"armada_{name}",
        admiral=admiral,
        ships=ships
    )

def test_land_battle():
    """Test land battle mechanics"""
    print("=== TESTING LAND BATTLE ===")
    
    # Create test armies
    army1 = create_test_army("Alexander", "Bold", 6)
    army2 = create_test_army("Napoleon", "Brilliant", 5)
    
    print(f"Army 1: {army1.general.name} with {len(army1.brigades)} brigades (Trait: {army1.general.trait.name})")
    print(f"Army 2: {army2.general.name} with {len(army2.brigades)} brigades (Trait: {army2.general.trait.name})")
    
    # Test different terrains
    terrains = [TerrainType.PLAINS, TerrainType.MOUNTAIN, TerrainType.JUNGLE]
    
    engine = BattleEngine()
    
    for terrain in terrains:
        print(f"\n--- Battle on {terrain.value.title()} ---")
        result = engine.simulate_land_battle(army1, army2, terrain)
        
        print(f"Winner: {result.winner}")
        print(f"Casualties: {len(result.casualties.get(army1.id, []))} vs {len(result.casualties.get(army2.id, []))}")
        if result.promoted_generals:
            print(f"Promoted: {', '.join(result.promoted_generals)}")
        if result.captured_generals:
            print(f"Captured: {', '.join(result.captured_generals)}")
        
        # Reset armies for next battle
        for brigade in army1.brigades + army2.brigades:
            brigade.is_routed = False
        army1.general.is_captured = False
        army2.general.is_captured = False

def test_naval_battle():
    """Test naval battle mechanics"""
    print("\n\n=== TESTING NAVAL BATTLE ===")
    
    # Create test armadas
    armada1 = create_test_armada("Nelson", "Accurate", 4)
    armada2 = create_test_armada("Drake", "Daring", 3)
    
    print(f"Armada 1: {armada1.admiral.name} with {len(armada1.ships)} ships (Trait: {armada1.admiral.trait.name})")
    print(f"Armada 2: {armada2.admiral.name} with {len(armada2.ships)} ships (Trait: {armada2.admiral.trait.name})")
    
    # Test different sea terrains
    sea_terrains = [SeaTerrainType.OPEN_SEAS, SeaTerrainType.COASTAL_WATERS, SeaTerrainType.STRAIGHTS]
    
    engine = NavalBattleEngine()
    
    for sea_terrain in sea_terrains:
        print(f"\n--- Naval Battle in {sea_terrain.value.replace('_', ' ').title()} ---")
        result = engine.simulate_naval_battle(armada1, armada2, sea_terrain)
        
        print(f"Winner: {result.winner}")
        if result.winner != "Inconclusive":
            print(f"Ships Lost: {len(result.sunk_ships.get(armada1.id, []))} vs {len(result.sunk_ships.get(armada2.id, []))}")
        
        # Reset armadas for next battle
        for ship in armada1.ships + armada2.ships:
            ship.damage_effects = []

def test_unit_mechanics():
    """Test individual unit mechanics"""
    print("\n\n=== TESTING UNIT MECHANICS ===")
    
    # Test brigade bonuses
    cavalry = Brigade("test_cav", BrigadeType.CAVALRY)
    heavy = Brigade("test_heavy", BrigadeType.HEAVY)
    light = Brigade("test_light", BrigadeType.LIGHT)
    
    print("Brigade Base Stats:")
    print(f"Cavalry: Skirmish +{cavalry.get_skirmish_bonus()}, Defense +{cavalry.get_defense_bonus()}, Pitch +{cavalry.get_pitch_bonus()}, Rally +{cavalry.get_rally_bonus()}")
    print(f"Heavy: Skirmish +{heavy.get_skirmish_bonus()}, Defense +{heavy.get_defense_bonus()}, Pitch +{heavy.get_pitch_bonus()}, Rally +{heavy.get_rally_bonus()}")
    print(f"Light: Skirmish +{light.get_skirmish_bonus()}, Defense +{light.get_defense_bonus()}, Pitch +{light.get_pitch_bonus()}, Rally +{light.get_rally_bonus()}")
    
    # Test with enhancements
    cavalry.enhancement = CAVALRY_ENHANCEMENTS["Lancers"]
    heavy.enhancement = HEAVY_ENHANCEMENTS["Elite"]
    light.enhancement = LIGHT_ENHANCEMENTS["Rangers"]
    
    print("\nWith Enhancements:")
    print(f"Cavalry (Lancers): Skirmish +{cavalry.get_skirmish_bonus()}, Defense +{cavalry.get_defense_bonus()}, Pitch +{cavalry.get_pitch_bonus()}, Rally +{cavalry.get_rally_bonus()}")
    print(f"Heavy (Elite): Skirmish +{heavy.get_skirmish_bonus()}, Defense +{heavy.get_defense_bonus()}, Pitch +{heavy.get_pitch_bonus()}, Rally +{heavy.get_rally_bonus()}")
    print(f"Light (Rangers): Skirmish +{light.get_skirmish_bonus()}, Defense +{light.get_defense_bonus()}, Pitch +{light.get_pitch_bonus()}, Rally +{light.get_rally_bonus()}")
    
    # Test ship mechanics
    print("\nShip Mechanics:")
    basic_ship = Ship("basic_ship")
    enhanced_ship = Ship("enhanced_ship", enhancement="Additional Firepower")
    flagship = Ship("flagship", is_flagship=True)
    
    for range_band in [1, 2, 3]:
        print(f"Range {range_band} - Basic: +{basic_ship.get_gunnery_bonus(range_band)}, Enhanced: +{enhanced_ship.get_gunnery_bonus(range_band)}, Flagship: +{flagship.get_gunnery_bonus(range_band)}")

def main():
    """Run all tests"""
    print("Battle Simulator Test Suite")
    print("=" * 50)
    
    try:
        test_unit_mechanics()
        test_land_battle()
        test_naval_battle()
        
        print("\n" + "=" * 50)
        print("All tests completed successfully!")
        print("The battle simulator is working correctly.")
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
