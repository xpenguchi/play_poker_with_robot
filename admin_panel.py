#!/usr/bin/env python3
"""
Admin Panel for Texas Hold'em Poker Game
Provides an interface for researchers to control the game's behavior
"""

import tkinter as tk
from tkinter import messagebox
from models import GameOutcome

class AdminPanel:
    """Admin panel for controlling game behavior"""
    
    def __init__(self, master, game_instance):
        """
        Initialize the admin panel
        
        Args:
            master: The Tkinter root window
            game_instance: The TexasHoldemGame instance
        """
        self.master = master
        self.game = game_instance
        self.admin_frame = None
        
        # Admin panel variables
        self.outcome_var = None
        self.bet_style_var = None
        self.bet_amount_var = None
        self.custom_cards_var = None
        self.deception_var = None
        self.deception_type_var = None
        self.voice_gender_var = None
        
        # Panel state
        self.visible = False
        
        # Create the admin panel
        self.create_panel()
        
    def create_panel(self):
        """Create the admin panel UI"""
        # Main admin frame
        self.admin_frame = tk.Frame(self.master, bg="#333333", padx=10, pady=10)
        
        # Admin panel title
        self.admin_label = tk.Label(
            self.admin_frame,
            text="Admin Controls (Remote Backend Simulation)",
            font=self.game.ui.info_font,
            bg="#333333",
            fg="white"
        )
        self.admin_label.pack(pady=(0, 10))
        
        # Outcome control section
        self.create_outcome_controls()
        
        # Robot betting control section
        self.create_betting_controls()
        
        # Card control section
        self.create_card_controls()
        
        # Robot deception control section
        self.create_deception_controls()
        
        # Robot voice gender control section
        self.create_voice_controls()
        
        # Apply settings button
        self.apply_button = tk.Button(
            self.admin_frame,
            text="Apply Settings",
            font=self.game.ui.button_font,
            command=self.apply_settings
        )
        self.apply_button.pack(pady=10)
    
    def create_outcome_controls(self):
        """Create the game outcome controls"""
        # Outcome frame
        outcome_frame = tk.Frame(self.admin_frame, bg="#333333")
        outcome_frame.pack(fill=tk.X, pady=5)
        
        # Outcome label
        tk.Label(
            outcome_frame,
            text="Next Round Outcome:",
            font=self.game.ui.info_font,
            bg="#333333",
            fg="white"
        ).pack(side=tk.LEFT, padx=5)
        
        # Outcome selector
        self.outcome_var = tk.StringVar(value="PLAYER_WINS")
        outcomes = ["PLAYER_WINS", "ROBOT_WINS", "TIE"]
        self.outcome_menu = tk.OptionMenu(outcome_frame, self.outcome_var, *outcomes)
        self.outcome_menu.pack(side=tk.LEFT, padx=5)
    
    def create_betting_controls(self):
        """Create the robot betting controls"""
        # Betting frame
        betting_frame = tk.Frame(self.admin_frame, bg="#333333")
        betting_frame.pack(fill=tk.X, pady=5)
        
        # Betting style label
        tk.Label(
            betting_frame,
            text="Robot Betting Style:",
            font=self.game.ui.info_font,
            bg="#333333",
            fg="white"
        ).pack(side=tk.LEFT, padx=5)
        
        # Betting style selector
        self.bet_style_var = tk.StringVar(value="neutral")
        bet_styles = ["aggressive", "neutral", "conservative"]
        self.bet_style_menu = tk.OptionMenu(betting_frame, self.bet_style_var, *bet_styles)
        self.bet_style_menu.pack(side=tk.LEFT, padx=5)
        
        # Betting amount label
        tk.Label(
            betting_frame,
            text="Amount:",
            font=self.game.ui.info_font,
            bg="#333333",
            fg="white"
        ).pack(side=tk.LEFT, padx=5)
        
        # Betting amount spinner
        self.bet_amount_var = tk.IntVar(value=1)
        self.bet_amount_spinner = tk.Spinbox(
            betting_frame,
            from_=1,
            to=5,
            width=2,
            textvariable=self.bet_amount_var
        )
        self.bet_amount_spinner.pack(side=tk.LEFT, padx=5)
    
    def create_card_controls(self):
        """Create the custom card controls"""
        # Card control frame
        card_frame = tk.Frame(self.admin_frame, bg="#333333")
        card_frame.pack(fill=tk.X, pady=5)
        
        # Custom cards label
        tk.Label(
            card_frame,
            text="Custom Cards:",
            font=self.game.ui.info_font,
            bg="#333333",
            fg="white"
        ).pack(side=tk.LEFT, padx=5)
        
        # Custom cards checkbox
        self.custom_cards_var = tk.BooleanVar(value=False)
        self.custom_cards_check = tk.Checkbutton(
            card_frame,
            text="Enable",
            variable=self.custom_cards_var,
            bg="#333333",
            fg="white",
            selectcolor="black",
            activebackground="#333333",
            activeforeground="white"
        )
        self.custom_cards_check.pack(side=tk.LEFT, padx=5)
    
    def create_deception_controls(self):
        """Create the robot deception controls"""
        # Deception frame
        deception_frame = tk.Frame(self.admin_frame, bg="#333333")
        deception_frame.pack(fill=tk.X, pady=5)
        
        # Deception label
        tk.Label(
            deception_frame,
            text="Robot Deception:",
            font=self.game.ui.info_font,
            bg="#333333",
            fg="white"
        ).pack(side=tk.LEFT, padx=5)
        
        # Deception checkbox
        self.deception_var = tk.BooleanVar(value=False)
        self.deception_check = tk.Checkbutton(
            deception_frame,
            text="Enable Bluffing",
            variable=self.deception_var,
            bg="#333333",
            fg="white",
            selectcolor="black",
            activebackground="#333333",
            activeforeground="white"
        )
        self.deception_check.pack(side=tk.LEFT, padx=5)
        
        # Deception type label
        tk.Label(
            deception_frame,
            text="Type:",
            font=self.game.ui.info_font,
            bg="#333333",
            fg="white"
        ).pack(side=tk.LEFT, padx=5)
        
        # Deception type selector
        self.deception_type_var = tk.StringVar(value="expression")
        deception_types = ["expression", "verbal", "both"]
        self.deception_type_menu = tk.OptionMenu(
            deception_frame, 
            self.deception_type_var, 
            *deception_types
        )
        self.deception_type_menu.pack(side=tk.LEFT, padx=5)
    
    def create_voice_controls(self):
        """Create the robot voice gender controls"""
        # Voice frame
        voice_frame = tk.Frame(self.admin_frame, bg="#333333")
        voice_frame.pack(fill=tk.X, pady=5)
        
        # Voice gender label
        tk.Label(
            voice_frame,
            text="Robot Voice Gender:",
            font=self.game.ui.info_font,
            bg="#333333",
            fg="white"
        ).pack(side=tk.LEFT, padx=5)
        
        # Voice gender selector
        self.voice_gender_var = tk.StringVar(value=self.game.robot_voice_gender)
        gender_options = ["male", "female"]
        self.voice_gender_menu = tk.OptionMenu(
            voice_frame, 
            self.voice_gender_var, 
            *gender_options
        )
        self.voice_gender_menu.pack(side=tk.LEFT, padx=5)
    
    def apply_settings(self):
        """Apply the admin settings to the game"""
        # Update the robot betting strategy
        self.game.robot_betting_strategy = {
            "style": self.bet_style_var.get(),
            "amount": self.bet_amount_var.get()
        }
        
        # Set the expected outcome for the next round
        outcome_map = {
            "PLAYER_WINS": GameOutcome.PLAYER_WINS,
            "ROBOT_WINS": GameOutcome.ROBOT_WINS,
            "TIE": GameOutcome.TIE
        }
        self.game.next_round_outcome = outcome_map[self.outcome_var.get()]
        
        # Enable custom cards if checked
        self.game.custom_cards_enabled = self.custom_cards_var.get()
        
        # Set robot deception settings
        self.game.robot_is_bluffing = self.deception_var.get()
        self.game.deception_type = self.deception_type_var.get()
        
        # Set robot voice gender
        self.game.robot_voice_gender = self.voice_gender_var.get()
        self.game.ui.robot_voice_label.config(text=f"Robot Voice: {self.game.robot_voice_gender.capitalize()}")
        
        messagebox.showinfo("Admin Settings", "Settings applied for the next round.")
    
    def toggle_visibility(self):
        """Toggle the visibility of the admin panel"""
        self.visible = not self.visible
        
        if self.visible:
            # Show admin panel
            self.admin_frame.pack(fill=tk.X, pady=5, after=self.game.ui.round_label)
        else:
            # Hide admin panel
            self.admin_frame.pack_forget()