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
        
        # Army size
        ttk.Label(left_panel, text="Army Size:").pack(anchor=tk.W)
        self.army_size = tk.IntVar(value=8)
        size_frame = ttk.Frame(left_panel)
        size_frame.pack(fill=tk.X, pady=2)
        ttk.Scale(size_frame, from_=3, to=15, variable=self.army_size, orient=tk.HORIZONTAL).pack(fill=tk.X)
        ttk.Label(size_frame, textvariable=self.army_size).pack()
        
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
        
        # Army size for mass simulation
        ttk.Label(control_frame, text="Army Size:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.mass_army_size = tk.IntVar(value=8)
        size_spinbox = ttk.Spinbox(control_frame, from_=3, to=15, textvariable=self.mass_army_size, width=10)
        size_spinbox.grid(row=0, column=3, padx=5, pady=2)
        
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
        start_btn.grid(row=1, column=0, columnspan=4, pady=10, sticky=tk.EW)
        
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
    
    def create_army_builder_tab(self):
        """Visual army builder with drag-and-drop style interface"""
        
        builder_frame = ttk.Frame(self.notebook)
        self.notebook.add(builder_frame, text="🏗️ Army Builder")
        
        # Split into left (builder) and right (preview)
        left_builder = ttk.LabelFrame(builder_frame, text="Army Configuration")
        left_builder.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        right_preview = ttk.LabelFrame(builder_frame, text="Army Preview")
        right_preview.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Army composition visualization
        self.army_fig = Figure(figsize=(6, 8), facecolor='#2c3e50')
        self.army_canvas = FigureCanvasTkAgg(self.army_fig, right_preview)
        self.army_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Builder controls
        general_frame = ttk.LabelFrame(left_builder, text="General Configuration")
        general_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(general_frame, text="General Level:").pack(anchor=tk.W)
        self.general_level = tk.IntVar(value=3)
        level_scale = ttk.Scale(general_frame, from_=1, to=5, variable=self.general_level, orient=tk.HORIZONTAL)
        level_scale.pack(fill=tk.X, pady=2)
        
        ttk.Label(general_frame, text="General Trait:").pack(anchor=tk.W, pady=(5,0))
        self.general_trait = tk.StringVar()
        trait_combo = ttk.Combobox(general_frame, textvariable=self.general_trait, state="readonly")
        trait_combo['values'] = [trait.name for trait in GENERAL_TRAITS]
        trait_combo.current(0)
        trait_combo.pack(fill=tk.X, pady=2)
        
        # Brigade composition
        brigade_frame = ttk.LabelFrame(left_builder, text="Brigade Composition")
        brigade_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Brigade type counters
        self.brigade_counts = {
            'Heavy': tk.IntVar(value=3),
            'Light': tk.IntVar(value=3),
            'Cavalry': tk.IntVar(value=2)
        }
        
        for i, (brigade_type, var) in enumerate(self.brigade_counts.items()):
            frame = ttk.Frame(brigade_frame)
            frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(frame, text=f"{brigade_type}:").pack(side=tk.LEFT)
            ttk.Scale(frame, from_=0, to=10, variable=var, orient=tk.HORIZONTAL, command=self.update_army_preview).pack(side=tk.RIGHT, fill=tk.X, expand=True)
            ttk.Label(frame, textvariable=var, width=3).pack(side=tk.RIGHT)
        
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
            # Generate armies
            army1 = self.generate_random_army("Red Army", self.army_size.get())
            army2 = self.generate_random_army("Blue Army", self.army_size.get())
            
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
            num_battles = self.mass_battles.get()
            army_size = self.mass_army_size.get()
            
            results = []
            for i in range(num_battles):
                # Update progress
                progress = (i / num_battles) * 100
                self.battle_queue.put(('progress', progress, f"Battle {i+1}/{num_battles}"))
                
                # Generate random armies
                army1 = self.generate_random_army("Red", army_size)
                army2 = self.generate_random_army("Blue", army_size)
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
            red_win_rate = sum(1 for b in window if 'Red' in b.get('winner', '')) / len(window)
            red_wins.append(red_win_rate * 100)
            battle_numbers.append(i)
        
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
        if not enhancement_data:
            ax.text(0.5, 0.5, 'No enhancement data', ha='center', va='center', color='white')
            return
        
        enhancements = list(enhancement_data.keys())
        usage = list(enhancement_data.values())
        
        colors = plt.cm.viridis(np.linspace(0, 1, len(enhancements)))
        wedges, texts, autotexts = ax.pie(usage, labels=enhancements, colors=colors, autopct='%1.1f%%')
        
        for text in texts:
            text.set_color('white')
            text.set_fontsize(8)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
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
        
        red_wins = sum(win_rates)
        blue_wins = len(results) - red_wins
        
        ax1.pie([red_wins, blue_wins], labels=['Red Army', 'Blue Army'], 
               colors=['#e74c3c', '#3498db'], autopct='%1.1f%%')
        ax1.set_title('Overall Win Distribution', color='white', fontweight='bold')
        
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
        self.army_fig.clear()
        
        # Get brigade counts
        heavy_count = self.brigade_counts['Heavy'].get()
        light_count = self.brigade_counts['Light'].get()
        cavalry_count = self.brigade_counts['Cavalry'].get()
        
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
            
            stats_text = f"""
Army Statistics:
• Total Brigades: {total_brigades}
• Estimated Power: {total_power:.1f}
• Heavy Infantry: {heavy_count} ({heavy_count/total_brigades*100:.1f}%)
• Light Infantry: {light_count} ({light_count/total_brigades*100:.1f}%)
• Cavalry: {cavalry_count} ({cavalry_count/total_brigades*100:.1f}%)
            """
            
            ax2.text(0.1, 0.5, stats_text.strip(), fontsize=10, color='white', fontweight='bold',
                    verticalalignment='center', fontfamily='monospace')
            ax2.set_xlim(0, 1)
            ax2.set_ylim(0, 1)
            ax2.axis('off')
        
        self.army_canvas.draw()
    
    # Helper methods
    def generate_random_army(self, name: str, size: int) -> Army:
        """Generate a random army for testing"""
        general = General(
            id=f"gen_{name.lower()}",
            name=f"General {name}",
            level=np.random.randint(1, 6),
            trait=np.random.choice(GENERAL_TRAITS)
        )
        
        brigades = []
        for i in range(size):
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
        from models import Admiral, Ship, ShipType, Armada
        
        admiral = Admiral(
            id=f"adm_{fleet_name.lower()}",
            name=f"Admiral {fleet_name}",
            level=army.general.level,
            trait=np.random.choice(ADMIRAL_TRAITS)
        )
        
        ships = []
        for i, brigade in enumerate(army.brigades):
            # Convert brigade type to ship type
            if brigade.type == BrigadeType.HEAVY:
                ship_type = ShipType.SHIP_OF_THE_LINE
            elif brigade.type == BrigadeType.LIGHT:
                ship_type = ShipType.FRIGATE
            else:
                ship_type = ShipType.CORVETTE
            
            ship = Ship(
                id=f"ship_{fleet_name.lower()}_{i}",
                type=ship_type,
                is_mercenary=brigade.is_mercenary
            )
            ships.append(ship)
        
        return Armada(
            id=f"armada_{fleet_name.lower()}",
            admiral=admiral,
            ships=ships,
            enhancements=army.enhancements
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
