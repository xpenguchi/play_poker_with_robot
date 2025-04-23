#!/usr/bin/env python3
"""
Texas Hold'em Poker Game with Misty Integration - Main Entry File
Research Topic: The Role of Robot Voice Gender in Trust and Deception during Strategic Gameplay
"""

import tkinter as tk
import argparse
from game_misty import TexasHoldemGame

def main():
    """
    Main program entry function with command line arguments
    for Misty robot integration
    """
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Texas Hold\'em Poker Game with optional Misty Robot integration')
    parser.add_argument('--misty', action='store_true', help='Enable Misty robot integration')
    parser.add_argument('--ip', type=str, default='192.168.1.100', help='IP address of the Misty robot')
    parser.add_argument('--chips', type=int, default=12, help='Initial number of chips for each player')
    args = parser.parse_args()
    
    # Initialize the Tkinter window
    root = tk.Tk()
    
    # Create the game instance with or without Misty
    game = TexasHoldemGame(
        root, 
        initial_chips=args.chips,
        use_misty=args.misty,
        misty_ip=args.ip
    )
    
    # Set up window close handler to ensure proper cleanup
    def on_closing():
        if hasattr(game, 'cleanup'):
            game.cleanup()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the Tkinter main loop
    root.mainloop()

if __name__ == "__main__":
    main()