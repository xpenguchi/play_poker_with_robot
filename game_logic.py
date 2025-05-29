#!/usr/bin/env python3
"""
Improved Game Logic for Texas Hold'em Poker Game
Uses 12 predefined hands with predetermined outcomes
"""

import random
from enum import Enum

class GameOutcome(Enum):
    PLAYER_WINS = 1
    ROBOT_WINS = 2
    TIE = 3

class Card:
    def __init__(self, rank, suit):
        self.rank = rank  # 1 (Ace) to 13 (King)
        self.suit = suit  # e.g., '♥', '♦', '♣', '♠'

    def __repr__(self):
        if self.rank == 1: rank_str = 'A'
        elif self.rank == 11: rank_str = 'J'
        elif self.rank == 12: rank_str = 'Q'
        elif self.rank == 13: rank_str = 'K'
        else: rank_str = str(self.rank)
        return f"{rank_str}{self.suit}"

# --- Hand Ranking Constants ---
HIGH_CARD = 0
ONE_PAIR = 1
TWO_PAIR = 2
THREE_OF_A_KIND = 3
STRAIGHT = 4
FLUSH = 5
FULL_HOUSE = 6
FOUR_OF_A_KIND = 7
STRAIGHT_FLUSH = 8

# Hand type names for display
HAND_TYPE_NAMES = {
    HIGH_CARD: "High Card",
    ONE_PAIR: "One Pair",
    TWO_PAIR: "Two Pair",
    THREE_OF_A_KIND: "Three of a Kind",
    STRAIGHT: "Straight",
    FLUSH: "Flush",
    FULL_HOUSE: "Full House",
    FOUR_OF_A_KIND: "Four of a Kind",
    STRAIGHT_FLUSH: "Straight Flush"
}

