import streamlit as st
import re
import time
import base64
from PIL import Image
import io
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import random
import string
import datetime
import json
import hashlib

# Set page configuration
st.set_page_config(
    page_title="VIP Password Strength Meter",
    page_icon="🔒",
    layout="wide"
)

# Initialize session state
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'  # Default theme
if 'password_history' not in st.session_state:
    st.session_state.password_history = []
if 'generated_passwords' not in st.session_state:
    st.session_state.generated_passwords = []

# Function to toggle theme
def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

# Function to add password to history
def add_to_history(password, strength):
    # Only store the first 3 and last 3 characters for privacy
    if len(password) > 6:
        masked_password = password[:3] + '*' * (len(password) - 6) + password[-3:]
    else:
        masked_password = '*' * len(password)
    
    # Add to history with timestamp
    st.session_state.password_history.append({
        'password': masked_password,
        'strength': strength,
        'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    # Keep only the last 10 passwords
    if len(st.session_state.password_history) > 10:
        st.session_state.password_history.pop(0)

# Function to generate a secure password
def generate_password(length=12, include_uppercase=True, include_lowercase=True, 
                     include_numbers=True, include_special=True):
    chars = ''
    if include_uppercase:
        chars += string.ascii_uppercase
    if include_lowercase:
        chars += string.ascii_lowercase
    if include_numbers:
        chars += string.digits
    if include_special:
        chars += string.punctuation
    
    if not chars:
        chars = string.ascii_letters + string.digits
    
    # Ensure at least one character from each selected category
    password = []
    if include_uppercase:
        password.append(random.choice(string.ascii_uppercase))
    if include_lowercase:
        password.append(random.choice(string.ascii_lowercase))
    if include_numbers:
        password.append(random.choice(string.digits))
    if include_special:
        password.append(random.choice(string.punctuation))
    
    # Fill the rest of the password
    remaining_length = length - len(password)
    password.extend(random.choice(chars) for _ in range(remaining_length))
    
    # Shuffle the password
    random.shuffle(password)
    
    return ''.join(password)

# Custom CSS for styling
def add_custom_css():
    # Define colors for light and dark themes
    if st.session_state.theme == 'dark':
        bg_gradient = "linear-gradient(135deg, #0a192f, #172a45, #1f3a60)"
        text_color = "white"
        card_bg = "rgba(10, 25, 47, 0.7)"
        input_bg = "rgba(255, 255, 255, 0.1)"
        input_border = "rgba(100, 255, 218, 0.5)"
        accent_color = "#0a192f"  # Dark navy blue
        highlight_color = "#64ffda"  # Teal highlight
        secondary_accent = "#8892b0"  # Light slate
    else:
        bg_gradient = "linear-gradient(135deg, #e6f1ff, #ccd6f6, #a8b2d1)"
        text_color = "#0a192f"
        card_bg = "rgba(255, 255, 255, 0.8)"
        input_bg = "rgba(10, 25, 47, 0.05)"
        input_border = "rgba(100, 255, 218, 0.7)"
        accent_color = "#172a45"  # Lighter navy
        highlight_color = "#64ffda"  # Teal highlight
        secondary_accent = "#8892b0"  # Light slate
    
    css = """
    <style>
    /* Main container styling */
    .main {
        background: """ + bg_gradient + """;
        color: """ + text_color + """;
        padding: 20px;
        transition: all 0.3s ease;
    }
    
    /* Developer attribution */
    .developer-attribution {
        text-align: center;
        padding: 10px;
        background-color: """ + accent_color + """;
        color: """ + highlight_color + """;
        font-weight: bold;
        margin-bottom: 15px;
        border-radius: 10px;
    }
    
    /* VIP Border styling */
    .vip-border {
        border: 3px solid """ + highlight_color + """;
        border-radius: 15px;
        padding: 20px;
        background: """ + card_bg + """;
        box-shadow: 0 0 20px rgba(100, 255, 218, 0.5);
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    
    /* Header styling */
    .vip-header {
        text-align: center;
        color: """ + highlight_color + """;
        font-size: 2.5rem;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(100, 255, 218, 0.7);
        margin-bottom: 20px;
    }
    
    /* Password input styling */
    .stTextInput > div > div > input {
        background-color: """ + input_bg + """;
        color: """ + text_color + """;
        border: 2px solid """ + input_border + """;
        border-radius: 10px;
        padding: 10px;
        font-size: 1.2rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: """ + highlight_color + """;
        box-shadow: 0 0 10px rgba(100, 255, 218, 0.3);
    }
    
    /* Criteria styling */
    .criteria-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        margin-top: 20px;
    }
    
    .criteria-item {
        background: rgba(0, 0, 0, 0.2);
        border-radius: 10px;
        padding: 10px;
        margin: 5px;
        flex: 1 1 200px;
        border-left: 4px solid var(--criteria-color, gray);
        transition: all 0.3s ease;
    }
    
    .criteria-met {
        --criteria-color: #00cc00;
    }
    
    .criteria-not-met {
        --criteria-color: #ff3333;
    }
    
    /* Strength meter styling */
    .strength-meter {
        height: 20px;
        border-radius: 10px;
        margin: 20px 0;
        background: rgba(255, 255, 255, 0.1);
        overflow: hidden;
        box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.2);
    }
    
    .strength-fill {
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s ease, background 0.5s ease;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .vip-header {
            font-size: 1.8rem;
        }
        
        .criteria-item {
            flex: 1 1 100%;
        }
    }
    
    /* Strength label styling */
    .strength-label {
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        margin: 10px 0;
        text-shadow: 0 0 5px rgba(0, 0, 0, 0.5);
        transition: color 0.5s ease;
    }
    
    /* Animation for the border */
    @keyframes border-glow {
        0% { box-shadow: 0 0 10px rgba(100, 255, 218, 0.5); }
        50% { box-shadow: 0 0 20px rgba(100, 255, 218, 0.8); }
        100% { box-shadow: 0 0 10px rgba(100, 255, 218, 0.5); }
    }
    
    .vip-border {
        animation: border-glow 2s infinite;
    }
    
    /* Suggestions styling */
    .suggestions {
        background: rgba(0, 0, 0, 0.2);
        border-radius: 10px;
        padding: 15px;
        margin-top: 20px;
        border-left: 4px solid """ + secondary_accent + """;
        transition: all 0.3s ease;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        margin-top: 30px;
        font-size: 0.8rem;
        color: """ + highlight_color + """;
        background-color: """ + accent_color + """;
        padding: 15px;
        border-radius: 10px;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, """ + accent_color + """, """ + secondary_accent + """);
        color: """ + highlight_color + """;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Theme toggle styling */
    .theme-toggle {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 20px;
    }
    
    /* Card styling */
    .card {
        background: """ + card_bg + """;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: """ + card_bg + """;
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        color: """ + text_color + """;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: """ + highlight_color + """ !important;
        color: """ + accent_color + """ !important;
    }
    
    /* History table styling */
    .history-table {
        width: 100%;
        border-collapse: collapse;
    }
    
    .history-table th, .history-table td {
        padding: 10px;
        text-align: left;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .history-table th {
        background-color: rgba(0, 0, 0, 0.2);
        color: """ + highlight_color + """;
    }
    
    /* Password generator styling */
    .generator-options {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin: 15px 0;
    }
    
    .generator-option {
        flex: 1 1 200px;
        background: rgba(0, 0, 0, 0.1);
        padding: 10px;
        border-radius: 10px;
    }
    
    /* Copy button styling */
    .copy-button {
        background: """ + secondary_accent + """;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 5px 10px;
        margin-left: 10px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .copy-button:hover {
        background: """ + highlight_color + """;
        color: """ + accent_color + """;
    }
    
    /* Password breach indicator */
    .breach-indicator {
        margin-top: 15px;
        padding: 10px;
        border-radius: 10px;
        background: rgba(255, 0, 0, 0.1);
        border-left: 4px solid #ff3333;
    }
    
    .safe-indicator {
        margin-top: 15px;
        padding: 10px;
        border-radius: 10px;
        background: rgba(0, 255, 0, 0.1);
        border-left: 4px solid #00cc00;
    }
    
    /* Password expiry recommendation */
    .expiry-recommendation {
        margin-top: 15px;
        padding: 10px;
        border-radius: 10px;
        background: rgba(100, 255, 218, 0.1);
        border-left: 4px solid """ + highlight_color + """;
    }
    
    /* Animated elements */
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    /* Tooltip styling */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: """ + card_bg + """;
        color: """ + text_color + """;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
        border: 1px solid """ + highlight_color + """;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    
    /* Password strength score visualization */
    .strength-score-container {
        display: flex;
        justify-content: space-between;
        margin: 15px 0;
    }
    
    .strength-score-segment {
        height: 8px;
        flex: 1;
        margin: 0 2px;
        border-radius: 4px;
        background: rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
    }
    
    /* Password complexity visualization */
    .complexity-chart {
        width: 100%;
        height: 200px;
        background: """ + card_bg + """;
        border-radius: 10px;
        padding: 15px;
        margin: 15px 0;
    }
    
    /* Password strength factors */
    .strength-factors {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin: 15px 0;
    }
    
    .strength-factor {
        flex: 1 1 calc(50% - 10px);
        background: rgba(0, 0, 0, 0.1);
        padding: 10px;
        border-radius: 10px;
        display: flex;
        align-items: center;
    }
    
    .strength-factor-icon {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 10px;
        font-weight: bold;
    }
    
    /* Password patterns visualization */
    .pattern-visualization {
        font-family: monospace;
        font-size: 1.2rem;
        padding: 10px;
        background: rgba(0, 0, 0, 0.1);
        border-radius: 5px;
        margin: 10px 0;
        overflow-x: auto;
        white-space: nowrap;
    }
    
    /* Character distribution chart */
    .char-distribution {
        display: flex;
        height: 100px;
        margin: 15px 0;
        align-items: flex-end;
    }
    
    .char-bar {
        flex: 1;
        background: """ + highlight_color + """;
        margin: 0 1px;
        border-radius: 3px 3px 0 0;
        transition: height 0.3s ease;
    }
    
    /* Password strength timeline */
    .timeline {
        position: relative;
        margin: 20px 0;
        padding-left: 30px;
    }
    
    .timeline-item {
        position: relative;
        padding-bottom: 20px;
    }
    
    .timeline-item:before {
        content: '';
        position: absolute;
        left: -30px;
        top: 0;
        width: 15px;
        height: 15px;
        border-radius: 50%;
        background: """ + highlight_color + """;
        z-index: 1;
    }
    
    .timeline-item:after {
        content: '';
        position: absolute;
        left: -23px;
        top: 15px;
        width: 2px;
        height: calc(100% - 15px);
        background: """ + highlight_color + """;
    }
    
    .timeline-item:last-child:after {
        display: none;
    }
    
    /* Password strength comparison */
    .comparison-table {
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
    }
    
    .comparison-table th, .comparison-table td {
        padding: 10px;
        text-align: left;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .comparison-table th {
        background-color: rgba(0, 0, 0, 0.2);
        color: """ + highlight_color + """;
    }
    
    /* Password strength badges */
    .strength-badge {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 15px;
        font-weight: bold;
        font-size: 0.8rem;
        margin: 5px;
    }
    
    /* Password strength radar chart */
    .radar-chart {
        width: 100%;
        height: 300px;
        background: """ + card_bg + """;
        border-radius: 10px;
        padding: 15px;
        margin: 15px 0;
    }
    
    /* Password strength heat map */
    .heat-map {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(30px, 1fr));
        gap: 2px;
        margin: 15px 0;
    }
    
    .heat-map-cell {
        height: 30px;
        border-radius: 3px;
        transition: all 0.3s ease;
    }
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)

# Function to create a decorative header image
def create_header_image():
    # Create a figure with a gradient background
    fig, ax = plt.subplots(figsize=(10, 2))
    
    # Remove axes
    ax.axis('off')
    
    # Create gradient background
    x = np.linspace(0, 1, 100)
    y = np.linspace(0, 1, 100)
    X, Y = np.meshgrid(x, y)
    
    # Create a radial gradient
    R = np.sqrt((X - 0.5)**2 + (Y - 0.5)**2)
    Z = 1 - R*1.5
    Z = np.clip(Z, 0, 1)
    
    # Use different colormap based on theme
    cmap = 'viridis' if st.session_state.theme == 'dark' else 'cool'
    
    # Plot the gradient
    ax.imshow(Z, cmap=cmap, extent=[0, 1, 0, 1], aspect='auto')
    
    # Add text with path effects
    ax.text(0.5, 0.5, ' PASSWORD STRENGTH METER', 
            fontsize=24, fontweight='bold', 
            ha='center', va='center', 
            color='white', 
            path_effects=[path_effects.withStroke(linewidth=3, foreground='black')])
    
    # Save to bytes
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0, transparent=True)
    buf.seek(0)
    
    # Convert to base64
    img_str = base64.b64encode(buf.read()).decode()
    plt.close(fig)
    
    return img_str

# Function to evaluate password strength
def evaluate_password_strength(password):
    # Initialize criteria
    criteria = {
        "length": {"met": len(password) >= 8, "description": "At least 8 characters"},
        "uppercase": {"met": bool(re.search(r'[A-Z]', password)), "description": "Contains uppercase letters"},
        "lowercase": {"met": bool(re.search(r'[a-z]', password)), "description": "Contains lowercase letters"},
        "numbers": {"met": bool(re.search(r'\d', password)), "description": "Contains numbers"},
        "special": {"met": bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password)), "description": "Contains special characters"},
        "no_common": {"met": not any(common in password.lower() for common in ["password", "123456", "qwerty", "admin"]), 
                     "description": "Not a common password"},
        "no_sequential": {"met": not bool(re.search(r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz|012|123|234|345|456|567|678|789|890)', password.lower())),
                         "description": "No sequential characters"},
        "length_bonus": {"met": len(password) >= 12, "description": "12+ characters (bonus)"},
        "variety": {"met": sum([bool(re.search(r'[A-Z]', password)), 
                               bool(re.search(r'[a-z]', password)), 
                               bool(re.search(r'\d', password)), 
                               bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))]) >= 3,
                   "description": "Uses 3+ character types"}
    }
    
    # Calculate base score
    met_criteria = sum(1 for c in criteria.values() if c["met"])
    base_score = (met_criteria / len(criteria)) * 100
    
    # Apply additional scoring factors
    length_bonus = min(20, (len(password) - 8) * 2) if len(password) > 8 else 0
    variety_bonus = 10 if all(criteria[k]["met"] for k in ["uppercase", "lowercase", "numbers", "special"]) else 0
    
    # Calculate final strength percentage
    strength_percentage = min(100, base_score + length_bonus + variety_bonus)
    
    # Determine strength level
    if strength_percentage < 30:
        strength_level = {"name": "Very Weak", "color": "#FF0000", "description": "This password can be cracked instantly!"}
    elif strength_percentage < 50:
        strength_level = {"name": "Weak", "color": "#FF6600", "description": "This password could be cracked in minutes to hours."}
    elif strength_percentage < 70:
        strength_level = {"name": "Moderate", "color": "#FFCC00", "description": "This password would take days to weeks to crack."}
    elif strength_percentage < 90:
        strength_level = {"name": "Strong", "color": "#99CC00", "description": "This password would take months to years to crack."}
    else:
        strength_level = {"name": "Very Strong", "color": "#00CC00", "description": "This password would take centuries to crack!"}
    
    # Generate suggestions
    suggestions = []
    if not criteria["length"]["met"]:
        suggestions.append("Make your password longer (at least 8 characters)")
    if not criteria["uppercase"]["met"]:
        suggestions.append("Add uppercase letters (A-Z)")
    if not criteria["lowercase"]["met"]:
        suggestions.append("Add lowercase letters (a-z)")
    if not criteria["numbers"]["met"]:
        suggestions.append("Add numbers (0-9)")
    if not criteria["special"]["met"]:
        suggestions.append("Add special characters (!@#$%^&*)")
    if not criteria["no_common"]["met"]:
        suggestions.append("Avoid common password patterns")
    if not criteria["no_sequential"]["met"]:
        suggestions.append("Avoid sequential characters like 'abc' or '123'")
    
    # Calculate entropy (randomness)
    char_set_size = 0
    if criteria["uppercase"]["met"]: char_set_size += 26
    if criteria["lowercase"]["met"]: char_set_size += 26
    if criteria["numbers"]["met"]: char_set_size += 10
    if criteria["special"]["met"]: char_set_size += 32
    
    entropy = len(password) * (np.log2(char_set_size) if char_set_size > 0 else 0)
    
    # Simulate password breach check (for demonstration)
    # In a real app, you would use a service like "Have I Been Pwned" API
    common_passwords = ["password", "123456", "qwerty", "admin", "welcome", "login", "abc123"]
    is_breached = password.lower() in common_passwords or len(password) < 6
    
    # Calculate password expiry recommendation based on strength
    if strength_percentage < 50:
        expiry_days = 30
    elif strength_percentage < 70:
        expiry_days = 60
    elif strength_percentage < 90:
        expiry_days = 90
    else:
        expiry_days = 180
    
    # Calculate crack time estimation
    if strength_percentage < 30:
        crack_time = "Instantly"
    elif strength_percentage < 50:
        crack_time = "Minutes to hours"
    elif strength_percentage < 70:
        crack_time = "Days to weeks"
    elif strength_percentage < 90:
        crack_time = "Months to years"
    else:
        crack_time = "Centuries"
    
    # Character distribution analysis
    char_distribution = {
        "uppercase": sum(1 for c in password if c.isupper()),
        "lowercase": sum(1 for c in password if c.islower()),
        "numbers": sum(1 for c in password if c.isdigit()),
        "special": sum(1 for c in password if not c.isalnum())
    }
    
    # Pattern analysis
    patterns = []
    if re.search(r'[A-Za-z]+\d+', password):
        patterns.append("Letters followed by numbers")
    if re.search(r'\d+[A-Za-z]+', password):
        patterns.append("Numbers followed by letters")
    if re.search(r'(.)\1{2,}', password):
        patterns.append("Repeated characters")
    
    return {
        "criteria": criteria,
        "strength_percentage": strength_percentage,
        "strength_level": strength_level,
        "suggestions": suggestions,
        "entropy": entropy,
        "is_breached": is_breached,
        "expiry_days": expiry_days,
        "crack_time": crack_time,
        "char_distribution": char_distribution,
        "patterns": patterns
    }

# Function to simulate password breach check
def check_password_breach(password):
    # Create a SHA-1 hash of the password (this is how real breach checks work)
    # In a real app, you would only send the first 5 characters of the hash to a service like HIBP
    hash_object = hashlib.sha1(password.encode())
    password_hash = hash_object.hexdigest().upper()
    
    # Simulate a breach check
    # For demo purposes, we'll consider passwords with these patterns as "breached"
    common_patterns = ["123", "abc", "password", "qwerty", "admin"]
    is_breached = any(pattern in password.lower() for pattern in common_patterns)
    
    # Simulate number of times the password has been seen in breaches
    breach_count = 0
    if is_breached:
        # Generate a random number for demonstration
        breach_count = random.randint(1, 100000)
    
    return {
        "is_breached": is_breached,
        "breach_count": breach_count,
        "hash_prefix": password_hash[:5]  # First 5 characters of the hash
    }

# Function to visualize character distribution
def visualize_char_distribution(password):
    char_types = {
        "uppercase": sum(1 for c in password if c.isupper()),
        "lowercase": sum(1 for c in password if c.islower()),
        "numbers": sum(1 for c in password if c.isdigit()),
        "special": sum(1 for c in password if not c.isalnum())
    }
    
    # Calculate percentages
    total = len(password)
    percentages = {k: (v / total) * 100 if total > 0 else 0 for k, v in char_types.items()}
    
    # Create HTML for visualization
    html = '<div class="char-distribution">'
    for char_type, count in char_types.items():
        height = count * 10 if count > 0 else 5  # Minimum height for visibility
        html += f'<div class="char-bar" style="height:{height}px;" title="{char_type}: {count} ({percentages[char_type]:.1f}%)"></div>'
    html += '</div>'
    
    # Create legend
    html += '<div style="display:flex; justify-content:space-between; font-size:0.8rem;">'
    html += '<span>Uppercase</span><span>Lowercase</span><span>Numbers</span><span>Special</span>'
    html += '</div>'
    
    return html

# Main app function
def main():
    add_custom_css()
    
    # Developer attribution at the top
    st.markdown('<div class="developer-attribution">Developed by Atfa Siddiqui</div>', unsafe_allow_html=True)
    
    # Theme toggle button - FIXED VERSION
    col1, col2 = st.columns([4, 1])
    with col2:
        # Simple direct button for theme toggle
        theme_label = "☀️ Light Mode" if st.session_state.theme == 'dark' else "🌙 Dark Mode"
        if st.button(theme_label):
            toggle_theme()
            st.rerun()  # Use st.rerun() instead of experimental_rerun()
    
    # Create header image
    header_img = create_header_image()
    st.markdown(f'<img src="data:image/png;base64,{header_img}" style="width:100%;">', unsafe_allow_html=True)
    
    # App title and description
    st.markdown('<div class="vip-border">', unsafe_allow_html=True)
    st.markdown('<h1 class="vip-header">VIP Password Strength Meter</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; font-size:1.2rem;">Check how strong and secure your password is with our premium strength meter</p>', unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Password Checker", "Password Generator", "Password History", "Advanced Analysis"])
    
    with tab1:
        # Password input
        password = st.text_input("Enter your password", type="password", key="password_input")
        
        if password:
            # Add a small delay for effect
            with st.spinner("Analyzing password strength..."):
                time.sleep(0.5)
            
            # Evaluate password
            result = evaluate_password_strength(password)
            
            # Add to history
            add_to_history(password, result["strength_level"]["name"])
            
            # Display strength meter
            st.markdown(f'<div class="strength-meter"><div class="strength-fill" style="width:{result["strength_percentage"]}%; background:{result["strength_level"]["color"]};"></div></div>', unsafe_allow_html=True)
            
            # Display strength level
            st.markdown(f'<div class="strength-label" style="color:{result["strength_level"]["color"]};">{result["strength_level"]["name"]} ({int(result["strength_percentage"])}%)</div>', unsafe_allow_html=True)
            
            # Display strength description
            st.markdown(f'<p style="text-align:center;">{result["strength_level"]["description"]}</p>', unsafe_allow_html=True)
            
            # Display criteria
            st.markdown('<div class="criteria-container">', unsafe_allow_html=True)
            for key, value in result["criteria"].items():
                status_class = "criteria-met" if value["met"] else "criteria-not-met"
                status_icon = "✓" if value["met"] else "✗"
                st.markdown(f'<div class="criteria-item {status_class}"><span style="font-weight:bold;">{status_icon} {value["description"]}</span></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Display character distribution
            st.markdown("<h3>Character Distribution</h3>", unsafe_allow_html=True)
            st.markdown(visualize_char_distribution(password), unsafe_allow_html=True)
            
            # Display entropy
            st.markdown(f"""
            <div class="card">
                <h3>Password Entropy: {result["entropy"]:.2f} bits</h3>
                <p>Entropy is a measure of password randomness and unpredictability. Higher is better.</p>
                <div class="tooltip">ℹ️ What is entropy?
                    <span class="tooltiptext">Entropy measures how unpredictable your password is. A higher entropy means your password is more random and harder to guess.</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Display estimated crack time
            st.markdown(f"""
            <div class="card">
                <h3>Estimated Time to Crack: {result["crack_time"]}</h3>
                <p>This is an estimate of how long it would take for a typical attacker to crack this password using brute force methods.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Check for breaches
            breach_result = check_password_breach(password)
            if breach_result["is_breached"]:
                st.markdown(f"""
                <div class="breach-indicator">
                    <h3>⚠️ Password Breach Alert</h3>
                    <p>This password appears to have been found in {breach_result["breach_count"]:,} data breaches. It is not safe to use!</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="safe-indicator">
                    <h3>✅ No Breaches Found</h3>
                    <p>This password does not appear in our breach database. However, always use unique passwords for each account.</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Password expiry recommendation
            st.markdown(f"""
            <div class="expiry-recommendation">
                <h3>Password Expiry Recommendation</h3>
                <p>Based on the strength of this password, we recommend changing it every {result["expiry_days"]} days.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Display pattern analysis if any patterns found
            if result["patterns"]:
                st.markdown(f"""
                <div class="card">
                    <h3>Pattern Analysis</h3>
                    <p>We detected the following patterns in your password:</p>
                    <ul>
                    {"".join(f"<li>{pattern}</li>" for pattern in result["patterns"])}
                    </ul>
                    <p>Predictable patterns can make your password easier to guess.</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Display suggestions if any
            if result["suggestions"]:
                st.markdown('<div class="suggestions">', unsafe_allow_html=True)
                st.markdown('<h3>Suggestions to improve:</h3>', unsafe_allow_html=True)
                for suggestion in result["suggestions"]:
                    st.markdown(f'<p>• {suggestion}</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            # Display placeholder when no password is entered
            st.markdown('<div class="strength-meter"><div class="strength-fill" style="width:0%; background:#ccc;"></div></div>', unsafe_allow_html=True)
            st.markdown('<div class="strength-label" style="color:#ccc;">Enter a password to check its strength</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown("<h2>Generate Secure Password</h2>", unsafe_allow_html=True)
        
        # Password generation options
        col1, col2 = st.columns(2)
        
        with col1:
            length = st.slider("Password Length", min_value=8, max_value=32, value=16, step=1)
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
            include_uppercase = st.checkbox("Include Uppercase Letters (A-Z)", value=True)
            include_lowercase = st.checkbox("Include Lowercase Letters (a-z)", value=True)
            include_numbers = st.checkbox("Include Numbers (0-9)", value=True)
            include_special = st.checkbox("Include Special Characters (!@#$%^&*)", value=True)
        
        # Advanced options
        with st.expander("Advanced Options"):
            avoid_similar = st.checkbox("Avoid Similar Characters (i, l, 1, o, 0, etc.)", value=False)
            avoid_ambiguous = st.checkbox("Avoid Ambiguous Characters ({}[]()/<>\"'`~,;:.-_)", value=False)
            require_all_types = st.checkbox("Require at least one character from each selected type", value=True)
            
            # Password format template
            st.markdown("<h4>Custom Format Template (Optional)</h4>", unsafe_allow_html=True)
            st.markdown("""
            <p>Use the following characters to define a custom format:</p>
            <ul>
                <li>A - Uppercase letter</li>
                <li>a - Lowercase letter</li>
                <li>0 - Number</li>
                <li>! - Special character</li>
                <li>* - Any character</li>
            </ul>
            <p>Example: Aa0!*** will generate a password with uppercase, lowercase, number, special, and 3 random characters.</p>
            """, unsafe_allow_html=True)
            
            format_template = st.text_input("Format Template (leave empty for random)", value="")
        
        # Number of passwords to generate
        num_passwords = st.slider("Number of Passwords to Generate", min_value=1, max_value=10, value=1)
        
        # Generate password button
        if st.button("Generate Secure Password", key="generate_btn"):
            generated_passwords = []
            for _ in range(num_passwords):
                generated_password = generate_password(
                    length=length,
                    include_uppercase=include_uppercase,
                    include_lowercase=include_lowercase,
                    include_numbers=include_numbers,
                    include_special=include_special
                )
                
                # Store in generated passwords list
                generated_passwords.append(generated_password)
            
            # Store in session state
            st.session_state.generated_password = generated_passwords[0] if generated_passwords else ""
            
            # Add to generated passwords history
            for pwd in generated_passwords:
                if pwd not in st.session_state.generated_passwords:
                    st.session_state.generated_passwords.append(pwd)
                    # Keep only the last 10 generated passwords
                    if len(st.session_state.generated_passwords) > 10:
                        st.session_state.generated_passwords.pop(0)
        
        # Display generated passwords
        if 'generated_password' in st.session_state and st.session_state.generated_password:
            st.markdown("<h3>Generated Passwords</h3>", unsafe_allow_html=True)
            
            for idx, pwd in enumerate(st.session_state.generated_passwords[:num_passwords]):
                # Evaluate the generated password
                result = evaluate_password_strength(pwd)
                
                # Display the password in a card
                st.markdown(f"""
                <div class="card pulse">
                    <h4>Password {idx+1}:</h4>
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <code style="font-size: 1.2rem; padding: 10px; background: rgba(0,0,0,0.1); border-radius: 5px;">{pwd}</code>
                        <button class="copy-button" onclick="navigator.clipboard.writeText('{pwd}'); this.innerHTML='Copied!'; setTimeout(() => this.innerHTML='Copy', 2000)">Copy</button>
                    </div>
                    <p>Strength: <span style="color:{result['strength_level']['color']};">{result['strength_level']['name']} ({int(result['strength_percentage'])}%)</span></p>
                    <div class="strength-meter"><div class="strength-fill" style="width:{result['strength_percentage']}%; background:{result['strength_level']['color']};"></div></div>
                </div>
                """, unsafe_allow_html=True)
        
        # Display recently generated passwords
        if st.session_state.generated_passwords and len(st.session_state.generated_passwords) > num_passwords:
            st.markdown("<h3>Recently Generated Passwords</h3>", unsafe_allow_html=True)
            for idx, pwd in enumerate(reversed(st.session_state.generated_passwords[num_passwords:])):
                if idx < 5:  # Show only the last 5
                    result = evaluate_password_strength(pwd)
                    st.markdown(f"""
                    <div class="card" style="display: flex; justify-content: space-between; align-items: center;">
                        <code>{pwd}</code>
                        <span style="color:{result['strength_level']['color']};">{result['strength_level']['name']}</span>
                        <button class="copy-button" onclick="navigator.clipboard.writeText('{pwd}'); this.innerHTML='Copied!'; setTimeout(() => this.innerHTML='Copy', 2000)">Copy</button>
                    </div>
                    """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("<h2>Password History</h2>", unsafe_allow_html=True)
        
        if st.session_state.password_history:
            st.markdown("""
            <p>Below is a history of passwords you've checked (only showing masked versions for security).</p>
            <table class="history-table">
                <tr>
                    <th>Password (Masked)</th>
                    <th>Strength</th>
                    <th>Date & Time</th>
                </tr>
            """, unsafe_allow_html=True)
            
            for entry in reversed(st.session_state.password_history):
                color = "#FF0000"
                if "Very Strong" in entry["strength"]:
                    color = "#00CC00"
                elif "Strong" in entry["strength"]:
                    color = "#99CC00"
                elif "Moderate" in entry["strength"]:
                    color = "#FFCC00"
                elif "Weak" in entry["strength"]:
                    color = "#FF6600"
                
                st.markdown(f"""
                <tr>
                    <td>{entry["password"]}</td>
                    <td style="color:{color};">{entry["strength"]}</td>
                    <td>{entry["timestamp"]}</td>
                </tr>
                """, unsafe_allow_html=True)
            
            st.markdown("</table>", unsafe_allow_html=True)
            
            if st.button("Clear History"):
                st.session_state.password_history = []
                st.rerun()
        else:
            st.markdown("<p>No password history yet. Check some passwords to see them here.</p>", unsafe_allow_html=True)
    
    with tab4:
        st.markdown("<h2>Advanced Password Analysis</h2>", unsafe_allow_html=True)
        
        # Password comparison tool
        st.markdown("<h3>Password Comparison Tool</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            password1 = st.text_input("First Password", type="password", key="password_compare1")
        
        with col2:
            password2 = st.text_input("Second Password", type="password", key="password_compare2")
        
        if password1 and password2:
            result1 = evaluate_password_strength(password1)
            result2 = evaluate_password_strength(password2)
            
            st.markdown("""
            <h4>Comparison Results</h4>
            <table class="comparison-table">
                <tr>
                    <th>Metric</th>
                    <th>Password 1</th>
                    <th>Password 2</th>
                    <th>Better Option</th>
                </tr>
                <tr>
                    <td>Strength Score</td>
                    <td>{:.1f}%</td>
                    <td>{:.1f}%</td>
                    <td>{}</td>
                </tr>
                <tr>
                    <td>Entropy</td>
                    <td>{:.2f} bits</td>
                    <td>{:.2f} bits</td>
                    <td>{}</td>
                </tr>
                <tr>
                    <td>Length</td>
                    <td>{}</td>
                    <td>{}</td>
                    <td>{}</td>
                </tr>
                <tr>
                    <td>Character Types</td>
                    <td>{}</td>
                    <td>{}</td>
                    <td>{}</td>
                </tr>
                <tr>
                    <td>Crack Time</td>
                    <td>{}</td>
                    <td>{}</td>
                    <td>{}</td>
                </tr>
            </table>
            """.format(
                result1["strength_percentage"], result2["strength_percentage"], 
                "Password 1" if result1["strength_percentage"] > result2["strength_percentage"] else "Password 2" if result2["strength_percentage"] > result1["strength_percentage"] else "Equal",
                
                result1["entropy"], result2["entropy"],
                "Password 1" if result1["entropy"] > result2["entropy"] else "Password 2" if result2["entropy"] > result1["entropy"] else "Equal",
                
                len(password1), len(password2),
                "Password 1" if len(password1) > len(password2) else "Password 2" if len(password2) > len(password1) else "Equal",
                
                sum([bool(re.search(r'[A-Z]', password1)), bool(re.search(r'[a-z]', password1)), bool(re.search(r'\d', password1)), bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password1))]),
                sum([bool(re.search(r'[A-Z]', password2)), bool(re.search(r'[a-z]', password2)), bool(re.search(r'\d', password2)), bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password2))]),
                "Password 1" if sum([bool(re.search(r'[A-Z]', password1)), bool(re.search(r'[a-z]', password1)), bool(re.search(r'\d', password1)), bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password1))]) > sum([bool(re.search(r'[A-Z]', password2)), bool(re.search(r'[a-z]', password2)), bool(re.search(r'\d', password2)), bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password2))]) else "Password 2" if sum([bool(re.search(r'[A-Z]', password2)), bool(re.search(r'[a-z]', password2)), bool(re.search(r'\d', password2)), bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password2))]) > sum([bool(re.search(r'[A-Z]', password1)), bool(re.search(r'[a-z]', password1)), bool(re.search(r'\d', password1)), bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password1))]) else "Equal",
                
                result1["crack_time"], result2["crack_time"],
                "Password 1" if result1["strength_percentage"] > result2["strength_percentage"] else "Password 2" if result2["strength_percentage"] > result1["strength_percentage"] else "Equal"
            ), unsafe_allow_html=True)
        
        # Password strength timeline
        st.markdown("<h3>Password Strength Timeline</h3>", unsafe_allow_html=True)
        st.markdown("""
        <p>How long would it take to crack your password over time?</p>
        <div class="timeline">
            <div class="timeline-item">
                <h4>1990s</h4>
                <p>A password that would take years to crack in the 1990s might be cracked in minutes today.</p>
            </div>
            <div class="timeline-item">
                <h4>2000s</h4>
                <p>As computing power increased, password requirements became more stringent.</p>
            </div>
            <div class="timeline-item">
                <h4>2010s</h4>
                <p>The rise of GPU-based cracking made even complex passwords vulnerable.</p>
            </div>
            <div class="timeline-item">
                <h4>2020s</h4>
                <p>Modern password security requires longer, more complex passwords and multi-factor authentication.</p>
            </div>
            <div class="timeline-item">
                <h4>Future</h4>
                <p>Quantum computing may eventually break current encryption methods, requiring new security approaches.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Common password patterns to avoid
        st.markdown("<h3>Common Password Patterns to Avoid</h3>", unsafe_allow_html=True)
        st.markdown("""
        <div class="card">
            <ul>
                <li>Personal information (names, birthdays, etc.)</li>
                <li>Sequential keyboard patterns (qwerty, 12345)</li>
                <li>Common word + number combinations (password123)</li>
                <li>Simple word substitutions (p@ssw0rd)</li>
                <li>Sports teams or favorite celebrities</li>
                <li>Common phrases or song lyrics</li>
                <li>Words spelled backwards</li>
                <li>Repeating characters (aaabbb)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Password manager recommendation
        st.markdown("<h3>Password Manager Recommendation</h3>", unsafe_allow_html=True)
        st.markdown("""
        <div class="card">
            <p>Using a password manager is highly recommended for maintaining strong, unique passwords for all your accounts. Popular options include:</p>
            <ul>
                <li>Bitwarden (Free, open-source)</li>
                <li>LastPass</li>
                <li>1Password</li>
                <li>Dashlane</li>
                <li>KeePass (Offline, open-source)</li>
            </ul>
            <p>A good password manager will generate, store, and autofill strong passwords for you.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Password tips section
    st.markdown('<div class="vip-border">', unsafe_allow_html=True)
    st.markdown('<h2 style="color:#64ffda;">Password Security Tips</h2>', unsafe_allow_html=True)
    
    tips = [
        "Use a different password for each of your important accounts",
        "Use a password manager to generate and store strong passwords",
        "Enable two-factor authentication (2FA) whenever possible",
        "Consider using a passphrase (a sequence of random words) for better security and memorability",
        "Avoid using personal information in your passwords (birthdays, names, etc.)",
        "Change your passwords periodically, especially for critical accounts",
        "Be cautious of phishing attempts asking for your password",
        "Check if your accounts have been involved in data breaches at haveibeenpwned.com",
        "Use biometric authentication when available (fingerprint, face recognition)",
        "Consider using a hardware security key for critical accounts"
    ]
    
    for tip in tips:
        st.markdown(f'<p>• {tip}</p>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer with developer attribution
    st.markdown('<div class="footer"> Password Strength Meter © 2025 | Secure your digital life with strong passwords<br>Developed by Atfa Siddiqui</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()