from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any
import random

class BrigadeType(Enum):
    CAVALRY = "cavalry"
    HEAVY = "heavy"
    LIGHT = "light"

class TerrainType(Enum):
    PLAINS = "plains"
    DESERT = "desert"
    TUNDRA = "tundra"
    FOREST = "forest"
    HIGHLANDS = "highlands"
    JUNGLE = "jungle"
    MARSHLAND = "marshland"
    MOUNTAIN = "mountain"

class FlagType(Enum):
    NATIONAL = "national"
    BLACK = "black"
    WHITE = "white"

class SeaTerrainType(Enum):
    OPEN_SEAS = "open_seas"
    COASTAL_WATERS = "coastal_waters"
    STRAIGHTS = "straights"
    CANAL = "canal"

@dataclass
class Enhancement:
    name: str
    description: str
    brigade_type: BrigadeType
    bonuses: Dict[str, int] = field(default_factory=dict)
    special_abilities: List[str] = field(default_factory=list)

@dataclass
class GeneralTrait:
    name: str
    description: str
    bonuses: Dict[str, int] = field(default_factory=dict)
    special_abilities: List[str] = field(default_factory=list)

@dataclass
class AdmiralTrait:
    name: str
    description: str
    bonuses: Dict[str, int] = field(default_factory=dict)
    special_abilities: List[str] = field(default_factory=list)

@dataclass
class Brigade:
    id: str
    type: BrigadeType
    enhancement: Optional[Enhancement] = None
    is_mercenary: bool = False
    is_fatigued: bool = False
    is_routed: bool = False
    is_garrisoned: bool = False
    movement_remaining: int = 0
    
    def get_skirmish_bonus(self) -> int:
        bonus = 0
        if self.type == BrigadeType.CAVALRY:
            bonus += 1
        elif self.type == BrigadeType.LIGHT:
            bonus += 2
        
        if self.enhancement:
            bonus += self.enhancement.bonuses.get('skirmish', 0)
        
        if self.is_fatigued:
            bonus -= 1
            
        return bonus
    
    def get_defense_bonus(self) -> int:
        bonus = 0
        if self.type == BrigadeType.HEAVY:
            bonus += 2
        
        if self.enhancement:
            bonus += self.enhancement.bonuses.get('defense', 0)
        
        if self.is_garrisoned:
            bonus += 2
        
        if self.is_fatigued:
            bonus -= 1
            
        return bonus
    
    def get_pitch_bonus(self) -> int:
        bonus = 0
        if self.type == BrigadeType.CAVALRY:
            bonus += 1
        elif self.type == BrigadeType.HEAVY:
            bonus += 1
        
        if self.enhancement:
            bonus += self.enhancement.bonuses.get('pitch', 0)
        
        if self.is_fatigued:
            bonus -= 1
            
        return bonus
    
    def get_rally_bonus(self) -> int:
        bonus = 0
        if self.type == BrigadeType.HEAVY:
            bonus += 1
        elif self.type == BrigadeType.LIGHT:
            bonus += 1
        
        if self.enhancement:
            bonus += self.enhancement.bonuses.get('rally', 0)
        
        if self.is_garrisoned:
            bonus += 1
        
        if self.is_fatigued:
            bonus -= 1
            
        return bonus
    
    def get_movement_speed(self) -> int:
        if self.type == BrigadeType.CAVALRY:
            return 5
        elif self.type == BrigadeType.HEAVY:
            return 3
        else:  # LIGHT
            return 4

@dataclass
class General:
    id: str
    name: str
    level: int = 1
    trait: Optional[GeneralTrait] = None
    is_captured: bool = False
    
    def get_pitch_bonus(self) -> int:
        bonus = self.level
        if self.trait and self.trait.name == "Brilliant":
            bonus *= 2
        return bonus

@dataclass
class Army:
    id: str
    general: General
    brigades: List[Brigade] = field(default_factory=list)
    enhancements: List[str] = field(default_factory=list)
    position: tuple = (0, 0)
    
    def get_movement_speed(self) -> int:
        if not self.brigades:
            return 0
        return min(brigade.get_movement_speed() for brigade in self.brigades)

