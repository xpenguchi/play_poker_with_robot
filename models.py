#!/usr/bin/env python3
"""
Models for Texas Hold'em Poker Game
Contains classes for cards, deck, and poker hands
"""

import random
from enum import Enum

class GameOutcome(Enum):
    """Possible game outcomes enum"""
    PLAYER_WINS = 1
    ROBOT_WINS = 2
    TIE = 3

class Card:
    """Represents a playing card with rank and suit"""
    def __init__(self, rank, suit):
        """
        Initialize a card
        
        Args:
            rank: Card rank (1=Ace, 11=Jack, 12=Queen, 13=King)
            suit: Card suit ('♥', '♦', '♣', '♠')
        """
        self.rank = rank
        self.suit = suit
        
    def __str__(self):
        """String representation of the card"""
        ranks = {1: 'A', 11: 'J', 12: 'Q', 13: 'K'}
        rank_str = ranks.get(self.rank, str(self.rank))
        return f"{rank_str}{self.suit}"
    
    def get_image_name(self):
        """
        Get the filename for the card image
        
        Returns:
            str: Filename for the card image (e.g., 'as.png' for Ace of Spades)
        """
        ranks = {1: 'a', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 
                 8: '8', 9: '9', 10: '10', 11: 'j', 12: 'q', 13: 'k'}
        suits = {'♥': 'h', '♦': 'd', '♣': 'c', '♠': 's'}
        rank_str = ranks.get(self.rank, str(self.rank))
        suit_str = suits.get(self.suit, self.suit)
        return f"{rank_str}{suit_str}.png"

class Deck:
    """Represents a deck of cards"""
    def __init__(self):
        """Initialize a new shuffled deck of cards"""
        self.reset()
    
    def reset(self):
        """Reset the deck to a full set of shuffled cards"""
        ranks = list(range(1, 14))  # 1 (Ace) through 13 (King)
        suits = ['♥', '♦', '♣', '♠']
        self.cards = [Card(rank, suit) for rank in ranks for suit in suits]
        random.shuffle(self.cards)
    
    def deal(self, n):
        """
        Deal n cards from the deck
        
        Args:
            n: Number of cards to deal
            
        Returns:
            list: List of Card objects
        """
        if n > len(self.cards):
            self.reset()
        dealt_cards = self.cards[:n]
        self.cards = self.cards[n:]
        return dealt_cards

class PokerHand:
    """Represents a poker hand (collection of cards)"""
    def __init__(self, cards):
        """
        Initialize a poker hand
        
        Args:
            cards: List of Card objects
        """
        self.cards = cards
    
    def __str__(self):
        """String representation of the hand"""
        return " ".join(str(card) for card in self.cards)
    
    # In a complete implementation, this class would include methods
    # to evaluate hand strength, determine hand type (pair, straight, etc.)
    # and compare hands to determine a winner