#!/usr/bin/env python3
"""
Enhanced Battle Simulator GUI with Graphs and Visual Analytics
Features colorful charts, real-time battle visualization, and statistical analysis
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import sys
import os
from collections import defaultdict, Counter
import threading
import queue
import time
import warnings

# Suppress matplotlib warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", message="invalid value encountered in divide")

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from models import *
from battle_engine import BattleEngine, NavalBattleEngine

class EnhancedBattleSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🏛️ Enhanced Battle Simulator with Analytics 🏛️")
        self.root.geometry("1200x800")
        self.root.configure(bg="#2c3e50")
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Custom colors
        self.colors = {
            'primary': '#3498db',
            'secondary': '#e74c3c',
            'success': '#2ecc71',
            'warning': '#f39c12',
            'info': '#9b59b6',
            'dark': '#2c3e50',
            'light': '#ecf0f1'
        }
        
        # Battle engines
        self.land_engine = BattleEngine()
        self.naval_engine = NavalBattleEngine()
        
        # Custom armies storage
        self.custom_armies = {}
        self.saved_armies_list = []
        
        # Battle statistics
        self.battle_stats = {
            'land_battles': [],
            'naval_battles': [],
            'terrain_performance': defaultdict(lambda: defaultdict(int)),
            'trait_wins': defaultdict(int),
            'enhancement_usage': defaultdict(int)
        }
        
        # Create GUI
        self.create_enhanced_widgets()
        
        # Queue for thread communication
        self.battle_queue = queue.Queue()
        self.check_queue()
    
    def create_enhanced_widgets(self):
        """Create enhanced GUI with tabs and graphs"""
        
        # Main notebook with custom styling
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_battle_simulator_tab()
        self.create_analytics_tab()
        self.create_mass_simulation_tab()
        self.create_army_builder_tab()
        
        # Initialize custom army lists
        self.update_custom_army_lists()
        
    def create_battle_simulator_tab(self):
        """Enhanced battle simulator with real-time visualization"""
        
        battle_frame = ttk.Frame(self.notebook)
        self.notebook.add(battle_frame, text="🗡️ Battle Simulator")
        
        # Left panel - Controls
        left_panel = ttk.Frame(battle_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Battle type selection
        ttk.Label(left_panel, text="Battle Type:", font=("Arial", 12, "bold")).pack(pady=5)
        self.battle_type = tk.StringVar(value="Land")
        battle_type_frame = ttk.Frame(left_panel)
        battle_type_frame.pack(pady=5)
        ttk.Radiobutton(battle_type_frame, text="🏞️ Land Battle", variable=self.battle_type, value="Land").pack(anchor=tk.W)
        ttk.Radiobutton(battle_type_frame, text="⚓ Naval Battle", variable=self.battle_type, value="Naval").pack(anchor=tk.W)
        
        # Army configuration
        ttk.Label(left_panel, text="Army Configuration:", font=("Arial", 12, "bold")).pack(pady=(20,5))
        
        # Army selection mode
        army_mode_frame = ttk.LabelFrame(left_panel, text="Army Selection Mode")
        army_mode_frame.pack(fill=tk.X, pady=5)
        
        self.army_mode = tk.StringVar(value="Random")
        ttk.Radiobutton(army_mode_frame, text="🎲 Random Armies", variable=self.army_mode, value="Random").pack(anchor=tk.W)
        ttk.Radiobutton(army_mode_frame, text="🏗️ Custom Armies", variable=self.army_mode, value="Custom").pack(anchor=tk.W)
        
        # Random army configuration
        random_frame = ttk.LabelFrame(left_panel, text="Random Army Settings")
        random_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(random_frame, text="Army Size:").pack(anchor=tk.W)
        self.army_size = tk.IntVar(value=8)
        size_frame = ttk.Frame(random_frame)
        size_frame.pack(fill=tk.X, pady=2)
        ttk.Scale(size_frame, from_=3, to=15, variable=self.army_size, orient=tk.HORIZONTAL).pack(fill=tk.X)
        ttk.Label(size_frame, textvariable=self.army_size).pack()
        
        # Custom army selection
        custom_frame = ttk.LabelFrame(left_panel, text="Custom Army Selection")
        custom_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(custom_frame, text="Red Army:").pack(anchor=tk.W)
        self.red_army_var = tk.StringVar()
        self.red_army_combo = ttk.Combobox(custom_frame, textvariable=self.red_army_var, state="readonly")
        self.red_army_combo.pack(fill=tk.X, pady=2)
        
        ttk.Label(custom_frame, text="Blue Army:").pack(anchor=tk.W, pady=(5,0))
        self.blue_army_var = tk.StringVar()
        self.blue_army_combo = ttk.Combobox(custom_frame, textvariable=self.blue_army_var, state="readonly")
        self.blue_army_combo.pack(fill=tk.X, pady=2)
        
        # Update custom armies button
        update_armies_btn = tk.Button(custom_frame, text="🔄 Refresh Army List", 
                                    command=self.update_custom_army_lists,
                                    bg=self.colors['info'], fg='white', font=("Arial", 8))
        update_armies_btn.pack(pady=5)
        
        # Terrain selection
        ttk.Label(left_panel, text="Terrain:").pack(anchor=tk.W, pady=(10,0))
        self.terrain_var = tk.StringVar()
        terrain_combo = ttk.Combobox(left_panel, textvariable=self.terrain_var, state="readonly")
        terrain_combo['values'] = [terrain.value for terrain in TerrainType]
        terrain_combo.current(0)
        terrain_combo.pack(fill=tk.X, pady=2)
        
        # Battle buttons
        button_frame = ttk.Frame(left_panel)
        button_frame.pack(pady=20)
        
        simulate_btn = tk.Button(
            button_frame, 
            text="⚔️ Simulate Battle", 
            command=self.simulate_single_battle,
            bg=self.colors['primary'], 
            fg='white',
            font=("Arial", 10, "bold"),
            height=2
        )
        simulate_btn.pack(fill=tk.X, pady=2)
        
        random_btn = tk.Button(
            button_frame, 
            text="🎲 Random Quick Battle", 
            command=self.simulate_random_battle,
            bg=self.colors['success'], 
            fg='white',
            font=("Arial", 10, "bold")
        )
        random_btn.pack(fill=tk.X, pady=2)
        
        clear_btn = tk.Button(
            button_frame, 
            text="🗑️ Clear Results", 
            command=self.clear_battle_results,
            bg=self.colors['warning'], 
            fg='white',
            font=("Arial", 10, "bold")
        )
        clear_btn.pack(fill=tk.X, pady=2)
        
        # Right panel - Battle visualization
        right_panel = ttk.Frame(battle_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Battle results with tabs
        result_notebook = ttk.Notebook(right_panel)
        result_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Battle log tab
        log_frame = ttk.Frame(result_notebook)
        result_notebook.add(log_frame, text="📜 Battle Log")
        
        self.battle_log = scrolledtext.ScrolledText(
            log_frame, 
            wrap=tk.WORD, 
            height=15,
            bg="#1e1e1e", 
            fg="#ffffff",
            font=("Consolas", 10)
        )
        self.battle_log.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Battle visualization tab
        viz_frame = ttk.Frame(result_notebook)
        result_notebook.add(viz_frame, text="📊 Battle Visualization")
        
        # Create matplotlib figure for battle visualization
        self.battle_fig = Figure(figsize=(8, 6), facecolor='#2c3e50')
        self.battle_canvas = FigureCanvasTkAgg(self.battle_fig, viz_frame)
        self.battle_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def create_analytics_tab(self):
        """Advanced analytics with multiple charts"""
        
        analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(analytics_frame, text="📈 Analytics Dashboard")
        
        # Create matplotlib figure with subplots
        self.analytics_fig = Figure(figsize=(12, 8), facecolor='#2c3e50')
        self.analytics_canvas = FigureCanvasTkAgg(self.analytics_fig, analytics_frame)
        self.analytics_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Control panel for analytics
        control_frame = ttk.Frame(analytics_frame)
        control_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        
        refresh_btn = tk.Button(
            control_frame, 
            text="🔄 Refresh Analytics", 
            command=self.update_analytics,
            bg=self.colors['info'], 
            fg='white',
            font=("Arial", 10, "bold")
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        export_btn = tk.Button(
            control_frame, 
            text="💾 Export Data", 
            command=self.export_analytics,
            bg=self.colors['secondary'], 
            fg='white',
            font=("Arial", 10, "bold")
        )
        export_btn.pack(side=tk.LEFT, padx=5)
        
        # Initialize analytics
        self.update_analytics()
    
    def create_mass_simulation_tab(self):
        """Mass simulation with progress tracking"""
        
        mass_frame = ttk.Frame(self.notebook)
        self.notebook.add(mass_frame, text="⚡ Mass Simulation")
        
        # Controls
        control_frame = ttk.LabelFrame(mass_frame, text="Simulation Controls")
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Number of battles
        ttk.Label(control_frame, text="Number of Battles:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.mass_battles = tk.IntVar(value=1000)
        battles_spinbox = ttk.Spinbox(control_frame, from_=100, to=10000, textvariable=self.mass_battles, width=10)
        battles_spinbox.grid(row=0, column=1, padx=5, pady=2)
        
        # Army type selection
        ttk.Label(control_frame, text="Army Type:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.mass_army_type = tk.StringVar(value="Random")
        army_type_combo = ttk.Combobox(control_frame, textvariable=self.mass_army_type, width=15, state="readonly")
        army_type_combo['values'] = ["Random", "Custom vs Custom", "Custom vs Random"]
        army_type_combo.grid(row=1, column=1, padx=5, pady=2)
        army_type_combo.bind('<<ComboboxSelected>>', self.on_mass_army_type_change)
        
        # Army size for random armies
        self.mass_army_size_label = ttk.Label(control_frame, text="Army Size:")
        self.mass_army_size_label.grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.mass_army_size = tk.IntVar(value=8)
        self.size_spinbox = ttk.Spinbox(control_frame, from_=3, to=15, textvariable=self.mass_army_size, width=10)
        self.size_spinbox.grid(row=0, column=3, padx=5, pady=2)
        
        # Custom army selection (initially hidden)
        self.army1_label = ttk.Label(control_frame, text="Army 1:")
        self.mass_army1 = tk.StringVar()
        self.army1_combo = ttk.Combobox(control_frame, textvariable=self.mass_army1, width=15, state="readonly")
        
        self.army2_label = ttk.Label(control_frame, text="Army 2:")
        self.mass_army2 = tk.StringVar()
        self.army2_combo = ttk.Combobox(control_frame, textvariable=self.mass_army2, width=15, state="readonly")
        
        # Update custom army lists
        self.update_mass_army_lists()
        
        # Start simulation button
        start_btn = tk.Button(
            control_frame, 
            text="🚀 Start Mass Simulation", 
            command=self.start_mass_simulation,
            bg=self.colors['success'], 
            fg='white',
            font=("Arial", 12, "bold"),
            height=2
        )
        start_btn.grid(row=3, column=0, columnspan=4, pady=10, sticky=tk.EW)
        
        # Progress tracking
        progress_frame = ttk.LabelFrame(mass_frame, text="Progress")
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=5, pady=5)
        
        self.progress_label = ttk.Label(progress_frame, text="Ready to simulate...")
        self.progress_label.pack(pady=2)
        
        # Results visualization
        results_frame = ttk.LabelFrame(mass_frame, text="Mass Simulation Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.mass_fig = Figure(figsize=(10, 6), facecolor='#2c3e50')
        self.mass_canvas = FigureCanvasTkAgg(self.mass_fig, results_frame)
        self.mass_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def on_mass_army_type_change(self, event=None):
        """Handle change in mass simulation army type"""
        army_type = self.mass_army_type.get()
        
        # Hide all optional widgets first
        self.army1_label.grid_remove()
        self.army1_combo.grid_remove()
        self.army2_label.grid_remove()
        self.army2_combo.grid_remove()
        self.mass_army_size_label.grid_remove()
        self.size_spinbox.grid_remove()
        
        if army_type == "Random":
            # Show army size controls
            self.mass_army_size_label.grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
            self.size_spinbox.grid(row=0, column=3, padx=5, pady=2)
        elif army_type == "Custom vs Custom":
            # Show both army selection dropdowns
            self.army1_label.grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
            self.army1_combo.grid(row=2, column=1, padx=5, pady=2)
            self.army2_label.grid(row=2, column=2, sticky=tk.W, padx=5, pady=2)
            self.army2_combo.grid(row=2, column=3, padx=5, pady=2)
        elif army_type == "Custom vs Random":
            # Show one army selection and army size
            self.army1_label.grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
            self.army1_combo.grid(row=2, column=1, padx=5, pady=2)
            self.mass_army_size_label.grid(row=2, column=2, sticky=tk.W, padx=5, pady=2)
            self.size_spinbox.grid(row=2, column=3, padx=5, pady=2)
            
        # Update custom army lists
        self.update_mass_army_lists()
    
    def update_mass_army_lists(self):
        """Update the custom army dropdown lists for mass simulation"""
        army_names = list(self.custom_armies.keys())
        if army_names:
            self.army1_combo['values'] = army_names
            self.army2_combo['values'] = army_names
            if not self.mass_army1.get() and army_names:
                self.mass_army1.set(army_names[0])
            if not self.mass_army2.get() and len(army_names) > 1:
                self.mass_army2.set(army_names[1] if len(army_names) > 1 else army_names[0])
        else:
            self.army1_combo['values'] = ["No custom armies available"]
            self.army2_combo['values'] = ["No custom armies available"]

    def create_army_builder_tab(self):
        """Enhanced army builder with custom army creation and management"""
        
        builder_frame = ttk.Frame(self.notebook)
        self.notebook.add(builder_frame, text="🏗️ Custom Army Builder")
        
        # Split into three sections: builder, preview, saved armies
        left_builder = ttk.LabelFrame(builder_frame, text="🔧 Army Configuration")
        left_builder.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        middle_preview = ttk.LabelFrame(builder_frame, text="👁️ Army Preview")
        middle_preview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        right_saved = ttk.LabelFrame(builder_frame, text="💾 Saved Armies")
        right_saved.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=5, pady=5)
        
        # Army composition visualization
        self.army_fig = Figure(figsize=(6, 8), facecolor='#2c3e50')
        self.army_canvas = FigureCanvasTkAgg(self.army_fig, middle_preview)
        self.army_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Builder controls
        general_frame = ttk.LabelFrame(left_builder, text="👨‍💼 General Configuration")
        general_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Army name
        ttk.Label(general_frame, text="Army Name:").pack(anchor=tk.W)
        self.army_name = tk.StringVar(value="Custom Army")
        name_entry = ttk.Entry(general_frame, textvariable=self.army_name, font=("Arial", 10))
        name_entry.pack(fill=tk.X, pady=2)
        
        # General name
        ttk.Label(general_frame, text="General Name:").pack(anchor=tk.W, pady=(5,0))
        self.general_name = tk.StringVar(value="Custom General")
        general_entry = ttk.Entry(general_frame, textvariable=self.general_name, font=("Arial", 10))
        general_entry.pack(fill=tk.X, pady=2)
        
        ttk.Label(general_frame, text="General Level:").pack(anchor=tk.W, pady=(5,0))
        self.general_level = tk.IntVar(value=3)
        level_frame = ttk.Frame(general_frame)
        level_frame.pack(fill=tk.X, pady=2)
        level_scale = ttk.Scale(level_frame, from_=1, to=5, variable=self.general_level, orient=tk.HORIZONTAL)
        level_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        level_label = ttk.Label(level_frame, textvariable=self.general_level, width=3)
        level_label.pack(side=tk.RIGHT)
        
        ttk.Label(general_frame, text="General Trait:").pack(anchor=tk.W, pady=(5,0))
        self.general_trait = tk.StringVar()
        trait_combo = ttk.Combobox(general_frame, textvariable=self.general_trait, state="readonly")
        trait_combo['values'] = [trait.name for trait in GENERAL_TRAITS]
        trait_combo.current(0)
        trait_combo.pack(fill=tk.X, pady=2)
        
        # Brigade composition with enhanced controls
        brigade_frame = ttk.LabelFrame(left_builder, text="⚔️ Brigade Composition")
        brigade_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Brigade type counters with more detailed controls
        self.brigade_counts = {
            'Heavy': tk.IntVar(value=3),
            'Light': tk.IntVar(value=3),
            'Cavalry': tk.IntVar(value=2)
        }
        
        brigade_info = {
            'Heavy': {'emoji': '🛡️', 'desc': 'Defensive, high armor'},
            'Light': {'emoji': '🏃', 'desc': 'Fast, versatile'},
            'Cavalry': {'emoji': '🐎', 'desc': 'Mobile, high damage'}
        }
        
        for i, (brigade_type, var) in enumerate(self.brigade_counts.items()):
            frame = ttk.LabelFrame(brigade_frame, text=f"{brigade_info[brigade_type]['emoji']} {brigade_type} Infantry")
            frame.pack(fill=tk.X, pady=5, padx=2)
            
            # Description
            desc_label = ttk.Label(frame, text=brigade_info[brigade_type]['desc'], font=("Arial", 8), foreground="gray")
            desc_label.pack(anchor=tk.W)
            
            # Controls frame
            controls_frame = ttk.Frame(frame)
            controls_frame.pack(fill=tk.X, pady=2)
            
            # Minus button
            minus_btn = tk.Button(controls_frame, text="−", width=3, 
                                command=lambda t=brigade_type: self.adjust_brigade_count(t, -1),
                                bg="#e74c3c", fg="white", font=("Arial", 12, "bold"))
            minus_btn.pack(side=tk.LEFT)
            
            # Scale
            scale = ttk.Scale(controls_frame, from_=0, to=15, variable=var, orient=tk.HORIZONTAL, 
                            command=self.update_army_preview)
            scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            
            # Plus button  
            plus_btn = tk.Button(controls_frame, text="+", width=3,
                               command=lambda t=brigade_type: self.adjust_brigade_count(t, 1),
                               bg="#27ae60", fg="white", font=("Arial", 12, "bold"))
            plus_btn.pack(side=tk.RIGHT)
            
            # Count display
            count_label = ttk.Label(controls_frame, textvariable=var, width=3, font=("Arial", 12, "bold"))
            count_label.pack(side=tk.RIGHT, padx=(0, 5))
        
        # Army actions
        action_frame = ttk.Frame(left_builder)
        action_frame.pack(fill=tk.X, pady=10)
        
        # Save army button
        save_btn = tk.Button(
            action_frame, 
            text="💾 Save Custom Army", 
            command=self.save_custom_army,
            bg=self.colors['success'], 
            fg='white',
            font=("Arial", 10, "bold")
        )
        save_btn.pack(side=tk.LEFT, padx=2)
        
        # Update preview button
        update_btn = tk.Button(
            action_frame, 
            text="🔄 Update Preview", 
            command=self.update_army_preview,
            bg=self.colors['primary'], 
            fg='white',
            font=("Arial", 10, "bold")
        )
        update_btn.pack(side=tk.LEFT, padx=2)
        
        # Quick preset buttons
        preset_frame = ttk.LabelFrame(left_builder, text="🎯 Quick Presets")
        preset_frame.pack(fill=tk.X, pady=5)
        
        presets = [
            ("🛡️ Heavy Defense", {"Heavy": 8, "Light": 1, "Cavalry": 1}),
            ("🏃 Light Assault", {"Heavy": 1, "Light": 8, "Cavalry": 1}),
            ("🐎 Cavalry Charge", {"Heavy": 2, "Light": 2, "Cavalry": 6}),
            ("⚖️ Balanced Force", {"Heavy": 3, "Light": 3, "Cavalry": 2})
        ]
        
        for name, composition in presets:
            btn = tk.Button(preset_frame, text=name, 
                          command=lambda comp=composition: self.apply_preset(comp),
                          bg=self.colors['info'], fg='white', font=("Arial", 8))
            btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Saved armies section
        self.create_saved_armies_panel(right_saved)
        
        # Initialize army preview
        self.update_army_preview()
    
    def create_saved_armies_panel(self, parent):
        """Create the saved armies management panel"""
        
        # Saved armies list
        armies_list_frame = ttk.Frame(parent)
        armies_list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        ttk.Label(armies_list_frame, text="📋 Saved Custom Armies", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        # Listbox with scrollbar
        list_frame = ttk.Frame(armies_list_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.armies_listbox = tk.Listbox(list_frame, height=15, font=("Arial", 9))
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.armies_listbox.yview)
        self.armies_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.armies_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.armies_listbox.bind('<<ListboxSelect>>', self.on_army_select)
        
        # Buttons for saved armies
        saved_buttons_frame = ttk.Frame(armies_list_frame)
        saved_buttons_frame.pack(fill=tk.X, pady=5)
        
        load_btn = tk.Button(saved_buttons_frame, text="📥 Load", command=self.load_selected_army,
                           bg=self.colors['primary'], fg='white', font=("Arial", 8, "bold"))
        load_btn.pack(side=tk.LEFT, padx=2)
        
        delete_btn = tk.Button(saved_buttons_frame, text="🗑️ Delete", command=self.delete_selected_army,
                             bg=self.colors['secondary'], fg='white', font=("Arial", 8, "bold"))
        delete_btn.pack(side=tk.LEFT, padx=2)
        
        export_btn = tk.Button(saved_buttons_frame, text="📤 Export", command=self.export_army,
                             bg=self.colors['warning'], fg='white', font=("Arial", 8, "bold"))
        export_btn.pack(side=tk.LEFT, padx=2)
        
        # Update the armies list
        self.update_armies_list()
    
    def adjust_brigade_count(self, brigade_type, delta):
        """Adjust brigade count with buttons"""
        try:
            current = self.brigade_counts[brigade_type].get()
            if not isinstance(current, (int, float)) or np.isnan(current):
                current = 0
            new_value = max(0, min(15, int(current) + delta))
            self.brigade_counts[brigade_type].set(new_value)
            self.update_army_preview()
        except (ValueError, TypeError):
            # Reset to safe default if there's an error
            self.brigade_counts[brigade_type].set(0)
            self.update_army_preview()
    
    def apply_preset(self, composition):
        """Apply a preset army composition"""
        for brigade_type, count in composition.items():
            self.brigade_counts[brigade_type].set(count)
        self.update_army_preview()
    
    def save_custom_army(self):
        """Save the current custom army configuration"""
        army_name = self.army_name.get().strip()
        if not army_name:
            messagebox.showerror("Error", "Please enter an army name!")
            return
        
        if army_name in self.custom_armies:
            if not messagebox.askyesno("Overwrite", f"Army '{army_name}' already exists. Overwrite?"):
                return
        
        # Get brigade counts
        heavy_count = self.brigade_counts['Heavy'].get()
        light_count = self.brigade_counts['Light'].get()
        cavalry_count = self.brigade_counts['Cavalry'].get()
        
        if heavy_count + light_count + cavalry_count == 0:
            messagebox.showerror("Error", "Army must have at least one brigade!")
            return
        
        # Create army configuration
        try:
            general_level = self.general_level.get()
            if not isinstance(general_level, (int, float)) or np.isnan(general_level):
                general_level = 3  # Default level
            general_level = max(1, min(5, int(general_level)))
        except (ValueError, TypeError):
            general_level = 3  # Default level
            
        army_config = {
            'name': army_name,
            'general_name': self.general_name.get().strip() or "Custom General",
            'general_level': general_level,
            'general_trait': self.general_trait.get(),
            'brigades': {
                'Heavy': heavy_count,
                'Light': light_count,
                'Cavalry': cavalry_count
            },
            'total_brigades': heavy_count + light_count + cavalry_count
        }
        
        # Save to dictionary
        self.custom_armies[army_name] = army_config
        
        # Update the armies list
        self.update_armies_list()
        
        # Update mass simulation army lists
        self.update_mass_army_lists()
        
        messagebox.showinfo("Success", f"Army '{army_name}' saved successfully!")
    
    def update_armies_list(self):
        """Update the saved armies listbox"""
        self.armies_listbox.delete(0, tk.END)
        
        for army_name, army_config in self.custom_armies.items():
            total = army_config['total_brigades']
            heavy = army_config['brigades']['Heavy']
            light = army_config['brigades']['Light']
            cavalry = army_config['brigades']['Cavalry']
            
            display_text = f"{army_name} ({total}) - H:{heavy} L:{light} C:{cavalry}"
            self.armies_listbox.insert(tk.END, display_text)
    
    def on_army_select(self, event):
        """Handle army selection in listbox"""
        selection = self.armies_listbox.curselection()
        if selection:
            index = selection[0]
            army_names = list(self.custom_armies.keys())
            if index < len(army_names):
                selected_army = army_names[index]
                # Could show army details here
    
    def load_selected_army(self):
        """Load the selected army configuration"""
        selection = self.armies_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an army to load!")
            return
        
        index = selection[0]
        army_names = list(self.custom_armies.keys())
        if index >= len(army_names):
            return
        
        army_name = army_names[index]
        army_config = self.custom_armies[army_name]
        
        # Load configuration with safe conversion
        self.army_name.set(army_config['name'])
        self.general_name.set(army_config['general_name'])
        
        # Safe general level loading
        try:
            general_level = army_config['general_level']
            if not isinstance(general_level, (int, float)) or np.isnan(general_level):
                general_level = 3
            general_level = max(1, min(5, int(general_level)))
            self.general_level.set(general_level)
        except (ValueError, TypeError, KeyError):
            self.general_level.set(3)
            
        self.general_trait.set(army_config['general_trait'])
        
        # Load brigade counts
        for brigade_type, count in army_config['brigades'].items():
            self.brigade_counts[brigade_type].set(count)
        
        # Update preview
        self.update_army_preview()
        
        messagebox.showinfo("Success", f"Army '{army_name}' loaded successfully!")
    
    def delete_selected_army(self):
        """Delete the selected army"""
        selection = self.armies_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an army to delete!")
            return
        
        index = selection[0]
        army_names = list(self.custom_armies.keys())
        if index >= len(army_names):
            return
        
        army_name = army_names[index]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{army_name}'?"):
            del self.custom_armies[army_name]
            self.update_armies_list()
            # Update mass simulation army lists
            self.update_mass_army_lists()
            messagebox.showinfo("Success", f"Army '{army_name}' deleted successfully!")
    
    def export_army(self):
        """Export army configuration to text format"""
        selection = self.armies_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an army to export!")
            return
        
        index = selection[0]
        army_names = list(self.custom_armies.keys())
        if index >= len(army_names):
            return
        
        army_name = army_names[index]
        army_config = self.custom_armies[army_name]
        
        # Create export text
        export_text = f"""
