import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import random
import json
import math
import turtle
from tkinter import colorchooser
import os

class AstroGuide:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🌌 AstroGuide - Complete Astrology Prediction System")
        self.root.geometry("1000x700")
        self.root.configure(bg='#0f0f23')
        
        # Color scheme variables
        self.bg_color = '#0f0f23'
        self.fg_color = '#ffffff'
        self.accent_color = '#4a5568'
        self.button_color = '#667eea'
        self.dark_mode = True
        
        # User profile storage
        self.user_profiles = {}
        
        # Initialize data
        self.init_astro_data()
        
        # Create main interface
        self.create_main_interface()
        
        # Apply color shifting
        self.start_color_shift()
        
    def init_astro_data(self):
        """Initialize all astrology data"""
        
        # Zodiac signs and dates
        self.zodiac_signs = {
            'Aries': (3, 21, 4, 19),
            'Taurus': (4, 20, 5, 20), 
            'Gemini': (5, 21, 6, 20),
            'Cancer': (6, 21, 7, 22),
            'Leo': (7, 23, 8, 22),
            'Virgo': (8, 23, 9, 22),
            'Libra': (9, 23, 10, 22),
            'Scorpio': (10, 23, 11, 21),
            'Sagittarius': (11, 22, 12, 21),
            'Capricorn': (12, 22, 1, 19),
            'Aquarius': (1, 20, 2, 18),
            'Pisces': (2, 19, 3, 20)
        }
        
        # Daily horoscope predictions
        self.horoscope_predictions = {
            'Aries': [
                "Today brings fiery energy and new opportunities. Trust your instincts!",
                "Your leadership skills shine today. Take charge of important matters.",
                "Adventure calls! Embrace spontaneity and explore new horizons.",
                "Passion drives you forward. Channel your energy into creative pursuits.",
                "Bold decisions lead to success. Don't hesitate to take calculated risks."
            ],
            'Taurus': [
                "Stability and comfort guide your day. Focus on building solid foundations.",
                "Your practical nature serves you well. Make steady progress toward goals.",
                "Material matters require attention. Financial planning brings security.",
                "Beauty surrounds you today. Appreciate art, nature, and luxury.",
                "Patience pays off. Slow and steady progress leads to lasting success."
            ],
            'Gemini': [
                "Communication is key today. Express your ideas with clarity and charm.",
                "Curiosity leads to discovery. Learn something new and exciting.",
                "Social connections bring opportunities. Network and make new friends.",
                "Adaptability is your strength. Embrace change with open arms.",
                "Mental agility helps solve complex problems. Trust your quick thinking."
            ],
            'Cancer': [
                "Emotional intuition guides your decisions. Listen to your inner voice.",
                "Home and family need your attention. Nurture those closest to you.",
                "Sensitivity brings deeper understanding. Empathy opens new doors.",
                "Memories surface with important lessons. Reflect on past experiences.",
                "Caring for others brings fulfillment. Your compassion makes a difference."
            ],
            'Leo': [
                "Your natural charisma attracts attention. Shine bright and inspire others.",
                "Creative expression flows freely. Share your talents with the world.",
                "Confidence opens doors. Step into the spotlight with pride.",
                "Generosity of spirit brings rewards. Your warmth touches many hearts.",
                "Leadership opportunities arise. Guide others with wisdom and grace."
            ],
            'Virgo': [
                "Attention to detail pays dividends. Perfectionism serves you well today.",
                "Organization brings clarity. Structure your day for maximum efficiency.",
                "Service to others fulfills your soul. Help those who need your skills.",
                "Health consciousness serves you well. Take care of your physical being.",
                "Analytical thinking solves complex problems. Trust your methodical approach."
            ],
            'Libra': [
                "Balance and harmony guide your choices. Seek equilibrium in all things.",
                "Relationships require attention. Diplomacy helps resolve conflicts.",
                "Beauty and aesthetics inspire you. Surround yourself with elegance.",
                "Justice matters deeply to you. Stand up for what's fair and right.",
                "Partnership opportunities arise. Collaboration brings mutual success."
            ],
            'Scorpio': [
                "Deep transformation is possible today. Embrace profound changes.",
                "Mysteries unfold before you. Investigation reveals hidden truths.",
                "Intense emotions guide your path. Channel passion into purpose.",
                "Psychic intuition is heightened. Trust your supernatural insights.",
                "Regeneration and renewal begin. Rise from challenges stronger than before."
            ],
            'Sagittarius': [
                "Adventure beckons from distant horizons. Explore new territories.",
                "Philosophical insights expand your worldview. Seek higher wisdom.",
                "Freedom and independence energize you. Break free from limitations.",
                "Teaching others brings satisfaction. Share your knowledge generously.",
                "Optimism attracts good fortune. Your positive attitude opens doors."
            ],
            'Capricorn': [
                "Ambition drives you toward success. Climb the mountain step by step.",
                "Responsibility weighs heavily but brings rewards. Duty leads to honor.",
                "Practical achievements build lasting legacy. Focus on tangible results.",
                "Authority recognizes your competence. Leadership roles await you.",
                "Discipline and structure create stability. Build strong foundations today."
            ],
            'Aquarius': [
                "Innovation sparks brilliant solutions. Think outside conventional boundaries.",
                "Humanitarian causes call your name. Make the world a better place.",
                "Friendship brings unexpected opportunities. Connect with like-minded souls.",
                "Technology enhances your capabilities. Embrace digital solutions.",
                "Independence fuels your creativity. March to your own drummer today."
            ],
            'Pisces': [
                "Imagination flows like a river of dreams. Create beautiful visions.",
                "Compassion opens hearts around you. Your empathy heals wounded souls.",
                "Spiritual insights bring profound understanding. Meditate on deeper truths.",
                "Artistic expression channels divine inspiration. Create something beautiful.",
                "Intuitive wisdom guides your decisions. Trust your psychic impressions."
            ]
        }
        
        # Compatibility matrix (percentage)
        self.compatibility_matrix = {
            'Aries': {'Aries': 85, 'Taurus': 60, 'Gemini': 90, 'Cancer': 55, 'Leo': 95, 'Virgo': 65, 
                      'Libra': 80, 'Scorpio': 70, 'Sagittarius': 95, 'Capricorn': 60, 'Aquarius': 85, 'Pisces': 65},
            'Taurus': {'Aries': 60, 'Taurus': 80, 'Gemini': 65, 'Cancer': 90, 'Leo': 70, 'Virgo': 95,
                       'Libra': 85, 'Scorpio': 85, 'Sagittarius': 55, 'Capricorn': 95, 'Aquarius': 60, 'Pisces': 85},
            'Gemini': {'Aries': 90, 'Taurus': 65, 'Gemini': 75, 'Cancer': 65, 'Leo': 85, 'Virgo': 70,
                       'Libra': 95, 'Scorpio': 60, 'Sagittarius': 90, 'Capricorn': 55, 'Aquarius': 95, 'Pisces': 70},
            'Cancer': {'Aries': 55, 'Taurus': 90, 'Gemini': 65, 'Cancer': 85, 'Leo': 75, 'Virgo': 90,
                       'Libra': 70, 'Scorpio': 95, 'Sagittarius': 60, 'Capricorn': 85, 'Aquarius': 55, 'Pisces': 95},
            'Leo': {'Aries': 95, 'Taurus': 70, 'Gemini': 85, 'Cancer': 75, 'Leo': 80, 'Virgo': 65,
                    'Libra': 90, 'Scorpio': 75, 'Sagittarius': 95, 'Capricorn': 65, 'Aquarius': 90, 'Pisces': 70},
            'Virgo': {'Aries': 65, 'Taurus': 95, 'Gemini': 70, 'Cancer': 90, 'Leo': 65, 'Virgo': 85,
                      'Libra': 75, 'Scorpio': 90, 'Sagittarius': 60, 'Capricorn': 95, 'Aquarius': 65, 'Pisces': 80},
            'Libra': {'Aries': 80, 'Taurus': 85, 'Gemini': 95, 'Cancer': 70, 'Leo': 90, 'Virgo': 75,
                      'Libra': 80, 'Scorpio': 70, 'Sagittarius': 85, 'Capricorn': 70, 'Aquarius': 95, 'Pisces': 80},
            'Scorpio': {'Aries': 70, 'Taurus': 85, 'Gemini': 60, 'Cancer': 95, 'Leo': 75, 'Virgo': 90,
                        'Libra': 70, 'Scorpio': 90, 'Sagittarius': 65, 'Capricorn': 85, 'Aquarius': 60, 'Pisces': 95},
            'Sagittarius': {'Aries': 95, 'Taurus': 55, 'Gemini': 90, 'Cancer': 60, 'Leo': 95, 'Virgo': 60,
                            'Libra': 85, 'Scorpio': 65, 'Sagittarius': 85, 'Capricorn': 60, 'Aquarius': 90, 'Pisces': 70},
            'Capricorn': {'Aries': 60, 'Taurus': 95, 'Gemini': 55, 'Cancer': 85, 'Leo': 65, 'Virgo': 95,
                          'Libra': 70, 'Scorpio': 85, 'Sagittarius': 60, 'Capricorn': 90, 'Aquarius': 65, 'Pisces': 80},
            'Aquarius': {'Aries': 85, 'Taurus': 60, 'Gemini': 95, 'Cancer': 55, 'Leo': 90, 'Virgo': 65,
                         'Libra': 95, 'Scorpio': 60, 'Sagittarius': 90, 'Capricorn': 65, 'Aquarius': 80, 'Pisces': 75},
            'Pisces': {'Aries': 65, 'Taurus': 85, 'Gemini': 70, 'Cancer': 95, 'Leo': 70, 'Virgo': 80,
                       'Libra': 80, 'Scorpio': 95, 'Sagittarius': 70, 'Capricorn': 80, 'Aquarius': 75, 'Pisces': 85}
        }
        
        # Numerology meanings
        self.numerology_meanings = {
            1: "Leadership, Independence, Pioneer",
            2: "Cooperation, Sensitivity, Peacemaker", 
            3: "Creativity, Communication, Optimism",
            4: "Stability, Hard work, Practicality",
            5: "Freedom, Adventure, Versatility",
            6: "Nurturing, Responsibility, Healing",
            7: "Spirituality, Analysis, Mystery",
            8: "Ambition, Material success, Authority",
            9: "Humanitarian, Wisdom, Completion",
            11: "Intuition, Spiritual insight, Inspiration",
            22: "Master builder, Visionary, Practical idealist",
            33: "Master teacher, Healing, Service to humanity"
        }
        
        # Planets and houses
        self.planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Rahu', 'Ketu']
        self.houses = list(range(1, 13))
        
    def create_main_interface(self):
        """Create the main tabbed interface"""
        
        # Main title
        title_frame = tk.Frame(self.root, bg=self.bg_color)
        title_frame.pack(fill=tk.X, pady=10)
        
        title_label = tk.Label(title_frame, text="🌌 AstroGuide - Complete Astrology Prediction System", 
                               font=('Arial', 18, 'bold'), bg=self.bg_color, fg=self.fg_color)
        title_label.pack()
        
        # Theme toggle button
        theme_btn = tk.Button(title_frame, text="🌙 Toggle Theme", command=self.toggle_theme,
                              bg=self.button_color, fg='white', font=('Arial', 10))
        theme_btn.pack(side=tk.RIGHT, padx=20)
        
        # Color picker button
        color_btn = tk.Button(title_frame, text="🎨 Pick Color", command=self.pick_accent_color,
                              bg=self.button_color, fg='white', font=('Arial', 10))
        color_btn.pack(side=tk.RIGHT, padx=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create all tabs
        self.create_horoscope_tab()
        self.create_birth_chart_tab()
        self.create_numerology_tab()
        self.create_compatibility_tab()
        self.create_career_tab()
        self.create_health_tab()
        self.create_transit_tab()
        self.create_quiz_tab()
        self.create_profile_tab()
        
    def create_horoscope_tab(self):
        """Create daily horoscope tab"""
        
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🔮 Daily Horoscope")
        
        # Configure frame
        frame.configure(style='Custom.TFrame')
        
        # Input section
        input_frame = tk.Frame(frame, bg=self.bg_color)
        input_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(input_frame, text="Enter Your Details:", font=('Arial', 14, 'bold'),
                 bg=self.bg_color, fg=self.fg_color).pack(anchor=tk.W)
        
        # Name field
        tk.Label(input_frame, text="Name:", bg=self.bg_color, fg=self.fg_color).pack(anchor=tk.W, pady=(10,0))
        self.name_entry = tk.Entry(input_frame, width=30, font=('Arial', 10))
        self.name_entry.pack(anchor=tk.W, pady=5)
        
        # Date of birth
        tk.Label(input_frame, text="Date of Birth (DD/MM/YYYY):", bg=self.bg_color, fg=self.fg_color).pack(anchor=tk.W)
        self.dob_entry = tk.Entry(input_frame, width=30, font=('Arial', 10))
        self.dob_entry.pack(anchor=tk.W, pady=5)
        
        # Zodiac sign dropdown
        tk.Label(input_frame, text="Zodiac Sign:", bg=self.bg_color, fg=self.fg_color).pack(anchor=tk.W)
        self.zodiac_var = tk.StringVar()
        zodiac_combo = ttk.Combobox(input_frame, textvariable=self.zodiac_var, 
                                    values=list(self.zodiac_signs.keys()), width=27)
        zodiac_combo.pack(anchor=tk.W, pady=5)
        
        # Auto-detect button
        auto_btn = tk.Button(input_frame, text="🔍 Auto-Detect Sign", command=self.auto_detect_sign,
                             bg=self.button_color, fg='white', font=('Arial', 10))
        auto_btn.pack(anchor=tk.W, pady=10)
        
        # Get horoscope button
        get_btn = tk.Button(input_frame, text="✨ Get Today's Horoscope", command=self.get_horoscope,
                            bg=self.accent_color, fg='white', font=('Arial', 12, 'bold'))
        get_btn.pack(anchor=tk.W, pady=10)
        
        # Results section
        result_frame = tk.Frame(frame, bg=self.bg_color)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(result_frame, text="Your Daily Horoscope:", font=('Arial', 14, 'bold'),
                 bg=self.bg_color, fg=self.fg_color).pack(anchor=tk.W)
        
        self.horoscope_text = tk.Text(result_frame, height=15, width=80, wrap=tk.WORD,
                                      font=('Arial', 11), bg='#2d3748', fg='white')
        self.horoscope_text.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(result_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.horoscope_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.horoscope_text.yview)
        
    def create_birth_chart_tab(self):
        """Create birth chart tab"""
        
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🏠 Birth Chart")
        
        # Input section
        input_frame = tk.Frame(frame, bg=self.bg_color)
        input_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(input_frame, text="Birth Chart Calculator:", font=('Arial', 14, 'bold'),
                 bg=self.bg_color, fg=self.fg_color).pack(anchor=tk.W)
        
        # Birth details
        details_frame = tk.Frame(input_frame, bg=self.bg_color)
        details_frame.pack(fill=tk.X, pady=10)
        
        # Date
        tk.Label(details_frame, text="Date:", bg=self.bg_color, fg=self.fg_color).grid(row=0, column=0, sticky=tk.W)
        self.birth_date = tk.Entry(details_frame, width=15)
        self.birth_date.grid(row=0, column=1, padx=10)
        
        # Time
        tk.Label(details_frame, text="Time (HH:MM):", bg=self.bg_color, fg=self.fg_color).grid(row=0, column=2, sticky=tk.W)
        self.birth_time = tk.Entry(details_frame, width=15)
        self.birth_time.grid(row=0, column=3, padx=10)
        
        # Place
        tk.Label(details_frame, text="Place:", bg=self.bg_color, fg=self.fg_color).grid(row=1, column=0, sticky=tk.W, pady=(10,0))
        self.birth_place = tk.Entry(details_frame, width=30)
        self.birth_place.grid(row=1, column=1, columnspan=2, padx=10, pady=(10,0))
        
        # Generate chart button
        chart_btn = tk.Button(input_frame, text="🌟 Generate Birth Chart", command=self.generate_birth_chart,
                              bg=self.accent_color, fg='white', font=('Arial', 12, 'bold'))
        chart_btn.pack(anchor=tk.W, pady=15)
        
        # Chart display area
        self.chart_frame = tk.Frame(frame, bg=self.bg_color)
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
    def create_numerology_tab(self):
        """Create numerology tab"""
        
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🔢 Numerology")
        
        # Input section
        input_frame = tk.Frame(frame, bg=self.bg_color)
        input_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(input_frame, text="Numerology Calculator:", font=('Arial', 14, 'bold'),
                 bg=self.bg_color, fg=self.fg_color).pack(anchor=tk.W)
        
        # Full name
        tk.Label(input_frame, text="Full Name:", bg=self.bg_color, fg=self.fg_color).pack(anchor=tk.W, pady=(10,0))
        self.full_name = tk.Entry(input_frame, width=40, font=('Arial', 10))
        self.full_name.pack(anchor=tk.W, pady=5)
        
        # Birth date
        tk.Label(input_frame, text="Birth Date (DD/MM/YYYY):", bg=self.bg_color, fg=self.fg_color).pack(anchor=tk.W)
        self.num_birth_date = tk.Entry(input_frame, width=40, font=('Arial', 10))
        self.num_birth_date.pack(anchor=tk.W, pady=5)
        
        # Calculate button
        calc_btn = tk.Button(input_frame, text="🧮 Calculate Numbers", command=self.calculate_numerology,
                             bg=self.accent_color, fg='white', font=('Arial', 12, 'bold'))
        calc_btn.pack(anchor=tk.W, pady=15)
        
        # Results area
        self.numerology_result = tk.Text(frame, height=20, width=80, wrap=tk.WORD,
                                         font=('Arial', 11), bg='#2d3748', fg='white')
        self.numerology_result.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
    def create_compatibility_tab(self):
        """Create compatibility checker tab"""
        
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="❤️ Love Compatibility")
        
        # Input section
        input_frame = tk.Frame(frame, bg=self.bg_color)
        input_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(input_frame, text="Love Compatibility Checker:", font=('Arial', 14, 'bold'),
                 bg=self.bg_color, fg=self.fg_color).pack(anchor=tk.W)
        
        # Partner details
        partners_frame = tk.Frame(input_frame, bg=self.bg_color)
        partners_frame.pack(fill=tk.X, pady=15)
        
        # Person 1
        person1_frame = tk.Frame(partners_frame, bg=self.bg_color)
        person1_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Label(person1_frame, text="Person 1:", font=('Arial', 12, 'bold'),
                 bg=self.bg_color, fg=self.fg_color).pack()
        
        tk.Label(person1_frame, text="Name:", bg=self.bg_color, fg=self.fg_color).pack(anchor=tk.W)
        self.partner1_name = tk.Entry(person1_frame, width=20)
        self.partner1_name.pack(pady=5)
        
        tk.Label(person1_frame, text="Zodiac:", bg=self.bg_color, fg=self.fg_color).pack(anchor=tk.W)
        self.partner1_sign = ttk.Combobox(person1_frame, values=list(self.zodiac_signs.keys()), width=17)
        self.partner1_sign.pack(pady=5)
        
        # Person 2
        person2_frame = tk.Frame(partners_frame, bg=self.bg_color)
        person2_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Label(person2_frame, text="Person 2:", font=('Arial', 12, 'bold'),
                 bg=self.bg_color, fg=self.fg_color).pack()
        
        tk.Label(person2_frame, text="Name:", bg=self.bg_color, fg=self.fg_color).pack(anchor=tk.W)
        self.partner2_name = tk.Entry(person2_frame, width=20)
        self.partner2_name.pack(pady=5)
        
        tk.Label(person2_frame, text="Zodiac:", bg=self.bg_color, fg=self.fg_color).pack(anchor=tk.W)
        self.partner2_sign = ttk.Combobox(person2_frame, values=list(self.zodiac_signs.keys()), width=17)
        self.partner2_sign.pack(pady=5)
        
        # Check compatibility button
        compat_btn = tk.Button(input_frame, text="💕 Check Compatibility", command=self.check_compatibility,
                               bg=self.accent_color, fg='white', font=('Arial', 12, 'bold'))
        compat_btn.pack(pady=15)
        
        # Results area
        self.compatibility_result = tk.Text(frame, height=15, width=80, wrap=tk.WORD,
                                            font=('Arial', 11), bg='#2d3748', fg='white')
        self.compatibility_result.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
    def create_career_tab(self):
        """Create career forecast tab"""
        
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="💼 Career & Wealth")
        
        # Input section
        input_frame = tk.Frame(frame, bg=self.bg_color)
        input_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(input_frame, text="Career & Wealth Forecast:", font=('Arial', 14, 'bold'),
                 bg=self.bg_color, fg=self.fg_color).pack(anchor=tk.W)
        
        # Zodiac selection
        tk.Label(input_frame, text="Your Zodiac Sign:", bg=self.bg_color, fg=self.fg_color).pack(anchor=tk.W, pady=(10,0))
        self.career_zodiac = ttk.Combobox(input_frame, values=list(self.zodiac_signs.keys()), width=30)
        self.career_zodiac.pack(anchor=tk.W, pady=5)
        
        # Current situation
        tk.Label(input_frame, text="Current Career Situation:", bg=self.bg_color, fg=self.fg_color).pack(anchor=tk.W)
        self.career_situation = ttk.Combobox(input_frame, values=[
            "Student", "Job Seeker", "Employee", "Manager", "Business Owner", "Freelancer", "Retired"
        ], width=30)
        self.career_situation.pack(anchor=tk.W, pady=5)
        
        # Get forecast button
        forecast_btn = tk.Button(input_frame, text="📊 Get Career Forecast", command=self.get_career_forecast,
                                 bg=self.accent_color, fg='white', font=('Arial', 12, 'bold'))
        forecast_btn.pack(anchor=tk.W, pady=15)
        
        # Results area
        self.career_result = tk.Text(frame, height=18, width=80, wrap=tk.WORD,
                                     font=('Arial', 11), bg='#2d3748', fg='white')
        self.career_result.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
    def create_health_tab(self):
        """Create health & wellness tab"""
        
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🏥 Health & Wellness")
        
        # Input section
        input_frame = tk.Frame(frame, bg=self.bg_color)
        input_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(input_frame, text="Health & Wellness Guide:", font=('Arial', 14, 'bold'),
                 bg=self.bg_color, fg=self.fg_color).pack(anchor=tk.W)
        
        # Zodiac selection
        tk.Label(input_frame, text="Your Zodiac Sign:", bg=self.bg_color, fg=self.fg_color).pack(anchor=tk.W, pady=(10,0))
        self.health_zodiac = ttk.Combobox(input_frame, values=list(self.zodiac_signs.keys()), width=30)
        self.health_zodiac.pack(anchor=tk.W, pady=5)
        
        # Health focus
        tk.Label(input_frame, text="Focus Area:", bg=self.bg_color, fg=self.fg_color).pack(anchor=tk.W)
        self.health_focus = ttk.Combobox(input_frame, values=[
            "General Wellness", "Physical Fitness", "Mental Health", "Diet & Nutrition", 
            "Sleep & Rest", "Stress Management", "Energy Levels"
        ], width=30)
        self.health_focus.pack(anchor=tk.W, pady=5)
        
        # Get advice button
        health_btn = tk.Button(input_frame, text="🌿 Get Health Advice", command=self.get_health_advice,
                               bg=self.accent_color, fg='white', font=('Arial', 12, 'bold'))
        health_btn.pack(anchor=tk.W, pady=15)
        
        # Results area
        self.health_result = tk.Text(frame, height=18, width=80, wrap=tk.WORD,
                                     font=('Arial', 11), bg='#2d3748', fg='white')
        self.health_result.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
    def create_transit_tab(self):
        """Create planetary transit tab"""
        
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🌠 Planetary Transits")
        
        # Input section
        input_frame = tk.Frame(frame, bg=self.bg_color)
        input_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(input_frame, text="Planetary Transit Alerts:", font=('Arial', 14, 'bold'),
                 bg=self.bg_color, fg=self.fg_color).pack(anchor=tk.W)
        
        # Date selection
        tk.Label(input_frame, text="Select Date:", bg=self.bg_color, fg=self.fg_color).pack(anchor=tk.W, pady=(10,0))
        self.transit_date = tk.Entry(input_frame, width=30, font=('Arial', 10))
        self.transit_date.insert(0, datetime.date.today().strftime("%d/%m/%Y"))
        self.transit_date.pack(anchor=tk.W, pady=5)
        
        # Your zodiac for personalized effects
        tk.Label(input_frame, text="Your Zodiac Sign:", bg=self.bg_color, fg=self.fg_color).pack(anchor=tk.W)
        self.transit_zodiac = ttk.Combobox(input_frame, values=list(self.zodiac_signs.keys()), width=27)
        self.transit_zodiac.pack(anchor=tk.W, pady=5)
        
        # Get transits button
        transit_btn = tk.Button(input_frame, text="🔭 Get Transit Report", command=self.get_transit_report,
                                bg=self.accent_color, fg='white', font=('Arial', 12, 'bold'))
        transit_btn.pack(anchor=tk.W, pady=15)
        
        # Results area
        self.transit_result = tk.Text(frame, height=18, width=80, wrap=tk.WORD,
                                      font=('Arial', 11), bg='#2d3748', fg='white')
        self.transit_result.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
    def create_quiz_tab(self):
        """Create astrology quiz tab"""
        
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🎯 Astrology Quiz")
        
        self.quiz_frame = tk.Frame(frame, bg=self.bg_color)
        self.quiz_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(self.quiz_frame, text="Astrology Knowledge Quiz", font=('Arial', 16, 'bold'),
                 bg=self.bg_color, fg=self.fg_color).pack(pady=20)
        
        # Quiz questions
        self.quiz_questions = [
            {
                "question": "Which planet rules Aries?",
                "options": ["Mars", "Venus", "Mercury", "Jupiter"],
                "correct": "Mars"
            },
            {
                "question": "What element is associated with Scorpio?",
                "options": ["Fire", "Earth", "Air", "Water"],
                "correct": "Water"
            },
            {
                "question": "Which zodiac sign is represented by twins?",
                "options": ["Pisces", "Gemini", "Libra", "Sagittarius"],
                "correct": "Gemini"
            },
            {
                "question": "What is the ruling planet of Taurus?",
                "options": ["Mars", "Venus", "Moon", "Sun"],
                "correct": "Venus"
            },
            {
                "question": "Which house represents career in astrology?",
                "options": ["7th House", "10th House", "4th House", "12th House"],
                "correct": "10th House"
            }
        ]
        
        self.current_question = 0
        self.quiz_score = 0
        self.quiz_started = False
        
        # Start quiz button
        self.start_quiz_btn = tk.Button(self.quiz_frame, text="🎮 Start Quiz", command=self.start_quiz,
                                        bg=self.accent_color, fg='white', font=('Arial', 14, 'bold'))
        self.start_quiz_btn.pack(pady=20)
        
        # Quiz content area
        self.quiz_content = tk.Frame(self.quiz_frame, bg=self.bg_color)
        
    def create_profile_tab(self):
        """Create user profile management tab"""
        
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="👤 Profile Manager")
        
        # Profile management
        profile_frame = tk.Frame(frame, bg=self.bg_color)
        profile_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(profile_frame, text="User Profile Manager", font=('Arial', 16, 'bold'),
                 bg=self.bg_color, fg=self.fg_color).pack(pady=10)
        
        # Profile form
        form_frame = tk.Frame(profile_frame, bg=self.bg_color)
        form_frame.pack(fill=tk.X, pady=20)
        
        # Left column
        left_col = tk.Frame(form_frame, bg=self.bg_color)
        left_col.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(left_col, text="Full Name:", bg=self.bg_color, fg=self.fg_color).pack(anchor=tk.W)
        self.profile_name = tk.Entry(left_col, width=30, font=('Arial', 10))
        self.profile_name.pack(anchor=tk.W, pady=5)
        
        tk.Label(left_col, text="Birth Date:", bg=self.bg_color, fg=self.fg_color).pack(anchor=tk.W)
        self.profile_birth_date = tk.Entry(left_col, width=30, font=('Arial', 10))
        self.profile_birth_date.pack(anchor=tk.W, pady=5)
        
        tk.Label(left_col, text="Birth Time:", bg=self.bg_color, fg=self.fg_color).pack(anchor=tk.W)
        self.profile_birth_time = tk.Entry(left_col, width=30, font=('Arial', 10))
        self.profile_birth_time.pack(anchor=tk.W, pady=5)
        
        # Right column
        right_col = tk.Frame(form_frame, bg=self.bg_color)
        right_col.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        tk.Label(right_col, text="Birth Place:", bg=self.bg_color, fg=self.fg_color).pack(anchor=tk.W)
        self.profile_birth_place = tk.Entry(right_col, width=30, font=('Arial', 10))
        self.profile_birth_place.pack(anchor=tk.W, pady=5)
        
        tk.Label(right_col, text="Zodiac Sign:", bg=self.bg_color, fg=self.fg_color).pack(anchor=tk.W)
        self.profile_zodiac = ttk.Combobox(right_col, values=list(self.zodiac_signs.keys()), width=27)
        self.profile_zodiac.pack(anchor=tk.W, pady=5)
        
        # Buttons
        btn_frame = tk.Frame(profile_frame, bg=self.bg_color)
        btn_frame.pack(fill=tk.X, pady=20)
        
        save_btn = tk.Button(btn_frame, text="💾 Save Profile", command=self.save_profile,
                             bg=self.accent_color, fg='white', font=('Arial', 11, 'bold'))
        save_btn.pack(side=tk.LEFT, padx=10)
        
        load_btn = tk.Button(btn_frame, text="📂 Load Profile", command=self.load_profile,
                             bg=self.button_color, fg='white', font=('Arial', 11, 'bold'))
        load_btn.pack(side=tk.LEFT, padx=10)
        
        export_btn = tk.Button(btn_frame, text="📄 Export Report", command=self.export_report,
                               bg='#38a169', fg='white', font=('Arial', 11, 'bold'))
        export_btn.pack(side=tk.LEFT, padx=10)
        
        # Saved profiles display
        tk.Label(profile_frame, text="Saved Profiles:", font=('Arial', 12, 'bold'),
                 bg=self.bg_color, fg=self.fg_color).pack(anchor=tk.W, pady=(20,5))
        
        self.profile_listbox = tk.Listbox(profile_frame, height=8, bg='#2d3748', fg='white', 
                                          font=('Arial', 10))
        self.profile_listbox.pack(fill=tk.X, pady=10)
        
        # Method implementations
        
    def auto_detect_sign(self):
        """Auto-detect zodiac sign from birth date"""
        try:
            dob = self.dob_entry.get()
            if not dob:
                messagebox.showwarning("Warning", "Please enter your date of birth first!")
                return
            
            day, month, year = map(int, dob.split('/'))
            
            for sign, (start_month, start_day, end_month, end_day) in self.zodiac_signs.items():
                if (month == start_month and day >= start_day) or (month == end_month and day <= end_day):
                    self.zodiac_var.set(sign)
                    messagebox.showinfo("Success", f"Your zodiac sign is {sign}! ✨")
                    return
                    
        except Exception as e:
            messagebox.showerror("Error", "Please enter date in DD/MM/YYYY format!")
    
    def get_horoscope(self):
        """Generate daily horoscope"""
        name = self.name_entry.get()
        zodiac = self.zodiac_var.get()
        
        if not name or not zodiac:
            messagebox.showwarning("Warning", "Please fill all fields!")
            return
        
        # Get random prediction for the zodiac sign
        prediction = random.choice(self.horoscope_predictions[zodiac])
        
        # Generate additional insights
        lucky_number = random.randint(1, 99)
        lucky_color = random.choice(['Blue', 'Red', 'Green', 'Purple', 'Gold', 'Silver', 'Orange'])
        mood = random.choice(['Energetic', 'Peaceful', 'Adventurous', 'Romantic', 'Focused', 'Creative'])
        
        today = datetime.date.today().strftime("%B %d, %Y")
        
        horoscope_text = f"""
🌟 DAILY HOROSCOPE FOR {name.upper()} 🌟
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 Date: {today}
♈ Zodiac Sign: {zodiac}

🔮 Today's Prediction:
{prediction}

✨ Personal Insights:
• Lucky Number: {lucky_number}
• Lucky Color: {lucky_color}
• Today's Mood: {mood}
• Best Time: {random.choice(['Morning', 'Afternoon', 'Evening'])}

🌙 Cosmic Advice:
{random.choice([
    "Trust your intuition today - it will guide you well.",
    "Focus on positive relationships and connections.",
    "Take time for self-care and reflection.",
    "Embrace new opportunities that come your way.",
    "Practice gratitude for the blessings in your life."
])}

💫 Affirmation for Today:
"I am aligned with the cosmic energies and open to abundance."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        self.horoscope_text.delete(1.0, tk.END)
        self.horoscope_text.insert(1.0, horoscope_text)
    
    def generate_birth_chart(self):
        """Generate birth chart visualization"""
        date = self.birth_date.get()
        time = self.birth_time.get()
        place = self.birth_place.get()
        
        if not all([date, time, place]):
            messagebox.showwarning("Warning", "Please fill all birth details!")
            return
        
        # Clear previous chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        # Create canvas for chart
        canvas = tk.Canvas(self.chart_frame, width=500, height=500, bg='#1a202c')
        canvas.pack(pady=20)
        
        # Draw birth chart circle
        center_x, center_y = 250, 250
        radius = 200
        
        # Outer circle
        canvas.create_oval(center_x-radius, center_y-radius, 
                           center_x+radius, center_y+radius, 
                           outline='white', width=3)
        
        # Draw houses (12 divisions)
        for i in range(12):
            angle = i * 30 * math.pi / 180
            x1 = center_x + (radius-20) * math.cos(angle)
            y1 = center_y + (radius-20) * math.sin(angle)
            x2 = center_x + radius * math.cos(angle)
            y2 = center_y + radius * math.sin(angle)
            
            canvas.create_line(x1, y1, x2, y2, fill='white', width=2)
            
            # House numbers
            house_x = center_x + (radius-40) * math.cos(angle + 15*math.pi/180)
            house_y = center_y + (radius-40) * math.sin(angle + 15*math.pi/180)
            canvas.create_text(house_x, house_y, text=str(i+1), fill='yellow', font=('Arial', 12, 'bold'))
        
        # Simulate planetary positions
        planets_colors = {
            'Sun': '#FFD700', 'Moon': '#C0C0C0', 'Mercury': '#FFA500',
            'Venus': '#98FB98', 'Mars': '#FF4500', 'Jupiter': '#4169E1',
            'Saturn': '#8B4513', 'Rahu': '#800080', 'Ketu': '#FF1493'
        }
        
        # Place planets randomly in houses
        for i, planet in enumerate(self.planets):
            house = random.randint(0, 11)
            angle = house * 30 * math.pi / 180 + random.uniform(-10, 10) * math.pi / 180
            
            planet_x = center_x + (radius-80) * math.cos(angle)
            planet_y = center_y + (radius-80) * math.sin(angle)
            
            canvas.create_oval(planet_x-8, planet_y-8, planet_x+8, planet_y+8,
                               fill=planets_colors[planet], outline='white')
            canvas.create_text(planet_x, planet_y-20, text=planet[:3], 
                               fill='white', font=('Arial', 8, 'bold'))
        
        # Chart information
        info_text = f"""
