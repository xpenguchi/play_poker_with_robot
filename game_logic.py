#!/usr/bin/env python3
"""
Improved Game Logic for Texas Hold'em Poker Game
Handles the core game logic with better randomization while still controlling outcomes
"""

import random
from models import Card, GameOutcome

def get_predetermined_hand_setup(round_num, robot_voice_gender, admin_settings=None):
    """
    Creates predetermined hand setups based on desired outcome with more randomization
    
    Args:
        round_num (int): Current round number
        robot_voice_gender (str): The robot's voice gender ('male' or 'female')
        admin_settings (dict, optional): Admin-defined settings to override defaults
        
    Returns:
        dict: Setup containing player cards, robot cards, community cards, outcome and robot betting strategy
    """
    # Use admin settings if provided
    if admin_settings and admin_settings.get('use_admin_settings', False):
        outcome = admin_settings.get('outcome', GameOutcome.PLAYER_WINS)
        robot_betting = admin_settings.get('robot_betting', {"style": "neutral", "amount": 1})
    else:
        # For simplicity, we'll rotate between three outcomes
        round_index = (round_num - 1) % 3
        outcomes = [GameOutcome.PLAYER_WINS, GameOutcome.ROBOT_WINS, GameOutcome.TIE]
        outcome = outcomes[round_index]
        
        # Default robot betting strategies
        betting_strategies = [
            {"style": "aggressive", "amount": 2},  # Player wins scenario
            {"style": "conservative", "amount": 1},  # Robot wins scenario
            {"style": "neutral", "amount": 1}  # Tie scenario
        ]
        robot_betting = betting_strategies[round_index]
    
    # Generate random cards with predetermined outcome
    setup = generate_random_hand_with_outcome(outcome)
    setup["outcome"] = outcome
    setup["robot_betting"] = robot_betting
    setup["robot_voice_gender"] = robot_voice_gender
    
    return setup

def generate_random_hand_with_outcome(outcome):
    """
    Generate a random hand setup that guarantees the specified outcome
    
    Args:
        outcome (GameOutcome): The desired outcome of the hand
        
    Returns:
        dict: Cards for player, robot, and community
    """
    # Create a deck of cards
    deck = create_shuffled_deck()
    
    if outcome == GameOutcome.PLAYER_WINS:
        # Generate hand where player wins
        return generate_player_wins_hand(deck)
    elif outcome == GameOutcome.ROBOT_WINS:
        # Generate hand where robot wins
        return generate_robot_wins_hand(deck)
    else:  # TIE
        # Generate hand where there's a tie
        return generate_tie_hand(deck)

def create_shuffled_deck():
    """
    Create a shuffled deck of cards
    
    Returns:
        list: Shuffled list of Card objects
    """
    ranks = list(range(1, 14))  # 1 (Ace) through 13 (King)
    suits = ['♥', '♦', '♣', '♠']
    deck = [Card(rank, suit) for rank in ranks for suit in suits]
    random.shuffle(deck)
    return deck

