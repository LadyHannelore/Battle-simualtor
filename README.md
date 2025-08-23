# Land and Naval Battle Simulator

A comprehensive tactical battle simulator implementing detailed warfare mechanics for both land and naval combat. This application is based on an extensive tutorial system featuring multi-phase combat, unit specialization, and strategic depth.

## Features

### 🎨 Enhanced GUI (New!)
- **Colorful Battle Visualization**: Real-time charts and graphs
- **Analytics Dashboard**: Comprehensive battle statistics
- **Mass Simulation**: Run thousands of battles with progress tracking
- **Visual Army Builder**: Interactive army composition tools
- **Export Capabilities**: Save battle data and analytics

### ⚔️ Core Battle System
- **Land & Naval Combat**: Two distinct battle systems
- **Realistic Terrain Effects**: 8 terrain types affecting combat
- **Multi-Phase Combat**: Skirmish, Pitch Battle, Rally, and Action Report phases
- **Complex Dice Mechanics**: D6-based resolution with multiple modifiers

### 🏗️ Army & Fleet Management
- **Ship Combat**: Individual ship-to-ship battles with range mechanics
- **Admiral System**: 10 unique admiral traits for fleet bonuses
- **Ship Enhancements**: Specialized upgrades for firepower, speed, and defense
- **Sea Terrain**: 4 different sea terrain types affecting combat width
- **Damage System**: Detailed ship damage with ongoing effects
- **Fleet Management**: Create and manage naval armadas

### Combat Mechanics
- **Dice-Based System**: D6 rolls with modifiers for all combat actions
- **Range Combat**: Naval battles feature 5 range bands (0-4)
- **Boarding Actions**: Close-quarters naval combat
- **Casualties & Promotions**: Realistic post-battle consequences
- **Terrain Modifiers**: Environment affects movement and combat effectiveness

## Installation

1. Clone the repository:
```bash
git clone https://github.com/LadyHannelore/Battle-simualtor.git
cd Battle-simualtor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure you have Python 3.6+ installed with tkinter support

## Running the Simulator

### 🎨 Enhanced GUI (Recommended)
For the full experience with colorful graphs and analytics:
```bash
python enhanced_gui.py
```

### 🖥️ Basic GUI
For the original interface:
```bash
python main.py
```

### ⚡ Large-Scale Analysis
For 1000+ battle statistical analysis:
```bash
python battle_analyzer.py
```

### 🎲 Quick Battles
For immediate battle action without the GUI:
```bash
python quick_battle.py
```

This launches an interactive menu for:
- Random land battles
- Random naval battles 
- Campaign simulations (5-10 battles)
- All with randomly generated armies and scenarios

For testing the battle mechanics:
```bash
python test_simulator.py
```

## Usage

### Getting Started
1. Launch the application using `python main.py`
2. The simulator comes with pre-created sample armies and fleets
3. Navigate between tabs to manage forces or simulate battles

### Army Management
1. Go to the "Army Management" tab
2. Create new armies by specifying general name and brigade count
3. Armies are automatically assigned random traits and brigade types
4. View army details in the list display

### Fleet Management
1. Go to the "Fleet Management" tab
2. Create new armadas by specifying admiral name and ship count
3. Ships are automatically assigned random enhancements
4. View fleet details in the list display

### Land Battles
1. Go to the "Land Battles" tab
2. Select two different armies from the dropdown menus
3. Choose terrain type (affects combat width and special rules)
4. Click "Simulate Battle" to run the combat
5. View detailed battle log showing all phases of combat

### Naval Battles
1. Go to the "Naval Battles" tab
2. Select two different armadas from the dropdown menus
3. Choose sea terrain type (affects combat width and victory conditions)
4. Click "Simulate Naval Battle" to run the combat
5. View detailed battle log showing ship-to-ship actions

## Battle System Overview

### Land Combat Phases
1. **Terrain Setup**: Determine combat width and special effects
2. **Skirmish Phase**: Best skirmishers target enemy units
3. **Pitch Phase**: Mass combat with dice rolls and bonuses
4. **Rally Phase**: Units may rout or continue fighting
5. **Action Report**: Casualties and promotions determined

### Naval Combat Phases
1. **Positioning**: Ships are matched up for individual duels
2. **Maneuver Phase**: Ships adjust range and positioning
3. **Gunnery Phase**: Exchange of cannon fire
4. **Damage Resolution**: Ships may be damaged or sunk
5. **Boarding**: Close-range capture attempts

## Technical Details

### Project Structure
```
Battle-simualtor/
├── app/
│   ├── main.py          # Main GUI application
│   ├── models.py        # Data models and game objects
│   ├── battle_engine.py # Combat simulation logic
│   └── static/          # Static assets (empty)
├── main.py              # Application launcher
├── quick_battle.py      # CLI battle generator
├── test_simulator.py    # Test suite
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

### Dependencies
- Python 3.6+
- tkinter (GUI framework, usually included)
- dataclasses (for Python < 3.7, install with pip)
- random (standard library)
- typing (standard library)

### Sample Data
The application includes pre-generated sample data:
- **Armies**: Alexander (Bold), Napoleon (Brilliant), Caesar (Disciplined)
- **Fleets**: Nelson (Accurate), Drake (Daring), Barbarossa (Experienced)

## Game Mechanics Reference

### Brigade Types
- **Cavalry**: +1 Skirmish, +1 Pitch, 5 Movement, terrain penalties
- **Heavy**: +2 Defense, +1 Pitch, +1 Rally, 3 Movement
- **Light**: +2 Skirmish, +1 Rally, 4 Movement, terrain bonuses

### Terrain Effects
- **Plains**: 8 Combat Width, no effects
- **Desert**: 8 Combat Width, no reinforcements
- **Mountains**: 4 Combat Width, +4 Defense to all
- **Jungle**: 5 Combat Width, units may get lost
- **And more...**

### General Traits (Examples)
- **Bold**: +2 Skirmish to all brigades
- **Brilliant**: Double general level in pitch phase
- **Disciplined**: +1 Pitch for all brigades
- **Resolute**: +4 Defense for all brigades

## Contributing

Feel free to submit issues and enhancement requests. The simulation system is designed to be extensible with additional unit types, traits, and combat mechanics.

## License

This project is open source. Feel free to use and modify as needed.