Birth Chart Generated for: {place}
Date: {date} | Time: {time}

🌟 Planetary Positions (Simulated):
"""
        
        for planet in self.planets:
            house = random.randint(1, 12)
            sign = random.choice(list(self.zodiac_signs.keys()))
            info_text += f"• {planet}: {house}th House ({sign})\n"
        
        info_label = tk.Text(self.chart_frame, height=15, width=60, wrap=tk.WORD,
                             font=('Arial', 10), bg='#2d3748', fg='white')
        info_label.pack(side=tk.RIGHT, padx=20)
        info_label.insert(1.0, info_text)
    
    def calculate_numerology(self):
        """Calculate numerology numbers"""
        name = self.full_name.get().strip().upper()
        birth_date = self.num_birth_date.get().strip()
        
        if not name or not birth_date:
            messagebox.showwarning("Warning", "Please fill all fields!")
            return
        
        try:
            # Calculate Life Path Number
            day, month, year = map(int, birth_date.split('/'))
            life_path = self.reduce_number(day + month + year)
            
            # Calculate Destiny Number (from full name)
            letter_values = {
                'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
                'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 6, 'P': 7, 'Q': 8, 'R': 9,
                'S': 1, 'T': 2, 'U': 3, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8
            }
            
            destiny_sum = sum(letter_values.get(char, 0) for char in name if char.isalpha())
            destiny_number = self.reduce_number(destiny_sum)
            
            # Calculate Soul Urge Number (from vowels)
            vowels = 'AEIOU'
            soul_urge_sum = sum(letter_values.get(char, 0) for char in name if char in vowels)
            soul_urge = self.reduce_number(soul_urge_sum)
            
            # Generate report
            report = f"""