def generate_player_wins_hand(deck):
    """
    Generate a hand setup where the player wins
    Various hand types are randomly selected to provide variety
    
    Args:
        deck (list): Shuffled deck of cards
        
    Returns:
        dict: Cards for player, robot, and community
    """
    # Choose a random hand type for player to win
    hand_type = random.choice([
        "high_card", "pair", "two_pair", "three_of_a_kind", 
        "straight", "flush", "full_house", "four_of_a_kind"
    ])
    
    if hand_type == "high_card":
        # Player has high card (Ace) vs robot's lower high card
        player_cards = [
            get_card_of_rank(deck, 1),  # Ace
            get_card_of_rank(deck, random.randint(2, 8))
        ]
        robot_cards = [
            get_card_of_rank(deck, random.randint(9, 13)),  # Face card
            get_card_of_rank(deck, random.randint(2, 8))
        ]
        # Community cards with random low cards
        community_cards = [
            get_card_of_rank(deck, random.randint(2, 7)),
            get_card_of_rank(deck, random.randint(2, 7)),
            get_card_of_rank(deck, random.randint(2, 7))
        ]
    
    elif hand_type == "pair":
        # Player has higher pair than robot
        player_pair_rank = random.randint(9, 13)  # 9-13 (9, 10, J, Q, K)
        robot_pair_rank = random.randint(2, 8)    # 2-8
        
        player_cards = [
            get_card_of_rank(deck, player_pair_rank),
            get_card_of_rank(deck, random.randint(2, 8))
        ]
        robot_cards = [
            get_card_of_rank(deck, robot_pair_rank),
            get_card_of_rank(deck, random.randint(2, 8))
        ]
        # Community cards with one matching player's pair
        community_cards = [
            get_card_of_rank(deck, player_pair_rank),
            get_card_of_rank(deck, robot_pair_rank),
            get_card_of_rank(deck, random.randint(2, 7))
        ]
    
    elif hand_type == "two_pair":
        # Player has two pair higher than robot's two pair
        player_pair1_rank = random.randint(9, 13)  # 9-13
        player_pair2_rank = random.randint(2, 8)   # 2-8
        
        # Make sure robot's pairs are lower
        if player_pair1_rank > 9:
            robot_pair1_rank = player_pair1_rank - 2
        else:
            robot_pair1_rank = player_pair1_rank - 1
            
        if player_pair2_rank > 3:
            robot_pair2_rank = player_pair2_rank - 2
        else:
            robot_pair2_rank = 2
        
        player_cards = [
            get_card_of_rank(deck, player_pair1_rank),
            get_card_of_rank(deck, player_pair2_rank)
        ]
        robot_cards = [
            get_card_of_rank(deck, robot_pair1_rank),
            get_card_of_rank(deck, robot_pair2_rank)
        ]
        # Community cards with one of each pair
        community_cards = [
            get_card_of_rank(deck, player_pair1_rank),
            get_card_of_rank(deck, player_pair2_rank),
            get_card_of_rank(deck, random.randint(2, 7))
        ]
    
    elif hand_type == "three_of_a_kind":
        # Player has three of a kind, robot has pair
        player_three_rank = random.randint(7, 13)  # 7-13
        robot_pair_rank = random.randint(2, 6)     # 2-6
        
        player_cards = [
            get_card_of_rank(deck, player_three_rank),
            get_card_of_rank(deck, player_three_rank)
        ]
        robot_cards = [
            get_card_of_rank(deck, robot_pair_rank),
            get_card_of_rank(deck, robot_pair_rank)
        ]
        # Community cards with one for player's three of a kind
        community_cards = [
            get_card_of_rank(deck, player_three_rank),
            get_card_of_rank(deck, random.randint(2, 6)),
            get_card_of_rank(deck, random.randint(2, 6))
        ]
    
    else:  # Default to a simple pair vs high card scenario
        # Player has a pair of aces, robot has king high
        player_cards = [
            get_card_of_rank(deck, 1),  # Ace
            get_card_of_rank(deck, 1)   # Another Ace
        ]
        robot_cards = [
            get_card_of_rank(deck, 13),  # King
            get_card_of_rank(deck, random.randint(2, 10))
        ]
        # Community cards with random low cards
        community_cards = [
            get_card_of_rank(deck, random.randint(2, 10)),
            get_card_of_rank(deck, random.randint(2, 10)),
            get_card_of_rank(deck, random.randint(2, 10))
        ]
    
    return {
        "player_cards": player_cards,
        "robot_cards": robot_cards,
        "community_cards": community_cards
    }

