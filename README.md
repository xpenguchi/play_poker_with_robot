# Texas Hold'em Poker Game with Misty Robot Integration

A simplified Texas Hold'em poker game that can be played against a Misty robot, designed to investigate the effects of robot voice gender on trust and deception during strategic gameplay.

## Research Background

This project was developed as part of a research study investigating "The Role of Robot Voice Gender in Trust and Deception during Strategic Gameplay." The game implements a simplified Texas Hold'em variant where players compete against a robot that exhibits deceptive behavior through facial expressions and verbal cues.

## Features

- **Simplified Texas Hold'em**: All community cards revealed at once with a single betting phase
- **Misty Robot Integration**: Connect to a physical Misty robot for lifelike interaction (optional)
- **Voice Gender Options**: Choose between male and female robot voices
- **Predetermined Hands**: 12 carefully balanced hand setups that ensure fair distribution of outcomes
- **Deception Modeling**: The robot bluffs in 50% of rounds, displaying misleading facial expressions or verbal cues
- **Data Collection**: Comprehensive tracking of game interactions and player responses

## Installation

### Prerequisites

- Python 3.6 or higher
- Tkinter (usually included with Python)
- PIL (Python Imaging Library)
- Network connection (if using a Misty robot)

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/texas-holdem-misty.git
   cd texas-holdem-misty
   ```

2. Install required packages:
   ```
   pip install pillow requests
   ```

3. Create a 'cards' directory for card images (optional - the game uses text placeholders if no images are found)

## Usage

### Starting the Game

Run the main.py file with the appropriate command-line arguments:

```
python main.py [--misty] [--ip IP_ADDRESS] [--chips NUM_CHIPS] [--voice VOICE_GENDER]
```

#### Command Line Arguments

- `--misty`: Enable Misty robot integration (default: disabled)
- `--ip`: IP address of the Misty robot (default: 192.168.0.137)
- `--chips`: Initial number of chips for each player (default: 6)
- `--voice`: Robot voice gender, 'male' or 'female' (default: random)

### Example Commands

- Run game without Misty integration:
  ```
  python main.py
  ```

- Run game with Misty integration:
  ```
  python main.py --misty --ip 192.168.1.100
  ```

- Run game with specific configuration:
  ```
  python main.py --chips 12 --voice female
  ```

## Gameplay

1. **Game Setup**: Each player (human and robot) starts with the same number of chips.
2. **Dealing**: In each round, players are dealt two hole cards, and three community cards are shown.
3. **Betting**: The player can check, bet, or fold. The robot responds accordingly.
4. **Resolution**: After betting, the best poker hand wins the pot.
5. **Rounds**: The game consists of 6 rounds.
6. **Post-Game**: After completing all rounds, a questionnaire appears to collect research data.

## Project Structure

- **main.py**: Entry point and command-line argument handling
- **game_misty.py**: Main game logic and Misty integration
- **game_logic.py**: Poker hand evaluation and predetermined hand setups
- **misty_interface.py**: Communication with the Misty robot
- **models.py**: Core classes for cards, deck, and hand evaluation
- **ui_misty.py**: User interface components
- **questionnaire.py**: Post-game questionnaire for data collection
- **utils.py**: Utility functions for data management

## Research Framework

This implementation is based on a research protocol that investigates:

1. **Trust Bias**: How voice gender affects players' trust in the robot
2. **Deception Susceptibility**: Whether players are more deceived by male or female-voiced robots
3. **Risk Assessment**: How voice gender influences betting behavior and risk-taking
4. **Confidence**: Player confidence levels when playing against different robot voices

## Acknowledgments

- Developed for research on human-robot interaction during strategic gameplay
- Uses a modified Texas Hold'em poker rule set for experimental purposes
- Integrates with Misty Robotics platform for physical embodiment