import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import random
from models import *
from battle_engine import BattleEngine, NavalBattleEngine

class BattleSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Land and Naval Battle Simulator")
        self.root.geometry("1200x800")
        
        # Battle engines
        self.land_engine = BattleEngine()
        self.naval_engine = NavalBattleEngine()
        
        # Data storage
        self.armies = {}
        self.armadas = {}
        self.next_id = 1
        
        self.create_widgets()
        self.create_sample_data()
    
    def create_widgets(self):
        """Create the main GUI widgets"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Land Battle Tab
        self.land_frame = ttk.Frame(notebook)
        notebook.add(self.land_frame, text="Land Battles")
        self.create_land_battle_widgets()
        
        # Naval Battle Tab
        self.naval_frame = ttk.Frame(notebook)
        notebook.add(self.naval_frame, text="Naval Battles")
        self.create_naval_battle_widgets()
        
        # Army Management Tab
        self.army_frame = ttk.Frame(notebook)
        notebook.add(self.army_frame, text="Army Management")
        self.create_army_management_widgets()
        
        # Fleet Management Tab
        self.fleet_frame = ttk.Frame(notebook)
        notebook.add(self.fleet_frame, text="Fleet Management")
        self.create_fleet_management_widgets()
    
    def create_land_battle_widgets(self):
        """Create widgets for land battle simulation"""
        # Army selection
        selection_frame = ttk.LabelFrame(self.land_frame, text="Battle Setup")
        selection_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(selection_frame, text="Army 1:").grid(row=0, column=0, padx=5, pady=5)
        self.army1_var = tk.StringVar()
        self.army1_combo = ttk.Combobox(selection_frame, textvariable=self.army1_var, state="readonly")
        self.army1_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(selection_frame, text="Army 2:").grid(row=0, column=2, padx=5, pady=5)
        self.army2_var = tk.StringVar()
        self.army2_combo = ttk.Combobox(selection_frame, textvariable=self.army2_var, state="readonly")
        self.army2_combo.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(selection_frame, text="Terrain:").grid(row=1, column=0, padx=5, pady=5)
        self.terrain_var = tk.StringVar(value="plains")
        self.terrain_combo = ttk.Combobox(selection_frame, textvariable=self.terrain_var, 
                                         values=[t.value for t in TerrainType], state="readonly")
        self.terrain_combo.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(selection_frame, text="Simulate Battle", 
                  command=self.simulate_land_battle).grid(row=1, column=2, padx=5, pady=5)
        
        ttk.Button(selection_frame, text="Clear Log", 
                  command=self.clear_land_log).grid(row=1, column=3, padx=5, pady=5)
        
        # Battle log
        log_frame = ttk.LabelFrame(self.land_frame, text="Battle Log")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.land_log = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=20)
        self.land_log.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_naval_battle_widgets(self):
        """Create widgets for naval battle simulation"""
        # Armada selection
        selection_frame = ttk.LabelFrame(self.naval_frame, text="Naval Battle Setup")
        selection_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(selection_frame, text="Armada 1:").grid(row=0, column=0, padx=5, pady=5)
        self.armada1_var = tk.StringVar()
        self.armada1_combo = ttk.Combobox(selection_frame, textvariable=self.armada1_var, state="readonly")
        self.armada1_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(selection_frame, text="Armada 2:").grid(row=0, column=2, padx=5, pady=5)
        self.armada2_var = tk.StringVar()
        self.armada2_combo = ttk.Combobox(selection_frame, textvariable=self.armada2_var, state="readonly")
        self.armada2_combo.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(selection_frame, text="Sea Terrain:").grid(row=1, column=0, padx=5, pady=5)
        self.sea_terrain_var = tk.StringVar(value="open_seas")
        self.sea_terrain_combo = ttk.Combobox(selection_frame, textvariable=self.sea_terrain_var, 
                                            values=[t.value for t in SeaTerrainType], state="readonly")
        self.sea_terrain_combo.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(selection_frame, text="Simulate Naval Battle", 
                  command=self.simulate_naval_battle).grid(row=1, column=2, padx=5, pady=5)
        
        ttk.Button(selection_frame, text="Clear Log", 
                  command=self.clear_naval_log).grid(row=1, column=3, padx=5, pady=5)
        
        # Battle log
        log_frame = ttk.LabelFrame(self.naval_frame, text="Naval Battle Log")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.naval_log = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=20)
        self.naval_log.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_army_management_widgets(self):
        """Create widgets for army management"""
        # Army creation
        creation_frame = ttk.LabelFrame(self.army_frame, text="Create Army")
        creation_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(creation_frame, text="General Name:").grid(row=0, column=0, padx=5, pady=5)
        self.general_name_var = tk.StringVar()
        ttk.Entry(creation_frame, textvariable=self.general_name_var).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(creation_frame, text="Number of Brigades:").grid(row=0, column=2, padx=5, pady=5)
        self.brigade_count_var = tk.IntVar(value=5)
        ttk.Spinbox(creation_frame, from_=1, to=20, textvariable=self.brigade_count_var).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Button(creation_frame, text="Create Army", 
                  command=self.create_army).grid(row=0, column=4, padx=5, pady=5)
        
        # Army list
        list_frame = ttk.LabelFrame(self.army_frame, text="Existing Armies")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview for armies
        self.army_tree = ttk.Treeview(list_frame, columns=("General", "Level", "Trait", "Brigades"), show="tree headings")
        self.army_tree.heading("#0", text="Army ID")
        self.army_tree.heading("General", text="General")
        self.army_tree.heading("Level", text="Level")
        self.army_tree.heading("Trait", text="Trait")
        self.army_tree.heading("Brigades", text="Brigades")
        
        army_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.army_tree.yview)
        self.army_tree.configure(yscrollcommand=army_scrollbar.set)
        
        self.army_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        army_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Army details
        details_frame = ttk.LabelFrame(self.army_frame, text="Army Details")
        details_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(details_frame, text="Delete Selected Army", 
                  command=self.delete_army).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(details_frame, text="Refresh List", 
                  command=self.refresh_army_list).pack(side=tk.LEFT, padx=5, pady=5)
    
    def create_fleet_management_widgets(self):
        """Create widgets for fleet management"""
        # Fleet creation
        creation_frame = ttk.LabelFrame(self.fleet_frame, text="Create Armada")
        creation_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(creation_frame, text="Admiral Name:").grid(row=0, column=0, padx=5, pady=5)
        self.admiral_name_var = tk.StringVar()
        ttk.Entry(creation_frame, textvariable=self.admiral_name_var).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(creation_frame, text="Number of Ships:").grid(row=0, column=2, padx=5, pady=5)
        self.ship_count_var = tk.IntVar(value=3)
        ttk.Spinbox(creation_frame, from_=1, to=10, textvariable=self.ship_count_var).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Button(creation_frame, text="Create Armada", 
                  command=self.create_armada).grid(row=0, column=4, padx=5, pady=5)
        
        # Fleet list
        list_frame = ttk.LabelFrame(self.fleet_frame, text="Existing Armadas")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview for armadas
        self.fleet_tree = ttk.Treeview(list_frame, columns=("Admiral", "Trait", "Ships"), show="tree headings")
        self.fleet_tree.heading("#0", text="Armada ID")
        self.fleet_tree.heading("Admiral", text="Admiral")
        self.fleet_tree.heading("Trait", text="Trait")
        self.fleet_tree.heading("Ships", text="Ships")
        
        fleet_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.fleet_tree.yview)
        self.fleet_tree.configure(yscrollcommand=fleet_scrollbar.set)
        
        self.fleet_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        fleet_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Fleet details
        details_frame = ttk.LabelFrame(self.fleet_frame, text="Armada Details")
        details_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(details_frame, text="Delete Selected Armada", 
                  command=self.delete_armada).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(details_frame, text="Refresh List", 
                  command=self.refresh_fleet_list).pack(side=tk.LEFT, padx=5, pady=5)
    
    def create_sample_data(self):
        """Create some sample armies and armadas for testing"""
        # Create sample armies
        self.create_sample_army("Alexander", 8, "Bold")
        self.create_sample_army("Napoleon", 6, "Brilliant")
        self.create_sample_army("Caesar", 10, "Disciplined")
        
        # Create sample armadas
        self.create_sample_armada("Nelson", 5, "Accurate")
        self.create_sample_armada("Drake", 4, "Daring")
        self.create_sample_armada("Barbarossa", 6, "Experienced")
        
        self.refresh_army_list()
        self.refresh_fleet_list()
        self.update_combo_boxes()
    
    def create_sample_army(self, general_name: str, brigade_count: int, trait_name: str):
        """Create a sample army with specified parameters"""
        army_id = f"army_{self.next_id}"
        self.next_id += 1
        
        # Create general with specified trait
        trait = next((t for t in GENERAL_TRAITS if t.name == trait_name), random.choice(GENERAL_TRAITS))
        general = General(
            id=f"gen_{army_id}",
            name=general_name,
            level=random.randint(1, 3),
            trait=trait
        )
        
        # Create brigades
        brigades = []
        for i in range(brigade_count):
            brigade_type = random.choice(list(BrigadeType))
            brigade = Brigade(
                id=f"brigade_{army_id}_{i}",
                type=brigade_type,
                is_mercenary=random.choice([True, False])
            )
            
            # Randomly add enhancements
            if random.random() < 0.3:  # 30% chance of enhancement
                if brigade_type == BrigadeType.CAVALRY:
                    enhancement = random.choice(list(CAVALRY_ENHANCEMENTS.values()))
                elif brigade_type == BrigadeType.HEAVY:
                    enhancement = random.choice(list(HEAVY_ENHANCEMENTS.values()))
                else:  # LIGHT
                    enhancement = random.choice(list(LIGHT_ENHANCEMENTS.values()))
                brigade.enhancement = enhancement
            
            brigades.append(brigade)
        
        # Create army
        army = Army(
            id=army_id,
            general=general,
            brigades=brigades
        )
        
        self.armies[army_id] = army
    
    def create_sample_armada(self, admiral_name: str, ship_count: int, trait_name: str):
        """Create a sample armada with specified parameters"""
        armada_id = f"armada_{self.next_id}"
        self.next_id += 1
        
        # Create admiral with specified trait
        trait = next((t for t in ADMIRAL_TRAITS if t.name == trait_name), random.choice(ADMIRAL_TRAITS))
        admiral = Admiral(
            id=f"adm_{armada_id}",
            name=admiral_name,
            trait=trait
        )
        
        # Create ships
        ships = []
        enhancements = ["Additional Firepower", "Additional Propulsion", "Marine Detachment", 
                       "Reinforced Hulls", None]
        
        for i in range(ship_count):
            ship = Ship(
                id=f"ship_{armada_id}_{i}",
                enhancement=random.choice(enhancements),
                flag=FlagType.NATIONAL
            )
            ships.append(ship)
        
        # Set flagship (first ship)
        if ships:
            ships[0].is_flagship = True
            admiral.flagship = ships[0]
        
        # Create armada
        armada = Armada(
            id=armada_id,
            admiral=admiral,
            ships=ships
        )
        
        self.armadas[armada_id] = armada
    
    def create_army(self):
        """Create a new army from GUI inputs"""
        general_name = self.general_name_var.get().strip()
        if not general_name:
            messagebox.showerror("Error", "Please enter a general name")
            return
        
        brigade_count = self.brigade_count_var.get()
        
        army_id = f"army_{self.next_id}"
        self.next_id += 1
        
        # Create general with random trait
        general = General(
            id=f"gen_{army_id}",
            name=general_name,
            level=1,
            trait=random.choice(GENERAL_TRAITS)
        )
        
        # Create brigades
        brigades = []
        for i in range(brigade_count):
            brigade_type = random.choice(list(BrigadeType))
            brigade = Brigade(
                id=f"brigade_{army_id}_{i}",
                type=brigade_type
            )
            brigades.append(brigade)
        
        # Create army
        army = Army(
            id=army_id,
            general=general,
            brigades=brigades
        )
        
        self.armies[army_id] = army
        self.refresh_army_list()
        self.update_combo_boxes()
        
        # Clear input
        self.general_name_var.set("")
        
        messagebox.showinfo("Success", f"Army created with {len(brigades)} brigades under General {general_name}")
    
    def create_armada(self):
        """Create a new armada from GUI inputs"""
        admiral_name = self.admiral_name_var.get().strip()
        if not admiral_name:
            messagebox.showerror("Error", "Please enter an admiral name")
            return
        
        ship_count = self.ship_count_var.get()
        
        armada_id = f"armada_{self.next_id}"
        self.next_id += 1
        
        # Create admiral with random trait
        admiral = Admiral(
            id=f"adm_{armada_id}",
            name=admiral_name,
            trait=random.choice(ADMIRAL_TRAITS)
        )
        
        # Create ships
        ships = []
        for i in range(ship_count):
            ship = Ship(
                id=f"ship_{armada_id}_{i}",
                flag=FlagType.NATIONAL
            )
            ships.append(ship)
        
        # Set flagship
        if ships:
            ships[0].is_flagship = True
            admiral.flagship = ships[0]
        
        # Create armada
        armada = Armada(
            id=armada_id,
            admiral=admiral,
            ships=ships
        )
        
        self.armadas[armada_id] = armada
        self.refresh_fleet_list()
        self.update_combo_boxes()
        
        # Clear input
        self.admiral_name_var.set("")
        
        messagebox.showinfo("Success", f"Armada created with {len(ships)} ships under Admiral {admiral_name}")
    
    def refresh_army_list(self):
        """Refresh the army list display"""
        for item in self.army_tree.get_children():
            self.army_tree.delete(item)
        
        for army_id, army in self.armies.items():
            trait_name = army.general.trait.name if army.general.trait else "None"
            self.army_tree.insert("", "end", text=army_id, values=(
                army.general.name,
                army.general.level,
                trait_name,
                len(army.brigades)
            ))
    
    def refresh_fleet_list(self):
        """Refresh the fleet list display"""
        for item in self.fleet_tree.get_children():
            self.fleet_tree.delete(item)
        
        for armada_id, armada in self.armadas.items():
            trait_name = armada.admiral.trait.name if armada.admiral.trait else "None"
            self.fleet_tree.insert("", "end", text=armada_id, values=(
                armada.admiral.name,
                trait_name,
                len(armada.ships)
            ))
    
    def update_combo_boxes(self):
        """Update the combo boxes with current armies and armadas"""
        army_names = [f"{army.general.name} ({army_id})" for army_id, army in self.armies.items()]
        self.army1_combo['values'] = army_names
        self.army2_combo['values'] = army_names
        
        armada_names = [f"{armada.admiral.name} ({armada_id})" for armada_id, armada in self.armadas.items()]
        self.armada1_combo['values'] = armada_names
        self.armada2_combo['values'] = armada_names
    
    def delete_army(self):
        """Delete selected army"""
        selection = self.army_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an army to delete")
            return
        
        army_id = self.army_tree.item(selection[0])['text']
        if army_id in self.armies:
            del self.armies[army_id]
            self.refresh_army_list()
            self.update_combo_boxes()
            messagebox.showinfo("Success", "Army deleted")
    
    def delete_armada(self):
        """Delete selected armada"""
        selection = self.fleet_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an armada to delete")
            return
        
        armada_id = self.fleet_tree.item(selection[0])['text']
        if armada_id in self.armadas:
            del self.armadas[armada_id]
            self.refresh_fleet_list()
            self.update_combo_boxes()
            messagebox.showinfo("Success", "Armada deleted")
    
    def simulate_land_battle(self):
        """Simulate a land battle between selected armies"""
        army1_selection = self.army1_var.get()
        army2_selection = self.army2_var.get()
        
        if not army1_selection or not army2_selection:
            messagebox.showerror("Error", "Please select both armies")
            return
        
        if army1_selection == army2_selection:
            messagebox.showerror("Error", "Please select different armies")
            return
        
        # Extract army IDs from selection
        army1_id = army1_selection.split('(')[1].rstrip(')')
        army2_id = army2_selection.split('(')[1].rstrip(')')
        
        army1 = self.armies[army1_id]
        army2 = self.armies[army2_id]
        
        # Get terrain
        terrain_str = self.terrain_var.get()
        terrain = TerrainType(terrain_str)
        
        # Simulate battle
        try:
            result = self.land_engine.simulate_land_battle(army1, army2, terrain)
            
            # Display results
            self.display_land_battle_log()
            
            # Show summary
            summary = f"Battle Result: {result.winner} defeats {result.loser}\n"
            summary += f"Terrain: {result.terrain.value}\n"
            summary += f"Casualties: {len(result.casualties.get(army1.id, []))} vs {len(result.casualties.get(army2.id, []))}\n"
            if result.promoted_generals:
                summary += f"Promoted: {', '.join(result.promoted_generals)}\n"
            if result.captured_generals:
                summary += f"Captured: {', '.join(result.captured_generals)}\n"
            
            messagebox.showinfo("Battle Complete", summary)
            
        except Exception as e:
            messagebox.showerror("Error", f"Battle simulation failed: {str(e)}")
    
    def simulate_naval_battle(self):
        """Simulate a naval battle between selected armadas"""
        armada1_selection = self.armada1_var.get()
        armada2_selection = self.armada2_var.get()
        
        if not armada1_selection or not armada2_selection:
            messagebox.showerror("Error", "Please select both armadas")
            return
        
        if armada1_selection == armada2_selection:
            messagebox.showerror("Error", "Please select different armadas")
            return
        
        # Extract armada IDs from selection
        armada1_id = armada1_selection.split('(')[1].rstrip(')')
        armada2_id = armada2_selection.split('(')[1].rstrip(')')
        
        armada1 = self.armadas[armada1_id]
        armada2 = self.armadas[armada2_id]
        
        # Get sea terrain
        sea_terrain_str = self.sea_terrain_var.get()
        sea_terrain = SeaTerrainType(sea_terrain_str)
        
        # Simulate battle
        try:
            result = self.naval_engine.simulate_naval_battle(armada1, armada2, sea_terrain)
            
            # Display results
            self.display_naval_battle_log()
            
            # Show summary
            summary = f"Naval Battle Result: {result.winner} defeats {result.loser}\n"
            summary += f"Sea Terrain: {result.sea_terrain.value}\n"
            summary += f"Sunk Ships: {len(result.sunk_ships.get(armada1.id, []))} vs {len(result.sunk_ships.get(armada2.id, []))}\n"
            
            messagebox.showinfo("Naval Battle Complete", summary)
            
        except Exception as e:
            messagebox.showerror("Error", f"Naval battle simulation failed: {str(e)}")
    
    def display_land_battle_log(self):
        """Display the land battle log in the text widget"""
        self.land_log.delete(1.0, tk.END)
        for message in self.land_engine.battle_log:
            self.land_log.insert(tk.END, message + "\n")
        self.land_log.see(tk.END)
    
    def display_naval_battle_log(self):
        """Display the naval battle log in the text widget"""
        self.naval_log.delete(1.0, tk.END)
        for message in self.naval_engine.battle_log:
            self.naval_log.insert(tk.END, message + "\n")
        self.naval_log.see(tk.END)
    
    def clear_land_log(self):
        """Clear the land battle log"""
        self.land_log.delete(1.0, tk.END)
        self.land_engine.clear_log()
    
    def clear_naval_log(self):
        """Clear the naval battle log"""
        self.naval_log.delete(1.0, tk.END)
        self.naval_engine.clear_log()

def main():
    root = tk.Tk()
    app = BattleSimulatorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
