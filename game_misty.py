#!/usr/bin/env python3
"""
Main Game Class for Texas Hold'em Poker Game with Misty Robot Integration
Integrates all components and manages the overall game flow, including Misty robot control
Fixed to properly compare poker hands and handle betting logic
"""

import tkinter as tk
from tkinter import messagebox
import random
import time
import threading
from PIL import Image, ImageTk, ImageSequence, ImageDraw

from models import Card, Deck, PokerHand, GameOutcome
from ui_misty import UIManager, CardImageManager
from questionnaire import PostGameQuestionnaire
from game_logic import get_predetermined_hand_setup, calculate_robot_bet, get_robot_expression, get_robot_message
from game_logic import get_hand_description, HAND_TYPE_NAMES
from utils import save_game_results, format_round_data
from misty_interface import MistyPokerPlayer

def enum_to_str(enum_value):
    if hasattr(enum_value, 'name'):
        return enum_value.name
    return str(enum_value)

def compare_poker_hands(player_cards, robot_cards, community_cards, player_hand_type, robot_hand_type):
    """
    Compare two poker hands and determine the winner based on standard poker rules.
    
    Args:
        player_cards (list): List of Card objects for player's hole cards
        robot_cards (list): List of Card objects for robot's hole cards
        community_cards (list): List of Card objects for community cards
        player_hand_type (int): The player's hand type (e.g., ONE_PAIR, TWO_PAIR)
        robot_hand_type (int): The robot's hand type (e.g., ONE_PAIR, TWO_PAIR)
        
    Returns:
        GameOutcome: PLAYER_WINS, ROBOT_WINS, or TIE
    """
    # First compare hand types (higher value is better)
    if player_hand_type > robot_hand_type:
        return GameOutcome.PLAYER_WINS
    elif robot_hand_type > player_hand_type:
        return GameOutcome.ROBOT_WINS
    
    # If hand types are the same, compare based on the specific hand type
    if player_hand_type == robot_hand_type:
        # Get all player and robot cards (hole + community)
        player_all_cards = player_cards + community_cards
        robot_all_cards = robot_cards + community_cards
        
        # For high card - compare highest cards
        if player_hand_type == 0:  # HIGH_CARD
            player_values = sorted([14 if c.rank == 1 else c.rank for c in player_all_cards], reverse=True)
            robot_values = sorted([14 if c.rank == 1 else c.rank for c in robot_all_cards], reverse=True)
            
            # Compare each card from highest to lowest
            for i in range(min(5, len(player_values))):
                if player_values[i] > robot_values[i]:
                    return GameOutcome.PLAYER_WINS
                elif robot_values[i] > player_values[i]:
                    return GameOutcome.ROBOT_WINS
                
        # For one pair - compare pair rank then kickers
        elif player_hand_type == 1:  # ONE_PAIR
            # Find player's pair
            player_ranks = [c.rank for c in player_all_cards]
            robot_ranks = [c.rank for c in robot_all_cards]
            
            player_pair_rank = next((r for r in player_ranks if player_ranks.count(r) >= 2), 0)
            robot_pair_rank = next((r for r in robot_ranks if robot_ranks.count(r) >= 2), 0)
            
            # Adjust for Aces
            if player_pair_rank == 1: player_pair_rank = 14
            if robot_pair_rank == 1: robot_pair_rank = 14
            
            if player_pair_rank > robot_pair_rank:
                return GameOutcome.PLAYER_WINS
            elif robot_pair_rank > player_pair_rank:
                return GameOutcome.ROBOT_WINS
                
            # If pairs are the same, compare kickers
            player_kickers = sorted([14 if c.rank == 1 else c.rank for c in player_all_cards 
                                     if c.rank != player_pair_rank], reverse=True)
            robot_kickers = sorted([14 if c.rank == 1 else c.rank for c in robot_all_cards 
                                   if c.rank != robot_pair_rank], reverse=True)
            
            for i in range(min(3, len(player_kickers), len(robot_kickers))):
                if player_kickers[i] > robot_kickers[i]:
                    return GameOutcome.PLAYER_WINS
                elif robot_kickers[i] > player_kickers[i]:
                    return GameOutcome.ROBOT_WINS
        
        # For two pair - compare higher pair, then lower pair, then kicker
        elif player_hand_type == 2:  # TWO_PAIR
            # Find player's pairs
            player_ranks = [c.rank for c in player_all_cards]
            robot_ranks = [c.rank for c in robot_all_cards]
            
            player_pairs = sorted([r for r in set(player_ranks) if player_ranks.count(r) >= 2], 
                                  key=lambda x: 14 if x == 1 else x, reverse=True)
            robot_pairs = sorted([r for r in set(robot_ranks) if robot_ranks.count(r) >= 2],
                                key=lambda x: 14 if x == 1 else x, reverse=True)
            
            # Compare higher pairs
            player_high_pair = player_pairs[0] if player_pairs else 0
            robot_high_pair = robot_pairs[0] if robot_pairs else 0
            player_high_pair = 14 if player_high_pair == 1 else player_high_pair
            robot_high_pair = 14 if robot_high_pair == 1 else robot_high_pair
            
            if player_high_pair > robot_high_pair:
                return GameOutcome.PLAYER_WINS
            elif robot_high_pair > player_high_pair:
                return GameOutcome.ROBOT_WINS
            
            # Compare lower pairs
            if len(player_pairs) > 1 and len(robot_pairs) > 1:
                player_low_pair = player_pairs[1]
                robot_low_pair = robot_pairs[1]
                player_low_pair = 14 if player_low_pair == 1 else player_low_pair
                robot_low_pair = 14 if robot_low_pair == 1 else robot_low_pair
                
                if player_low_pair > robot_low_pair:
                    return GameOutcome.PLAYER_WINS
                elif robot_low_pair > player_low_pair:
                    return GameOutcome.ROBOT_WINS
            
            # If both pairs are the same, compare kickers
            player_kickers = [14 if c.rank == 1 else c.rank for c in player_all_cards 
                             if c.rank != player_pairs[0] and c.rank != (player_pairs[1] if len(player_pairs) > 1 else -1)]
            robot_kickers = [14 if c.rank == 1 else c.rank for c in robot_all_cards 
                            if c.rank != robot_pairs[0] and c.rank != (robot_pairs[1] if len(robot_pairs) > 1 else -1)]
            
            player_kicker = max(player_kickers) if player_kickers else 0
            robot_kicker = max(robot_kickers) if robot_kickers else 0
            
            if player_kicker > robot_kicker:
                return GameOutcome.PLAYER_WINS
            elif robot_kicker > player_kicker:
                return GameOutcome.ROBOT_WINS
        
        # For three of a kind - compare trips rank then kickers
        elif player_hand_type == 3:  # THREE_OF_A_KIND
            # Find player's trips
            player_ranks = [c.rank for c in player_all_cards]
            robot_ranks = [c.rank for c in robot_all_cards]
            
            player_trips_rank = next((r for r in player_ranks if player_ranks.count(r) >= 3), 0)
            robot_trips_rank = next((r for r in robot_ranks if robot_ranks.count(r) >= 3), 0)
            
            # Adjust for Aces
            if player_trips_rank == 1: player_trips_rank = 14
            if robot_trips_rank == 1: robot_trips_rank = 14
            
            if player_trips_rank > robot_trips_rank:
                return GameOutcome.PLAYER_WINS
            elif robot_trips_rank > player_trips_rank:
                return GameOutcome.ROBOT_WINS
                
            # If trips are the same, compare kickers (very unlikely in Texas Hold'em)
            player_kickers = sorted([14 if c.rank == 1 else c.rank for c in player_all_cards 
                                     if c.rank != player_trips_rank], reverse=True)
            robot_kickers = sorted([14 if c.rank == 1 else c.rank for c in robot_all_cards 
                                   if c.rank != robot_trips_rank], reverse=True)
            
            for i in range(min(2, len(player_kickers), len(robot_kickers))):
                if player_kickers[i] > robot_kickers[i]:
                    return GameOutcome.PLAYER_WINS
                elif robot_kickers[i] > player_kickers[i]:
                    return GameOutcome.ROBOT_WINS
        
        # For straight - compare highest card
        elif player_hand_type == 4:  # STRAIGHT
            player_values = sorted([14 if c.rank == 1 else c.rank for c in player_all_cards])
            robot_values = sorted([14 if c.rank == 1 else c.rank for c in robot_all_cards])
            
            # Special case for A-5 straight (where Ace is low)
            if set([14, 2, 3, 4, 5]).issubset(set(player_values)):
                player_straight_high = 5
            else:
                player_straight_high = max(player_values)
                
            if set([14, 2, 3, 4, 5]).issubset(set(robot_values)):
                robot_straight_high = 5
            else:
                robot_straight_high = max(robot_values)
                
            if player_straight_high > robot_straight_high:
                return GameOutcome.PLAYER_WINS
            elif robot_straight_high > player_straight_high:
                return GameOutcome.ROBOT_WINS
        
        # For flush - compare highest card, then next highest, etc.
        elif player_hand_type == 5:  # FLUSH
            # Group cards by suit
            player_suits = {}
            robot_suits = {}
            
            for card in player_all_cards:
                if card.suit not in player_suits:
                    player_suits[card.suit] = []
                player_suits[card.suit].append(14 if card.rank == 1 else card.rank)
                
            for card in robot_all_cards:
                if card.suit not in robot_suits:
                    robot_suits[card.suit] = []
                robot_suits[card.suit].append(14 if card.rank == 1 else card.rank)
            
            # Find flush suit
            player_flush_suit = next((suit for suit, cards in player_suits.items() if len(cards) >= 5), None)
            robot_flush_suit = next((suit for suit, cards in robot_suits.items() if len(cards) >= 5), None)
            
            if player_flush_suit and robot_flush_suit:
                player_flush = sorted(player_suits[player_flush_suit], reverse=True)[:5]
                robot_flush = sorted(robot_suits[robot_flush_suit], reverse=True)[:5]
                
                for i in range(5):
                    if player_flush[i] > robot_flush[i]:
                        return GameOutcome.PLAYER_WINS
                    elif robot_flush[i] > player_flush[i]:
                        return GameOutcome.ROBOT_WINS
        
        # For full house - compare trips, then pair
        elif player_hand_type == 6:  # FULL_HOUSE
            player_ranks = [c.rank for c in player_all_cards]
            robot_ranks = [c.rank for c in robot_all_cards]
            
            # Find trips and pair
            player_rank_counts = {r: player_ranks.count(r) for r in set(player_ranks)}
            robot_rank_counts = {r: robot_ranks.count(r) for r in set(robot_ranks)}
            
            player_trips = [r for r, count in player_rank_counts.items() if count >= 3]
            player_pairs = [r for r, count in player_rank_counts.items() if count >= 2]
            robot_trips = [r for r, count in robot_rank_counts.items() if count >= 3]
            robot_pairs = [r for r, count in robot_rank_counts.items() if count >= 2]
            
            # Compare trips (adjust for Aces)
            player_trip_rank = max(player_trips, key=lambda x: 14 if x == 1 else x)
            robot_trip_rank = max(robot_trips, key=lambda x: 14 if x == 1 else x)
            
            player_trip_rank = 14 if player_trip_rank == 1 else player_trip_rank
            robot_trip_rank = 14 if robot_trip_rank == 1 else robot_trip_rank
            
            if player_trip_rank > robot_trip_rank:
                return GameOutcome.PLAYER_WINS
            elif robot_trip_rank > player_trip_rank:
                return GameOutcome.ROBOT_WINS
            
            # If trips are the same, compare pairs
            player_pair_candidates = [r for r in player_pairs if r != player_trip_rank]
            robot_pair_candidates = [r for r in robot_pairs if r != robot_trip_rank]
            
            if player_pair_candidates and robot_pair_candidates:
                player_pair_rank = max(player_pair_candidates, key=lambda x: 14 if x == 1 else x)
                robot_pair_rank = max(robot_pair_candidates, key=lambda x: 14 if x == 1 else x)
                
                player_pair_rank = 14 if player_pair_rank == 1 else player_pair_rank
                robot_pair_rank = 14 if robot_pair_rank == 1 else robot_pair_rank
                
                if player_pair_rank > robot_pair_rank:
                    return GameOutcome.PLAYER_WINS
                elif robot_pair_rank > player_pair_rank:
                    return GameOutcome.ROBOT_WINS
        
        # For four of a kind - compare quads, then kicker
        elif player_hand_type == 7:  # FOUR_OF_A_KIND
            player_ranks = [c.rank for c in player_all_cards]
            robot_ranks = [c.rank for c in robot_all_cards]
            
            player_quads_rank = next((r for r in player_ranks if player_ranks.count(r) >= 4), 0)
            robot_quads_rank = next((r for r in robot_ranks if robot_ranks.count(r) >= 4), 0)
            
            # Adjust for Aces
            if player_quads_rank == 1: player_quads_rank = 14
            if robot_quads_rank == 1: robot_quads_rank = 14
            
            if player_quads_rank > robot_quads_rank:
                return GameOutcome.PLAYER_WINS
            elif robot_quads_rank > player_quads_rank:
                return GameOutcome.ROBOT_WINS
                
            # If quads are the same, compare kickers
            player_kicker = max([14 if c.rank == 1 else c.rank for c in player_all_cards 
                                if c.rank != player_quads_rank])
            robot_kicker = max([14 if c.rank == 1 else c.rank for c in robot_all_cards 
                               if c.rank != robot_quads_rank])
            
            if player_kicker > robot_kicker:
                return GameOutcome.PLAYER_WINS
            elif robot_kicker > player_kicker:
                return GameOutcome.ROBOT_WINS
        
        # For straight flush - compare highest card
        elif player_hand_type == 8:  # STRAIGHT_FLUSH
            # Similar to straight comparison but with suit check
            player_suits = {}
            robot_suits = {}
            
            for card in player_all_cards:
                if card.suit not in player_suits:
                    player_suits[card.suit] = []
                player_suits[card.suit].append(14 if card.rank == 1 else card.rank)
                
            for card in robot_all_cards:
                if card.suit not in robot_suits:
                    robot_suits[card.suit] = []
                robot_suits[card.suit].append(14 if card.rank == 1 else card.rank)
            
            # Find straight flush
            player_sf_high = 0
            robot_sf_high = 0
            
            for suit, values in player_suits.items():
                if len(values) >= 5:
                    # Check for straight in this suit
                    values = sorted(set(values))
                    for i in range(len(values) - 4):
                        if values[i:i+5] == list(range(values[i], values[i] + 5)):
                            player_sf_high = max(player_sf_high, values[i] + 4)
                    # Check for wheel (A-5) straight flush
                    if set([14, 2, 3, 4, 5]).issubset(set(values)):
                        player_sf_high = max(player_sf_high, 5)
            
            for suit, values in robot_suits.items():
                if len(values) >= 5:
                    # Check for straight in this suit
                    values = sorted(set(values))
                    for i in range(len(values) - 4):
                        if values[i:i+5] == list(range(values[i], values[i] + 5)):
                            robot_sf_high = max(robot_sf_high, values[i] + 4)
                    # Check for wheel (A-5) straight flush
                    if set([14, 2, 3, 4, 5]).issubset(set(values)):
                        robot_sf_high = max(robot_sf_high, 5)
            
            if player_sf_high > robot_sf_high:
                return GameOutcome.PLAYER_WINS
            elif robot_sf_high > player_sf_high:
                return GameOutcome.ROBOT_WINS
    
    # If we get here, it's a true tie
    return GameOutcome.TIE

