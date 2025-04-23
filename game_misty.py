#!/usr/bin/env python3
"""
Main Game Class for Texas Hold'em Poker Game with Misty Robot Integration
Integrates all components and manages the overall game flow, including Misty robot control
"""

import tkinter as tk
from tkinter import messagebox
import random
import time
import threading
from PIL import Image, ImageTk, ImageSequence, ImageDraw

from models import Card, Deck, PokerHand, GameOutcome
from ui_misty import UIManager, CardImageManager
from admin_panel import AdminPanel
from questionnaire import PostGameQuestionnaire
from game_logic import get_predetermined_hand_setup, calculate_robot_bet, get_robot_expression
from utils import save_game_results, format_round_data
from misty_interface import MistyPokerPlayer

class TexasHoldemGame:
    """Main game class that manages the poker game with Misty integration"""
    
    def __init__(self, master, initial_chips=12, use_misty=True, misty_ip="192.168.1.100"):
        """
        Initialize the game
        
        Args:
            master: The Tkinter root window
            initial_chips (int, optional): Initial number of chips for each player. Defaults to 12.
            use_misty (bool, optional): Whether to use a Misty robot. Defaults to True.
            misty_ip (str, optional): IP address of the Misty robot. Defaults to "192.168.1.100".
        """
        self.master = master
        
        # Game state variables
        self.initial_chips = initial_chips
        self.player_chips = initial_chips
        self.robot_chips = initial_chips
        self.current_pot = 0
        self.round_num = 0
        self.max_rounds = 6
        self.player_wins = 0
        self.robot_wins = 0
        self.ties = 0
        self.round_results = []
        
        # Game components
        self.deck = Deck()
        self.community_cards = []
        self.player_hand = None
        self.robot_hand = None
        self.expected_outcome = None
        
        # Remote control variables
        self.admin_mode = False
        self.robot_betting_strategy = {"style": "neutral", "amount": 1}
        
        # Robot behavior variables
        self.robot_is_bluffing = False
        self.robot_voice_gender = "male"  # Default voice gender
        self.deception_type = "expression"
        
        # Misty robot integration
        self.use_misty = use_misty
        self.misty_ip = misty_ip
        self.misty = None
        if self.use_misty:
            try:
                self.misty = MistyPokerPlayer(ip_address=self.misty_ip)
                if not self.misty.misty.connected:
                    print("Failed to connect to Misty robot. Continuing without physical robot.")
                    self.use_misty = False
            except Exception as e:
                print(f"Error initializing Misty robot: {e}. Continuing without physical robot.")
                self.use_misty = False
        
        # Initialize UI components
        self.ui = UIManager(master, self)
        self.card_manager = CardImageManager(master)
        
        # Initialize admin panel
        self.admin_panel = AdminPanel(master, self)
        
        # Initialize questionnaire
        self.questionnaire = PostGameQuestionnaire(master, self)
        
        # Data tracking
        self.round_data = []
        
        # Add Misty connection status to UI if using Misty
        if self.use_misty and self.misty and self.misty.misty.connected:
            self.ui.add_misty_status("Connected to Misty robot")
        elif self.use_misty:
            self.ui.add_misty_status("Misty robot not connected")
        
        # Start the first round after a short delay
        self.master.after(500, self.start_new_round)
    
    def toggle_admin_mode(self, event=None):
        """
        Toggle the admin control panel visibility (Ctrl+A)
        
        Args:
            event: Key event (not used)
        """
        self.admin_mode = not self.admin_mode
        self.admin_panel.toggle_visibility()
    
    def start_new_round(self):
        """Start a new round of the game"""
        if self.round_num >= self.max_rounds:
            self.end_game()
            return
        
        if self.player_chips <= 0:
            messagebox.showinfo("Game Over", "You've run out of chips!")
            self.end_game()
            return
        
        self.round_num += 1
        self.current_pot = 0
        self.ui.update_labels()
        
        # Update robot voice gender display
        self.ui.robot_voice_label.config(text=f"Robot Voice: {self.robot_voice_gender.capitalize()}")
        
        # Reset robot expression to neutral
        self.ui.robot_expression_label.config(text="😐")
        
        # Update Misty if connected
        if self.use_misty and self.misty and self.misty.misty.connected:
            # Set Misty's voice gender
            self.misty.set_voice_gender(self.robot_voice_gender)
            
            # Handle new round
            threading.Thread(target=self.misty.handle_new_round).start()
        
        # Reset the deck and deal new cards
        self.deck.reset()
        
        # If admin mode is active and next_round_outcome is set, use it
        # Otherwise use the default rotating pattern
        if hasattr(self, 'next_round_outcome') and self.admin_mode:
            self.expected_outcome = self.next_round_outcome
        else:
            # Determine the outcome for this round (rotate between outcomes)
            outcomes = [GameOutcome.PLAYER_WINS, GameOutcome.ROBOT_WINS, GameOutcome.TIE]
            self.expected_outcome = outcomes[self.round_num % 3]
        
        # Set robot's bluffing for this round (50% chance by default)
        # In the prototype, this is controlled via the admin panel
        if not hasattr(self, 'robot_is_bluffing') or not self.admin_mode:
            self.robot_is_bluffing = random.choice([True, False])
        
        # Create new round data entry
        self.current_round_data = {
            'round_num': self.round_num,
            'expected_outcome': self.expected_outcome,
            'robot_bluffed': self.robot_is_bluffing,
            'player_folded': False,
            'player_bet_amount': 0,
            'robot_bet_amount': 0,
            'robot_voice_gender': self.robot_voice_gender,
            'player_detected_bluff': False  # Will be updated after the round
        }
        
        # Deal cards according to the expected outcome
        self.deal_predetermined_hand()
        
        # Show player cards and hidden robot cards
        self.show_player_cards()
        self.show_robot_cards_hidden()
        
        # If robot is bluffing, show deception cues
        if self.robot_is_bluffing:
            self.show_robot_deception()
        
        # Set hand quality for Misty
        if self.use_misty and self.misty and self.misty.misty.connected:
            if self.expected_outcome == GameOutcome.ROBOT_WINS:
                self.misty.set_hand_quality("good")
            elif self.expected_outcome == GameOutcome.PLAYER_WINS:
                self.misty.set_hand_quality("bad")
            else:  # TIE
                self.misty.set_hand_quality("average")
            
            self.misty.set_bluffing(self.robot_is_bluffing)
        
        # Set up betting controls
        self.ui.enable_betting_controls()
        self.ui.status_label.config(text="Your turn to bet")
        self.ui.next_round_button.config(state=tk.DISABLED)
    
    def deal_predetermined_hand(self):
        """Deal cards that will result in the expected outcome"""
        # Get the predetermined setup from the "backend"
        admin_settings = None
        if self.admin_mode:
            admin_settings = {
                'use_admin_settings': True,
                'outcome': self.expected_outcome,
                'robot_betting': self.robot_betting_strategy
            }
        
        hand_setup = get_predetermined_hand_setup(
            self.round_num,
            self.robot_voice_gender,
            admin_settings
        )
        
        # Set the cards based on the remote setup
        self.player_hand = PokerHand(hand_setup["player_cards"])
        self.robot_hand = PokerHand(hand_setup["robot_cards"])
        self.community_cards = hand_setup["community_cards"]
        self.expected_outcome = hand_setup["outcome"]
        
        # This would also set the robot's betting strategy
        self.robot_betting_strategy = hand_setup["robot_betting"]
        
        # Show community cards
        self.show_community_cards()
    
    def show_community_cards(self):
        """Display the community cards on the UI"""
        for i, card in enumerate(self.community_cards):
            # Get card image and update label
            card_image = self.card_manager.get_card_image(card)
            self.ui.community_card_labels[i].config(image=card_image)
            self.ui.community_card_labels[i].image = card_image  # Keep a reference to prevent garbage collection
    
    def show_player_cards(self):
        """Display the player's cards on the UI"""
        for i, card in enumerate(self.player_hand.cards):
            # Get card image and update label
            card_image = self.card_manager.get_card_image(card)
            self.ui.player_card_labels[i].config(image=card_image)
            self.ui.player_card_labels[i].image = card_image  # Keep a reference
    
    def show_robot_cards_hidden(self):
        """Display the robot's cards face down"""
        card_back = self.card_manager.get_card_back()
        for label in self.ui.robot_card_labels:
            label.config(image=card_back)
            label.image = card_back  # Keep a reference
    
    def show_robot_cards_revealed(self):
        """Display the robot's cards face up"""
        for i, card in enumerate(self.robot_hand.cards):
            # Get card image and update label
            card_image = self.card_manager.get_card_image(card)
            self.ui.robot_card_labels[i].config(image=card_image)
            self.ui.robot_card_labels[i].image = card_image  # Keep a reference
    
    def show_robot_deception(self):
        """Show deceptive cues from the robot"""
        # Determine the type of deception to show
        deception_type = getattr(self, 'deception_type', random.choice(['expression', 'verbal', 'both']))
        
        # Update robot's expression based on its hand and whether it's bluffing
        if deception_type in ['expression', 'both']:
            # Get appropriate expression based on bluffing status and expected outcome
            expression = get_robot_expression(self.expected_outcome, self.robot_is_bluffing)
            self.ui.robot_expression_label.config(text=expression)
        
        # Add verbal deception if applicable
        if deception_type in ['verbal', 'both']:
            if self.expected_outcome == GameOutcome.ROBOT_WINS:
                # Robot has good cards but pretends they're bad
                self.ui.status_label.config(text="Robot looks at its cards and sighs.")
            else:
                # Robot has bad/average cards but pretends they're good
                self.ui.status_label.config(text="Robot looks at its cards and seems confident.")
    
    def player_fold(self):
        """Handle player's decision to fold"""
        self.ui.disable_betting_controls()
        self.ui.status_label.config(text="You folded. Robot wins this round.")
        
        # Update round data
        if hasattr(self, 'current_round_data'):
            self.current_round_data['player_folded'] = True
            
            # If robot was bluffing and player folded, player was deceived
            if self.robot_is_bluffing and self.expected_outcome != GameOutcome.ROBOT_WINS:
                self.current_round_data['player_detected_bluff'] = False
            
            # Save the round data
            self.round_data.append(self.current_round_data)
        
