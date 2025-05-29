#!/usr/bin/env python3
"""
Misty Robot Interface for Texas Hold'em Poker Game
Handles communication with the Misty robot for expressions, voice, and movement
"""
import sys, os, time
sys.path.append(os.path.join(os.path.join(os.path.dirname(__file__)), 'Python-SDK'))

from mistyPy.Robot import Robot
from mistyPy.Events import Events

import requests
import json
import time
import threading
from enum import Enum
import random

class MistyExpression(Enum):
    """Enum for Misty's facial expressions"""
    NEUTRAL = "e_ContentLeft.jpg"
    HAPPY = "e_Joy.jpg"
    SAD = "e_Sadness.jpg"
    CONFIDENT = "e_Surprise.jpg"
    UNCERTAIN = "e_Fear.jpg"
    THINKING = "e_Contempt.jpg"

class MistyVoiceGender(Enum):
    """Enum for Misty's voice gender"""
    MALE = "en-gb-x-gbb-local" # Male voice option
    FEMALE = "en-gb-x-gba-local"  # Female voice option

class MistyInterface:
    """Interface for controlling the Misty robot"""
    
    def __init__(self, ip_address="192.168.1.100", connect_on_init=True):
        """
        Initialize the Misty interface
        
        Args:
            ip_address (str): IP address of the Misty robot
            connect_on_init (bool): Whether to connect to Misty on initialization
        """
        self.ip_address = ip_address
        self.base_url = f"http://{ip_address}/api"
        self.connected = False
        self.current_voice = MistyVoiceGender.MALE
        self.robot = Robot(ip_address)
        
        # If requested, connect to Misty on initialization
        if connect_on_init:
            self.connect()
    
    def connect(self):
        """
        Connect to the Misty robot
        
        Returns:
            bool: Whether the connection was successful
        """
        try:
            print(f"Attempting to connect to Misty at {self.ip_address}")
            url = f"http://{self.ip_address}/api/device"
            print(f"API URL: {url}")
            response = requests.get(url)
            print(f"Status code: {response.status_code}")
            print(f"Response content: {response.text}")
            
            if response.status_code == 200:
                self.connected = True
                print(f"Successfully connected to Misty at {self.ip_address}")
                
                self.set_expression(MistyExpression.NEUTRAL)
                return True
            else:
                print(f"Failed to connect to Misty: Status code {response.status_code}")
                return False
        except Exception as e:
            print(f"Error connecting to Misty: {e}")
            return False
    
    def set_expression(self, expression):
        """
        Set Misty's facial expression
        
        Args:
            expression (MistyExpression): The expression to set
            
        Returns:
            bool: Whether the operation was successful
        """
        if not self.connected:
            print("Not connected to Misty")
            return False
        
        try:
            # Use Misty's API to change the displayed image
            response = requests.post(
                f"{self.base_url}/images/display",
                json={
                    "FileName": expression.value,
                    "Alpha": 1,
                    "Layer": 1
                }
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error setting Misty's expression: {e}")
            return False
    
    def say_text(self, text, use_current_voice=True, voice=None):
        """
        Make Misty speak text
        
        Args:
            text (str): The text for Misty to speak
            use_current_voice (bool): Whether to use the current voice setting
            voice (MistyVoiceGender, optional): Override the voice to use
            
        Returns:
            bool: Whether the operation was successful
        """
        # if not self.connected:
        #     print("Not connected to Misty")
        #     return False
        
        # try:
        #     # Determine which voice to use
        #     selected_voice = self.current_voice
        #     if not use_current_voice and voice is not None:
        #         selected_voice = voice
            
        #     # Use Misty's API to speak text
        #     response = requests.post(
        #         f"{self.base_url}/tts/speak",
        #         json={
        #             "Text": text,
        #             "VoiceId": selected_voice.value,
        #             "UtteranceId": f"poker_game_{int(time.time())}"
        #         }
        #     )
        #     return response.status_code == 200
        # except Exception as e:
        #     print(f"Error making Misty speak: {e}")
        #     return False
        selected_voice = self.current_voice
        self.robot.speak(text, voice=selected_voice.value)
    
    def set_voice_gender(self, gender):
        """
        Set Misty's voice gender
        
        Args:
            gender (MistyVoiceGender): The voice gender to use
            
        Returns:
            bool: Whether the operation was successful
        """
        if gender not in [MistyVoiceGender.MALE, MistyVoiceGender.FEMALE]:
            print(f"Invalid voice gender: {gender}")
            return False
        
        self.current_voice = gender
        return True
    
    def move_head(self, pitch=0, roll=0, yaw=0, velocity=10):
        """
        Move Misty's head
        
        Args:
            pitch (float): Up/down movement (-40 to 26 degrees)
            roll (float): Tilt left/right (-43 to 43 degrees)
            yaw (float): Turn left/right (-70 to 70 degrees)
            velocity (int): Movement velocity (0-100)
            
        Returns:
            bool: Whether the operation was successful
        """
        self.robot.move_head(pitch, roll, yaw, velocity)

    def move_arms(self, leftArmPosition=None, rightArmPosition=None, leftArmVelocity=None, rightArmVelocity=None, duration=None, units=None):
        """
        Move Misty's arms
        """
        if not self.connected:
            print("Not connected to Misty")
            return False
        self.robot.move_arms(leftArmPosition, rightArmPosition, leftArmVelocity, rightArmVelocity, duration, units)
    
    def play_happy_animation(self):
        """
        Play a happy animation sequence
        
        Returns:
            bool: Whether the operation was successful
        """
        try:
            self.set_expression(MistyExpression.HAPPY)
            self.move_head(pitch=10, yaw=15)
            time.sleep(0.5)
            self.move_head(pitch=10, yaw=-15)
            time.sleep(0.5)
            self.move_head(pitch=0, yaw=0)
            return True
        except Exception as e:
            print(f"Error playing happy animation: {e}")
            return False
    
    def play_sad_animation(self):
        """
        Play a sad animation sequence
        
        Returns:
            bool: Whether the operation was successful
        """
        try:
            self.set_expression(MistyExpression.SAD)
            self.move_head(pitch=-20)
            time.sleep(1)
            self.move_head(pitch=0)
            return True
        except Exception as e:
            print(f"Error playing sad animation: {e}")
            return False
    
    def play_thinking_animation(self):
        """
        Play a thinking animation sequence
        
        Returns:
            bool: Whether the operation was successful
        """
        try:
            self.set_expression(MistyExpression.THINKING)
            self.move_head(roll=15)
            time.sleep(0.7)
            self.move_head(roll=-15)
            time.sleep(0.7)
            self.move_head(roll=0)
            return True
        except Exception as e:
            print(f"Error playing thinking animation: {e}")
            return False
    
    def play_uncertain_animation(self):
        """
        Play an uncertain animation sequence
        
        Returns:
            bool: Whether the operation was successful
        """
        try:
            self.set_expression(MistyExpression.UNCERTAIN)
            self.move_head(roll=10, yaw=20)
            time.sleep(0.5)
            self.move_head(roll=-10, yaw=-20)
            time.sleep(0.5)
            self.move_head(roll=0, yaw=0)
            return True
        except Exception as e:
            print(f"Error playing uncertain animation: {e}")
            return False
    
    def play_confident_animation(self):
        """
        Play a confident animation sequence
        
        Returns:
            bool: Whether the operation was successful
        """
        try:
            self.set_expression(MistyExpression.CONFIDENT)
            self.move_head(pitch=15)
            time.sleep(0.5)
            self.move_head(pitch=0)
            return True
        except Exception as e:
            print(f"Error playing confident animation: {e}")
            return False
    
    def disconnect(self):
        """
        Disconnect from the Misty robot
        
        Returns:
            bool: Whether the operation was successful
        """
        if self.connected:
            # Reset Misty to a neutral state before disconnecting
            try:
                self.set_expression(MistyExpression.NEUTRAL)
                self.move_head(pitch=0, roll=0, yaw=0)
                self.connected = False
                print(f"Disconnected from Misty at {self.ip_address}")
                return True
            except Exception as e:
                print(f"Error disconnecting from Misty: {e}")
                return False
        return True  # Already disconnected

class MistyPokerPlayer:
    """
    Class to manage Misty as a poker player
    Integrates with the poker game and translates game states to Misty behaviors
    """
    
    def __init__(self, ip_address="192.168.1.100", auto_connect=True):
        """
        Initialize the Misty poker player
        
        Args:
            ip_address (str): IP address of the Misty robot
            auto_connect (bool): Whether to automatically connect to Misty
        """
        self.misty = MistyInterface(ip_address, connect_on_init=auto_connect)
        self.is_bluffing = False
        self.hand_quality = "average"  # can be "good", "average", or "bad"
        self.current_voice_gender = "male"
        self.robot = Robot(ip_address)
    
    def set_voice_gender(self, gender):
        """
        Set Misty's voice gender
        
        Args:
            gender (str): The voice gender ("male" or "female")
            
        Returns:
            bool: Whether the operation was successful
        """
        if gender.lower() == "male":
            self.misty.set_voice_gender(MistyVoiceGender.MALE)
            self.current_voice_gender = "male"
            return True
        elif gender.lower() == "female":
            self.misty.set_voice_gender(MistyVoiceGender.FEMALE)
            self.current_voice_gender = "female"
            return True
        else:
            print(f"Invalid gender: {gender}")
            return False
    
    def set_hand_quality(self, quality):
        """
        Set the quality of Misty's current hand
        
        Args:
            quality (str): The hand quality ("good", "average", or "bad")
            
        Returns:
            bool: Whether the operation was successful
        """
        if quality.lower() in ["good", "average", "bad"]:
            self.hand_quality = quality.lower()
            return True
        else:
            print(f"Invalid hand quality: {quality}")
            return False
    
    def set_bluffing(self, is_bluffing):
        """
        Set whether Misty is bluffing
        
        Args:
            is_bluffing (bool): Whether Misty is bluffing
            
        Returns:
            bool: Whether the operation was successful
        """
        self.is_bluffing = bool(is_bluffing)
        return True
    
    def handle_new_round(self):
        """Handle the start of a new round"""
        # Reset to neutral expression
        self.misty.set_expression(MistyExpression.NEUTRAL)
        
        # Say something to indicate a new round
        phrases = [
            "Let's play a new round.",
            "Ready for the next hand?",
            "New cards, new opportunities.",
            "Let's see what we get this time."
        ]
        self.misty.say_text(random.choice(phrases))
    
    def handle_betting_turn(self):
        """Handle Misty's turn to bet"""
        # Depending on bluffing status and hand quality, show appropriate behavior
        self.misty.play_thinking_animation()
        
        # Wait for "thinking" time
        time.sleep(2)
        
        # Show appropriate expression based on bluffing and hand quality
        if self.is_bluffing:
            if self.hand_quality == "good":
                # Has good hand but pretending it's not good
                self.misty.play_uncertain_animation()
                phrases = [
                    "Hmm, I'm not sure about this hand.",
                    "This is tricky.",
                    "I need to think about this one."
                ]
            else:
                # Has average/bad hand but pretending it's good
                self.misty.play_confident_animation()
                phrases = [
                    "I like these cards!",
                    "This looks promising.",
                    "I'm feeling lucky with this hand."
                ]
        else:
            # Not bluffing - expressions match hand quality
            if self.hand_quality == "good":
                self.misty.play_confident_animation()
                phrases = [
                    "I have a strong hand.",
                    "These cards look great!",
                    "I'm feeling confident."
                ]
            elif self.hand_quality == "average":
                self.misty.set_expression(MistyExpression.NEUTRAL)
                phrases = [
                    "My cards are okay.",
                    "This is a decent hand.",
                    "Let's see what happens."
                ]
            else:  # bad hand
                self.misty.play_uncertain_animation()
                phrases = [
                    "Not the best cards.",
                    "This hand is challenging.",
                    "I'll need some luck with these cards."
                ]
        
        # Say something based on the situation
        time.sleep(1)
        self.misty.say_text(random.choice(phrases))
    
    def handle_win(self):
        """Handle Misty winning a round with movement, expression and sound"""
        # Play victory sound effect
        try:
            # Play a triumph sound (if available on Misty)
            self.robot.play_audio("s_Triumph.wav")  # Or another victory sound available on Misty
        except:
            # Fallback if specific sound isn't available
            print("Could not play victory sound - continuing without it")
        
        self.misty.play_happy_animation()
        
        # Add victory arm movements - corrected understanding of arm positions
        # For victory, move arms from natural resting position (90°) to slightly upward
        self.misty.move_arms(60, 60, 60, 60)  # Arms slightly raised from resting position
        time.sleep(0.6)
        self.misty.move_arms(90, 90, 60, 60)  # Return to resting position
        time.sleep(0.6)
        self.misty.move_arms(60, 60, 60, 60)  # Arms slightly raised again
        time.sleep(0.6)
        self.misty.move_arms(90, 90, 60, 60)  # Return to resting position
        
        # Add head movement for celebration
        self.misty.move_head(pitch=10, yaw=15)
        time.sleep(0.5)
        self.misty.move_head(pitch=10, yaw=-15)
        time.sleep(0.5)
        self.misty.move_head(pitch=0, yaw=0)
        
        phrases = [
            "I won this round!",
            "Great! I take this pot.",
            "That was a good hand for me.",
            "Looks like I won this time."
        ]
        self.misty.say_text(random.choice(phrases))

    # Enhance the handle_loss method in the MistyPokerPlayer class
    def handle_loss(self):
        """Handle Misty losing a round with movement, expression and sound"""
        # Play defeat sound effect
        try:
            # Play a disappointment sound (if available on Misty)
            self.robot.play_audio("s_Disappointment.wav")  # Or another sad sound available on Misty
        except:
            # Fallback if specific sound isn't available
            print("Could not play defeat sound - continuing without it")
        
        self.misty.play_sad_animation()
        
        # Add defeated arm movements - corrected understanding
        # For defeat, move arms from resting position to forward (dejected)
        self.misty.move_arms(50, 50, 30, 30)  # Arms forward/limp (dejected pose)
        time.sleep(1)
        
        # Add head movement for disappointment
        self.misty.move_head(pitch=-15)  # Look down in defeat
        time.sleep(1)
        self.misty.move_head(pitch=0)    # Return to neutral position
        
        phrases = [
            "You won this round.",
            "Congratulations, that was a good play.",
            "You got me this time.",
            "Well played."
        ]
        self.misty.say_text(random.choice(phrases))
        
        # Return arms to natural resting position
        self.misty.move_arms(90, 90, 40, 40)  # Back to natural downward position

    # Enhance the handle_tie method in the MistyPokerPlayer class
    def handle_tie(self):
        """Handle a tie with movement, expression and sound"""
        # Play tie sound effect
        try:
            # Play a neutral/curious sound (if available on Misty)
            self.robot.play_audio("s_PhraseHmm.wav")  # Or another tie-appropriate sound available on Misty
        except:
            # Fallback if specific sound isn't available
            print("Could not play tie sound - continuing without it")
        
        self.misty.set_expression(MistyExpression.NEUTRAL)
        
        # Add tie gesture - corrected understanding
        # For tie, small movement from resting to slightly forward and back
        self.misty.move_arms(70, 70, 40, 40)  # Arms slightly forward for shrug
        time.sleep(0.8)
        self.misty.move_arms(90, 90, 40, 40)  # Back to resting position
        
        # Head tilt for "not sure" gesture
        self.misty.move_head(roll=10)
        time.sleep(0.8)
        self.misty.move_head(roll=-10)
        time.sleep(0.8)
        self.misty.move_head(roll=0)
        
        phrases = [
            "It's a tie.",
            "We both had similar hands.",
            "Let's split the pot.",
            "Neither of us wins this time."
        ]
        self.misty.say_text(random.choice(phrases))
        
        # Ensure arms are in natural resting position
        self.misty.move_arms(90, 90, 40, 40)  # Natural downward position
    
    def cleanup(self):
        """Clean up and disconnect from Misty"""
        return self.misty.disconnect()

    def perform_welcome(self):
        """perform a welcome action"""
        try:
            # Set a happy expression
            self.misty.set_expression(MistyExpression.HAPPY)
            
            # Move head to a friendly position
            self.misty.move_head(pitch=10, yaw=15)
            time.sleep(0.5)
            self.misty.move_head(pitch=10, yaw=-15)
            time.sleep(0.5)
            self.misty.move_head(pitch=0, yaw=0)
            
            welcome_messages = [
                "Hi I'm Misty. Welcome to our Texas Hold'em Poker experiment! I'm excited to play with you today.",
                "Hello and welcome! I'm Misty, and I'll be your poker opponent for this experiment.",
                "Hi I'm Misty. Welcome to our research study on poker gameplay. I hope you enjoy playing with me today."
            ]
            welcome_message = random.choice(welcome_messages)
            self.misty.say_text(welcome_message)
            self.misty.move_arms(90, 90, 100, 100)
            time.sleep(2)
            self.misty.move_arms(-20, -20, 1000)
            time.sleep(2)
            self.misty.move_arms(90, 90, 100, 100)
            time.sleep(2)

            # Additional instructions
            instructions = "We will play 6 rounds of simplified Texas Hold'em. Let's get started!"
            self.misty.say_text(instructions)
        
            # Set a neutral expression after the welcome
            time.sleep(2)
            self.misty.set_expression(MistyExpression.NEUTRAL)
            
        except Exception as e:
            print(f"Error during welcome sequence: {e}")

    def perform_goodbye(self):
        """Perform a goodbye action"""
        try:
            # Set a happy expression
            self.misty.set_expression(MistyExpression.HAPPY)
            
            # Move head to a friendly position
            self.misty.move_head(pitch=20)
            time.sleep(1)
            self.misty.move_head(pitch=0)
            
            # Move head side to side
            self.misty.move_head(yaw=10)
            time.sleep(0.5)
            self.misty.move_head(yaw=-10)
            time.sleep(0.5)
            self.misty.move_head(yaw=0)
            
            thank_you_messages = [
                "Thank you for participating in our poker experiment! I really enjoyed playing with you.",
                "The experiment is now complete. Thank you for your time and participation!",
                "Thank you for being part of our research. Your participation is greatly appreciated."
            ]
            thank_you_message = random.choice(thank_you_messages)
            self.misty.say_text(thank_you_message)
            time.sleep(5)
            
            # Additional message
            extra_message = "Please complete the questionnaire to help us with our research. Have a great day!"
            self.misty.say_text(extra_message)
            
            # Set a neutral expression after the goodbye
            time.sleep(3)
            self.misty.set_expression(MistyExpression.NEUTRAL)
            
        except Exception as e:
            print(f"Error during goodbye sequence: {e}")


# if __name__ == "__main__":
#     # Simple test of Misty poker player functionality
#     misty_player = MistyPokerPlayer()
    
#     if misty_player.misty.connected:
#         print("Testing Misty poker player...")
        
#         # Test male voice
#         misty_player.set_voice_gender("male")
#         misty_player.handle_new_round()
#         time.sleep(2)
        
#         # Test female voice
#         misty_player.set_voice_gender("female")
#         misty_player.handle_new_round()
#         time.sleep(2)
        
#         # Test bluffing with good hand
#         misty_player.set_hand_quality("good")
#         misty_player.set_bluffing(True)
#         misty_player.handle_betting_turn()
#         time.sleep(3)
        
#         # Test not bluffing with bad hand
#         misty_player.set_hand_quality("bad")
#         misty_player.set_bluffing(False)
#         misty_player.handle_betting_turn()
#         time.sleep(3)
        
#         # Test win, loss, tie
#         misty_player.handle_win()
#         time.sleep(2)
#         misty_player.handle_loss()
#         time.sleep(2)
#         misty_player.handle_tie()
#         time.sleep(2)
        
#         # Clean up
#         misty_player.cleanup()
#     else:
#         print("Failed to connect to Misty. Check the IP address and try again.")