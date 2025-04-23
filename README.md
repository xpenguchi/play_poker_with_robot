# Texas Hold'em Poker Research Game

## Project Overview
This application implements a simplified version of Texas Hold'em poker designed for research on how robot voice gender affects human trust, confidence, and deception during strategic gameplay. The game is based on the research proposal "Trust and Deception: The Role of Robot Voice Gender in Strategic Gameplay."

## Features
- Simplified Texas Hold'em game with predetermined outcomes that can be controlled remotely
- Robot voice gender switching (male/female) to study its effect on player behavior
- Robot deception through facial expressions and verbal cues
- Admin controls for researchers to manipulate game outcomes and robot behavior
- Data collection for player responses and behaviors
- Post-game questionnaire based on the research measures

## Project Structure
- `main.py` - Main entry point for the application
- `models.py` - Data models for cards, deck, and game outcomes
- `game_misty.py` - Main game class that integrates all components
- `game_logic.py` - Game logic for determining outcomes and robot behavior
- `ui_misty.py` - User interface components
- `admin_panel.py` - Admin control panel for researchers
- `questionnaire.py` - Post-game questionnaire implementation
- `utils.py` - Utility functions for data tracking and analysis
- `misty_interface.py` - Express the misty interface

## Requirements
- Python 3.6+
- Tkinter (for GUI)
- PIL/Pillow (for card images)

## Installation
1. Clone the repository
2. Install dependencies:
   ```
   pip install pillow
   ```
3. Run the application:
   ```
   python main.py
   ```

## Usage
### Player Controls
- **Fold**: Give up the current hand (robot wins)
- **Bet 1**: Bet 1 chip
- **Bet 2**: Bet 2 chips
- **Next Round**: Proceed to the next round (enabled after a round completes)

### Admin Controls (Research Mode)
Press **Ctrl+A** to toggle the admin panel, which allows researchers to control:
- Game outcomes (player wins, robot wins, tie)
- Robot betting style (aggressive, neutral, conservative)
- Robot betting amount
- Robot bluffing behavior
- Robot voice gender

### Game Flow
1. The game consists of 2 sets of 6 rounds each
2. The first set uses one robot voice gender
3. After the first set, the voice gender changes for the second set
4. Each round reveals community cards, player cards, and hidden robot cards
5. Players can choose to bet or fold based on their hand and the robot's behavior
6. After betting, the robot's cards are revealed and the winner is determined
7. After all rounds, a questionnaire collects data about the player's experience

## Data Collection
- The game collects data about player betting behavior, responses to robot deception, and outcomes
- Results are saved to a JSON file in the `results` directory
- Questionnaire responses are saved to a JSON file in the `questionnaire_results` directory

## Research Variables Measured
- **Trust**: Whether players follow the robot's cues
- **Deception Detection**: Whether players can identify the robot's bluffing
- **Deception Engagement**: How frequently players bluff against the robot
- **Risk-Taking**: Betting behavior based on robot voice gender
- **Confidence**: Self-reported confidence in decisions

## Customization
- Card images can be placed in a `cards` directory with filenames like `ah.png` (Ace of Hearts)
- If no card images are found, simple placeholders will be created