@dataclass
class Ship:
    id: str
    enhancement: Optional[str] = None
    flag: FlagType = FlagType.NATIONAL
    is_flagship: bool = False
    damage_effects: List[str] = field(default_factory=list)
    position: tuple = (0, 0)
    
    def get_gunnery_bonus(self, range_band: int) -> int:
        bonus = 0
        if range_band == 1:
            bonus += 2
        elif range_band == 2:
            bonus += 1
        
        if self.enhancement == "Additional Firepower":
            bonus += 2
        
        if self.is_flagship:
            bonus += 1
            
        return bonus
    
    def get_maneuver_bonus(self) -> int:
        bonus = 0
        if self.enhancement == "Additional Propulsion":
            bonus += 1
        
        if self.is_flagship:
            bonus += 1
            
        return bonus
    
    def get_boarding_bonus(self) -> int:
        bonus = 0
        if self.enhancement == "Marine Detachment":
            bonus += 2
        
        if self.is_flagship:
            bonus += 1
            
        return bonus

@dataclass
class Admiral:
    id: str
    name: str
    trait: Optional[AdmiralTrait] = None
    flagship: Optional[Ship] = None
    is_captured: bool = False

@dataclass
class Armada:
    id: str
    admiral: Admiral
    ships: List[Ship] = field(default_factory=list)
    position: tuple = (0, 0)
    
    def get_movement_speed(self) -> int:
        base_speed = 2
        if self.admiral.trait and self.admiral.trait.name == "Experienced":
            # Additional speed from trait if applicable
            pass
        return base_speed

@dataclass
class BattleResult:
    winner: str
    loser: str
    casualties: Dict[str, List[str]] = field(default_factory=dict)
    captured_generals: List[str] = field(default_factory=list)
    promoted_generals: List[str] = field(default_factory=list)
    terrain: TerrainType = TerrainType.PLAINS

@dataclass
class NavalBattleResult:
    winner: str
    loser: str
    sunk_ships: Dict[str, List[str]] = field(default_factory=dict)
    captured_ships: Dict[str, List[str]] = field(default_factory=dict)
    retreated_ships: Dict[str, List[str]] = field(default_factory=dict)
    sea_terrain: SeaTerrainType = SeaTerrainType.OPEN_SEAS

# Enhancement definitions based on the tutorial
CAVALRY_ENHANCEMENTS = {
    "Cuirassiers": Enhancement("Cuirassiers", "+2 Defense. +1 Pitch. Free Destruction Reroll.", 
                              BrigadeType.CAVALRY, {"defense": 2, "pitch": 1}, ["free_destruction_reroll"]),
    "Dragoons": Enhancement("Dragoons", "+1 Pitch. +1 Rally. +1 Pitch if not in initial pitch.", 
                           BrigadeType.CAVALRY, {"pitch": 1, "rally": 1}, ["conditional_pitch_bonus"]),
    "Hussars": Enhancement("Hussars", "+1 Skirmish. +1 Rally. -1 terrain cost.", 
                          BrigadeType.CAVALRY, {"skirmish": 1, "rally": 1}, ["terrain_bonus"]),
    "Lancers": Enhancement("Lancers", "+3 Skirmish. Auto overrun on skirmish win.", 
                          BrigadeType.CAVALRY, {"skirmish": 3}, ["auto_overrun"]),
    "Life Guard": Enhancement("Life Guard", "+2 Rally. General reroll promotion once per battle.", 
                             BrigadeType.CAVALRY, {"rally": 2}, ["general_reroll"]),
    "Officer Corps": Enhancement("Officer Corps", "+2 Rally. General promotes on 5-6. Choose retreat direction.", 
                                BrigadeType.CAVALRY, {"rally": 2}, ["easy_promotion", "choose_retreat"]),
}