# Robot wins the pot
        self.round_results.append(False)  # Player lost
        self.robot_wins += 1
        
        # Have Misty react if connected
        if self.use_misty and self.misty and self.misty.misty.connected:
            threading.Thread(target=self.misty.handle_win).start()
        
        # Show robot's cards
        self.show_robot_cards_revealed()
        
        # Enable next round button
        self.ui.next_round_button.config(state=tk.NORMAL)
    
    def player_bet(self, amount):
        """
        Handle player's bet
        
        Args:
            amount (int): The amount to bet
        """
        if amount > self.player_chips:
            messagebox.showinfo("Not enough chips", f"You only have {self.player_chips} chips!")
            return
        
        self.ui.disable_betting_controls()
        self.player_chips -= amount
        self.current_pot += amount
        self.ui.update_labels()
        
        # Update round data
        if hasattr(self, 'current_round_data'):
            self.current_round_data['player_bet_amount'] = amount
        
        self.ui.status_label.config(text=f"You bet {amount} chip(s). Robot is thinking...")
        
        # Simulate robot thinking - with actual Misty thinking animation if connected
        if self.use_misty and self.misty and self.misty.misty.connected:
            # Start Misty's thinking in a separate thread
            thinking_thread = threading.Thread(target=self.misty.handle_betting_turn)
            thinking_thread.start()
            
            # Wait a bit longer for Misty to finish its actions
            self.master.after(3000, lambda: self.robot_bet(amount))
        else:
            # Standard delay if no Misty
            self.master.after(1500, lambda: self.robot_bet(amount))
    
    def robot_bet(self, player_amount):
        """
        Handle robot's betting decision based on strategy
        
        Args:
            player_amount (int): The player's bet amount
        """
        # Calculate robot's bet based on its strategy and bluffing status
        robot_amount, message = calculate_robot_bet(
            player_amount,
            self.robot_chips,
            self.robot_betting_strategy,
            self.expected_outcome,
            self.robot_is_bluffing
        )
        
        # Update round data
        if hasattr(self, 'current_round_data'):
            self.current_round_data['robot_bet_amount'] = robot_amount
        
        # Update game state
        self.robot_chips -= robot_amount
        self.current_pot += robot_amount
        self.ui.update_labels()
        
        # Show robot's action
        self.ui.status_label.config(text=f"{message} Amount: {robot_amount} chip(s).")
        
        # Update robot expression based on deception status
        expression = get_robot_expression(self.expected_outcome, self.robot_is_bluffing)
        self.ui.robot_expression_label.config(text=expression)
        
        # Reveal robot's cards
        self.show_robot_cards_revealed()
        
        # Resolve the round after a delay
        self.master.after(1500, self.resolve_round)
    
    def resolve_round(self):
        """Determine the winner and update chips"""
        result_message = ""
        
        if self.expected_outcome == GameOutcome.PLAYER_WINS:
            result_message = "You win this round!"
            self.player_chips += self.current_pot
            self.round_results.append(True)  # Player won
            self.player_wins += 1
            
            # Have Misty react if connected
            if self.use_misty and self.misty and self.misty.misty.connected:
                threading.Thread(target=self.misty.handle_loss).start()
            
            # Update round data - if robot was bluffing with bad cards and player won
            if hasattr(self, 'current_round_data'):
                if self.robot_is_bluffing and self.expected_outcome != GameOutcome.ROBOT_WINS:
                    self.current_round_data['player_detected_bluff'] = True
        
        elif self.expected_outcome == GameOutcome.ROBOT_WINS:
            result_message = "Robot wins this round!"
            self.robot_chips += self.current_pot
            self.round_results.append(False)  # Player lost
            self.robot_wins += 1
            
            # Have Misty react if connected
            if self.use_misty and self.misty and self.misty.misty.connected:
                threading.Thread(target=self.misty.handle_win).start()
            
            # Update round data - if robot was bluffing with good cards and robot won
            if hasattr(self, 'current_round_data'):
                if self.robot_is_bluffing:
                    self.current_round_data['player_detected_bluff'] = False
        
        else:  # TIE
            result_message = "It's a tie! Pot is split."
            split_amount = self.current_pot // 2
            self.player_chips += split_amount
            self.robot_chips += split_amount
            # If odd amount, give the extra chip to the player
            if self.current_pot % 2 == 1:
                self.player_chips += 1
            self.round_results.append(None)  # Tie
            self.ties += 1
            
            # Have Misty react if connected
            if self.use_misty and self.misty and self.misty.misty.connected:
                threading.Thread(target=self.misty.handle_tie).start()
        
        # Save round data for analysis
        if hasattr(self, 'current_round_data'):
            self.round_data.append(self.current_round_data)
        
        self.current_pot = 0
        self.ui.update_labels()
        
        # Show result and hand comparison
        player_hand_str = str(self.player_hand)
        robot_hand_str = str(self.robot_hand)
        
        # Add information about robot's bluffing
        bluff_message = ""
        if hasattr(self, 'robot_is_bluffing') and self.robot_is_bluffing:
            if self.expected_outcome == GameOutcome.ROBOT_WINS:
                bluff_message = "The robot was bluffing by hiding its strong hand!"
            else:
                bluff_message = "The robot was bluffing by pretending to have a strong hand!"
        
        self.ui.status_label.config(
            text=f"{result_message}\nYour hand: {player_hand_str}\nRobot's hand: {robot_hand_str}\n{bluff_message}"
        )
        
        # Check if we need to switch voice gender (research proposal design)
        if self.round_num == self.max_rounds // 2:  # After half the rounds
            set_complete = True
            for result in self.round_results:
                if result is None:  # If any round hasn't been played
                    set_complete = False
                    break
            
            if set_complete and not hasattr(self, 'voice_switched'):
                self.voice_switched = True
                self.master.after(1000, self.alternate_voice_gender)
        
        # Enable next round button
        self.ui.next_round_button.config(state=tk.NORMAL)
    
    def alternate_voice_gender(self):
        """Alternate the robot's voice gender (as per the research proposal)"""
        # Switch voice gender
        self.robot_voice_gender = "female" if self.robot_voice_gender == "male" else "male"
        
        # Update display
        self.ui.robot_voice_label.config(text=f"Robot Voice: {self.robot_voice_gender.capitalize()}")
        
        # Update Misty if connected
        if self.use_misty and self.misty and self.misty.misty.connected:
            self.misty.set_voice_gender(self.robot_voice_gender)
        
        # Show a message about the change
        self.ui.status_label.config(
            text=f"The robot's voice has changed to {self.robot_voice_gender}. Taking a short break before continuing..."
        )
        
        # Disable all buttons during the break
        self.ui.disable_betting_controls()
        self.ui.next_round_button.config(state=tk.DISABLED)
        
        # Create a break message in a popup
        break_window = tk.Toplevel(self.master)
        break_window.title("Break Between Sets")
        break_window.geometry("400x200")
        break_window.configure(bg="white")
        
        tk.Label(
            break_window,
            text="Break Between Sets",
            font=("Arial", 16, "bold"),
            bg="white"
        ).pack(pady=10)
        
        tk.Label(
            break_window,
            text=f"You've completed the first set of rounds.\n\nThe robot's voice has been changed to {self.robot_voice_gender}.\n\nPlease take a short break before continuing with the next set.",
            font=("Arial", 12),
            bg="white",
            wraplength=350
        ).pack(pady=20)
        
        def close_break():
            break_window.destroy()
            self.ui.next_round_button.config(state=tk.NORMAL)
        
        tk.Button(
            break_window,
            text="Continue",
            font=("Arial", 12, "bold"),
            command=close_break
        ).pack(pady=10)
        
        # Have Misty announce the voice change if connected
        if self.use_misty and self.misty and self.misty.misty.connected:
            self.misty.misty.say_text(
                f"We are changing to a {self.robot_voice_gender} voice for the next set of rounds."
            )
    
    def end_game(self):
        """End the game and show final results"""
        final_message = f"Game Over!\n\n"
        final_message += f"Player wins: {self.player_wins}\n"
        final_message += f"Robot wins: {self.robot_wins}\n"
        final_message += f"Ties: {self.ties}\n\n"
        
        # Count how many times the robot bluffed
        bluff_count = sum(1 for round_data in self.round_data if round_data.get('robot_bluffed', False))
        
        # Count how many times the player was deceived
        deceived_count = sum(1 for round_data in self.round_data
                             if round_data.get('robot_bluffed', False) and 
                             not round_data.get('player_detected_bluff', True))
        
        if bluff_count > 0:
            final_message += f"Robot bluffed in {bluff_count} rounds\n"
            final_message += f"You were deceived {deceived_count} times\n\n"
        
        final_message += f"Your final chip count: {self.player_chips}\n"
        final_message += f"Robot's final chip count: {self.robot_chips}\n\n"
        
        if self.player_chips > self.robot_chips:
            final_message += "Congratulations! You beat the robot!"
            game_result = "player_wins"
        elif self.player_chips < self.robot_chips:
            final_message += "The robot won this time. Better luck next time!"
            game_result = "robot_wins"
        else:
            final_message += "It's a tie! An even match!"
            game_result = "tie"
        
        # Have Misty give a final reaction if connected
        if self.use_misty and self.misty and self.misty.misty.connected:
            if game_result == "player_wins":
                self.misty.handle_loss()
                self.misty.misty.say_text("Congratulations! You beat me this time.")
            elif game_result == "robot_wins":
                self.misty.handle_win()
                self.misty.misty.say_text("I won the overall game! Good playing.")
            else:
                self.misty.handle_tie()
                self.misty.misty.say_text("It's a tie game! We're evenly matched.")
        
        # Show final results
        self.ui.status_label.config(text=final_message)
        
        # Display round results
        results_text = "Round results:\n"
        for i, result in enumerate(self.round_results):
            icon = "✅" if result is True else "❌" if result is False else "🟰"
            results_text += f"Round {i+1}: {icon}  "
            if (i+1) % 3 == 0:
                results_text += "\n"
        
        self.ui.results_label.config(text=results_text)
        
        # Disable all game controls
        self.ui.disable_betting_controls()
        self.ui.next_round_button.config(state=tk.DISABLED)
        
        # Save game results
        results_data = {
            "player_wins": self.player_wins,
            "robot_wins": self.robot_wins,
            "ties": self.ties,
            "player_final_chips": self.player_chips,
            "robot_final_chips": self.robot_chips,
            "round_data": self.round_data,
            "stats": format_round_data(self.round_data)
        }
        save_game_results(results_data)
        
        # Show post-game questionnaire button
        questionnaire_button = tk.Button(
            self.master, 
            text="Complete Questionnaire", 
            font=self.ui.button_font,
            command=self.questionnaire.show_questionnaire
        )
        questionnaire_button.pack(pady=5)
        
        # Add a replay button
        replay_button = tk.Button(
            self.master, 
            text="Play Again", 
            font=self.ui.button_font,
            command=self.restart_game
        )
        replay_button.pack(pady=5)
    
    def restart_game(self):
        """Restart the entire game"""
        # Remove extra buttons
        for widget in self.master.winfo_children():
            if isinstance(widget, tk.Button) and widget.cget("text") in ["Complete Questionnaire", "Play Again"]:
                widget.destroy()
        
        # Reset game state
        self.player_chips = self.initial_chips
        self.robot_chips = self.initial_chips
        self.current_pot = 0
        self.round_num = 0
        self.player_wins = 0
        self.robot_wins = 0
        self.ties = 0
        self.round_results = []
        self.round_data = []
        
        # Reset robot voice to default
        self.robot_voice_gender = "male"  # Start with male voice
        if hasattr(self, 'voice_switched'):
            delattr(self, 'voice_switched')
        
        # Update Misty if connected
        if self.use_misty and self.misty and self.misty.misty.connected:
            self.misty.set_voice_gender(self.robot_voice_gender)
            self.misty.misty.say_text("Let's start a new game!")
        
        # Clear displays
        self.ui.status_label.config(text="")
        self.ui.results_label.config(text="")
        self.ui.robot_voice_label.config(text=f"Robot Voice: {self.robot_voice_gender.capitalize()}")
        
        # Clear card displays
        for label in self.ui.community_card_labels + self.ui.player_card_labels + self.ui.robot_card_labels:
            label.config(image="")
            label.image = None
        
        # Update UI
        self.ui.update_labels()
        
        # Start new round
        self.start_new_round()
    
    def cleanup(self):
        """Clean up resources when closing the game"""
        # Clean up Misty if connected
        if self.use_misty and self.misty and self.misty.misty.connected:
            try:
                self.misty.cleanup()
                print("Successfully disconnected from Misty robot.")
            except Exception as e:
                print(f"Error disconnecting from Misty: {e}")
        
        # Other cleanup tasks can be added here