class TexasHoldemGame:
    """Main game class that manages the poker game with Misty integration"""
    
    def __init__(self, master, initial_chips=12, use_misty=True, misty_ip="192.168.1.100", robot_voice="random"):
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
        # Game seed for reproducibility
        self.seed = random.randint(0, 1000000)
        random.seed(self.seed)
        
        # Game components
        self.deck = Deck()
        self.community_cards = []
        self.player_hand = None
        self.robot_hand = None
        self.expected_outcome = None
        
        # Robot behavior variables
        self.robot_is_bluffing = False
        if robot_voice == "random":
            self.robot_voice_gender = random.choice(["male", "female"])
        else:
            self.robot_voice_gender = robot_voice
        self.robot_betting_strategy = {"style": "neutral", "amount": 1}
        self.hand_setup = None
        
        # Turn-based betting variables
        self.current_betting_round = 0
        self.player_has_bet = False
        
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
                else:
                    self.misty.set_voice_gender(self.robot_voice_gender)
            except Exception as e:
                print(f"Error initializing Misty robot: {e}. Continuing without physical robot.")
                self.use_misty = False
        
        # Initialize UI components
        self.ui = UIManager(master, self)
        self.card_manager = CardImageManager(master)
        
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
        
        # Deal cards according to the predetermined hand setup
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
            
            # Have Misty say something about its hand based on bluffing status
            robot_message = get_robot_message(self.hand_setup, self.robot_is_bluffing)
            self.misty.misty.say_text(robot_message)
        
        # Create new round data entry
        self.current_round_data = {
            'round_num': self.round_num,
            'expected_outcome': self.expected_outcome.name if hasattr(self.expected_outcome, 'name') else str(self.expected_outcome),
            'robot_bluffed': self.robot_is_bluffing,
            'player_folded': False,
            'player_bet_amount': 0,
            'robot_bet_amount': 0,
            'robot_voice_gender': self.robot_voice_gender,
            'player_detected_bluff': False
        }
        
        # Set up betting controls for turn-based play
        self.ui.reset_betting_controls()
        self.ui.enable_betting_controls()
        self.ui.status_label.config(text="Your turn to bet. You can check (0) or bet.")
        self.ui.next_round_button.config(state=tk.DISABLED)
        
        # Initialize the betting phase
        self.current_betting_round = 1
        self.player_has_bet = False

        self.ui.reset_betting_controls()
        
        # Set up the thinking time countdown and disable betting controls
        self.ui.status_label.config(text="Thinking time: 5 seconds... Please observe the cards carefully.")
        self.ui.disable_betting_controls()
        self.ui.next_round_button.config(state=tk.DISABLED)
        
        # Use a countdown timer for the thinking time
        self.thinking_time = 5
        self.update_thinking_countdown()

    def update_thinking_countdown(self):
        """Update the countdown for the thinking time"""
        if self.thinking_time > 0:
            self.ui.status_label.config(text=f"Thinking time: {self.thinking_time} seconds... Please observe the cards carefully.")
            self.thinking_time -= 1
            self.master.after(1000, self.update_thinking_countdown)
        else:
            self.enable_betting_after_thinking()

    def enable_betting_after_thinking(self):
        """Enable betting controls after thinking time is over"""
        self.ui.enable_betting_controls()
        self.ui.status_label.config(text="Your turn to bet. You can check (0) or bet.")
        self.ui.next_round_button.config(state=tk.DISABLED)
        
        self.current_betting_round = 1
        self.player_has_bet = False
    
    def deal_predetermined_hand(self):
        """Deal cards that will result in the expected outcome"""
        # Get the predetermined setup from the new handler
        self.hand_setup = get_predetermined_hand_setup(
            self.round_num,
            self.robot_voice_gender,
            self.seed
        )
        
        # Set the cards based on the setup
        self.player_hand = PokerHand(self.hand_setup["player_cards"])
        self.robot_hand = PokerHand(self.hand_setup["robot_cards"])
        self.community_cards = self.hand_setup["community_cards"]
        self.expected_outcome = self.hand_setup["outcome"]
        
        # Set robot's betting strategy
        self.robot_betting_strategy = self.hand_setup["robot_betting"]
        
        # Set robot's bluffing status
        self.robot_is_bluffing = self.hand_setup["robot_is_bluffing"]
        
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
        # Update robot's expression based on its hand and whether it's bluffing
        expression = get_robot_expression(self.expected_outcome, self.robot_is_bluffing)
        self.ui.robot_expression_label.config(text=expression)
        
        # Display verbal deception
        if self.expected_outcome == GameOutcome.ROBOT_WINS and self.robot_is_bluffing:
            # Robot has good cards but pretends they're bad
            self.ui.status_label.config(text="Robot looks at its cards and sighs.")
        elif self.expected_outcome != GameOutcome.ROBOT_WINS and self.robot_is_bluffing:
            # Robot has bad/average cards but pretends they're good
            self.ui.status_label.config(text="Robot looks at its cards and seems confident.")
    
    def player_fold(self):
        """Handle player's decision to fold"""
        self.ui.disable_betting_controls()
        
        # Update round data
        if hasattr(self, 'current_round_data'):
            self.current_round_data['player_folded'] = True
            
            # If robot was bluffing and player folded, player was deceived
            if self.robot_is_bluffing and self.expected_outcome != GameOutcome.ROBOT_WINS:
                self.current_round_data['player_detected_bluff'] = False

            if not isinstance(self.current_round_data['expected_outcome'], str):
                self.current_round_data['expected_outcome'] = self.expected_outcome.name if hasattr(self.expected_outcome, 'name') else str(self.expected_outcome)
            
            # Save the round data
            self.round_data.append(self.current_round_data)
        
        # Robot wins the pot
        self.robot_chips += self.current_pot
        self.round_results.append(False)  # Player lost
        self.robot_wins += 1
        
        # Have Misty react if connected
        if self.use_misty and self.misty and self.misty.misty.connected:
            threading.Thread(target=self.misty.handle_win).start()
        
        # Show robot's cards
        self.show_robot_cards_revealed()
        
        # Get hand descriptions for display
        player_hand_type = self.hand_setup.get("player_hand_type", 0)
        robot_hand_type = self.hand_setup.get("robot_hand_type", 0)
        player_hand_desc = get_hand_description(player_hand_type, self.player_hand.cards + self.community_cards)
        robot_hand_desc = get_hand_description(robot_hand_type, self.robot_hand.cards + self.community_cards)
        
        # Update status with hand types
        self.ui.status_label.config(
            text=f"You folded. Robot wins this round.\nYour hand: {player_hand_desc} ({HAND_TYPE_NAMES[player_hand_type]})\nRobot's hand: {robot_hand_desc} ({HAND_TYPE_NAMES[robot_hand_type]})"
        )
        
        # Update UI labels
        self.current_pot = 0
        self.ui.update_labels()
        
        # Enable next round button
        self.ui.next_round_button.config(state=tk.NORMAL)
    
    def player_check(self):
        """Handle player's decision to check (bet 0)"""
        # Player checks (bets 0)
        self.ui.disable_betting_controls()
        self.ui.status_label.config(text="You checked. Robot is thinking...")
        
        # Update round data if needed
        if hasattr(self, 'current_round_data'):
            self.current_round_data['player_bet_amount'] = 0
        
        # Let the robot respond
        self.robot_turn_to_bet(0)
    
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
        
        # Now it's the robot's turn to respond
        self.robot_turn_to_bet(amount)
    
    def robot_turn_to_bet(self, player_amount):
        """
        Handle the robot's turn to bet after the player's action
        
        Args:
            player_amount (int): The player's bet amount
        """
        # Simulate robot thinking with Misty
        if self.use_misty and self.misty and self.misty.misty.connected:
            # Start Misty's thinking in a separate thread
            thinking_thread = threading.Thread(target=self.misty.handle_betting_turn)
            thinking_thread.start()
            
            # Wait a bit longer for Misty to finish its actions
            self.master.after(3000, lambda: self.robot_bet(player_amount))
        else:
            # Standard delay if no Misty
            self.master.after(1500, lambda: self.robot_bet(player_amount))
    
    def robot_bet(self, player_amount):
        """
        Handle robot's betting decision with proper calling options
        
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
        if robot_amount == 0 and player_amount == 0:
            self.ui.status_label.config(text="Robot checks.")
        elif robot_amount == player_amount:
            self.ui.status_label.config(text=f"{message} Amount: {robot_amount} chip(s).")
        elif robot_amount > player_amount:
            self.ui.status_label.config(text=f"{message} Raises to {robot_amount} chip(s).")
        
        # Update robot expression based on deception status
        expression = get_robot_expression(self.expected_outcome, self.robot_is_bluffing)
        self.ui.robot_expression_label.config(text=expression)
        
        # Check if more betting rounds are needed
        if robot_amount > player_amount:
            # Robot raised, player needs to call or fold
            self.ui.status_label.config(text=f"{message} Raises to {robot_amount} chip(s). You need to call or fold.")
            self.handle_robot_raise(robot_amount - player_amount)
        else:
            # Betting is complete, show cards and resolve
            self.master.after(1000, self.show_cards_and_resolve)
    
    def handle_robot_raise(self, raise_amount):
        """
        Improved function to handle when the robot raises the bet
        
        Args:
            raise_amount (int): The amount the robot raised beyond the player's bet
        """
        # Clear existing buttons except fold
        for widget in self.ui.betting_frame.winfo_children():
            if widget != self.ui.fold_button:
                widget.destroy()
        
        # Create a call button with the correct call amount
        call_button = tk.Button(
            self.ui.betting_frame,
            text=f"Call {raise_amount}",
            font=self.ui.button_font,
            command=lambda: self.player_call(raise_amount)
        )
        
        # Enable fold button and add the call button
        self.ui.fold_button.config(state=tk.NORMAL)
        call_button.pack(side=tk.LEFT, padx=5)

    def player_call(self, amount):
        """
        Handle player's decision to call the robot's raise
        
        Args:
            amount (int): The amount to call
        """
        if amount > self.player_chips:
            amount = self.player_chips  # All-in
        
        self.ui.disable_betting_controls()
        self.player_chips -= amount
        self.current_pot += amount
        self.ui.update_labels()
        
        # Update round data
        if hasattr(self, 'current_round_data'):
            self.current_round_data['player_bet_amount'] += amount
        
        self.ui.status_label.config(text=f"You called with {amount} chip(s).")
        
        # Show cards and resolve the round
        self.master.after(1000, self.show_cards_and_resolve)
    
    def show_cards_and_resolve(self):
        """Show cards and resolve the round"""
        # Reveal robot's cards
        self.show_robot_cards_revealed()
        
        # Resolve the round after a short delay
        self.master.after(1000, self.resolve_round)
    
    def resolve_round(self):
        """Determine the winner based on actual hand comparison and update chips"""
        # First, get the actual outcome based on correct poker hand comparison
        actual_outcome = compare_poker_hands(
            self.player_hand.cards,
            self.robot_hand.cards,
            self.community_cards,
            self.hand_setup.get("player_hand_type", 0),
            self.hand_setup.get("robot_hand_type", 0)
        )
        
        # Get hand types and descriptions for display
        player_hand_type = self.hand_setup.get("player_hand_type", 0)
        robot_hand_type = self.hand_setup.get("robot_hand_type", 0)
        player_hand_desc = get_hand_description(player_hand_type, self.player_hand.cards + self.community_cards)
        robot_hand_desc = get_hand_description(robot_hand_type, self.robot_hand.cards + self.community_cards)
        
        result_message = ""
        
        # Use the ACTUAL outcome instead of the predetermined one
        if actual_outcome == GameOutcome.PLAYER_WINS:
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
        
        elif actual_outcome == GameOutcome.ROBOT_WINS:
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
        
        # Save round data for analysis - with modification for the research study
        # (using actual outcome for gameplay but tracking predetermined outcome for research)
        if hasattr(self, 'current_round_data'):
            # Add both outcomes to the data for later analysis - use strings instead of enum
            self.current_round_data['actual_outcome'] = actual_outcome.name if hasattr(actual_outcome, 'name') else str(actual_outcome)
            # Make sure predetermined_outcome is already a string (in case it wasn't converted in start_new_round)
            if 'predetermined_outcome' not in self.current_round_data or not isinstance(self.current_round_data['predetermined_outcome'], str):
                self.current_round_data['predetermined_outcome'] = self.expected_outcome.name if hasattr(self.expected_outcome, 'name') else str(self.expected_outcome)
            self.round_data.append(self.current_round_data)
        
        self.current_pot = 0
        self.ui.update_labels()
        
        # Show result and hand comparison with hand types
        player_hand_type_name = HAND_TYPE_NAMES[player_hand_type]
        robot_hand_type_name = HAND_TYPE_NAMES[robot_hand_type]
        
        # Add information about robot's bluffing
        bluff_message = ""
        if hasattr(self, 'robot_is_bluffing') and self.robot_is_bluffing:
            if actual_outcome == GameOutcome.ROBOT_WINS:
                bluff_message = "The robot was bluffing by hiding its strong hand!"
            else:
                bluff_message = "The robot was bluffing by pretending to have a strong hand!"
        
        self.ui.status_label.config(
            text=f"{result_message}\nYour hand: {player_hand_desc} ({player_hand_type_name})\nRobot's hand: {robot_hand_desc} ({robot_hand_type_name})\n{bluff_message}"
        )
        
        # Reset betting UI to standard buttons
        self.ui.reset_betting_controls()
        
        # Enable next round button
        self.ui.next_round_button.config(state=tk.NORMAL)
    
    # def alternate_voice_gender(self):
    #     """Alternate the robot's voice gender (as per the research proposal)"""
    #     # Switch voice gender
    #     self.robot_voice_gender = "female" if self.robot_voice_gender == "male" else "male"
        
    #     # Update display
    #     self.ui.robot_voice_label.config(text=f"Robot Voice: {self.robot_voice_gender.capitalize()}")
        
    #     # Update Misty if connected
    #     if self.use_misty and self.misty and self.misty.misty.connected:
    #         self.misty.set_voice_gender(self.robot_voice_gender)
        
    #     # Show a message about the change
    #     self.ui.status_label.config(
    #         text=f"The robot's voice has changed to {self.robot_voice_gender}. Taking a short break before continuing..."
    #     )
        
    #     # Disable all buttons during the break
    #     self.ui.disable_betting_controls()
    #     self.ui.next_round_button.config(state=tk.DISABLED)
        
    #     # Create a break message in a popup
    #     break_window = tk.Toplevel(self.master)
    #     break_window.title("Break Between Sets")
    #     break_window.geometry("400x200")
    #     break_window.configure(bg="white")
        
    #     tk.Label(
    #         break_window,
    #         text="Break Between Sets",
    #         font=("Arial", 16, "bold"),
    #         bg="white"
    #     ).pack(pady=10)
        
    #     tk.Label(
    #         break_window,
    #         text=f"You've completed the first set of rounds.\n\nThe robot's voice has been changed to {self.robot_voice_gender}.\n\nPlease take a short break before continuing with the next set.",
    #         font=("Arial", 12),
    #         bg="white",
    #         wraplength=350
    #     ).pack(pady=20)
        
    #     def close_break():
    #         break_window.destroy()
    #         self.ui.next_round_button.config(state=tk.NORMAL)
        
    #     tk.Button(
    #         break_window,
    #         text="Continue",
    #         font=("Arial", 12, "bold"),
    #         command=close_break
    #     ).pack(pady=10)
        
    #     # Have Misty announce the voice change if connected
    #     if self.use_misty and self.misty and self.misty.misty.connected:
    #         self.misty.misty.say_text(
    #             f"We are changing to a {self.robot_voice_gender} voice for the next set of rounds."
    #         )
    
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
        
        # if hasattr(self, 'voice_switched'):
        #     delattr(self, 'voice_switched')
        
        # Update Misty if connected
        if self.use_misty and self.misty and self.misty.misty.connected:
            self.misty.set_voice_gender(self.robot_voice_gender)
            self.misty.misty.say_text("Let's start a new game!")
        
        # Clear displays
        self.ui.status_label.config(text="")
        self.ui.results_label.config(text="")
        self.ui.robot_voice_label.config(text=f"Robot Voice: {self.robot_voice_gender.capitalize()}")
        
        # Start a new round
        self.master.after(500, self.start_new_round)
        
    def cleanup(self):
        """Clean up resources when the game is closed"""
        # Disconnect from Misty if connected
        if self.use_misty and self.misty and hasattr(self.misty, 'cleanup'):
            self.misty.cleanup()