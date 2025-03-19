import streamlit as st
import re
import time
import random
import string
import datetime
import hashlib

# Set page configuration
st.set_page_config(
    page_title="VIP Password Strength Meter",
    page_icon="🔒",
    layout="wide"
)

# Apply custom CSS for VIP styling
def apply_vip_styling():
    st.markdown("""
    <style>
    /* Main styling */
    .main {
        background: linear-gradient(135deg, #0a192f, #172a45);
        color: white;
        padding: 20px;
    }
    
    /* VIP container */
    .vip-container {
        border: 3px solid #64ffda;
        border-radius: 15px;
        padding: 20px;
        background: rgba(10, 25, 47, 0.7);
        box-shadow: 0 0 20px rgba(100, 255, 218, 0.5);
        margin-bottom: 20px;
        animation: border-glow 2s infinite;
    }
    
    /* Header styling */
    .vip-header {
        text-align: center;
        color: #64ffda;
        font-size: 2.5rem;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(100, 255, 218, 0.7);
        margin-bottom: 20px;
    }
    
    /* Strength meter */
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
    
    /* Strength label */
    .strength-label {
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        margin: 10px 0;
        text-shadow: 0 0 5px rgba(0, 0, 0, 0.5);
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
    }
    
    .criteria-met {
        --criteria-color: #00cc00;
    }
    
    .criteria-not-met {
        --criteria-color: #ff3333;
    }
    
    /* Suggestions styling */
    .suggestions {
        background: rgba(0, 0, 0, 0.2);
        border-radius: 10px;
        padding: 15px;
        margin-top: 20px;
        border-left: 4px solid #8892b0;
    }
    
    /* Card styling */
    .card {
        background: rgba(10, 25, 47, 0.7);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        margin-top: 30px;
        font-size: 0.8rem;
        color: #64ffda;
        background-color: #0a192f;
        padding: 15px;
        border-radius: 10px;
    }
    
    /* Animation for the border */
    @keyframes border-glow {
        0% { box-shadow: 0 0 10px rgba(100, 255, 218, 0.5); }
        50% { box-shadow: 0 0 20px rgba(100, 255, 218, 0.8); }
        100% { box-shadow: 0 0 10px rgba(100, 255, 218, 0.5); }
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(10, 25, 47, 0.7);
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        color: white;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #64ffda !important;
        color: #0a192f !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, #0a192f, #8892b0);
        color: #64ffda;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Password input styling */
    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
        border: 2px solid rgba(100, 255, 218, 0.5);
        border-radius: 10px;
        padding: 10px;
        font-size: 1.2rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #64ffda;
        box-shadow: 0 0 10px rgba(100, 255, 218, 0.3);
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
        color: #64ffda;
    }
    
    /* Developer attribution */
    .developer-attribution {
        text-align: center;
        padding: 10px;
        background-color: #0a192f;
        color: #64ffda;
        font-weight: bold;
        margin-bottom: 15px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    if 'password_history' not in st.session_state:
        st.session_state.password_history = []
    if 'generated_passwords' not in st.session_state:
        st.session_state.generated_passwords = []

# Function to evaluate password strength
def evaluate_password_strength(password):
    # Define criteria for password strength
    criteria = {
        "length": {"met": len(password) >= 8, "description": "At least 8 characters"},
        "uppercase": {"met": bool(re.search(r'[A-Z]', password)), "description": "Contains uppercase letters"},
        "lowercase": {"met": bool(re.search(r'[a-z]', password)), "description": "Contains lowercase letters"},
        "numbers": {"met": bool(re.search(r'\d', password)), "description": "Contains numbers"},
        "special": {"met": bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password)), "description": "Contains special characters"},
        "no_common": {"met": not any(common in password.lower() for common in ["password", "123456", "qwerty", "admin"]), 
                     "description": "Not a common password"},
        "no_sequential": {"met": not bool(re.search(r'(abc|bcd|cde|def|123|234|345|456)', password.lower())),
                         "description": "No sequential characters"}
    }
    
    # Calculate score based on met criteria
    met_criteria = sum(1 for c in criteria.values() if c["met"])
    base_score = (met_criteria / len(criteria)) * 100
    
    # Add bonus for length
    length_bonus = min(20, (len(password) - 8) * 2) if len(password) > 8 else 0
    
    # Add bonus for variety of character types
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
    
    # Generate suggestions for improvement
    suggestions = []
    for key, value in criteria.items():
        if not value["met"]:
            if key == "length":
                suggestions.append("Make your password longer (at least 8 characters)")
            elif key == "uppercase":
                suggestions.append("Add uppercase letters (A-Z)")
            elif key == "lowercase":
                suggestions.append("Add lowercase letters (a-z)")
            elif key == "numbers":
                suggestions.append("Add numbers (0-9)")
            elif key == "special":
                suggestions.append("Add special characters (!@#$%^&*)")
            elif key == "no_common":
                suggestions.append("Avoid common password patterns")
            elif key == "no_sequential":
                suggestions.append("Avoid sequential characters like 'abc' or '123'")
    
    return {
        "criteria": criteria,
        "strength_percentage": strength_percentage,
        "strength_level": strength_level,
        "suggestions": suggestions
    }

# Function to generate a secure password
def generate_password(length=12, include_uppercase=True, include_lowercase=True, 
                     include_numbers=True, include_special=True):
    # Define character sets
    chars = ''
    if include_uppercase:
        chars += string.ascii_uppercase
    if include_lowercase:
        chars += string.ascii_lowercase
    if include_numbers:
        chars += string.digits
    if include_special:
        chars += string.punctuation
    
    # Default to alphanumeric if no options selected
    if not chars:
        chars = string.ascii_letters + string.digits
    
    # Ensure at least one character from each selected category
    password = []
    if include_uppercase and string.ascii_uppercase:
        password.append(random.choice(string.ascii_uppercase))
    if include_lowercase and string.ascii_lowercase:
        password.append(random.choice(string.ascii_lowercase))
    if include_numbers and string.digits:
        password.append(random.choice(string.digits))
    if include_special and string.punctuation:
        password.append(random.choice(string.punctuation))
    
    # Fill the rest of the password
    remaining_length = max(0, length - len(password))
    if chars:
        password.extend(random.choice(chars) for _ in range(remaining_length))
    
    # Shuffle the password
    random.shuffle(password)
    
    return ''.join(password)

# Function to add password to history
def add_to_history(password, strength):
    # Mask password for privacy
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

# Function to check if password is in common breaches
def check_password_breach(password):
    # Simulate a breach check (for demonstration)
    common_passwords = ["password", "123456", "qwerty", "admin", "welcome", "login", "abc123"]
    is_breached = password.lower() in common_passwords or len(password) < 6
    
    return is_breached

# Function to display password checker tab
def show_password_checker():
    st.markdown("<h2>Check Your Password Strength</h2>", unsafe_allow_html=True)
    
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
        
        # Check for breaches
        is_breached = check_password_breach(password)
        if is_breached:
            st.markdown("""
            <div class="card" style="border-left: 4px solid #FF0000; margin-top: 20px;">
                <h3>⚠️ Password Breach Alert</h3>
                <p>This password appears to have been found in data breaches. It is not safe to use!</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="card" style="border-left: 4px solid #00CC00; margin-top: 20px;">
                <h3>✅ No Breaches Found</h3>
                <p>This password does not appear in our breach database. However, always use unique passwords for each account.</p>
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

# Function to display password generator tab
def show_password_generator():
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
    
    # Number of passwords to generate
    num_passwords = st.slider("Number of Passwords to Generate", min_value=1, max_value=5, value=1)
    
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
        
        # Add to generated passwords history
        for pwd in generated_passwords:
            if pwd not in st.session_state.generated_passwords:
                st.session_state.generated_passwords.append(pwd)
                # Keep only the last 10 generated passwords
                if len(st.session_state.generated_passwords) > 10:
                    st.session_state.generated_passwords.pop(0)
        
        # Display generated passwords
        st.markdown("<h3>Generated Passwords</h3>", unsafe_allow_html=True)
        
        for idx, pwd in enumerate(generated_passwords):
            # Evaluate the generated password
            result = evaluate_password_strength(pwd)
            
            # Display the password in a card
            st.markdown(f"""
            <div class="card" style="margin-bottom: 15px;">
                <h4>Password {idx+1}:</h4>
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <code style="font-size: 1.2rem; padding: 10px; background: rgba(0,0,0,0.1); border-radius: 5px;">{pwd}</code>
                </div>
                <p>Strength: <span style="color:{result['strength_level']['color']};">{result['strength_level']['name']} ({int(result['strength_percentage'])}%)</span></p>
                <div class="strength-meter"><div class="strength-fill" style="width:{result['strength_percentage']}%; background:{result['strength_level']['color']};"></div></div>
            </div>
            """, unsafe_allow_html=True)

# Function to display password history tab
def show_password_history():
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

# Function to display tips tab
def show_password_tips():
    st.markdown("<h2>Password Security Tips</h2>", unsafe_allow_html=True)
    
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
        st.markdown(f'<p style="margin: 10px 0; padding: 10px; background: rgba(0,0,0,0.1); border-radius: 5px;">• {tip}</p>', unsafe_allow_html=True)

# Main function
def main():
    try:
        # Apply VIP styling
        apply_vip_styling()
        
        # Initialize session state
        initialize_session_state()
        
        # Developer attribution at the top
        st.markdown('<div class="developer-attribution">Developed by Atfa Siddiqui</div>', unsafe_allow_html=True)
        
        # App title and description
        st.markdown('<div class="vip-container">', unsafe_allow_html=True)
        st.markdown('<h1 class="vip-header">VIP Password Strength Meter</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align:center; font-size:1.2rem;">Check how strong and secure your password is with our premium strength meter</p>', unsafe_allow_html=True)
        
        # Create tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Password Checker", "Password Generator", "Password History", "Security Tips"])
        
        with tab1:
            show_password_checker()
        
        with tab2:
            show_password_generator()
        
        with tab3:
            show_password_history()
        
        with tab4:
            show_password_tips()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Footer with developer attribution
        st.markdown('<div class="footer">Password Strength Meter © 2025 | Secure your digital life with strong passwords<br>Developed by Atfa Siddiqui</div>', unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Please try refreshing the page. If the problem persists, contact support.")

# Run the app
if __name__ == "__main__":
    main()