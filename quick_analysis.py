#!/usr/bin/env python3
"""
Quick Battle Analysis - Run large-scale battle analysis with command line arguments
Usage: python quick_analysis.py [number_of_battles] [army_size]
Example: python quick_analysis.py 5000 8
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from battle_analyzer import BattleAnalyzer

def main():
    # Default values
    num_battles = 1000
    army_size = 8
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        try:
            num_battles = int(sys.argv[1])
        except ValueError:
            print(f"Invalid number of battles: {sys.argv[1]}. Using default: 1000")
    
    if len(sys.argv) > 2:
        try:
            army_size = int(sys.argv[2])
        except ValueError:
            print(f"Invalid army size: {sys.argv[2]}. Using default: 8")
    
    print(f"🏛️ QUICK BATTLE ANALYSIS 🏛️")
    print("=" * 50)
    print(f"Running {num_battles:,} battles with {army_size}-unit armies")
    print("=" * 50)
    
    # Run analysis
    analyzer = BattleAnalyzer()
    stats = analyzer.conduct_battle_analysis(num_battles, army_size)
    filename = analyzer.save_results_to_file()
    
    print(f"\n🎉 ANALYSIS COMPLETE! 🎉")
    print(f"📊 Generated visual reports and data files")
    print(f"💾 Results saved to: {filename}")
    print(f"🖼️  Check directory for PNG graph files")

if __name__ == "__main__":
    main()