# Predefined 12 hand setups with guaranteed outcomes
PREDEFINED_HANDS = [
    # 1. Player wins with high-quality hand (Three of a Kind)
    {
        "outcome": GameOutcome.PLAYER_WINS,
        "player_hand_quality": "high",
        "player_cards": [Card(10, "♥"), Card(10, "♦")],  # Pair of 10s
        "robot_cards": [Card(13, "♥"), Card(12, "♦")],   # King, Queen
        "community_cards": [Card(10, "♣"), Card(5, "♠"), Card(2, "♣")],  # Another 10 for player's trips
        "robot_betting": {"style": "conservative", "amount": 1},
        "player_hand_type": THREE_OF_A_KIND,
        "robot_hand_type": HIGH_CARD
    },
    
    # 2. Player wins with medium-quality hand (Two Pair)
    {
        "outcome": GameOutcome.PLAYER_WINS,
        "player_hand_quality": "medium",
        "player_cards": [Card(11, "♥"), Card(8, "♦")],  # Jack, 8
        "robot_cards": [Card(10, "♥"), Card(7, "♦")],   # 10, 7
        "community_cards": [Card(11, "♣"), Card(8, "♠"), Card(7, "♣")],  # Jack, 8, 7 (player gets two pair, robot gets one pair)
        "robot_betting": {"style": "neutral", "amount": 1},
        "player_hand_type": TWO_PAIR,
        "robot_hand_type": ONE_PAIR
    },
    
    # 3. Player wins with low-quality hand (High Card)
    {
        "outcome": GameOutcome.PLAYER_WINS,
        "player_hand_quality": "low",
        "player_cards": [Card(1, "♥"), Card(5, "♦")],   # Ace, 5
        "robot_cards": [Card(12, "♥"), Card(10, "♦")],  # Queen, 10
        "community_cards": [Card(7, "♣"), Card(3, "♠"), Card(2, "♣")],  # Low cards
        "robot_betting": {"style": "aggressive", "amount": 2},
        "player_hand_type": HIGH_CARD,
        "robot_hand_type": HIGH_CARD
    },
    
    # 4. Player wins with another medium-quality hand (Pair of Aces)
    {
        "outcome": GameOutcome.PLAYER_WINS,
        "player_hand_quality": "medium",
        "player_cards": [Card(1, "♥"), Card(10, "♦")],  # Ace, 10
        "robot_cards": [Card(13, "♥"), Card(13, "♦")],  # Pair of Kings
        "community_cards": [Card(1, "♣"), Card(7, "♠"), Card(5, "♣")],  # Ace, 7, 5
        "robot_betting": {"style": "aggressive", "amount": 2},
        "player_hand_type": ONE_PAIR,
        "robot_hand_type": ONE_PAIR
    },
    
    # 5. Robot wins against player's low-quality hand
    {
        "outcome": GameOutcome.ROBOT_WINS,
        "player_hand_quality": "low",
        "player_cards": [Card(7, "♥"), Card(4, "♦")],   # 7, 4
        "robot_cards": [Card(12, "♥"), Card(12, "♦")],  # Pair of Queens
        "community_cards": [Card(10, "♣"), Card(8, "♠"), Card(2, "♣")],  # 10, 8, 2
        "robot_betting": {"style": "aggressive", "amount": 2},
        "player_hand_type": HIGH_CARD,
        "robot_hand_type": ONE_PAIR
    },
    
    # 6. Robot wins against player's medium-quality hand
    {
        "outcome": GameOutcome.ROBOT_WINS,
        "player_hand_quality": "medium",
        "player_cards": [Card(9, "♥"), Card(9, "♦")],   # Pair of 9s
        "robot_cards": [Card(1, "♥"), Card(1, "♦")],    # Pair of Aces
        "community_cards": [Card(13, "♣"), Card(5, "♠"), Card(2, "♣")],  # King, 5, 2
        "robot_betting": {"style": "aggressive", "amount": 2},
        "player_hand_type": ONE_PAIR,
        "robot_hand_type": ONE_PAIR
    },
    
    # 7. Robot wins against player's high-quality hand
    {
        "outcome": GameOutcome.ROBOT_WINS,
        "player_hand_quality": "high",
        "player_cards": [Card(10, "♥"), Card(10, "♦")],   # Pair of 10s
        "robot_cards": [Card(1, "♠"), Card(1, "♣")],      # Pair of Aces
        "community_cards": [Card(10, "♣"), Card(1, "♥"), Card(5, "♣")],  # 10, Ace, 5 (player gets trips, robot gets trips of aces)
        "robot_betting": {"style": "aggressive", "amount": 2},
        "player_hand_type": THREE_OF_A_KIND,
        "robot_hand_type": THREE_OF_A_KIND
    },
    
    # 8. Robot wins with another hand
    {
        "outcome": GameOutcome.ROBOT_WINS,
        "player_hand_quality": "medium",
        "player_cards": [Card(13, "♥"), Card(12, "♦")],  # King, Queen
        "robot_cards": [Card(5, "♥"), Card(5, "♦")],     # Pair of 5s
        "community_cards": [Card(5, "♣"), Card(8, "♠"), Card(2, "♣")],  # 5, 8, 2 (robot gets three of a kind)
        "robot_betting": {"style": "conservative", "amount": 1},
        "player_hand_type": HIGH_CARD,
        "robot_hand_type": THREE_OF_A_KIND
    },
    
    # 9. Tie with low-quality hands (high card)
    {
        "outcome": GameOutcome.TIE,
        "player_hand_quality": "low",
        "player_cards": [Card(1, "♥"), Card(6, "♦")],  # Ace, 6
        "robot_cards": [Card(1, "♠"), Card(6, "♣")],   # Ace, 6 (different suits)
        "community_cards": [Card(10, "♣"), Card(8, "♠"), Card(3, "♣")],  # 10, 8, 3
        "robot_betting": {"style": "neutral", "amount": 1},
        "player_hand_type": HIGH_CARD,
        "robot_hand_type": HIGH_CARD
    },
    
    # 10. Tie with medium-quality hands (one pair)
    {
        "outcome": GameOutcome.TIE,
        "player_hand_quality": "medium",
        "player_cards": [Card(9, "♥"), Card(7, "♦")],   # 9, 7
        "robot_cards": [Card(9, "♠"), Card(7, "♣")],    # 9, 7 (different suits)
        "community_cards": [Card(9, "♣"), Card(8, "♠"), Card(3, "♣")],  # 9, 8, 3 (both get pair of 9s with same kickers)
        "robot_betting": {"style": "neutral", "amount": 1},
        "player_hand_type": ONE_PAIR,
        "robot_hand_type": ONE_PAIR
    },
    
    # 11. Tie with high-quality hands (two pair)
    {
        "outcome": GameOutcome.TIE,
        "player_hand_quality": "high",
        "player_cards": [Card(12, "♥"), Card(10, "♦")],  # Queen, 10
        "robot_cards": [Card(12, "♠"), Card(10, "♣")],   # Queen, 10 (different suits)
        "community_cards": [Card(12, "♦"), Card(10, "♥"), Card(3, "♣")],  # Queen, 10, 3 (both get two pair Q-Q-10-10)
        "robot_betting": {"style": "neutral", "amount": 1},
        "player_hand_type": TWO_PAIR,
        "robot_hand_type": TWO_PAIR
    },
    
    # 12. Another tie scenario
    {
        "outcome": GameOutcome.TIE,
        "player_hand_quality": "medium",
        "player_cards": [Card(8, "♥"), Card(8, "♦")],  # Pair of 8s
        "robot_cards": [Card(8, "♠"), Card(8, "♣")],   # Pair of 8s (different suits)
        "community_cards": [Card(13, "♣"), Card(10, "♠"), Card(3, "♦")],  # King, 10, 3 (both get pair of 8s with same kickers)
        "robot_betting": {"style": "aggressive", "amount": 2},
        "player_hand_type": ONE_PAIR,
        "robot_hand_type": ONE_PAIR
    }
]

