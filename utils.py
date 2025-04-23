#!/usr/bin/env python3
"""
Utility Functions for Texas Hold'em Poker Game
Contains utility functions for data tracking and misc operations
"""

import json
import os
from datetime import datetime
from pathlib import Path

def save_game_results(results_data, filename=None):
    """
    Save game results to a JSON file
    
    Args:
        results_data (dict): Dictionary containing game results
        filename (str, optional): Filename to save data to. If None, a timestamp-based name is used.
    
    Returns:
        str: Path to the saved file
    """
    # Create results directory if it doesn't exist
    results_dir = Path("results")
    if not results_dir.exists():
        results_dir.mkdir(parents=True)
    
    # Generate filename with timestamp if not provided
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"game_results_{timestamp}.json"
    
    # Add timestamp to results data
    results_data["timestamp"] = datetime.now().isoformat()
    
    # Save data to file
    file_path = results_dir / filename
    with open(file_path, 'w') as f:
        json.dump(results_data, f, indent=4)
    
    return str(file_path)

def load_game_results(filename):
    """
    Load game results from a JSON file
    
    Args:
        filename (str): Path to the results file
    
    Returns:
        dict: The loaded game results data
    """
    file_path = Path(filename)
    if not file_path.exists():
        raise FileNotFoundError(f"Results file not found: {filename}")
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    return data

def format_round_data(round_data):
    """
    Format round data for display or export
    
    Args:
        round_data (list): List of round data dictionaries
    
    Returns:
        dict: Formatted statistics about the rounds
    """
    stats = {
        "total_rounds": len(round_data),
        "player_wins": 0,
        "robot_wins": 0,
        "ties": 0,
        "bluff_count": 0,
        "player_detected_bluffs": 0,
        "avg_player_bet": 0,
        "avg_robot_bet": 0,
        "male_voice_rounds": 0,
        "female_voice_rounds": 0,
        "rounds_by_voice": {
            "male": {"wins": 0, "losses": 0, "ties": 0, "bluffs": 0, "detected_bluffs": 0},
            "female": {"wins": 0, "losses": 0, "ties": 0, "bluffs": 0, "detected_bluffs": 0}
        }
    }
    
    # Skip if no round data
    if not round_data:
        return stats
    
    # Calculate statistics
    total_player_bet = 0
    total_robot_bet = 0
    
    for round_info in round_data:
        # Get round outcome
        outcome = round_info.get("expected_outcome", None)
        voice_gender = round_info.get("robot_voice_gender", "male")
        
        # Count by voice gender
        if voice_gender == "male":
            stats["male_voice_rounds"] += 1
        else:
            stats["female_voice_rounds"] += 1
        
        # Track wins/losses
        if outcome:
            if outcome == "PLAYER_WINS":
                stats["player_wins"] += 1
                stats["rounds_by_voice"][voice_gender]["wins"] += 1
            elif outcome == "ROBOT_WINS":
                stats["robot_wins"] += 1
                stats["rounds_by_voice"][voice_gender]["losses"] += 1
            else:  # TIE
                stats["ties"] += 1
                stats["rounds_by_voice"][voice_gender]["ties"] += 1
        
        # Track bluffs
        if round_info.get("robot_bluffed", False):
            stats["bluff_count"] += 1
            stats["rounds_by_voice"][voice_gender]["bluffs"] += 1
            
            if round_info.get("player_detected_bluff", False):
                stats["player_detected_bluffs"] += 1
                stats["rounds_by_voice"][voice_gender]["detected_bluffs"] += 1
        
        # Track bets
        player_bet = round_info.get("player_bet_amount", 0)
        robot_bet = round_info.get("robot_bet_amount", 0)
        total_player_bet += player_bet
        total_robot_bet += robot_bet
    
    # Calculate averages
    if stats["total_rounds"] > 0:
        stats["avg_player_bet"] = total_player_bet / stats["total_rounds"]
        stats["avg_robot_bet"] = total_robot_bet / stats["total_rounds"]
    
    return stats

def export_questionnaire_results(likert_responses, text_responses, participant_id=None):
    """
    Export questionnaire results to a file
    
    Args:
        likert_responses (list): List of Likert scale responses
        text_responses (list): List of text responses
        participant_id (str, optional): Participant ID for filename
    
    Returns:
        str: Path to the saved file
    """
    # Create results directory if it doesn't exist
    results_dir = Path("questionnaire_results")
    if not results_dir.exists():
        results_dir.mkdir(parents=True)
    
    # Generate filename with timestamp and participant ID if provided
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if participant_id:
        filename = f"questionnaire_{participant_id}_{timestamp}.json"
    else:
        filename = f"questionnaire_{timestamp}.json"
    
    # Prepare data
    data = {
        "timestamp": datetime.now().isoformat(),
        "participant_id": participant_id,
        "likert_responses": likert_responses,
        "text_responses": text_responses
    }
    
    # Save data to file
    file_path = results_dir / filename
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)
    
    return str(file_path)