HEAVY_ENHANCEMENTS = {
    "Artillery Team": Enhancement("Artillery Team", "+2 Defense. +1 Pitch. +1 Pitch when garrisoned. -1 defense to all enemies.", 
                                 BrigadeType.HEAVY, {"defense": 2, "pitch": 1}, ["garrison_bonus", "enemy_defense_reduction"]),
    "Elite": Enhancement("Elite", "+1 Skirmish. +2 Defense. +1 Pitch. +1 Rally.", 
                        BrigadeType.HEAVY, {"skirmish": 1, "defense": 2, "pitch": 1, "rally": 1}),
    "Grenadiers": Enhancement("Grenadiers", "+2 Skirmish. +2 Pitch. +1 Pitch in initial stage.", 
                             BrigadeType.HEAVY, {"skirmish": 2, "pitch": 2}, ["initial_pitch_bonus"]),
    "Line Infantry": Enhancement("Line Infantry", "+1 Pitch. +1 Pitch per 2 friendly Line Infantry.", 
                                BrigadeType.HEAVY, {"pitch": 1}, ["line_infantry_bonus"]),
    "Pikes": Enhancement("Pikes", "+4 Defense. +1 Pitch. +2 Pitch vs cavalry. Negates lancer overrun. -1 rally to enemy cavalry.", 
                        BrigadeType.HEAVY, {"defense": 4, "pitch": 1}, ["anti_cavalry"]),
    "Stormtroopers": Enhancement("Stormtroopers", "+1 Pitch. +1 Rally. -1 terrain cost.", 
                                BrigadeType.HEAVY, {"pitch": 1, "rally": 1}, ["terrain_bonus"]),
}

LIGHT_ENHANCEMENTS = {
    "Assault Team": Enhancement("Assault Team", "+2 Skirmish. +1 Pitch. Select skirmish target. Negate garrison.", 
                               BrigadeType.LIGHT, {"skirmish": 2, "pitch": 1}, ["select_target", "negate_garrison"]),
    "Chasseurs": Enhancement("Chasseurs", "+2 Skirmish. +2 Defense. +1 sight range.", 
                            BrigadeType.LIGHT, {"skirmish": 2, "defense": 2}, ["extended_sight"]),
    "Commando": Enhancement("Commando", "+2 Defense. +1 Pitch. +1 Rally. Cannot be seen unless in battle.", 
                           BrigadeType.LIGHT, {"defense": 2, "pitch": 1, "rally": 1}, ["stealth"]),
    "Fusiliers": Enhancement("Fusiliers", "+1 Skirmish. +2 Defense. +2 Pitch.", 
                            BrigadeType.LIGHT, {"skirmish": 1, "defense": 2, "pitch": 2}),
    "Rangers": Enhancement("Rangers", "+2 Pitch. -2 terrain cost.", 
                          BrigadeType.LIGHT, {"pitch": 2}, ["major_terrain_bonus"]),
    "Sharpshooters": Enhancement("Sharpshooters", "+2 Defense. +1 Pitch. +2 Pitch when garrisoned. Rout failed skirmishers.", 
                                BrigadeType.LIGHT, {"defense": 2, "pitch": 1}, ["garrison_bonus", "rout_skirmishers"]),
}