🏛️ CUSTOM ARMY EXPORT 🏛️
=========================================
Army Name: {army_config['name']}
General: {army_config['general_name']} (Level {army_config['general_level']})
Trait: {army_config['general_trait']}

Brigade Composition:
• Heavy Infantry: {army_config['brigades']['Heavy']} brigades
• Light Infantry: {army_config['brigades']['Light']} brigades  
• Cavalry: {army_config['brigades']['Cavalry']} brigades
• Total Brigades: {army_config['total_brigades']}

Army Power Estimation:
• Heavy Power: {army_config['brigades']['Heavy'] * 3.5:.1f}
• Light Power: {army_config['brigades']['Light'] * 2.8:.1f}
• Cavalry Power: {army_config['brigades']['Cavalry'] * 4.2:.1f}
• Total Power: {army_config['brigades']['Heavy'] * 3.5 + army_config['brigades']['Light'] * 2.8 + army_config['brigades']['Cavalry'] * 4.2:.1f}
=========================================
        """.strip()
        
        # Show in a popup window
        export_window = tk.Toplevel(self.root)
        export_window.title(f"Export: {army_name}")
        export_window.geometry("500x400")
        export_window.configure(bg="#2c3e50")
        
        text_area = scrolledtext.ScrolledText(export_window, wrap=tk.WORD, font=("Courier", 10))
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_area.insert(tk.END, export_text)
        text_area.config(state=tk.DISABLED)
    
    def create_custom_army_object(self, army_config):
        """Create an actual Army object from saved configuration"""
        try:
            from models import General, Brigade, Army, BrigadeType, GENERAL_TRAITS
            
            # Find the trait object
            trait = None
            for t in GENERAL_TRAITS:
                if t.name == army_config['general_trait']:
                    trait = t
                    break
            
            if not trait:
                trait = GENERAL_TRAITS[0]  # Default trait
            
            # Create general with safe level conversion
            try:
                general_level = army_config['general_level']
                if not isinstance(general_level, (int, float)) or np.isnan(general_level):
                    general_level = 3
                general_level = max(1, min(5, int(general_level)))
            except (ValueError, TypeError, KeyError):
                general_level = 3
                
            general = General(
                id=f"gen_{army_config['name'].lower().replace(' ', '_')}",
                name=army_config['general_name'],
                level=general_level,
                trait=trait
            )
            
            # Create brigades
            brigades = []
            
            # Add heavy brigades
            for i in range(army_config['brigades']['Heavy']):
                brigade = Brigade(
                    id=f"heavy_{i}_{army_config['name'].lower().replace(' ', '_')}",
                    type=BrigadeType.HEAVY
                )
                brigades.append(brigade)
            
            # Add light brigades  
            for i in range(army_config['brigades']['Light']):
                brigade = Brigade(
                    id=f"light_{i}_{army_config['name'].lower().replace(' ', '_')}",
                    type=BrigadeType.LIGHT
                )
                brigades.append(brigade)
            
            # Add cavalry brigades
            for i in range(army_config['brigades']['Cavalry']):
                brigade = Brigade(
                    id=f"cavalry_{i}_{army_config['name'].lower().replace(' ', '_')}",
                    type=BrigadeType.CAVALRY
                )
                brigades.append(brigade)
            
            # Create army
            army = Army(
                id=f"army_{army_config['name'].lower().replace(' ', '_')}",
                general=general,
                brigades=brigades
            )
            
            return army
            
        except Exception as e:
            print(f"Error creating custom army: {e}")
            return None
        
        # Update preview button
        update_btn = tk.Button(
            left_builder, 
            text="🔄 Update Preview", 
            command=self.update_army_preview,
            bg=self.colors['primary'], 
            fg='white',
            font=("Arial", 10, "bold")
        )
        update_btn.pack(pady=10)
        
        # Initialize army preview
        self.update_army_preview()
    
    def simulate_single_battle(self):
        """Simulate a single battle with visualization"""
        try:
            # Generate or select armies based on mode
            if self.army_mode.get() == "Custom":
                # Use custom armies
                red_army_name = self.red_army_var.get()
                blue_army_name = self.blue_army_var.get()
                
                if not red_army_name or not blue_army_name:
                    messagebox.showerror("Error", "Please select both Red and Blue custom armies!")
                    return
                
                if red_army_name not in self.custom_armies or blue_army_name not in self.custom_armies:
                    messagebox.showerror("Error", "Selected armies not found! Please refresh army list.")
                    return
                
                # Create army objects from custom configurations
                army1 = self.create_custom_army_object(self.custom_armies[red_army_name])
                army2 = self.create_custom_army_object(self.custom_armies[blue_army_name])
                
                if not army1 or not army2:
                    messagebox.showerror("Error", "Failed to create custom armies!")
                    return
                    
                # Set army names for battle
                army1.name = f"Red: {red_army_name}"
                army2.name = f"Blue: {blue_army_name}"
                
            else:
                # Generate random armies with safe size conversion
                try:
                    army_size = int(self.army_size.get())
                    if army_size < 1 or army_size > 15:
                        army_size = 8  # Default safe value
                except (ValueError, TypeError):
                    army_size = 8  # Default safe value
                    
                army1 = self.generate_random_army("Red Army", army_size)
                army2 = self.generate_random_army("Blue Army", army_size)
            
            # Get terrain
            terrain = TerrainType(self.terrain_var.get())
            
            if self.battle_type.get() == "Land":
                result = self.land_engine.simulate_land_battle(army1, army2, terrain)
                battle_log = self.land_engine.battle_log
            else:
                # Convert to armadas for naval battle
                armada1 = self.army_to_armada(army1, "Red Fleet")
                armada2 = self.army_to_armada(army2, "Blue Fleet")
                result = self.naval_engine.simulate_naval_battle(armada1, armada2, terrain)
                battle_log = self.naval_engine.battle_log
            
            # Display battle log
            self.display_battle_log(battle_log, result)
            
            # Update battle visualization
            self.visualize_battle_result(result, army1, army2)
            
            # Store statistics
            self.store_battle_stats(result, terrain, army1, army2)
            
        except Exception as e:
            messagebox.showerror("Error", f"Battle simulation failed: {str(e)}")
    
    def update_custom_army_lists(self):
        """Update the custom army dropdown lists"""
        army_names = list(self.custom_armies.keys())
        
        self.red_army_combo['values'] = army_names
        self.blue_army_combo['values'] = army_names
        
        # Set default selections if armies exist
        if army_names:
            if not self.red_army_var.get() or self.red_army_var.get() not in army_names:
                self.red_army_combo.current(0)
            if not self.blue_army_var.get() or self.blue_army_var.get() not in army_names:
                if len(army_names) > 1:
                    self.blue_army_combo.current(1)
                else:
                    self.blue_army_combo.current(0)
    
    def simulate_random_battle(self):
        """Simulate a quick random battle"""
        # Randomize settings
        self.army_size.set(np.random.randint(5, 12))
        self.terrain_var.set(np.random.choice([terrain.value for terrain in TerrainType]))
        self.battle_type.set(np.random.choice(["Land", "Naval"]))
        
        # Run simulation
        self.simulate_single_battle()
    
    def start_mass_simulation(self):
        """Start mass simulation in a separate thread"""
        def run_simulation():
            from models import TerrainType
            
            num_battles = self.mass_battles.get()
            army_type = self.mass_army_type.get()
            
            # Validate inputs based on army type
            if army_type in ["Custom vs Custom", "Custom vs Random"]:
                if not self.custom_armies:
                    self.battle_queue.put(('error', "No custom armies available!"))
                    return
                if army_type == "Custom vs Custom" and len(self.custom_armies) < 2:
                    self.battle_queue.put(('error', "Need at least 2 custom armies for Custom vs Custom!"))
                    return
            
            results = []
            for i in range(num_battles):
                # Update progress
                progress = (i / num_battles) * 100
                self.battle_queue.put(('progress', progress, f"Battle {i+1}/{num_battles}"))
                
                # Generate armies based on type
                if army_type == "Random":
                    army_size = self.mass_army_size.get()
                    army1 = self.generate_random_army("Red", army_size)
                    army2 = self.generate_random_army("Blue", army_size)
                elif army_type == "Custom vs Custom":
                    army1_name = self.mass_army1.get()
                    army2_name = self.mass_army2.get()
                    if army1_name not in self.custom_armies or army2_name not in self.custom_armies:
                        self.battle_queue.put(('error', "Selected custom armies not found!"))
                        return
                    army1 = self.create_custom_army_object(self.custom_armies[army1_name])
                    army2 = self.create_custom_army_object(self.custom_armies[army2_name])
                    if army1 is None or army2 is None:
                        self.battle_queue.put(('error', "Failed to create custom army objects!"))
                        return
                    army1.name = f"Red: {army1_name}"
                    army2.name = f"Blue: {army2_name}"
                elif army_type == "Custom vs Random":
                    army1_name = self.mass_army1.get()
                    if army1_name not in self.custom_armies:
                        self.battle_queue.put(('error', "Selected custom army not found!"))
                        return
                    army_size = self.mass_army_size.get()
                    army1 = self.create_custom_army_object(self.custom_armies[army1_name])
                    if army1 is None:
                        self.battle_queue.put(('error', "Failed to create custom army object!"))
                        return
                    army2 = self.generate_random_army("Blue", army_size)
                    army1.name = f"Red: {army1_name}"
                
                terrain = np.random.choice(list(TerrainType))
                
                # Simulate battle (suppress logging for performance)
                original_log = self.land_engine.battle_log
                self.land_engine.battle_log = []
                
                result = self.land_engine.simulate_land_battle(army1, army2, terrain)
                results.append({
                    'result': result,
                    'terrain': terrain,
                    'army1': army1,
                    'army2': army2
                })
                
                self.land_engine.battle_log = original_log
            
            # Signal completion
            self.battle_queue.put(('complete', results))
        
        # Start simulation thread
        self.progress_label.config(text="Starting mass simulation...")
        threading.Thread(target=run_simulation, daemon=True).start()
    
    def check_queue(self):
        """Check for updates from simulation thread"""
        try:
            while True:
                msg = self.battle_queue.get_nowait()
                if msg[0] == 'progress':
                    _, progress, text = msg
                    self.progress_var.set(progress)
                    self.progress_label.config(text=text)
                elif msg[0] == 'complete':
                    _, results = msg
                    self.progress_var.set(100)
                    self.progress_label.config(text=f"Completed {len(results)} battles!")
                    self.visualize_mass_results(results)
                elif msg[0] == 'error':
                    _, error_text = msg
                    self.progress_label.config(text=f"Error: {error_text}")
                    self.progress_var.set(0)
                    # Show error message box
                    messagebox.showerror("Mass Simulation Error", error_text)
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.check_queue)
    
    def visualize_battle_result(self, result, army1, army2):
        """Create colorful visualization of battle result"""
        self.battle_fig.clear()
        
        # Create subplots
        gs = self.battle_fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        
        # Army composition comparison
        ax1 = self.battle_fig.add_subplot(gs[0, :])
        self.plot_army_comparison(ax1, army1, army2, result)
        
        # Casualty analysis
        ax2 = self.battle_fig.add_subplot(gs[1, 0])
        self.plot_casualties(ax2, result, army1, army2)
        
        # Battle phases
        ax3 = self.battle_fig.add_subplot(gs[1, 1])
        self.plot_battle_phases(ax3, result)
        
        self.battle_canvas.draw()
    
    def plot_army_comparison(self, ax, army1, army2, result):
        """Plot army composition comparison"""
        ax.set_facecolor('#34495e')
        
        # Count brigade types for each army
        army1_types = Counter([brigade.type.value for brigade in army1.brigades])
        army2_types = Counter([brigade.type.value for brigade in army2.brigades])
        
        brigade_types = ['Heavy', 'Light', 'Cavalry']
        army1_counts = [army1_types.get(bt, 0) for bt in brigade_types]
        army2_counts = [army2_types.get(bt, 0) for bt in brigade_types]
        
        x = np.arange(len(brigade_types))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, army1_counts, width, label='Red Army', color='#e74c3c', alpha=0.8)
        bars2 = ax.bar(x + width/2, army2_counts, width, label='Blue Army', color='#3498db', alpha=0.8)
        
        # Highlight winner
        if "Red" in result.winner:
            for bar in bars1:
                bar.set_edgecolor('#f1c40f')
                bar.set_linewidth(3)
        elif "Blue" in result.winner:
            for bar in bars2:
                bar.set_edgecolor('#f1c40f')
                bar.set_linewidth(3)
        
        ax.set_xlabel('Brigade Type', color='white', fontweight='bold')
        ax.set_ylabel('Count', color='white', fontweight='bold')
        ax.set_title(f'Army Composition - Winner: {result.winner}', color='white', fontweight='bold', fontsize=14)
        ax.set_xticks(x)
        ax.set_xticklabels(brigade_types)
        ax.legend()
        ax.tick_params(colors='white')
    
    def plot_casualties(self, ax, result, army1, army2):
        """Plot casualty analysis"""
        ax.set_facecolor('#34495e')
        
        army1_casualties = len(result.casualties.get(army1.id, []))
        army2_casualties = len(result.casualties.get(army2.id, []))
        
        casualties = [army1_casualties, army2_casualties]
        colors = ['#e74c3c', '#3498db']
        labels = ['Red Army', 'Blue Army']
        
        wedges, texts, autotexts = ax.pie(casualties, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        
        # Style the text
        for text in texts:
            text.set_color('white')
            text.set_fontweight('bold')
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title('Casualties Distribution', color='white', fontweight='bold')
    
    def plot_battle_phases(self, ax, result):
        """Plot battle phases simulation"""
        ax.set_facecolor('#34495e')
        
        # Simulate battle intensity over phases
        phases = ['Skirmish', 'Pitch Battle', 'Rally', 'Resolution']
        intensity = np.random.uniform(3, 8, len(phases))  # Mock intensity data
        
        colors = ['#f39c12', '#e74c3c', '#9b59b6', '#2ecc71']
        bars = ax.bar(phases, intensity, color=colors, alpha=0.8)
        
        ax.set_ylabel('Battle Intensity', color='white', fontweight='bold')
        ax.set_title('Battle Phase Analysis', color='white', fontweight='bold')
        ax.tick_params(colors='white')
        
        # Add value labels on bars
        for bar, value in zip(bars, intensity):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{value:.1f}', ha='center', va='bottom', color='white', fontweight='bold')
    
    def update_analytics(self):
        """Update the analytics dashboard"""
        self.analytics_fig.clear()
        
        if not self.battle_stats['land_battles'] and not self.battle_stats['naval_battles']:
            # No data yet, show placeholder
            ax = self.analytics_fig.add_subplot(111)
            ax.set_facecolor('#34495e')
            ax.text(0.5, 0.5, 'No Battle Data Yet\nSimulate some battles to see analytics!', 
                   ha='center', va='center', fontsize=16, color='white', fontweight='bold')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
        else:
            # Create 2x2 subplot grid
            gs = self.analytics_fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
            
            # Terrain performance
            ax1 = self.analytics_fig.add_subplot(gs[0, 0])
            self.plot_terrain_performance(ax1)
            
            # Trait effectiveness
            ax2 = self.analytics_fig.add_subplot(gs[0, 1])
            self.plot_trait_effectiveness(ax2)
            
            # Win rate over time
            ax3 = self.analytics_fig.add_subplot(gs[1, 0])
            self.plot_win_rate_trend(ax3)
            
            # Enhancement usage
            ax4 = self.analytics_fig.add_subplot(gs[1, 1])
            self.plot_enhancement_usage(ax4)
        
        self.analytics_canvas.draw()
    
    def plot_terrain_performance(self, ax):
        """Plot terrain performance analytics"""
        ax.set_facecolor('#34495e')
        
        terrain_data = self.battle_stats['terrain_performance']
        if not terrain_data:
            ax.text(0.5, 0.5, 'No terrain data', ha='center', va='center', color='white')
            return
        
        terrains = list(terrain_data.keys())
        red_wins = [terrain_data[t]['red'] for t in terrains]
        blue_wins = [terrain_data[t]['blue'] for t in terrains]
        
        x = np.arange(len(terrains))
        width = 0.35
        
        ax.bar(x - width/2, red_wins, width, label='Red Wins', color='#e74c3c', alpha=0.8)
        ax.bar(x + width/2, blue_wins, width, label='Blue Wins', color='#3498db', alpha=0.8)
        
        ax.set_xlabel('Terrain', color='white', fontweight='bold')
        ax.set_ylabel('Wins', color='white', fontweight='bold')
        ax.set_title('Terrain Performance', color='white', fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(terrains, rotation=45)
        ax.legend()
        ax.tick_params(colors='white')
    
    def plot_trait_effectiveness(self, ax):
        """Plot general trait effectiveness"""
        ax.set_facecolor('#34495e')
        
        trait_data = dict(self.battle_stats['trait_wins'].most_common(8))
        if not trait_data:
            ax.text(0.5, 0.5, 'No trait data', ha='center', va='center', color='white')
            return
        
        traits = list(trait_data.keys())
        wins = list(trait_data.values())
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(traits)))
        bars = ax.bar(traits, wins, color=colors, alpha=0.8)
        
        ax.set_xlabel('General Traits', color='white', fontweight='bold')
        ax.set_ylabel('Wins', color='white', fontweight='bold')
        ax.set_title('Most Effective Traits', color='white', fontweight='bold')
        ax.tick_params(colors='white')
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    
    def plot_win_rate_trend(self, ax):
        """Plot win rate trend over battles"""
        ax.set_facecolor('#34495e')
        
        battles = self.battle_stats['land_battles'] + self.battle_stats['naval_battles']
        if len(battles) < 2:
            ax.text(0.5, 0.5, 'Need more battles', ha='center', va='center', color='white')
            return
        
        # Calculate moving average win rate
        window_size = max(5, len(battles) // 10)
        red_wins = []
        battle_numbers = []
        
        for i in range(window_size, len(battles) + 1):
            window = battles[i-window_size:i]
            if len(window) > 0:  # Prevent division by zero
                red_win_rate = sum(1 for b in window if 'Red' in b.get('winner', '')) / len(window)
                red_wins.append(red_win_rate * 100)
                battle_numbers.append(i)
        
        if len(red_wins) > 0:  # Only plot if we have data
            ax.plot(battle_numbers, red_wins, color='#e74c3c', linewidth=3, label='Red Army Win Rate')
            ax.axhline(y=50, color='white', linestyle='--', alpha=0.5, label='50% Line')
        
        ax.set_xlabel('Battle Number', color='white', fontweight='bold')
        ax.set_ylabel('Win Rate (%)', color='white', fontweight='bold')
        ax.set_title('Win Rate Trend', color='white', fontweight='bold')
        ax.legend()
        ax.tick_params(colors='white')
        ax.grid(True, alpha=0.3)
    
    def plot_enhancement_usage(self, ax):
        """Plot enhancement usage statistics"""
        ax.set_facecolor('#34495e')
        
        enhancement_data = dict(self.battle_stats['enhancement_usage'].most_common(6))
        if not enhancement_data or sum(enhancement_data.values()) == 0:
            ax.text(0.5, 0.5, 'No enhancement data', ha='center', va='center', color='white')
            return
        
        enhancements = list(enhancement_data.keys())
        usage = list(enhancement_data.values())
        
        # Filter out zero values to prevent division warnings
        filtered_data = [(e, u) for e, u in zip(enhancements, usage) if u > 0]
        if not filtered_data:
            ax.text(0.5, 0.5, 'No enhancement data', ha='center', va='center', color='white')
            return
        
        enhancements, usage = zip(*filtered_data)
        colors = plt.cm.viridis(np.linspace(0, 1, len(enhancements)))
        
        try:
            wedges, texts, autotexts = ax.pie(usage, labels=enhancements, colors=colors, autopct='%1.1f%%')
            
            for text in texts:
                text.set_color('white')
                text.set_fontsize(8)
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
        except (ValueError, ZeroDivisionError):
            ax.text(0.5, 0.5, 'Insufficient data', ha='center', va='center', color='white')
            return
        
        ax.set_title('Enhancement Usage', color='white', fontweight='bold')
    
    def visualize_mass_results(self, results):
        """Visualize mass simulation results"""
        self.mass_fig.clear()
        
        # Analyze results
        terrain_wins = defaultdict(lambda: defaultdict(int))
        win_rates = []
        
        for i, battle in enumerate(results):
            result = battle['result']
            terrain = battle['terrain']
            
            if 'Red' in result.winner:
                terrain_wins[terrain.value]['red'] += 1
                win_rates.append(1)
            elif 'Blue' in result.winner:
                terrain_wins[terrain.value]['blue'] += 1
                win_rates.append(0)
            else:
                win_rates.append(0.5)  # Draw
        
        # Create subplots
        gs = self.mass_fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        
        # Overall win rate
        ax1 = self.mass_fig.add_subplot(gs[0, 0])
        ax1.set_facecolor('#34495e')
        
        if len(results) == 0:
            ax1.text(0.5, 0.5, 'No results', ha='center', va='center', color='white')
        else:
            red_wins = sum(win_rates)
            blue_wins = len(results) - red_wins
            
            # Avoid empty pie chart
            if red_wins > 0 or blue_wins > 0:
                ax1.pie([red_wins, blue_wins], labels=['Red Army', 'Blue Army'], 
                       colors=['#e74c3c', '#3498db'], autopct='%1.1f%%')
                ax1.set_title('Overall Win Distribution', color='white', fontweight='bold')
            else:
                ax1.text(0.5, 0.5, 'No battles completed', ha='center', va='center', color='white')
        
        # Terrain analysis
        ax2 = self.mass_fig.add_subplot(gs[0, 1])
        ax2.set_facecolor('#34495e')
        
        terrains = list(terrain_wins.keys())
        red_terrain_wins = [terrain_wins[t]['red'] for t in terrains]
        blue_terrain_wins = [terrain_wins[t]['blue'] for t in terrains]
        
        x = np.arange(len(terrains))
        width = 0.35
        
        ax2.bar(x - width/2, red_terrain_wins, width, label='Red', color='#e74c3c', alpha=0.8)
        ax2.bar(x + width/2, blue_terrain_wins, width, label='Blue', color='#3498db', alpha=0.8)
        
        ax2.set_xlabel('Terrain', color='white', fontweight='bold')
        ax2.set_ylabel('Wins', color='white', fontweight='bold')
        ax2.set_title('Wins by Terrain', color='white', fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(terrains, rotation=45)
        ax2.legend()
        ax2.tick_params(colors='white')
        
        # Win rate trend
        ax3 = self.mass_fig.add_subplot(gs[1, :])
        ax3.set_facecolor('#34495e')
        
        # Calculate rolling win rate
        window = 50
        rolling_winrate = []
        x_vals = []
        
        for i in range(window, len(win_rates) + 1):
            winrate = np.mean(win_rates[i-window:i]) * 100
            rolling_winrate.append(winrate)
            x_vals.append(i)
        
        ax3.plot(x_vals, rolling_winrate, color='#f39c12', linewidth=2, label='Red Army Win Rate (50-battle rolling avg)')
        ax3.axhline(y=50, color='white', linestyle='--', alpha=0.5, label='50% Balance Line')
        ax3.fill_between(x_vals, rolling_winrate, 50, alpha=0.3, color='#f39c12')
        
        ax3.set_xlabel('Battle Number', color='white', fontweight='bold')
        ax3.set_ylabel('Win Rate (%)', color='white', fontweight='bold')
        ax3.set_title(f'Win Rate Trend - {len(results)} Battles', color='white', fontweight='bold')
        ax3.legend()
        ax3.tick_params(colors='white')
        ax3.grid(True, alpha=0.3)
        
        self.mass_canvas.draw()
    
    def update_army_preview(self, *args):
        """Update army composition preview"""
        try:
            self.army_fig.clear()
            
            # Get brigade counts with safe conversion
            def safe_get_count(var):
                try:
                    value = var.get()
                    if not isinstance(value, (int, float)) or np.isnan(value):
                        return 0
                    return max(0, int(value))
                except (ValueError, TypeError):
                    return 0
            
            heavy_count = safe_get_count(self.brigade_counts['Heavy'])
            light_count = safe_get_count(self.brigade_counts['Light'])
            cavalry_count = safe_get_count(self.brigade_counts['Cavalry'])
            
            total_brigades = heavy_count + light_count + cavalry_count
            
            if total_brigades == 0:
                ax = self.army_fig.add_subplot(111)
                ax.text(0.5, 0.5, 'No Brigades\nAdd some units!', ha='center', va='center', 
                       fontsize=14, color='white', fontweight='bold')
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.axis('off')
            else:
                # Create army visualization
                gs = self.army_fig.add_gridspec(2, 1, height_ratios=[2, 1], hspace=0.3)
                
                # Brigade composition pie chart
                ax1 = self.army_fig.add_subplot(gs[0])
                ax1.set_facecolor('#34495e')
                
                counts = [heavy_count, light_count, cavalry_count]
                labels = ['Heavy Infantry', 'Light Infantry', 'Cavalry']
                colors = ['#95a5a6', '#3498db', '#e67e22']
                
                # Only include non-zero counts
                non_zero_data = [(count, label, color) for count, label, color in zip(counts, labels, colors) if count > 0]
                
                if non_zero_data:
                    counts, labels, colors = zip(*non_zero_data)
                    wedges, texts, autotexts = ax1.pie(counts, labels=labels, colors=colors, autopct='%1.0f', startangle=90)
                    
                    for text in texts:
                        text.set_color('white')
                        text.set_fontweight('bold')
                    for autotext in autotexts:
                        autotext.set_color('white')
                        autotext.set_fontweight('bold')
                
                ax1.set_title(f'Army Composition ({total_brigades} brigades)', color='white', fontweight='bold', fontsize=14)
                
                # Army stats
                ax2 = self.army_fig.add_subplot(gs[1])
                ax2.set_facecolor('#34495e')
                
                # Calculate army power estimation
                heavy_power = heavy_count * 3.5  # Heavy infantry are strong
                light_power = light_count * 2.8  # Light infantry are versatile  
                cavalry_power = cavalry_count * 4.2  # Cavalry are powerful but situational
                
                total_power = heavy_power + light_power + cavalry_power
                
                # Safe percentage calculation
                heavy_pct = (heavy_count / total_brigades * 100) if total_brigades > 0 else 0
                light_pct = (light_count / total_brigades * 100) if total_brigades > 0 else 0
                cavalry_pct = (cavalry_count / total_brigades * 100) if total_brigades > 0 else 0
                
                stats_text = f"""