🔢 NUMEROLOGY REPORT FOR {name} 🔢
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Core Numbers:

🌟 Life Path Number: {life_path}
Meaning: {self.numerology_meanings.get(life_path, 'Special spiritual significance')}

🎯 Destiny Number: {destiny_number}
Meaning: {self.numerology_meanings.get(destiny_number, 'Special spiritual significance')}

💫 Soul Urge Number: {soul_urge}
Meaning: {self.numerology_meanings.get(soul_urge, 'Special spiritual significance')}

🔍 Detailed Interpretations:

Life Path {life_path}:
{self.get_life_path_meaning(life_path)}

Destiny {destiny_number}:
{self.get_destiny_meaning(destiny_number)}

Soul Urge {soul_urge}:
{self.get_soul_urge_meaning(soul_urge)}

🎲 Lucky Numbers: {', '.join(str(random.randint(1, 9)) for _ in range(5))}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            """
            
            self.numerology_result.delete(1.0, tk.END)
            self.numerology_result.insert(1.0, report)
            
        except Exception as e:
            messagebox.showerror("Error", "Please enter date in DD/MM/YYYY format!")
    
    def reduce_number(self, num):
        """Reduce number to single digit or master number"""
        while num > 9 and num not in [11, 22, 33]:
            num = sum(int(digit) for digit in str(num))
        return num
    
    def get_life_path_meaning(self, num):
        meanings = {
            1: "You are a natural leader with strong independence. Your path involves pioneering new ideas and taking initiative.",
            2: "You are a natural peacemaker and diplomat. Your path involves cooperation, partnership, and bringing harmony.",
            3: "You are creative and expressive. Your path involves communication, creativity, and bringing joy to others.",
            4: "You are practical and hardworking. Your path involves building solid foundations and bringing order.",
            5: "You seek freedom and adventure. Your path involves exploration, change, and bringing new experiences.",
            6: "You are nurturing and responsible. Your path involves caring for others and bringing healing to the world.",
            7: "You are analytical and spiritual. Your path involves seeking truth, wisdom, and deeper understanding.",
            8: "You are ambitious and material-focused. Your path involves achieving success and bringing practical results.",
            9: "You are humanitarian and wise. Your path involves serving humanity and bringing completion to projects.",
            11: "You are intuitive and inspirational. Your path involves bringing spiritual insights to others.",
            22: "You are a master builder. Your path involves turning dreams into reality on a large scale.",
            33: "You are a master teacher. Your path involves healing and uplifting humanity through service."
        }
        return meanings.get(num, "You have a special spiritual mission in this lifetime.")
    
    def get_destiny_meaning(self, num):
        meanings = {
            1: "Your destiny is to lead and pioneer. You're meant to start new ventures and inspire others to follow.",
            2: "Your destiny is to cooperate and support. You're meant to work behind the scenes and help others succeed.",
            3: "Your destiny is to create and communicate. You're meant to express yourself and bring beauty to the world.",
            4: "Your destiny is to build and organize. You're meant to create lasting structures and bring stability.",
            5: "Your destiny is to explore and liberate. You're meant to break free from restrictions and inspire change.",
            6: "Your destiny is to nurture and heal. You're meant to care for others and create harmony in relationships.",
            7: "Your destiny is to seek and teach. You're meant to uncover hidden truths and share spiritual wisdom.",
            8: "Your destiny is to achieve and prosper. You're meant to attain material success and financial abundance.",
            9: "Your destiny is to serve and complete. You're meant to help humanity and bring projects to fruition."
        }
        return meanings.get(num, "Your destiny holds special significance beyond traditional interpretations.")
    
    def get_soul_urge_meaning(self, num):
        meanings = {
            1: "Your soul urges you toward independence and leadership. You crave recognition and want to be first.",
            2: "Your soul urges you toward peace and partnership. You crave harmony and emotional connections.",
            3: "Your soul urges you toward self-expression and creativity. You crave artistic outlets and communication.",
            4: "Your soul urges you toward security and order. You crave stability and practical achievements.",
            5: "Your soul urges you toward freedom and adventure. You crave variety and new experiences.",
            6: "Your soul urges you toward love and service. You crave deep relationships and family connections.",
            7: "Your soul urges you toward knowledge and spirituality. You crave understanding and inner wisdom.",
            8: "Your soul urges you toward success and recognition. You crave material achievement and authority.",
            9: "Your soul urges you toward compassion and service. You crave opportunities to help humanity."
        }
        return meanings.get(num, "Your soul has a unique calling that transcends ordinary desires.")
    
    def check_compatibility(self):
        """Check zodiac compatibility"""
        name1 = self.partner1_name.get()
        sign1 = self.partner1_sign.get()
        name2 = self.partner2_name.get()
        sign2 = self.partner2_sign.get()
        
        if not all([name1, sign1, name2, sign2]):
            messagebox.showwarning("Warning", "Please fill all fields!")
            return
        
        # Get compatibility percentage
        compatibility = self.compatibility_matrix[sign1][sign2]
        
        # Generate compatibility description
        if compatibility >= 90:
            level = "PERFECT MATCH! 💕"
            description = "You two are made for each other! Your signs complement each other beautifully."
        elif compatibility >= 80:
            level = "Excellent Match! ❤️"
            description = "You have wonderful compatibility with great potential for lasting love."
        elif compatibility >= 70:
            level = "Good Match! 💖"
            description = "You complement each other well with minor challenges that can strengthen your bond."
        elif compatibility >= 60:
            level = "Fair Match 💛"
            description = "You can work well together with understanding and compromise from both sides."
        else:
            level = "Challenging Match 💙"
            description = "While challenging, your differences can lead to growth and learning for both."
        
        # Detailed compatibility aspects
        aspects = self.get_compatibility_aspects(sign1, sign2)
        
        report = f"""
