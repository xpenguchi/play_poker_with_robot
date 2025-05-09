#!/usr/bin/env python3
"""
Misty Robot Interface for Texas Hold'em Poker Game
Handles communication with the Misty robot for expressions, voice, and movement
"""

import requests
import json
import time
import threading
from enum import Enum
import os
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
    MALE = "en-US-Chirp-HD-D"  # Male voice option
    FEMALE = "en-US-Chirp-HD-F"  # Female voice option

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
        if not self.connected:
            print("Not connected to Misty")
            return False
        
        try:
            # Determine which voice to use
            selected_voice = self.current_voice
            if not use_current_voice and voice is not None:
                selected_voice = voice
            
            # Use Misty's API to speak text
            response = requests.post(
                f"{self.base_url}/tts/speak",
                json={
                    "Text": text,
                    "VoiceId": selected_voice.value,
                    "UtteranceId": f"poker_game_{int(time.time())}"
                }
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error making Misty speak: {e}")
            return False
    
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
        if not self.connected:
            print("Not connected to Misty")
            return False
        
        try:
            # Use Misty's API to move head
            response = requests.post(
                f"{self.base_url}/head",
                json={
                    "Pitch": pitch,
                    "Roll": roll,
                    "Yaw": yaw,
                    "Velocity": velocity
                }
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error moving Misty's head: {e}")
            return False
    
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
        self.misty.say_text(random.choice(phrases))
    
    def handle_win(self):
        """Handle Misty winning a round"""
        self.misty.play_happy_animation()
        
        phrases = [
            "I won this round!",
            "Great! I take this pot.",
            "That was a good hand for me.",
            "Looks like I won this time."
        ]
        self.misty.say_text(random.choice(phrases))
    
    def handle_loss(self):
        """Handle Misty losing a round"""
        self.misty.play_sad_animation()
        
        phrases = [
            "You won this round.",
            "Congratulations, that was a good play.",
            "You got me this time.",
            "Well played."
        ]
        self.misty.say_text(random.choice(phrases))
    
    def handle_tie(self):
        """Handle a tie"""
        self.misty.set_expression(MistyExpression.NEUTRAL)
        
        phrases = [
            "It's a tie.",
            "We both had similar hands.",
            "Let's split the pot.",
            "Neither of us wins this time."
        ]
        self.misty.say_text(random.choice(phrases))
    
    def cleanup(self):
        """Clean up and disconnect from Misty"""
        return self.misty.disconnect()


# Example usage if run as a script
if __name__ == "__main__":
    # Simple test of Misty poker player functionality
    misty_player = MistyPokerPlayer()
    
    if misty_player.misty.connected:
        print("Testing Misty poker player...")
        
        # Test male voice
        misty_player.set_voice_gender("male")
        misty_player.handle_new_round()
        time.sleep(2)
        
        # Test female voice
        misty_player.set_voice_gender("female")
        misty_player.handle_new_round()
        time.sleep(2)
        
        # Test bluffing with good hand
        misty_player.set_hand_quality("good")
        misty_player.set_bluffing(True)
        misty_player.handle_betting_turn()
        time.sleep(3)
        
        # Test not bluffing with bad hand
        misty_player.set_hand_quality("bad")
        misty_player.set_bluffing(False)
        misty_player.handle_betting_turn()
        time.sleep(3)
        
        # Test win, loss, tie
        misty_player.handle_win()
        time.sleep(2)
        misty_player.handle_loss()
        time.sleep(2)
        misty_player.handle_tie()
        time.sleep(2)
        
        # Clean up
        misty_player.cleanup()
    else:
        print("Failed to connect to Misty. Check the IP address and try again.")