def generate_robot_wins_hand(deck):
    """
    Generate a hand setup where the robot wins
    Various hand types are randomly selected to provide variety
    
    Args:
        deck (list): Shuffled deck of cards
        
    Returns:
        dict: Cards for player, robot, and community
    """
    # Choose a random hand type for robot to win
    hand_type = random.choice([
        "high_card", "pair", "two_pair", "three_of_a_kind", 
        "straight", "flush", "full_house", "four_of_a_kind"
    ])
    
    if hand_type == "high_card":
        # Robot has high card (Ace) vs player's lower high card
        robot_cards = [
            get_card_of_rank(deck, 1),  # Ace
            get_card_of_rank(deck, random.randint(2, 8))
        ]
        player_cards = [
            get_card_of_rank(deck, random.randint(9, 13)),  # Face card
            get_card_of_rank(deck, random.randint(2, 8))
        ]
        # Community cards with random low cards
        community_cards = [
            get_card_of_rank(deck, random.randint(2, 7)),
            get_card_of_rank(deck, random.randint(2, 7)),
            get_card_of_rank(deck, random.randint(2, 7))
        ]
    
    elif hand_type == "pair":
        # Robot has higher pair than player
        robot_pair_rank = random.randint(9, 13)  # 9-13 (9, 10, J, Q, K)
        player_pair_rank = random.randint(2, 8)  # 2-8
        
        robot_cards = [
            get_card_of_rank(deck, robot_pair_rank),
            get_card_of_rank(deck, random.randint(2, 8))
        ]
        player_cards = [
            get_card_of_rank(deck, player_pair_rank),
            get_card_of_rank(deck, random.randint(2, 8))
        ]
        # Community cards with one matching robot's pair
        community_cards = [
            get_card_of_rank(deck, robot_pair_rank),
            get_card_of_rank(deck, player_pair_rank),
            get_card_of_rank(deck, random.randint(2, 7))
        ]
    
    elif hand_type == "two_pair":
        # Robot has two pair higher than player's two pair
        robot_pair1_rank = random.randint(9, 13)  # 9-13
        robot_pair2_rank = random.randint(2, 8)   # 2-8
        
        # Make sure player's pairs are lower
        if robot_pair1_rank > 9:
            player_pair1_rank = robot_pair1_rank - 2
        else:
            player_pair1_rank = robot_pair1_rank - 1
            
        if robot_pair2_rank > 3:
            player_pair2_rank = robot_pair2_rank - 2
        else:
            player_pair2_rank = 2
        
        robot_cards = [
            get_card_of_rank(deck, robot_pair1_rank),
            get_card_of_rank(deck, robot_pair2_rank)
        ]
        player_cards = [
            get_card_of_rank(deck, player_pair1_rank),
            get_card_of_rank(deck, player_pair2_rank)
        ]
        # Community cards with one of each pair
        community_cards = [
            get_card_of_rank(deck, robot_pair1_rank),
            get_card_of_rank(deck, robot_pair2_rank),
            get_card_of_rank(deck, random.randint(2, 7))
        ]
    
    elif hand_type == "three_of_a_kind":
        # Robot has three of a kind, player has pair
        robot_three_rank = random.randint(7, 13)  # 7-13
        player_pair_rank = random.randint(2, 6)   # 2-6
        
        robot_cards = [
            get_card_of_rank(deck, robot_three_rank),
            get_card_of_rank(deck, robot_three_rank)
        ]
        player_cards = [
            get_card_of_rank(deck, player_pair_rank),
            get_card_of_rank(deck, player_pair_rank)
        ]
        # Community cards with one for robot's three of a kind
        community_cards = [
            get_card_of_rank(deck, robot_three_rank),
            get_card_of_rank(deck, random.randint(2, 6)),
            get_card_of_rank(deck, random.randint(2, 6))
        ]
    
    else:  # Default to a simple pair vs high card scenario
        # Robot has a pair of aces, player has king high
        robot_cards = [
            get_card_of_rank(deck, 1),  # Ace
            get_card_of_rank(deck, 1)   # Another Ace
        ]
        player_cards = [
            get_card_of_rank(deck, 13),  # King
            get_card_of_rank(deck, random.randint(2, 10))
        ]
        # Community cards with random low cards
        community_cards = [
            get_card_of_rank(deck, random.randint(2, 10)),
            get_card_of_rank(deck, random.randint(2, 10)),
            get_card_of_rank(deck, random.randint(2, 10))
        ]
    
    return {
        "player_cards": player_cards,
        "robot_cards": robot_cards,
        "community_cards": community_cards
    }