class PredefinedHandManager:
    """
    Manages the 12 predefined hand setups.
    Ensures balanced outcomes (2 player wins, 2 robot wins, 2 ties every 6 rounds)
    """
    
    def __init__(self, seed=None):
        """Initialize the predefined hand manager."""
        if seed is not None:
            random.seed(seed)
            
        self.hand_setups = PREDEFINED_HANDS.copy()
        self.current_round = 0
        self.setup_outcomes()
        
    def setup_outcomes(self):
        """
        Organize hand setups to ensure balanced outcomes.
        Every 6 rounds will have 2 player wins, 2 robot wins, and 2 ties.
        """
        # Create a list of indices for each outcome type
        player_wins = [i for i, setup in enumerate(self.hand_setups) if setup["outcome"] == GameOutcome.PLAYER_WINS]
        robot_wins = [i for i, setup in enumerate(self.hand_setups) if setup["outcome"] == GameOutcome.ROBOT_WINS]
        ties = [i for i, setup in enumerate(self.hand_setups) if setup["outcome"] == GameOutcome.TIE]
        
        # Shuffle each list
        random.shuffle(player_wins)
        random.shuffle(robot_wins)
        random.shuffle(ties)
        
        # Ensure we have at least 2 of each outcome
        if len(player_wins) < 2 or len(robot_wins) < 2 or len(ties) < 2:
            raise ValueError("Need at least 2 hands of each outcome type")
        
        # Create a pattern for every 6 rounds: 2 player wins, 2 robot wins, 2 ties
        self.round_patterns = []
        for i in range(0, min(len(player_wins), len(robot_wins), len(ties)), 2):
            pattern = player_wins[i:i+2] + robot_wins[i:i+2] + ties[i:i+2]
            random.shuffle(pattern)  # Randomize order within each set of 6
            self.round_patterns.extend(pattern)
    
    def get_next_hand_setup(self, robot_voice_gender):
        """
        Get the next hand setup based on the balanced outcome pattern.
        
        Args:
            robot_voice_gender (str): The robot's voice gender
            
        Returns:
            dict: Hand setup for the next round
        """
        # Get the index from the pattern
        pattern_index = self.current_round % len(self.round_patterns)
        hand_index = self.round_patterns[pattern_index]
        
        # Get the hand setup
        hand_setup = self.hand_setups[hand_index].copy()
        
        # Increment round counter
        self.current_round += 1
        
        # Add robot voice gender to the setup
        hand_setup["robot_voice_gender"] = robot_voice_gender
        
        # Randomly determine if the robot will bluff (50% chance)
        hand_setup["robot_is_bluffing"] = random.choice([True, False])
        
        return hand_setup

