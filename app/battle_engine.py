import random
from typing import List, Tuple, Dict, Optional
from models import *

class BattleEngine:
    def __init__(self):
        self.battle_log = []
    
    def log(self, message: str):
        """Add message to battle log"""
        self.battle_log.append(message)
        print(message)  # Also print for immediate feedback
    
    def clear_log(self):
        """Clear the battle log"""
        self.battle_log = []
    
    def roll_dice(self, count: int = 1, sides: int = 6) -> List[int]:
        """Roll dice and return results"""
        return [random.randint(1, sides) for _ in range(count)]
    
    def simulate_land_battle(self, army1: Army, army2: Army, terrain: TerrainType) -> BattleResult:
        """Simulate a complete land battle between two armies"""
        self.clear_log()
        self.log(f"=== LAND BATTLE ===")
        self.log(f"Army 1 ({army1.general.name}): {len(army1.brigades)} brigades")
        self.log(f"Army 2 ({army2.general.name}): {len(army2.brigades)} brigades")
        self.log(f"Terrain: {terrain.value}")
        
        # Get terrain effects
        terrain_data = TERRAIN_EFFECTS[terrain]
        combat_width = terrain_data["combat_width"]
        terrain_effects = terrain_data["effects"]
        
        self.log(f"Combat Width: {combat_width}")
        
        # Apply terrain effects
        self._apply_terrain_effects(army1.brigades, army2.brigades, terrain_effects)
        
        # Determine initial active brigades
        active_army1 = [b for b in army1.brigades if not b.is_routed][:combat_width]
        active_army2 = [b for b in army2.brigades if not b.is_routed][:combat_width]
        
        # Determine sides (randomly assign positive/negative)
        positive_army = army1 if random.choice([True, False]) else army2
        negative_army = army2 if positive_army == army1 else army1
        
        self.log(f"Positive side: {positive_army.general.name}")
        self.log(f"Negative side: {negative_army.general.name}")
        
        # Battle phases
        pitch_tally = 0
        round_count = 0
        max_rounds = 10  # Safety limit
        
        while round_count < max_rounds:
            round_count += 1
            self.log(f"\n--- Round {round_count} ---")
            
            # Skirmish Phase (only in first round)
            if round_count == 1:
                self._skirmish_phase(active_army1, active_army2)
            
            # Check if either side has no active brigades
            active_army1 = [b for b in active_army1 if not b.is_routed]
            active_army2 = [b for b in active_army2 if not b.is_routed]
            
            if not active_army1:
                self.log("Army 1 has no active brigades remaining!")
                return self._create_battle_result(army2, army1, terrain)
            elif not active_army2:
                self.log("Army 2 has no active brigades remaining!")
                return self._create_battle_result(army1, army2, terrain)
            
            # Pitch Phase
            pitch_result = self._pitch_phase(
                active_army1 if positive_army == army1 else active_army2,
                active_army2 if positive_army == army1 else active_army1,
                positive_army,
                negative_army
            )
            
            pitch_tally += pitch_result
            self.log(f"Pitch tally: {pitch_tally}")
            
            # Check for decisive victory
            if pitch_tally >= 20:
                self.log(f"Decisive victory for {positive_army.general.name}!")
                winner = positive_army
                loser = negative_army
                break
            elif pitch_tally <= -20:
                self.log(f"Decisive victory for {negative_army.general.name}!")
                winner = negative_army
                loser = positive_army
                break
            
            # Rally Phase
            rally_result = self._rally_phase(active_army1, active_army2, army1, army2, combat_width, terrain_effects)
            
            active_army1, active_army2 = rally_result
            
            # Check for complete rout
            if not active_army1:
                self.log("Army 1 completely routed!")
                return self._create_battle_result(army2, army1, terrain)
            elif not active_army2:
                self.log("Army 2 completely routed!")
                return self._create_battle_result(army1, army2, terrain)
            
            # Reset pitch tally for next round
            if round_count > 1:
                pitch_tally = 0
        
        # Stalemate after max rounds
        self.log("Battle ends in stalemate!")
        return BattleResult("Stalemate", "Stalemate", {}, [], [], terrain)
    
    def _apply_terrain_effects(self, army1_brigades: List[Brigade], army2_brigades: List[Brigade], effects: List[str]):
        """Apply terrain effects to brigades"""
        if "lost_brigades" in effects:
            # Jungle effect - brigades get lost
            for brigade in army1_brigades + army2_brigades:
                if self.roll_dice()[0] == 1:
                    brigade.is_routed = True
                    self.log(f"Brigade {brigade.id} gets lost in the jungle!")
    
    def _skirmish_phase(self, army1: List[Brigade], army2: List[Brigade]):
        """Handle the skirmish phase"""
        self.log("\n=== SKIRMISH PHASE ===")
        
        # Select best skirmishers (top 2 from each side)
        army1_skirmishers = sorted(army1, key=lambda b: b.get_skirmish_bonus(), reverse=True)[:2]
        army2_skirmishers = sorted(army2, key=lambda b: b.get_skirmish_bonus(), reverse=True)[:2]
        
        # Each skirmisher targets a random enemy
        for skirmisher in army1_skirmishers:
            target = random.choice(army2)
            self._resolve_skirmish(skirmisher, target)
        
        for skirmisher in army2_skirmishers:
            target = random.choice(army1)
            self._resolve_skirmish(skirmisher, target)
    
    def _resolve_skirmish(self, attacker: Brigade, defender: Brigade):
        """Resolve individual skirmish combat"""
        attacker_roll = self.roll_dice()[0] + attacker.get_skirmish_bonus()
        defender_roll = self.roll_dice()[0] + defender.get_defense_bonus()
        
        self.log(f"Skirmish: {attacker.id} ({attacker_roll}) vs {defender.id} ({defender_roll})")
        
        if attacker_roll > defender_roll:
            defender.is_routed = True
            self.log(f"{defender.id} is routed!")
            
            # Check for overrun (3+ difference)
            if attacker_roll - defender_roll >= 3:
                destruction_roll = self.roll_dice()[0]
                self.log(f"Overrun! {defender.id} rolls destruction: {destruction_roll}")
                if destruction_roll <= 3:  # Destroyed
                    self.log(f"{defender.id} is destroyed in overrun!")
    
    def _pitch_phase(self, positive_brigades: List[Brigade], negative_brigades: List[Brigade], 
                     positive_army: Army, negative_army: Army) -> int:
        """Handle the pitch phase"""
        self.log("\n=== PITCH PHASE ===")
        
        # Positive side rolls first
        positive_rolls = self.roll_dice(len(positive_brigades))
        positive_bonuses = sum(b.get_pitch_bonus() for b in positive_brigades)
        positive_general_bonus = positive_army.general.get_pitch_bonus()
        positive_total = sum(positive_rolls) + positive_bonuses + positive_general_bonus
        
        self.log(f"Positive side: {positive_rolls} + {positive_bonuses} + {positive_general_bonus} = {positive_total}")
        
        # Negative side rolls second
        negative_rolls = self.roll_dice(len(negative_brigades))
        negative_bonuses = sum(b.get_pitch_bonus() for b in negative_brigades)
        negative_general_bonus = negative_army.general.get_pitch_bonus()
        negative_total = sum(negative_rolls) + negative_bonuses + negative_general_bonus
        
        self.log(f"Negative side: {negative_rolls} + {negative_bonuses} + {negative_general_bonus} = {negative_total}")
        
        # Calculate pitch result
        pitch_result = positive_total - negative_total
        self.log(f"Pitch result: {pitch_result}")
        
        return pitch_result
    
    def _rally_phase(self, army1: List[Brigade], army2: List[Brigade], 
                     full_army1: Army, full_army2: Army, combat_width: int, terrain_effects: List[str]) -> Tuple[List[Brigade], List[Brigade]]:
        """Handle the rally phase"""
        self.log("\n=== RALLY PHASE ===")
        
        # Rally rolls for all brigades that participated
        new_army1 = []
        new_army2 = []
        
        for brigade in army1:
            rally_roll = self.roll_dice()[0] + brigade.get_rally_bonus()
            # Apply terrain effects
            if "rally_penalty" in terrain_effects:
                rally_roll -= 1
            
            self.log(f"{brigade.id} rally roll: {rally_roll}")
            if rally_roll >= 6:
                new_army1.append(brigade)
                self.log(f"{brigade.id} stays in battle")
            else:
                brigade.is_routed = True
                self.log(f"{brigade.id} routs!")
        
        for brigade in army2:
            rally_roll = self.roll_dice()[0] + brigade.get_rally_bonus()
            # Apply terrain effects
            if "rally_penalty" in terrain_effects:
                rally_roll -= 1
            
            self.log(f"{brigade.id} rally roll: {rally_roll}")
            if rally_roll >= 6:
                new_army2.append(brigade)
                self.log(f"{brigade.id} stays in battle")
            else:
                brigade.is_routed = True
                self.log(f"{brigade.id} routs!")
        
        # Bring in reinforcements up to combat width
        reserve1 = [b for b in full_army1.brigades if b not in army1 and not b.is_routed]
        reserve2 = [b for b in full_army2.brigades if b not in army2 and not b.is_routed]
        
        # Don't bring reinforcements in desert terrain
        if "no_reinforcements" not in terrain_effects:
            needed1 = combat_width - len(new_army1)
            needed2 = combat_width - len(new_army2)
            
            new_army1.extend(reserve1[:needed1])
            new_army2.extend(reserve2[:needed2])
            
            if needed1 > 0:
                self.log(f"Army 1 brings in {min(needed1, len(reserve1))} reinforcements")
            if needed2 > 0:
                self.log(f"Army 2 brings in {min(needed2, len(reserve2))} reinforcements")
        
        return new_army1, new_army2
    
    def _create_battle_result(self, winner: Army, loser: Army, terrain: TerrainType) -> BattleResult:
        """Create battle result and handle action report"""
        self.log("\n=== ACTION REPORT ===")
        
        casualties = {winner.id: [], loser.id: []}
        
        # Destruction rolls for winner (1-2) and loser (1-3)
        for brigade in winner.brigades:
            if not brigade.is_routed:  # Only brigades that fought
                destruction_roll = self.roll_dice()[0]
                if destruction_roll <= 2:
                    casualties[winner.id].append(brigade.id)
                    self.log(f"Winner casualty: {brigade.id} (rolled {destruction_roll})")
        
        for brigade in loser.brigades:
            if not brigade.is_routed:  # Only brigades that fought
                destruction_roll = self.roll_dice()[0]
                if destruction_roll <= 3:
                    casualties[loser.id].append(brigade.id)
                    self.log(f"Loser casualty: {brigade.id} (rolled {destruction_roll})")
        
        # General promotion/capture rolls
        captured_generals = []
        promoted_generals = []
        
        # Winner general gets a free reroll
        winner_roll = self.roll_dice()[0]
        if winner_roll == 1:
            self.log(f"{winner.general.name} rolled 1, rerolling...")
            winner_roll = self.roll_dice()[0]
        
        if winner_roll == 6:
            winner.general.level = min(5, winner.general.level + 1)
            promoted_generals.append(winner.general.name)
            self.log(f"{winner.general.name} promoted to level {winner.general.level}!")
        
        # Loser general
        loser_roll = self.roll_dice()[0]
        if loser_roll == 1:
            loser.general.is_captured = True
            captured_generals.append(loser.general.name)
            self.log(f"{loser.general.name} captured!")
        elif loser_roll == 6:
            loser.general.level = min(5, loser.general.level + 1)
            promoted_generals.append(loser.general.name)
            self.log(f"{loser.general.name} promoted to level {loser.general.level}!")
        
        return BattleResult(
            winner=winner.general.name,
            loser=loser.general.name,
            casualties=casualties,
            captured_generals=captured_generals,
            promoted_generals=promoted_generals,
            terrain=terrain
        )