def generate_tie_hand(deck):
    """
    Generate a hand setup where there's a tie
    
    Args:
        deck (list): Shuffled deck of cards
        
    Returns:
        dict: Cards for player, robot, and community
    """
    # Choose a random hand type for the tie
    hand_type = random.choice([
        "high_card", "pair", "two_pair", "three_of_a_kind"
    ])
    
    if hand_type == "high_card":
        # Both have the same high card
        high_card_rank = random.randint(9, 13)  # 9-13 (9, 10, J, Q, K)
        kicker_rank = random.randint(2, 8)      # 2-8
        
        player_cards = [
            get_card_of_rank(deck, high_card_rank, "♥"),
            get_card_of_rank(deck, random.randint(2, kicker_rank - 1))
        ]
        robot_cards = [
            get_card_of_rank(deck, high_card_rank, "♦"),
            get_card_of_rank(deck, random.randint(2, kicker_rank - 1))
        ]
        # Community cards with kicker that makes it tie
        community_cards = [
            get_card_of_rank(deck, kicker_rank),
            get_card_of_rank(deck, random.randint(2, 7)),
            get_card_of_rank(deck, random.randint(2, 7))
        ]
    
    elif hand_type == "pair":
        # Both have the same pair
        pair_rank = random.randint(9, 13)  # 9-13 (9, 10, J, Q, K)
        
        player_cards = [
            get_card_of_rank(deck, pair_rank, "♥"),
            get_card_of_rank(deck, random.randint(2, 8))
        ]
        robot_cards = [
            get_card_of_rank(deck, pair_rank, "♦"),
            get_card_of_rank(deck, random.randint(2, 8))
        ]
        # Community cards with third card for the pair
        community_cards = [
            get_card_of_rank(deck, pair_rank, "♣"),
            get_card_of_rank(deck, random.randint(2, 7)),
            get_card_of_rank(deck, random.randint(2, 7))
        ]
    
    elif hand_type == "two_pair":
        # Both have the same two pairs
        pair1_rank = random.randint(9, 13)  # 9-13
        pair2_rank = random.randint(2, 8)   # 2-8
        
        player_cards = [
            get_card_of_rank(deck, pair1_rank, "♥"),
            get_card_of_rank(deck, pair2_rank, "♥")
        ]
        robot_cards = [
            get_card_of_rank(deck, pair1_rank, "♦"),
            get_card_of_rank(deck, pair2_rank, "♦")
        ]
        # Community cards with one of each pair
        community_cards = [
            get_card_of_rank(deck, pair1_rank, "♣"),
            get_card_of_rank(deck, pair2_rank, "♣"),
            get_card_of_rank(deck, random.randint(2, 7))
        ]
    
    else:  # Default to a simple equal pairs scenario
        # Both have a pair of queens
        player_cards = [
            get_card_of_rank(deck, 12, "♥"),  # Queen of Hearts
            get_card_of_rank(deck, 12, "♠")   # Queen of Spades
        ]
        robot_cards = [
            get_card_of_rank(deck, 12, "♦"),  # Queen of Diamonds
            get_card_of_rank(deck, 12, "♣")   # Queen of Clubs
        ]
        # Community cards with random low cards
        community_cards = [
            get_card_of_rank(deck, random.randint(2, 10)),
            get_card_of_rank(deck, random.randint(2, 10)),
            get_card_of_rank(deck, random.randint(2, 10))
        ]
    
    return {
        "player_cards": player_cards,
        "robot_cards": robot_cards,
        "community_cards": community_cards
    }

def get_card_of_rank(deck, rank, suit=None):
    """
    Get a card of specified rank (and optionally suit) from the deck
    If no matching card is found, generate a new one
    
    Args:
        deck (list): List of available Card objects
        rank (int): Desired rank (1=Ace, 2-10, 11=Jack, 12=Queen, 13=King)
        suit (str, optional): Desired suit. If None, any suit is accepted.
        
    Returns:
        Card: A card with the specified rank
    """
    suits = ['♥', '♦', '♣', '♠']
    
    # Find a card with the specified rank and suit
    for i, card in enumerate(deck):
        if card.rank == rank and (suit is None or card.suit == suit):
            return deck.pop(i)
    
    # If no matching card was found but suit was specified, create one
    if suit is not None:
        return Card(rank, suit)
        
    # If no matching card was found, create a new card with random suit
    return Card(rank, random.choice(suits))

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
    
    # Apply additional logic for bet amounts
    if betting_style == "aggressive" and player_bet == 1:
        # If player bet small and robot is aggressive, it raises
        robot_bet = min(robot_chips, player_bet + base_bet)
    elif betting_style == "conservative" and player_bet > 1:
        # If player bet big and robot is conservative, it just calls
        robot_bet = player_bet
    else:
        # Otherwise, use the predetermined amount but at least match the player
        robot_bet = max(base_bet, player_bet)
    
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
            return "😕"
        else:
            # Robot has bad cards but acts confident
            return "😎"
    else:
        # No bluffing, expressions match actual hand
        if expected_outcome == GameOutcome.ROBOT_WINS:
            return "😎"
        else:
            return "😕"