Army Statistics:
• Total Brigades: {total_brigades}
• Estimated Power: {total_power:.1f}
• Heavy Infantry: {heavy_count} ({heavy_pct:.1f}%)
• Light Infantry: {light_count} ({light_pct:.1f}%)
• Cavalry: {cavalry_count} ({cavalry_pct:.1f}%)
                """
                
                ax2.text(0.1, 0.5, stats_text.strip(), fontsize=10, color='white', fontweight='bold',
                        verticalalignment='center', fontfamily='monospace')
                ax2.set_xlim(0, 1)
                ax2.set_ylim(0, 1)
                ax2.axis('off')
            
            self.army_canvas.draw()
        except Exception as e:
            print(f"Error updating army preview: {e}")
            # Create a simple error display
            self.army_fig.clear()
            ax = self.army_fig.add_subplot(111)
            ax.text(0.5, 0.5, 'Preview Error\nCheck console', ha='center', va='center', 
                   fontsize=14, color='red', fontweight='bold')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            self.army_canvas.draw()
    
    # Helper methods
    def generate_random_army(self, name: str, size: int) -> Army:
        """Generate a random army for testing"""
        # Ensure size is valid
        if not isinstance(size, int) or size < 1:
            size = 8  # Default size
            
        general = General(
            id=f"gen_{name.lower()}",
            name=f"General {name}",
            level=int(np.random.randint(1, 6)),
            trait=np.random.choice(GENERAL_TRAITS)
        )
        
        brigades = []
        for i in range(int(size)):
            brigade_type = np.random.choice(list(BrigadeType))
            brigade = Brigade(
                id=f"brigade_{name.lower()}_{i}",
                type=brigade_type,
                is_mercenary=np.random.choice([True, False])
            )
            brigades.append(brigade)
        
        return Army(
            id=f"army_{name.lower()}",
            general=general,
            brigades=brigades,
            enhancements=np.random.choice([
                "Blacksmiths", "Combat Engineers", "Field Hospitals", "Local Maps", "Signal Companies"
            ], size=2, replace=False).tolist()
        )
    
    def army_to_armada(self, army: Army, fleet_name: str) -> 'Armada':
        """Convert army to armada for naval battles"""
        from models import Admiral, Ship, Armada
        
        admiral = Admiral(
            id=f"adm_{fleet_name.lower()}",
            name=f"Admiral {fleet_name}",
            level=army.general.level,
            trait=np.random.choice(ADMIRAL_TRAITS)
        )
        
        ships = []
        for i, brigade in enumerate(army.brigades):
            # Create ship without ship type since it doesn't exist in models
            ship = Ship(
                id=f"ship_{fleet_name.lower()}_{i}",
                enhancement=None,
                is_flagship=(i == 0)  # First ship is flagship
            )
            ships.append(ship)
        
        return Armada(
            id=f"armada_{fleet_name.lower()}",
            admiral=admiral,
            ships=ships
        )
    
    def display_battle_log(self, battle_log, result):
        """Display colorful battle log"""
        self.battle_log.delete(1.0, tk.END)
        
        # Add header
        header = f"{'='*60}\n🏛️ BATTLE REPORT 🏛️\n{'='*60}\n"
        self.battle_log.insert(tk.END, header)
        
        # Add battle log entries
        for entry in battle_log:
            self.battle_log.insert(tk.END, f"{entry}\n")
        
        # Add result summary
        summary = f"\n{'='*60}\n"
        summary += f"🏆 WINNER: {result.winner}\n"
        summary += f"{'='*60}\n"
        
        self.battle_log.insert(tk.END, summary)
        self.battle_log.see(tk.END)
    
    def store_battle_stats(self, result, terrain, army1, army2):
        """Store battle statistics for analytics"""
        battle_data = {
            'winner': result.winner,
            'terrain': terrain.value,
            'casualties': result.casualties
        }
        
        self.battle_stats['land_battles'].append(battle_data)
        
        # Update terrain performance
        if 'Red' in result.winner:
            self.battle_stats['terrain_performance'][terrain.value]['red'] += 1
        elif 'Blue' in result.winner:
            self.battle_stats['terrain_performance'][terrain.value]['blue'] += 1
        
        # Update trait performance
        if 'Red' in result.winner:
            self.battle_stats['trait_wins'][army1.general.trait.name] += 1
        elif 'Blue' in result.winner:
            self.battle_stats['trait_wins'][army2.general.trait.name] += 1
        
        # Update enhancement usage
        for brigade in army1.brigades + army2.brigades:
            if brigade.enhancement:
                self.battle_stats['enhancement_usage'][brigade.enhancement.name] += 1
    
    def clear_battle_results(self):
        """Clear all battle results and statistics"""
        self.battle_log.delete(1.0, tk.END)
        self.battle_stats = {
            'land_battles': [],
            'naval_battles': [],
            'terrain_performance': defaultdict(lambda: defaultdict(int)),
            'trait_wins': defaultdict(int),
            'enhancement_usage': defaultdict(int)
        }
        
        # Clear visualizations
        self.battle_fig.clear()
        self.battle_canvas.draw()
        self.update_analytics()
        
        self.battle_log.insert(tk.END, "🗑️ All battle data cleared!\n")
    
    def export_analytics(self):
        """Export analytics data to file"""
        try:
            import json
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"battle_analytics_{timestamp}.json"
            
            export_data = {
                'timestamp': timestamp,
                'total_land_battles': len(self.battle_stats['land_battles']),
                'total_naval_battles': len(self.battle_stats['naval_battles']),
                'terrain_performance': dict(self.battle_stats['terrain_performance']),
                'trait_wins': dict(self.battle_stats['trait_wins']),
                'enhancement_usage': dict(self.battle_stats['enhancement_usage']),
                'battle_details': self.battle_stats['land_battles'] + self.battle_stats['naval_battles']
            }
            
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            messagebox.showinfo("Export Complete", f"Analytics data exported to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")

def main():
    """Launch the enhanced battle simulator"""
    root = tk.Tk()
    app = EnhancedBattleSimulatorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