def get_hand_description(hand_type, cards):
    """
    Get a text description of a hand type with the most significant cards
    
    Args:
        hand_type (int): The hand type constant
        cards (list): List of Card objects
        
    Returns:
        str: Description of the hand
    """
    if hand_type == HIGH_CARD:
        highest_card = max(cards, key=lambda c: 14 if c.rank == 1 else c.rank)
        return f"High Card {highest_card}"
    
    elif hand_type == ONE_PAIR:
        # Find the pair rank
        ranks = [c.rank for c in cards]
        for rank in ranks:
            if ranks.count(rank) == 2:
                rank_str = 'A' if rank == 1 else ('K' if rank == 13 else 
                            'Q' if rank == 12 else 'J' if rank == 11 else str(rank))
                return f"Pair of {rank_str}s"
    
    elif hand_type == TWO_PAIR:
        # Find the two pair ranks
        ranks = [c.rank for c in cards]
        pairs = []
        for rank in sorted(set(ranks), reverse=True):
            if ranks.count(rank) == 2:
                pairs.append(rank)
                if len(pairs) == 2:
                    break
        
        pair1_str = 'A' if pairs[0] == 1 else ('K' if pairs[0] == 13 else 
                    'Q' if pairs[0] == 12 else 'J' if pairs[0] == 11 else str(pairs[0]))
        pair2_str = 'A' if pairs[1] == 1 else ('K' if pairs[1] == 13 else 
                    'Q' if pairs[1] == 12 else 'J' if pairs[1] == 11 else str(pairs[1]))
        
        return f"Two Pair, {pair1_str}s and {pair2_str}s"
    
    elif hand_type == THREE_OF_A_KIND:
        # Find the three of a kind rank
        ranks = [c.rank for c in cards]
        for rank in ranks:
            if ranks.count(rank) == 3:
                rank_str = 'A' if rank == 1 else ('K' if rank == 13 else 
                            'Q' if rank == 12 else 'J' if rank == 11 else str(rank))
                return f"Three of a Kind, {rank_str}s"
    
    elif hand_type == STRAIGHT:
        # Get highest card in straight
        highest_rank = max([14 if c.rank == 1 else c.rank for c in cards])
        rank_str = 'A' if highest_rank == 14 else ('K' if highest_rank == 13 else 
                   'Q' if highest_rank == 12 else 'J' if highest_rank == 11 else str(highest_rank))
        return f"Straight, {rank_str} high"
    
    elif hand_type == FLUSH:
        # Get suit and highest card
        suit = cards[0].suit
        highest_rank = max([14 if c.rank == 1 else c.rank for c in cards])
        rank_str = 'A' if highest_rank == 14 else ('K' if highest_rank == 13 else 
                   'Q' if highest_rank == 12 else 'J' if highest_rank == 11 else str(highest_rank))
        return f"Flush, {rank_str} high"
    
    elif hand_type == FULL_HOUSE:
        # Find the three of a kind and pair ranks
        ranks = [c.rank for c in cards]
        trips_rank = None
        pair_rank = None
        
        for rank in ranks:
            if ranks.count(rank) == 3:
                trips_rank = rank
            elif ranks.count(rank) == 2:
                pair_rank = rank
        
        trips_str = 'A' if trips_rank == 1 else ('K' if trips_rank == 13 else 
                   'Q' if trips_rank == 12 else 'J' if trips_rank == 11 else str(trips_rank))
        pair_str = 'A' if pair_rank == 1 else ('K' if pair_rank == 13 else 
                  'Q' if pair_rank == 12 else 'J' if pair_rank == 11 else str(pair_rank))
        
        return f"Full House, {trips_str}s full of {pair_str}s"
    
    elif hand_type == FOUR_OF_A_KIND:
        # Find the four of a kind rank
        ranks = [c.rank for c in cards]
        for rank in ranks:
            if ranks.count(rank) == 4:
                rank_str = 'A' if rank == 1 else ('K' if rank == 13 else 
                            'Q' if rank == 12 else 'J' if rank == 11 else str(rank))
                return f"Four of a Kind, {rank_str}s"
    
    elif hand_type == STRAIGHT_FLUSH:
        # Get highest card in straight flush
        highest_rank = max([14 if c.rank == 1 else c.rank for c in cards])
        rank_str = 'A' if highest_rank == 14 else ('K' if highest_rank == 13 else 
                   'Q' if highest_rank == 12 else 'J' if highest_rank == 11 else str(highest_rank))
        suit = cards[0].suit
        return f"Straight Flush, {rank_str} high"
    
    # Default fallback
    return HAND_TYPE_NAMES[hand_type]