💕 LOVE COMPATIBILITY REPORT 💕
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👫 Partners: {name1} ({sign1}) & {name2} ({sign2})

🎯 Compatibility Score: {compatibility}% - {level}

💝 Overall Assessment:
{description}

🔍 Detailed Analysis:

{aspects}

💡 Relationship Tips:
• Focus on your shared interests and values
• Communicate openly about your differences
• Give each other space to grow individually
• Celebrate what makes each of you unique
• Practice patience and understanding

🌟 Lucky Days for Your Relationship:
• {random.choice(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])}s and {random.choice(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])}s

💫 Best Activities Together:
• {random.choice(['Romantic dinners', 'Adventure trips', 'Art galleries', 'Nature walks', 'Home cooking', 'Dancing', 'Reading together'])}
• {random.choice(['Yoga classes', 'Beach visits', 'Mountain hiking', 'Movie nights', 'Gardening', 'Music concerts', 'Stargazing'])}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        self.compatibility_result.delete(1.0, tk.END)
        self.compatibility_result.insert(1.0, report)
    
    def get_compatibility_aspects(self, sign1, sign2):
        """Get detailed compatibility aspects"""
        # Element compatibility
        elements = {
            'Aries': 'Fire', 'Leo': 'Fire', 'Sagittarius': 'Fire',
            'Taurus': 'Earth', 'Virgo': 'Earth', 'Capricorn': 'Earth',
            'Gemini': 'Air', 'Libra': 'Air', 'Aquarius': 'Air',
            'Cancer': 'Water', 'Scorpio': 'Water', 'Pisces': 'Water'
        }
        
        element1 = elements[sign1]
        element2 = elements[sign2]
        
        if element1 == element2:
            element_compat = "You share the same element, creating natural understanding and similar approaches to life."
        elif (element1 in ['Fire', 'Air'] and element2 in ['Fire', 'Air']) or \
             (element1 in ['Earth', 'Water'] and element2 in ['Earth', 'Water']):
            element_compat = "Your elements complement each other well, creating balance and mutual support."
        else:
            element_compat = "Your different elements can create dynamic energy, though it may require more understanding."
        
        aspects = f"""
🌊 Elemental Harmony ({element1} & {element2}):
{element_compat}

💭 Communication Style:
{random.choice([
    "You communicate on the same wavelength, making understanding natural.",
    "Your different communication styles can lead to interesting conversations.",
    "You may need to work on expressing yourselves clearly to each other.",
    "Your communication flows well with occasional misunderstandings to work through."
])}

🎭 Emotional Connection:
{random.choice([
    "Deep emotional resonance creates a strong bond between you.",
    "Your emotional needs complement each other beautifully.",
    "You help each other grow emotionally in positive ways.",
    "Balance is key to maintaining emotional harmony."
])}

🌟 Shared Values:
{random.choice([
    "Your core values align, creating a solid foundation for your relationship.",
    "Different values can lead to interesting perspectives and growth.",
    "You share important life goals that bring you together.",
    "Learning from each other's values strengthens your bond."
])}
        """
        return aspects
    
    def get_career_forecast(self):
        """Generate career and wealth forecast"""
        zodiac = self.career_zodiac.get()
        situation = self.career_situation.get()

        if not zodiac or not situation:
            messagebox.showwarning("Warning", "Please select your zodiac sign and career situation!")
            return

        career_advice = {
            'Aries': "Leadership roles suit you best. Consider management, entrepreneurship, or pioneering fields.",
            'Taurus': "Stable careers in finance, real estate, or luxury goods align with your nature.",
            'Gemini': "Communication-based careers like journalism, sales, or teaching are ideal.",
            'Cancer': "Nurturing roles in healthcare, childcare, or hospitality fulfill you.",
            'Leo': "Creative industries, entertainment, or public roles showcase your talents.",
            'Virgo': "Detail-oriented careers in analysis, healthcare, or organization suit you.",
            'Libra': "Diplomatic roles in law, design, or counseling utilize your skills.",
            'Scorpio': "Investigative careers in research, psychology, or detective work appeal.",
            'Sagittarius': "Travel-related careers, education, or publishing match your spirit.",
            'Capricorn': "Traditional careers in business, government, or engineering bring success.",
            'Aquarius': "Innovative careers in technology, science, or social reform fit your vision.",
            'Pisces': "Creative and healing roles in arts, spirituality, or therapy fulfill your soul."
        }

        advice = career_advice[zodiac]
        wealth_tip = random.choice([
            "Invest in long-term goals for steady growth.",
            "Focus on building multiple income streams.",
            "A partnership may bring financial opportunities.",
            "Stay disciplined with budgeting for wealth security."
        ])

        report = f"""
💼 CAREER & WEALTH FORECAST 💼
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

♈ Zodiac Sign: {zodiac}
🎓 Current Status: {situation}

📊 Career Advice:
{advice}

💰 Wealth Insight:
{wealth_tip}

🌟 Lucky Day for Career Moves: {random.choice(['Monday','Wednesday','Friday'])}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        self.career_result.delete(1.0, tk.END)
        self.career_result.insert(1.0, report)

    def get_health_advice(self):
        zodiac = self.health_zodiac.get()
        focus = self.health_focus.get()

        if not zodiac or not focus:
            messagebox.showwarning("Warning", "Please select your zodiac sign and focus area!")
            return

        focus_tips = {
            "General Wellness": "Maintain balance with rest, nutrition, and regular activity.",
            "Physical Fitness": "Consistency in workouts is more important than intensity.",
            "Mental Health": "Practice mindfulness and give yourself mental breaks.",
            "Diet & Nutrition": "Focus on whole foods and hydration for vitality.",
            "Sleep & Rest": "Create a routine and limit screens before bedtime.",
            "Stress Management": "Deep breathing and meditation help reduce stress.",
            "Energy Levels": "Balance work with rest and avoid overexertion."
        }

        report = f"""
