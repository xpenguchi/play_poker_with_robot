#!/usr/bin/env python3
"""
UI Components for Texas Hold'em Poker Game with Misty Integration
Handles the creation and management of the game's user interface elements
"""

import tkinter as tk
from tkinter import font
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
import sys
from pathlib import Path

class UIManager:
    """Manages the creation and updating of UI components"""
    
    def __init__(self, master, game_instance):
        """
        Initialize the UI manager
        
        Args:
            master: The Tkinter root window
            game_instance: The TexasHoldemGame instance
        """
        self.master = master
        self.game = game_instance
        
        # Set up fonts
        self.title_font = font.Font(family="Arial", size=16, weight="bold")
        self.info_font = font.Font(family="Arial", size=12)
        self.button_font = font.Font(family="Arial", size=12, weight="bold")
        
        # UI elements
        self.round_label = None
        self.player_chips_label = None
        self.pot_label = None
        self.robot_chips_label = None
        self.robot_voice_label = None
        self.robot_expression_label = None
        self.status_label = None
        self.results_label = None
        self.misty_status_label = None
        
        # Card display elements
        self.community_card_labels = []
        self.player_card_labels = []
        self.robot_card_labels = []
        
        # Control buttons
        self.fold_button = None
        self.check_button = None
        self.bet_button = None
        self.bet2_button = None
        self.next_round_button = None
        self.betting_frame = None
        
        # Create the UI layout
        self.setup_ui()
        
    def setup_ui(self):
        """Create the main UI layout"""
        # Configure the main window
        self.master.title("Simplified Texas Hold'em with Misty")
        self.master.geometry("800x600")
        self.master.configure(bg="#076324")  # Poker table green
        
        # Main header with round information
        self.round_label = tk.Label(
            self.master, 
            text="Round 0/6", 
            font=self.title_font, 
            bg="#076324", 
            fg="white"
        )
        self.round_label.pack(pady=(10, 0))
        
        # Misty status area (will be populated later if Misty is used)
        self.misty_status_frame = tk.Frame(self.master, bg="#076324")
        self.misty_status_frame.pack(pady=5)
        
        # Chips information display
        self.setup_chips_display()
        
        # Community cards area
        self.setup_community_cards()
        
        # Player cards area
        self.setup_player_cards()
        
        # Robot cards area
        self.setup_robot_cards()
        
        # Game status message
        self.status_label = tk.Label(
            self.master, 
            text="", 
            font=self.info_font, 
            bg="#076324", 
            fg="white",
            wraplength=600
        )
        self.status_label.pack(pady=10)
        
        # Betting controls
        self.setup_betting_controls()
        
        # Next round button
        self.next_round_button = tk.Button(
            self.master,
            text="Next Round", 
            font=self.button_font,
            command=self.game.start_new_round,
            state=tk.DISABLED
        )
        self.next_round_button.pack(pady=10)
        
        # Results area
        results_frame = tk.Frame(self.master, bg="#076324")
        results_frame.pack(expand=True, fill=tk.BOTH, pady=10)
        
        self.results_label = tk.Label(
            results_frame, 
            text="", 
            font=self.info_font, 
            bg="#076324", 
            fg="white"
        )
        self.results_label.pack()
    
    def add_misty_status(self, status_text):
        """
        Add or update Misty robot status in the UI
        
        Args:
            status_text (str): Status text to display
        """
        if self.misty_status_label is None:
            # Create the status label if it doesn't exist
            self.misty_status_label = tk.Label(
                self.misty_status_frame,
                text=status_text,
                font=self.info_font,
                bg="#076324",
                fg="#FFFF00"  # Yellow text for visibility
            )
            self.misty_status_label.pack(side=tk.LEFT, padx=10)
        else:
            # Update existing label
            self.misty_status_label.config(text=status_text)
    
    def update_misty_status(self, status_text):
        """
        Update Misty robot status in the UI
        
        Args:
            status_text (str): Status text to display
        """
        self.add_misty_status(status_text)
    
    def setup_chips_display(self):
        """Create the display for chips and pot"""
        chips_frame = tk.Frame(self.master, bg="#076324")
        chips_frame.pack(pady=5)
        
        self.player_chips_label = tk.Label(
            chips_frame, 
            text=f"Player Chips: {self.game.player_chips}", 
            font=self.info_font, 
            bg="#076324", 
            fg="white"
        )
        self.player_chips_label.pack(side=tk.LEFT, padx=10)
        
        self.pot_label = tk.Label(
            chips_frame, 
            text=f"Pot: {self.game.current_pot}", 
            font=self.info_font, 
            bg="#076324", 
            fg="white"
        )
        self.pot_label.pack(side=tk.LEFT, padx=10)
        
        self.robot_chips_label = tk.Label(
            chips_frame, 
            text=f"Robot Chips: {self.game.robot_chips}", 
            font=self.info_font, 
            bg="#076324", 
            fg="white"
        )
        self.robot_chips_label.pack(side=tk.LEFT, padx=10)
    
    def setup_community_cards(self):
        """Create the community cards display area"""
        community_frame = tk.Frame(self.master, bg="#076324")
        community_frame.pack(pady=10)
        
        tk.Label(
            community_frame, 
            text="Community Cards:", 
            font=self.info_font, 
            bg="#076324", 
            fg="white"
        ).pack(pady=(0, 5))
        
        cards_frame = tk.Frame(community_frame, bg="#076324")
        cards_frame.pack()
        
        # Create placeholders for 3 community cards
        for i in range(3):
            label = tk.Label(cards_frame, bg="#076324")
            label.pack(side=tk.LEFT, padx=5)
            self.community_card_labels.append(label)
    
    def setup_player_cards(self):
        """Create the player cards display area"""
        player_frame = tk.Frame(self.master, bg="#076324")
        player_frame.pack(pady=10)
        
        tk.Label(
            player_frame, 
            text="Your Hand:", 
            font=self.info_font, 
            bg="#076324", 
            fg="white"
        ).pack(pady=(0, 5))
        
        cards_frame = tk.Frame(player_frame, bg="#076324")
        cards_frame.pack()
        
        # Create placeholders for 2 player cards
        for i in range(2):
            label = tk.Label(cards_frame, bg="#076324")
            label.pack(side=tk.LEFT, padx=5)
            self.player_card_labels.append(label)
    
    def setup_robot_cards(self):
        """Create the robot cards display area"""
        robot_frame = tk.Frame(self.master, bg="#076324")
        robot_frame.pack(pady=10)
        
        info_frame = tk.Frame(robot_frame, bg="#076324")
        info_frame.pack()
        
        # Robot voice gender indicator
        self.robot_voice_label = tk.Label(
            info_frame,
            text=f"Robot Voice: {self.game.robot_voice_gender.capitalize()}",
            font=self.info_font,
            bg="#076324",
            fg="white"
        )
        self.robot_voice_label.pack(side=tk.LEFT, padx=5, pady=(0, 5))
        
        tk.Label(
            info_frame, 
            text="Robot's Hand:", 
            font=self.info_font, 
            bg="#076324", 
            fg="white"
        ).pack(side=tk.LEFT, pady=(0, 5))
        
        # Robot's expression (for deception cues)
        self.robot_expression_label = tk.Label(
            info_frame,
            text="😐",  # Neutral expression
            font=font.Font(family="Arial", size=20),
            bg="#076324",
            fg="white"
        )
        self.robot_expression_label.pack(side=tk.LEFT, padx=10, pady=(0, 5))
        
        cards_frame = tk.Frame(robot_frame, bg="#076324")
        cards_frame.pack()
        
        # Create placeholders for 2 robot cards
        for i in range(2):
            label = tk.Label(cards_frame, bg="#076324")
            label.pack(side=tk.LEFT, padx=5)
            self.robot_card_labels.append(label)
    
    def setup_betting_controls(self):
        """Create the betting control buttons"""
        betting_frame = tk.Frame(self.master, bg="#076324")
        betting_frame.pack(pady=10)
        self.betting_frame = betting_frame  # Store reference for later modifications
        
        self.fold_button = tk.Button(
            betting_frame, 
            text="Fold", 
            font=self.button_font,
            command=self.game.player_fold,
            state=tk.DISABLED
        )
        self.fold_button.pack(side=tk.LEFT, padx=5)
        
        self.check_button = tk.Button(
            betting_frame, 
            text="Check", 
            font=self.button_font,
            command=self.game.player_check,
            state=tk.DISABLED
        )
        self.check_button.pack(side=tk.LEFT, padx=5)
        
        self.bet_button = tk.Button(
            betting_frame, 
            text="Bet 1", 
            font=self.button_font,
            command=lambda: self.game.player_bet(1),
            state=tk.DISABLED
        )
        self.bet_button.pack(side=tk.LEFT, padx=5)
        
        self.bet2_button = tk.Button(
            betting_frame, 
            text="Bet 2", 
            font=self.button_font,
            command=lambda: self.game.player_bet(2),
            state=tk.DISABLED
        )
        self.bet2_button.pack(side=tk.LEFT, padx=5)
    
    def reset_betting_controls(self):
        """Reset betting controls to their default state"""
        # Clear all existing buttons first
        for widget in self.betting_frame.winfo_children():
            widget.destroy()
            
        # Recreate the default buttons
        self.fold_button = tk.Button(
            self.betting_frame, 
            text="Fold", 
            font=self.button_font,
            command=self.game.player_fold,
            state=tk.DISABLED
        )
        self.fold_button.pack(side=tk.LEFT, padx=5)
        
        self.check_button = tk.Button(
            self.betting_frame, 
            text="Check", 
            font=self.button_font,
            command=self.game.player_check,
            state=tk.DISABLED
        )
        self.check_button.pack(side=tk.LEFT, padx=5)
        
        self.bet_button = tk.Button(
            self.betting_frame, 
            text="Bet 1", 
            font=self.button_font,
            command=lambda: self.game.player_bet(1),
            state=tk.DISABLED
        )
        self.bet_button.pack(side=tk.LEFT, padx=5)
        
        self.bet2_button = tk.Button(
            self.betting_frame, 
            text="Bet 2", 
            font=self.button_font,
            command=lambda: self.game.player_bet(2),
            state=tk.DISABLED
        )
        self.bet2_button.pack(side=tk.LEFT, padx=5)
    
    def enable_betting_controls(self):
        """Enable the betting control buttons"""
        # Find and enable all buttons in the betting frame
        for widget in self.betting_frame.winfo_children():
            if isinstance(widget, tk.Button):
                widget.config(state=tk.NORMAL)
    
    def disable_betting_controls(self):
        """Disable the betting control buttons"""
        # Find and disable all buttons in the betting frame
        for widget in self.betting_frame.winfo_children():
            if isinstance(widget, tk.Button):
                widget.config(state=tk.DISABLED)
    
    def update_labels(self):
        """Update all UI labels with current game state"""
        self.round_label.config(text=f"Round {self.game.round_num}/{self.game.max_rounds}")
        self.player_chips_label.config(text=f"Player Chips: {self.game.player_chips}")
        self.pot_label.config(text=f"Pot: {self.game.current_pot}")
        self.robot_chips_label.config(text=f"Robot Chips: {self.game.robot_chips}")
        self.robot_voice_label.config(text=f"Robot Voice: {self.game.robot_voice_gender.capitalize()}")
        
        # Update results display
        results_text = "Results: "
        for i, result in enumerate(self.game.round_results):
            if result is True:
                results_text += "✅ "  # Win
            elif result is False:
                results_text += "❌ "  # Loss
            else:
                results_text += "🟰 "  # Tie
        
        self.results_label.config(text=results_text)
    
    def update_status(self, message):
        """Update the status message"""
        self.status_label.config(text=message)
    
    def update_robot_expression(self, expression):
        """Update the robot's facial expression"""
        self.robot_expression_label.config(text=expression)


