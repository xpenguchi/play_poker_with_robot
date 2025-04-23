#!/usr/bin/env python3
"""
Post-Game Questionnaire for Texas Hold'em Poker Game
Implements the post-game questionnaire to collect research data
"""

import tkinter as tk
from tkinter import messagebox

class PostGameQuestionnaire:
    """Post-game questionnaire to collect research data"""
    
    def __init__(self, master, game_instance):
        """
        Initialize the post-game questionnaire
        
        Args:
            master: The Tkinter root window
            game_instance: The TexasHoldemGame instance
        """
        self.master = master
        self.game = game_instance
        
        # Questionnaire responses
        self.likert_responses = []
        self.text_responses = []
    
    def show_questionnaire(self):
        """Show the post-game questionnaire window"""
        # Create a new window for the questionnaire
        questionnaire_window = tk.Toplevel(self.master)
        questionnaire_window.title("Post-Game Questionnaire")
        questionnaire_window.geometry("600x700")
        questionnaire_window.configure(bg="white")
        
        # Add scrolling capability
        canvas = tk.Canvas(questionnaire_window, bg="white")
        scrollbar = tk.Scrollbar(questionnaire_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add title
        title_label = tk.Label(
            scrollable_frame,
            text="Post-Game Questionnaire",
            font=("Arial", 16, "bold"),
            bg="white"
        )
        title_label.pack(pady=10)
        
        # Instructions
        instruction_label = tk.Label(
            scrollable_frame,
            text="Please answer the following questions about your experience.",
            font=("Arial", 12),
            bg="white",
            wraplength=550
        )
        instruction_label.pack(pady=10)
        
        # Define Likert scale questions based on the research proposal's measures
        self.create_likert_questions(scrollable_frame)
        
        # Add open-ended questions
        self.create_open_questions(scrollable_frame)
        
        # Submit button
        submit_button = tk.Button(
            scrollable_frame,
            text="Submit Responses",
            font=("Arial", 12, "bold"),
            command=lambda: self.submit_responses(questionnaire_window)
        )
        submit_button.pack(pady=20)
    
    def create_likert_questions(self, parent_frame):
        """
        Create Likert scale questions
        
        Args:
            parent_frame: The parent frame to add questions to
        """
        # Define questions based on the research proposal's measures
        likert_questions = [
            # Trust (H1)
            {"category": "Trust", "text": "I trusted the robot during the game."},
            {"category": "Trust", "text": "The robot appeared trustworthy."},
            {"category": "Trust", "text": "I could rely on the robot's expressions."},
            
            # Deception Detection (H2)
            {"category": "Deception Detection", "text": "I could tell when the robot was bluffing."},
            {"category": "Deception Detection", "text": "The robot's expressions matched its actual hand."},
            {"category": "Deception Detection", "text": "I found it difficult to read the robot's intentions."},
            
            # Deception Engagement (H3)
            {"category": "Deception Engagement", "text": "I felt comfortable bluffing against the robot."},
            {"category": "Deception Engagement", "text": "I bluffed more frequently against the male-voiced robot."},
            {"category": "Deception Engagement", "text": "I bluffed more frequently against the female-voiced robot."},
            
            # Risk Assessment (H4)
            {"category": "Risk Assessment", "text": "I took more risks when playing against the robot."},
            {"category": "Risk Assessment", "text": "I placed higher bets against the male-voiced robot."},
            {"category": "Risk Assessment", "text": "I placed higher bets against the female-voiced robot."},
            
            # Confidence (H5)
            {"category": "Confidence", "text": "I felt confident in my decisions during the game."},
            {"category": "Confidence", "text": "I felt more confident against the male-voiced robot."},
            {"category": "Confidence", "text": "I felt more confident against the female-voiced robot."}
        ]
        
        # Create Likert scale questions
        current_category = ""
        self.likert_responses = []
        
        for i, question in enumerate(likert_questions):
            if question["category"] != current_category:
                current_category = question["category"]
                
                # Add category header
                category_label = tk.Label(
                    parent_frame,
                    text=current_category,
                    font=("Arial", 14, "bold"),
                    bg="white"
                )
                category_label.pack(pady=(15, 5), anchor="w", padx=20)
            
            # Create frame for each question
            question_frame = tk.Frame(parent_frame, bg="white")
            question_frame.pack(fill="x", padx=20, pady=5)
            
            # Question text
            question_label = tk.Label(
                question_frame,
                text=question["text"],
                font=("Arial", 12),
                bg="white",
                anchor="w",
                justify="left",
                wraplength=400
            )
            question_label.pack(side="left")
            
            # Likert scale (1-7)
            scale_var = tk.IntVar(value=4)  # Default middle value
            self.likert_responses.append(scale_var)
            
            scale_frame = tk.Frame(question_frame, bg="white")
            scale_frame.pack(side="right")
            
            scale = tk.Scale(
                scale_frame,
                from_=1,
                to=7,
                orient="horizontal",
                variable=scale_var,
                bg="white",
                label=""
            )
            scale.pack(side="top")
            
            # Scale labels
            scale_label_frame = tk.Frame(scale_frame, bg="white")
            scale_label_frame.pack(side="bottom", fill="x")
            
            tk.Label(scale_label_frame, text="Strongly\nDisagree", font=("Arial", 8), bg="white").pack(side="left")
            tk.Label(scale_label_frame, text="Neutral", font=("Arial", 8), bg="white").pack(side="left", padx=30)
            tk.Label(scale_label_frame, text="Strongly\nAgree", font=("Arial", 8), bg="white").pack(side="left")
    
    def create_open_questions(self, parent_frame):
        """
        Create open-ended questions
        
        Args:
            parent_frame: The parent frame to add questions to
        """
        # Add open-ended questions section header
        open_label = tk.Label(
            parent_frame,
            text="Open-Ended Questions",
            font=("Arial", 14, "bold"),
            bg="white"
        )
        open_label.pack(pady=(15, 5), anchor="w", padx=20)
        
        # Define open-ended questions from the research proposal
        open_questions = [
            "What factors influenced your decision to trust or not trust the robot's expression?",
            "How did your trust in the robot's expressions change throughout the experiment?",
            "Did you feel more competitive or confident with one robot voice?",
            "Did your strategies differ by robot?"
        ]
        
        self.text_responses = []
        
        for question in open_questions:
            question_frame = tk.Frame(parent_frame, bg="white")
            question_frame.pack(fill="x", padx=20, pady=5)
            
            question_label = tk.Label(
                question_frame,
                text=question,
                font=("Arial", 12),
                bg="white",
                anchor="w",
                justify="left",
                wraplength=550
            )
            question_label.pack(anchor="w")
            
            text_var = tk.Text(
                question_frame,
                height=4,
                width=60,
                wrap="word"
            )
            text_var.pack(pady=5)
            self.text_responses.append(text_var)
    
    def submit_responses(self, questionnaire_window):
        """
        Submit questionnaire responses
        
        Args:
            questionnaire_window: The questionnaire window to close after submission
        """
        # Collect Likert scale responses
        likert_data = [var.get() for var in self.likert_responses]
        
        # Collect text responses
        text_data = [text.get("1.0", "end-1c") for text in self.text_responses]
        
        # In a real implementation, this would save the data to a file or database
        # Here we just print to console and show a confirmation
        print("Likert Scale Responses:", likert_data)
        print("Open-Ended Responses:", text_data)
        
        messagebox.showinfo(
            "Responses Submitted",
            "Thank you for completing the questionnaire. Your responses have been recorded."
        )
        
        questionnaire_window.destroy()