🏥 HEALTH & WELLNESS REPORT 🏥
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

♈ Zodiac Sign: {zodiac}
⚕️ Focus Area: {focus}

💡 Health Tip:
{focus_tips[focus]}

🌿 Bonus Advice:
{random.choice(['Drink herbal tea for calmness.','Stretch every morning.','Take mindful walks in nature.','Keep a gratitude journal.'])}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        self.health_result.delete(1.0, tk.END)
        self.health_result.insert(1.0, report)

    def get_transit_report(self):
        date = self.transit_date.get()
        zodiac = self.transit_zodiac.get()

        if not date or not zodiac:
            messagebox.showwarning("Warning", "Please enter date and zodiac sign!")
            return

        planets = random.sample(self.planets, 3)
        effects = [
            "Brings opportunities for growth.",
            "Time to release old patterns.",
            "Enhances creativity and passion.",
            "Focus on discipline and patience.",
            "Strengthens intuition and dreams."
        ]

        report = f"""
🌠 PLANETARY TRANSIT REPORT 🌠
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 Date: {date}
♈ Zodiac Sign: {zodiac}

🔭 Planetary Influences:
"""
        for planet in planets:
            report += f"• {planet}: {random.choice(effects)}\n"

        report += f"""

✨ Cosmic Guidance:
{random.choice(['This is a great time for self-reflection.','Embrace new beginnings with courage.','Stay grounded while changes unfold.'])}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """

        self.transit_result.delete(1.0, tk.END)
        self.transit_result.insert(1.0, report)

    # Quiz System
    def start_quiz(self):
        self.quiz_started = True
        self.quiz_score = 0
        self.current_question = 0
        self.start_quiz_btn.pack_forget()
        self.quiz_content.pack(fill=tk.BOTH, expand=True)
        self.show_question()

    def show_question(self):
        for widget in self.quiz_content.winfo_children():
            widget.destroy()

        if self.current_question < len(self.quiz_questions):
            q = self.quiz_questions[self.current_question]
            tk.Label(self.quiz_content, text=q["question"], font=("Arial",14,"bold"),
                     bg=self.bg_color, fg=self.fg_color).pack(pady=10)

            self.quiz_answer = tk.StringVar()
            for opt in q["options"]:
                tk.Radiobutton(self.quiz_content, text=opt, variable=self.quiz_answer, value=opt,
                               bg=self.bg_color, fg=self.fg_color, selectcolor=self.accent_color).pack(anchor=tk.W)

            tk.Button(self.quiz_content, text="Next", command=self.next_question,
                      bg=self.accent_color, fg="white", font=("Arial", 12)).pack(pady=20)
        else:
            self.show_results()

    def next_question(self):
        answer = self.quiz_answer.get()
        if answer == self.quiz_questions[self.current_question]["correct"]:
            self.quiz_score += 1
        self.current_question += 1
        self.show_question()

    def show_results(self):
        for widget in self.quiz_content.winfo_children():
            widget.destroy()
        tk.Label(self.quiz_content, text=f"Your Score: {self.quiz_score}/{len(self.quiz_questions)}", 
                 font=("Arial",16,"bold"), bg=self.bg_color, fg=self.fg_color).pack(pady=20)

    # Profile Management
    def save_profile(self):
        profile = {
            "name": self.profile_name.get(),
            "birth_date": self.profile_birth_date.get(),
            "birth_time": self.profile_birth_time.get(),
            "birth_place": self.profile_birth_place.get(),
            "zodiac": self.profile_zodiac.get()
        }
        if not profile["name"]:
            messagebox.showwarning("Warning", "Please enter at least a name!")
            return
        self.user_profiles[profile["name"]] = profile
        self.profile_listbox.insert(tk.END, profile["name"])
        messagebox.showinfo("Saved", f"Profile for {profile['name']} saved!")

    def load_profile(self):
        selection = self.profile_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Select a profile to load!")
            return
        name = self.profile_listbox.get(selection)
        profile = self.user_profiles[name]
        self.profile_name.delete(0, tk.END)
        self.profile_name.insert(0, profile["name"])
        self.profile_birth_date.delete(0, tk.END)
        self.profile_birth_date.insert(0, profile["birth_date"])
        self.profile_birth_time.delete(0, tk.END)
        self.profile_birth_time.insert(0, profile["birth_time"])
        self.profile_birth_place.delete(0, tk.END)
        self.profile_birth_place.insert(0, profile["birth_place"])
        self.profile_zodiac.set(profile["zodiac"])

    def export_report(self):
        selection = self.profile_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Select a profile to export!")
            return
        name = self.profile_listbox.get(selection)
        profile = self.user_profiles[name]
        file = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files","*.txt")])
        if file:
            with open(file,"w") as f:
                f.write(json.dumps(profile, indent=4))
            messagebox.showinfo("Exported", f"Profile exported to {file}")

    # Theme and Color
    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.bg_color = "#0f0f23"
            self.fg_color = "white"
        else:
            self.bg_color = "#ffffff"
            self.fg_color = "black"
        self.root.configure(bg=self.bg_color)

    def pick_accent_color(self):
        color = colorchooser.askcolor(title="Pick Accent Color")
        if color[1]:
            self.accent_color = color[1]

    def start_color_shift(self):
        # Simple placeholder for animation
        self.root.after(5000, self.start_color_shift)

if __name__ == "__main__":
    app = AstroGuide()
    app.root.mainloop()