class CardImageManager:
    """Manages loading and displaying card images"""
    
    def __init__(self, master):
        """
        Initialize the card image manager
        
        Args:
            master: The Tkinter root window
        """
        self.master = master
        self.card_images = {}
        self.card_back_image = None
        
        # Load card images
        self.load_card_images()
    
    def load_card_images(self):
        """Load card images from the cards directory"""
        # Find the directory where the script or executable is located
        if getattr(sys, 'frozen', False):  # Running as compiled
            application_path = Path(sys.executable).parent
        else:  # Running as script
            application_path = Path(__file__).parent
        
        cards_dir = application_path / "cards"
        
        # Create a directory for card images if it doesn't exist
        if not cards_dir.exists():
            cards_dir.mkdir(parents=True)
        
        # Load card back image
        back_path = cards_dir / "back.png"
        if back_path.exists():
            img = Image.open(back_path)
            img = img.resize((80, 120), Image.LANCZOS)
            self.card_back_image = ImageTk.PhotoImage(img)
        else:
            # Create a simple placeholder for card back
            self.card_back_image = self.create_placeholder_card("BACK", "#000080")
        
        # Create placeholder images for all cards
        ranks = {1: 'A', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 
                 8: '8', 9: '9', 10: '10', 11: 'J', 12: 'Q', 13: 'K'}
        suits = {'♥': 'hearts', '♦': 'diamonds', '♣': 'clubs', '♠': 'spades'}
        
        for rank in range(1, 14):
            for suit in ['♥', '♦', '♣', '♠']:
                card_key = f"{ranks[rank]}{suit}"
                text_color = "red" if suit in ['♥', '♦'] else "black"
                self.card_images[card_key] = self.create_placeholder_card(
                    card_key, "#FFFFFF", text_color)
    
    def create_placeholder_card(self, text, bg_color, text_color="white"):
        """
        Create a placeholder image for a card using PIL
        
        Args:
            text: Text to display on the card
            bg_color: Background color of the card
            text_color: Text color
            
        Returns:
            ImageTk.PhotoImage: The card placeholder image
        """
        # Create a new image with a solid background color
        img = Image.new('RGB', (80, 120), color=bg_color)
        draw = ImageDraw.Draw(img)
        
        # Try to use a built-in font, or default to a simple one
        try:
            font = ImageFont.truetype("Arial", 20)
        except IOError:
            font = ImageFont.load_default()
        
        # Calculate text position (centered)
        text_width = len(text) * 10  # Approximate width
        text_x = (80 - text_width) // 2
        text_y = (120 - 20) // 2  # Approximate height
        
        # Draw text on the image
        draw.text((text_x, text_y), text, fill=text_color, font=font)
        
        # Add a border
        draw.rectangle((0, 0, 79, 119), outline='black', width=2)
        
        # Convert to PhotoImage for Tkinter
        photo_img = ImageTk.PhotoImage(img)
        return photo_img
    
    def get_card_image(self, card):
        """
        Get the image for a card
        
        Args:
            card: Card object
            
        Returns:
            ImageTk.PhotoImage: The card image
        """
        card_key = str(card)
        return self.card_images.get(card_key, self.create_placeholder_card(card_key, "#FFFFFF"))
    
    def get_card_back(self):
        """
        Get the image for card back
        
        Returns:
            ImageTk.PhotoImage: The card back image
        """
        return self.card_back_image