def calculate_robot_bet(player_bet, robot_chips, robot_betting, expected_outcome, is_bluffing):
    """
    Calculate the robot's bet based on its strategy and whether it's bluffing
    
    Args:
        player_bet (int): The player's bet amount
        robot_chips (int): The robot's remaining chips
        robot_betting (dict): The robot's betting strategy
        expected_outcome (GameOutcome): The expected outcome for the round
        is_bluffing (bool): Whether the robot is bluffing
        
    Returns:
        int: The robot's bet amount
        str: A message describing the robot's behavior
    """
    # Get base bet amount and style from robot betting strategy
    base_bet = robot_betting.get("amount", 1)
    betting_style = robot_betting.get("style", "neutral")
    
    # Start with default message templates
    style_messages = {
        "aggressive": "Robot raises confidently!",
        "conservative": "Robot calls cautiously.",
        "neutral": "Robot matches your bet."
    }
    
    # Adjust bet and message based on bluffing status and expected outcome
    if is_bluffing:
        # Robot is bluffing - behavior should contradict its hand quality
        if expected_outcome == GameOutcome.ROBOT_WINS:
            # Robot has good cards but acts unsure
            style_messages = {
                "aggressive": "Robot raises, but seems uncertain.",
                "conservative": "Robot calls reluctantly.",
                "neutral": "Robot matches your bet with a sigh."
            }
            # If robot has good cards but is bluffing, it might bet lower
            if betting_style == "aggressive":
                base_bet = max(1, base_bet - 1)  # Reduce the bet amount slightly
        else:
            # Robot has bad/average cards but acts confident
            style_messages = {
                "aggressive": "Robot raises confidently!",
                "conservative": "Robot calls with a smile.",
                "neutral": "Robot matches your bet without hesitation."
            }
            # If robot has bad cards but is bluffing, it might bet higher
            if betting_style != "aggressive":
                base_bet = min(robot_chips, base_bet + 1)  # Increase the bet amount
    else:
        # Robot is not bluffing - expressions and betting match its hand quality
        if expected_outcome == GameOutcome.ROBOT_WINS:
            # Robot has good cards and shows it
            style_messages = {
                "aggressive": "Robot raises with confidence!",
                "conservative": "Robot calls decisively.",
                "neutral": "Robot matches your bet confidently."
            }
            # Robot might bet higher with good cards
            if betting_style != "aggressive":
                base_bet = min(robot_chips, base_bet + 1)
        else:
            # Robot has bad/average cards and shows it
            style_messages = {
                "aggressive": "Robot raises, but seems uncertain.",
                "conservative": "Robot calls cautiously.",
                "neutral": "Robot hesitantly matches your bet."
            }
            # Robot might bet lower with bad cards
            if betting_style == "aggressive":
                base_bet = max(1, base_bet - 1)
    
    # Standard poker betting logic
    if player_bet == 0:  # Player checks
        if betting_style == "aggressive" or (expected_outcome == GameOutcome.ROBOT_WINS and not is_bluffing):
            # If player checks and robot is aggressive or has a good hand, it bets
            robot_bet = min(robot_chips, base_bet)
            style_messages[betting_style] = "Robot opens with a bet!"
        else:
            # Robot also checks
            robot_bet = 0
            style_messages[betting_style] = "Robot checks."
    else:  # Player bet something
        if betting_style == "aggressive" and random.random() < 0.7:
            # 70% chance aggressive robot raises
            robot_bet = min(robot_chips, player_bet + base_bet)
            style_messages[betting_style] = "Robot raises!"
        elif betting_style == "conservative" and player_bet > 1 and random.random() < 0.6:
            # 60% chance conservative robot just calls if bet is high
            robot_bet = min(robot_chips, player_bet)
            style_messages[betting_style] = "Robot calls your bet."
        else:
            # Otherwise, match the player's bet
            robot_bet = min(robot_chips, player_bet)
            style_messages[betting_style] = f"Robot calls your bet of {player_bet} chips."
    
    # Make sure the robot doesn't bet more than it has
    if robot_bet > robot_chips:
        robot_bet = robot_chips  # All-in
        style_messages[betting_style] += " (All in!)"
    
    # Get the appropriate message
    message = style_messages.get(betting_style, "Robot bets.")
    
    return robot_bet, message