class NavalBattleEngine:
    def __init__(self):
        self.battle_log = []
    
    def log(self, message: str):
        """Add message to battle log"""
        self.battle_log.append(message)
        print(message)
    
    def clear_log(self):
        """Clear the battle log"""
        self.battle_log = []
    
    def roll_dice(self, count: int = 1, sides: int = 6) -> List[int]:
        """Roll dice and return results"""
        return [random.randint(1, sides) for _ in range(count)]
    
    def simulate_naval_battle(self, armada1: Armada, armada2: Armada, sea_terrain: SeaTerrainType) -> NavalBattleResult:
        """Simulate a complete naval battle between two armadas"""
        self.clear_log()
        self.log(f"=== NAVAL BATTLE ===")
        self.log(f"Armada 1 ({armada1.admiral.name}): {len(armada1.ships)} ships")
        self.log(f"Armada 2 ({armada2.admiral.name}): {len(armada2.ships)} ships")
        self.log(f"Sea Terrain: {sea_terrain.value}")
        
        # Get terrain effects
        terrain_data = SEA_TERRAIN_EFFECTS[sea_terrain]
        combat_width = terrain_data["combat_width"]
        victory_limit = terrain_data["victory_limit"]
        
        self.log(f"Combat Width: {combat_width}, Victory Limit: {victory_limit}")
        
        # Track victories
        victories = {armada1.id: 0, armada2.id: 0}
        
        # Available ships
        ships1 = armada1.ships.copy()
        ships2 = armada2.ships.copy()
        
        round_count = 0
        max_rounds = 10
        
        while round_count < max_rounds and max(victories.values()) < victory_limit // 2:
            round_count += 1
            self.log(f"\n--- Naval Round {round_count} ---")
            
            # Determine active ships
            active_ships1 = ships1[:min(combat_width, len(ships1))]
            active_ships2 = ships2[:min(combat_width, len(ships2))]
            
            if not active_ships1 or not active_ships2:
                break
            
            # Create matchups
            matchups = self._create_matchups(active_ships1, active_ships2)
            
            # Resolve each matchup
            for ship1, ship2 in matchups:
                result = self._resolve_ship_combat(ship1, ship2)
                
                if result == "ship1_wins":
                    victories[armada1.id] += 1
                    ships2.remove(ship2)
                    self.log(f"{ship1.id} defeats {ship2.id}!")
                elif result == "ship2_wins":
                    victories[armada2.id] += 1
                    ships1.remove(ship1)
                    self.log(f"{ship2.id} defeats {ship1.id}!")
                elif result == "both_retreat":
                    # Both ships go to reserve
                    pass
            
            self.log(f"Victories: {armada1.admiral.name} {victories[armada1.id]}, {armada2.admiral.name} {victories[armada2.id]}")
            
            # Check for victory
            if victories[armada1.id] > victory_limit // 2:
                return self._create_naval_result(armada1, armada2, sea_terrain, ships1, ships2)
            elif victories[armada2.id] > victory_limit // 2:
                return self._create_naval_result(armada2, armada1, sea_terrain, ships2, ships1)
        
        # Inconclusive battle
        self.log("Naval battle ends inconclusively!")
        return NavalBattleResult("Inconclusive", "Inconclusive", {}, {}, {}, sea_terrain)
    
    def _create_matchups(self, ships1: List[Ship], ships2: List[Ship]) -> List[Tuple[Ship, Ship]]:
        """Create random matchups between ships"""
        matchups = []
        min_ships = min(len(ships1), len(ships2))
        
        # Randomly pair ships
        paired_ships1 = random.sample(ships1, min_ships)
        paired_ships2 = random.sample(ships2, min_ships)
        
        for i in range(min_ships):
            matchups.append((paired_ships1[i], paired_ships2[i]))
        
        return matchups
    
    def _resolve_ship_combat(self, ship1: Ship, ship2: Ship) -> str:
        """Resolve combat between two ships"""
        self.log(f"\nShip Combat: {ship1.id} vs {ship2.id}")
        
        range_band = 2  # Start at range 2
        max_rounds = 5
        
        for round_num in range(max_rounds):
            self.log(f"Round {round_num + 1}, Range {range_band}")
            
            # Maneuver phase
            maneuver1 = self.roll_dice()[0] + ship1.get_maneuver_bonus()
            maneuver2 = self.roll_dice()[0] + ship2.get_maneuver_bonus()
            
            self.log(f"Maneuver: {ship1.id} ({maneuver1}) vs {ship2.id} ({maneuver2})")
            
            if maneuver1 > maneuver2:
                # Ship1 wins maneuver, can choose range
                if range_band > 1:
                    range_band -= 1  # Close distance
                    self.log(f"{ship1.id} closes to range {range_band}")
            elif maneuver2 > maneuver1:
                # Ship2 wins maneuver
                if range_band < 4:
                    range_band += 1  # Increase distance
                    self.log(f"{ship2.id} increases range to {range_band}")
            
            # Check for retreat or boarding
            if range_band >= 4:
                self.log("Ships disengage!")
                return "both_retreat"
            elif range_band == 0:
                # Boarding action
                return self._resolve_boarding(ship1, ship2)
            
            # Gunnery phase
            hit1, hit2 = self._resolve_gunnery(ship1, ship2, range_band)
            
            # Damage reports
            if hit1:
                damage_result = self._resolve_damage(ship2)
                if damage_result == "sunk":
                    return "ship1_wins"
            
            if hit2:
                damage_result = self._resolve_damage(ship1)
                if damage_result == "sunk":
                    return "ship2_wins"
        
        # Combat ends inconclusively
        return "both_retreat"
    
    def _resolve_gunnery(self, ship1: Ship, ship2: Ship, range_band: int) -> Tuple[bool, bool]:
        """Resolve gunnery exchange"""
        gunnery1 = self.roll_dice()[0] + ship1.get_gunnery_bonus(range_band)
        gunnery2 = self.roll_dice()[0] + ship2.get_gunnery_bonus(range_band)
        
        hit1 = gunnery1 >= 5
        hit2 = gunnery2 >= 5
        
        self.log(f"Gunnery: {ship1.id} ({gunnery1}) {'HIT' if hit1 else 'MISS'}, {ship2.id} ({gunnery2}) {'HIT' if hit2 else 'MISS'}")
        
        return hit1, hit2
    
    def _resolve_boarding(self, ship1: Ship, ship2: Ship) -> str:
        """Resolve boarding action"""
        self.log("BOARDING ACTION!")
        
        boarding1 = self.roll_dice()[0] + ship1.get_boarding_bonus()
        boarding2 = self.roll_dice()[0] + ship2.get_boarding_bonus()
        
        self.log(f"Boarding: {ship1.id} ({boarding1}) vs {ship2.id} ({boarding2})")
        
        if boarding1 >= boarding2 + 3:
            self.log(f"{ship1.id} captures {ship2.id}!")
            return "ship1_wins"
        elif boarding2 >= boarding1 + 3:
            self.log(f"{ship2.id} captures {ship1.id}!")
            return "ship2_wins"
        else:
            self.log("Boarding fails, combat continues")
            return "continue"
    
    def _resolve_damage(self, ship: Ship) -> str:
        """Resolve damage to a ship"""
        damage_roll = self.roll_dice()[0]
        
        # Apply ship enhancements
        if ship.enhancement == "Reinforced Hulls":
            damage_roll += 1
        
        if damage_roll >= 6:
            self.log(f"{ship.id}: Glancing blow")
            return "glancing"
        elif damage_roll == 5:
            self.log(f"{ship.id}: Blasted deck (-1 boarding)")
            ship.damage_effects.append("blasted_deck")
            return "damaged"
        elif damage_roll == 4:
            self.log(f"{ship.id}: Ammunition strike (-2 gunnery)")
            ship.damage_effects.append("ammunition_strike")
            return "damaged"
        elif damage_roll == 3:
            self.log(f"{ship.id}: Raking fire (-1 next damage)")
            ship.damage_effects.append("raking_fire")
            return "damaged"
        elif damage_roll == 2:
            self.log(f"{ship.id}: Hull breach (fail maneuver, -2 damage)")
            ship.damage_effects.append("hull_breach")
            return "damaged"
        elif damage_roll == 1:
            self.log(f"{ship.id}: Critical hit (-4 next damage)")
            ship.damage_effects.append("critical_hit")
            return "damaged"
        else:  # 0 or below
            self.log(f"{ship.id}: SUNK!")
            return "sunk"
    
    def _create_naval_result(self, winner: Armada, loser: Armada, terrain: SeaTerrainType, 
                           winner_ships: List[Ship], loser_ships: List[Ship]) -> NavalBattleResult:
        """Create naval battle result"""
        self.log(f"\n{winner.admiral.name} wins the naval battle!")
        
        sunk_ships = {
            winner.id: [ship.id for ship in winner.ships if ship not in winner_ships],
            loser.id: [ship.id for ship in loser.ships if ship not in loser_ships]
        }
        
        return NavalBattleResult(
            winner=winner.admiral.name,
            loser=loser.admiral.name,
            sunk_ships=sunk_ships,
            captured_ships={},
            retreated_ships={},
            sea_terrain=terrain
        )