# General Traits
GENERAL_TRAITS = [
    GeneralTrait("Ambitious", "-1 to promotion number", {}, ["easy_promotion"]),
    GeneralTrait("Bold", "+2 Skirmish to all brigades", {"skirmish": 2}),
    GeneralTrait("Brilliant", "Double general level in pitch", {}, ["double_pitch"]),
    GeneralTrait("Brutal", "Double pillaging resources, enhanced sacking", {}, ["brutal_pillaging"]),
    GeneralTrait("Cautious", "May skip skirmishing stage", {}, ["skip_skirmish"]),
    GeneralTrait("Chivalrous", "Enemy rolls 1-2 on destruction, faster starve, safe sacking", {}, ["chivalrous"]),
    GeneralTrait("Clever", "+1 Pitch and Skirmish for Light Brigades", {}, ["light_bonus"]),
    GeneralTrait("Defiant", "+1 Rally for all brigades", {"rally": 1}),
    GeneralTrait("Disciplined", "+1 Pitch for all brigades", {"pitch": 1}),
    GeneralTrait("Elusive", "Retreat after skirmish once per week", {}, ["tactical_retreat"]),
    GeneralTrait("Flamboyant", "+1 Skirmish and Rally for Cavalry", {}, ["cavalry_bonus"]),
    GeneralTrait("Inspiring", "Free reroll on rally rolls", {}, ["rally_reroll"]),
    GeneralTrait("Judicious", "+1 Pitch and Rally for Heavy Brigades", {}, ["heavy_bonus"]),
    GeneralTrait("Lucky", "Reroll promotion die on 1", {}, ["lucky_reroll"]),
    GeneralTrait("Merciless", "Enemies destroyed on 1-4 instead of 1-3", {}, ["merciless"]),
    GeneralTrait("Prodigious", "Starts with additional level", {}, ["bonus_level"]),
    GeneralTrait("Relentless", "-1 movement cost, may pursue retreating enemies", {}, ["pursuit"]),
    GeneralTrait("Resolute", "+4 Defense for all brigades", {"defense": 4}),
    GeneralTrait("Wary", "Alert when seen, +1 sight, reveal enemy traits", {}, ["enhanced_awareness"]),
    GeneralTrait("Zealous", "+1 Pitch and Rally during Holy War", {}, ["holy_war_bonus"]),
]

# Admiral Traits
ADMIRAL_TRAITS = [
    AdmiralTrait("Dauntless", "+1 Boarding, bonus victory on boarding win", {"boarding": 1}, ["boarding_bonus"]),
    AdmiralTrait("Implacable", "Chase retreating ships for second battle", {}, ["pursuit"]),
    AdmiralTrait("Privateer", "Piracy with national flags, steal both trade sides", {}, ["enhanced_piracy"]),
    AdmiralTrait("Raider", "Pillage coastal tiles with armada", {}, ["coastal_raiding"]),
    AdmiralTrait("Stoic", "Fight 2 additional gunnery rounds", {}, ["extended_combat"]),
    AdmiralTrait("Multilingual", "Fly any national flag", {}, ["false_flags"]),
    AdmiralTrait("Daring", "+1 combat width", {}, ["increased_width"]),
    AdmiralTrait("Experienced", "+1 on all Maneuver rolls", {"maneuver": 1}),
    AdmiralTrait("Accurate", "+1 on all Gunnery rolls", {"gunnery": 1}),
    AdmiralTrait("Wary", "Alert when seen, +1 sight, reveal enemy traits", {}, ["enhanced_awareness"]),
]

# Terrain combat width and effects
TERRAIN_EFFECTS = {
    TerrainType.PLAINS: {"combat_width": 8, "effects": []},
    TerrainType.DESERT: {"combat_width": 8, "effects": ["no_reinforcements"]},
    TerrainType.TUNDRA: {"combat_width": 7, "effects": ["rally_penalty"]},
    TerrainType.FOREST: {"combat_width": 6, "effects": ["skirmish_penalty"]},
    TerrainType.HIGHLANDS: {"combat_width": 6, "effects": ["see_retreat"]},
    TerrainType.JUNGLE: {"combat_width": 5, "effects": ["lost_brigades"]},
    TerrainType.MARSHLAND: {"combat_width": 5, "effects": ["destruction_bonus"]},
    TerrainType.MOUNTAIN: {"combat_width": 4, "effects": ["defense_bonus"]},
}

# Sea terrain effects
SEA_TERRAIN_EFFECTS = {
    SeaTerrainType.OPEN_SEAS: {"combat_width": 4, "victory_limit": 8},
    SeaTerrainType.COASTAL_WATERS: {"combat_width": 3, "victory_limit": 6},
    SeaTerrainType.STRAIGHTS: {"combat_width": 2, "victory_limit": 4},
    SeaTerrainType.CANAL: {"combat_width": 1, "victory_limit": 2},
}