def get_robot_expression(expected_outcome, is_bluffing):
    """
    Determine the robot's facial expression based on its hand and bluffing status
    
    Args:
        expected_outcome (GameOutcome): The expected outcome for the round
        is_bluffing (bool): Whether the robot is bluffing
        
    Returns:
        str: Emoji representing the robot's expression
    """
    if is_bluffing:
        if expected_outcome == GameOutcome.ROBOT_WINS:
            # Robot has good cards but acts unsure
            return random.choice(["😕", "😐"])
        else:
            # Robot has bad cards but acts confident
            return "😎"
    else:
        # No bluffing, expressions match actual hand
        if expected_outcome == GameOutcome.ROBOT_WINS:
            return "😎"
        elif expected_outcome == GameOutcome.PLAYER_WINS:
            return "😕"
        else:  # TIE
            return "😐"

def get_robot_message(hand_setup, is_bluffing):
    """
    Generate appropriate verbal messages for the robot based on its hand and bluffing status
    
    Args:
        hand_setup (dict): The hand setup for the round
        is_bluffing (bool): Whether the robot is bluffing
        
    Returns:
        str: Message for the robot to speak
    """
    import random
    
    outcome = hand_setup["outcome"]
    hand_quality = hand_setup.get("player_hand_quality", "medium")
    
    # Messages based on bluffing status and hand quality
    if is_bluffing:
        if outcome == GameOutcome.ROBOT_WINS:
            # Robot has good cards but pretends they're not good
            messages = [
                "I'm not sure about these cards.",
                "This hand doesn't look great.",
                "I might need to be careful with this one.",
                "These cards are quite tricky.",
                "I don't know about this hand."
            ]
        else:
            # Robot has average/bad cards but pretends they're good
            messages = [
                "I have a strong hand this time!",
                "These cards look promising.",
                "I'm feeling confident about this round.",
                "This might be my lucky hand!",
                "I've got a good feeling about these cards."
            ]
    else:
        # Not bluffing - message matches hand quality
        if outcome == GameOutcome.ROBOT_WINS:
            messages = [
                "These cards look good.",
                "I've got a strong hand.",
                "I'm quite happy with these cards.",
                "This is a promising hand.",
                "I think I have an advantage this round."
            ]
        elif outcome == GameOutcome.PLAYER_WINS:
            messages = [
                "My cards aren't the best.",
                "This hand is a bit challenging.",
                "I'll need some luck with these cards.",
                "Not the greatest hand.",
                "I'm not very confident about these cards."
            ]
        else:  # TIE
            messages = [
                "This is an okay hand.",
                "These cards are decent.",
                "Not bad, not great.",
                "A middle-of-the-road hand.",
                "This could go either way."
            ]
    
    return random.choice(messages)

def get_predetermined_hand_setup(round_num, robot_voice_gender, seed=None):
    """
    Get the next predetermined hand setup based on the round number
    
    Args:
        round_num (int): Current round number
        robot_voice_gender (str): The robot's voice gender
        seed (int, optional): Random seed for reproducibility
        
    Returns:
        dict: Hand setup containing player cards, robot cards, community cards, and outcome
    """
    # Initialize or get the hand manager
    # This is a global variable to persist across function calls
    global _hand_manager
    if '_hand_manager' not in globals() or _hand_manager is None:
        _hand_manager = PredefinedHandManager(seed)
    
    # Get the next hand setup
    hand_setup = _hand_manager.get_next_hand_setup(robot_voice_gender)
    
    return hand_setup