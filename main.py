#!/usr/bin/env python3
"""
Land and Naval Battle Simulator
Based on the comprehensive warfare tutorial provided

This application simulates tactical battles between armies and naval fleets
with detailed combat mechanics including:

Land Battles:
- Brigade types (Cavalry, Heavy, Light) with unique bonuses
- General traits and levels affecting combat
- Terrain effects on battle outcomes
- Enhancements for specialized units
- Multi-phase combat (Skirmish, Pitch, Rally)

Naval Battles:
- Ship-to-ship combat with gunnery and boarding
- Admiral traits affecting fleet performance
- Sea terrain effects on combat width
- Ship enhancements and damage systems
- Range-based combat mechanics

Usage:
    python main.py

Requirements:
    - Python 3.6+
    - tkinter (usually included with Python)
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

if __name__ == "__main__":
    try:
        from app.main import main
        main()
    except ImportError as e:
        print(f"Error importing modules: {e}")
        print("Make sure you're running this from the project root directory")
        sys.exit(1)
    except Exception as e:
        print(f"Error running application: {e}")
        sys.exit(1)
