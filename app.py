import os
import re
import sys
import contextlib
import importlib
import streamlit as st
from dotenv import load_dotenv

# Force reload of agents to ensure changes to agents.py are immediately picked up by Streamlit
import agents
importlib.reload(agents)
from agents import run_content_studio

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="GenAI Multi-Agent Content Studio",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Premium Styling (Cosmic Amethyst & Amber Gold Glassmorphism Theme)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=JetBrains+Mono:wght@400;500&family=Inter:wght@300;400;600&display=swap');
    
    /* Hide sidebar and its toggle control completely */
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    
    /* Custom Scrollbars */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #0b0813;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(155, 89, 182, 0.35);
        border-radius: 4px;
        transition: background 0.3s ease;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(241, 196, 15, 0.65);
    }
    
    /* Main App Background & Fonts (Amethyst Obsidian Ambient Aura) */
    .stApp {
        background: radial-gradient(circle at 15% 15%, rgba(241, 196, 15, 0.08) 0%, transparent 45%),
                    radial-gradient(circle at 85% 85%, rgba(155, 89, 182, 0.1) 0%, transparent 45%),
                    radial-gradient(circle at 50% 50%, #130a24 0%, #06030c 100%) !important;
        color: #F1F5F9;
        font-family: 'Inter', sans-serif;
    }
    
    /* Titles & Subheadings */
    h1, h2, h3 {
        font-family: 'Outfit', sans-serif;
        color: #F8FAFC;
    }
    
    /* Glowing Neon Title Banner with moving gradient text */
    .title-banner {
        background: linear-gradient(90deg, #F1C40F, #E67E22, #9B59B6, #E84393, #F1C40F);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.8rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
        font-family: 'Outfit', sans-serif;
        text-align: center;
        animation: gradientMove 6s linear infinite;
        text-shadow: 0 0 35px rgba(155, 89, 182, 0.25);
    }
    @keyframes gradientMove {
        0% { background-position: 0% 50%; }
        100% { background-position: 200% 50%; }
    }
    .subtitle-banner {
        color: #A5A5C7;
        font-size: 1.15rem;
        text-align: center;
        margin-bottom: 3rem;
        letter-spacing: 0.5px;
    }
    
    /* Glassmorphic settings container overrides with interactive glow border */
    div[data-testid="stContainer"] {
        background: rgba(18, 12, 30, 0.65) !important;
        backdrop-filter: blur(25px);
        border: 1px solid rgba(155, 89, 182, 0.22) !important;
        border-radius: 18px !important;
        padding: 1.8rem !important;
        box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.85), inset 0 1px 1px rgba(255, 255, 255, 0.05) !important;
        transition: all 0.3s ease;
    }
    div[data-testid="stContainer"]:hover {
        border-color: rgba(241, 196, 15, 0.45) !important;
        box-shadow: 0 25px 50px -12px rgba(241, 196, 15, 0.15), 0 20px 40px -15px rgba(0, 0, 0, 0.85) !important;
    }
    
    /* macOS-style terminal top bar */
    .mac-header {
        background: #19102c;
        padding: 12px 18px;
        display: flex;
        align-items: center;
        border: 1px solid rgba(155, 89, 182, 0.22);
        border-bottom: none;
        border-radius: 12px 12px 0 0;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    }
    .mac-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
        display: inline-block;
    }
    .mac-dot.red { background: #FF5F56; }
    .mac-dot.yellow { background: #FFBD2E; }
    .mac-dot.green { background: #27C93F; }
    .mac-title {
        color: #A5A5C7;
        font-size: 0.85rem;
        margin-left: auto;
        margin-right: auto;
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        transform: translateX(-30px);
        letter-spacing: 1px;
    }
    
    /* Inputs glowing focus settings */
    div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea {
        background-color: rgba(18, 12, 30, 0.8) !important;
        color: #F8FAFC !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 10px !important;
        padding: 0.6rem 0.8rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    div[data-testid="stTextInput"] input:focus, div[data-testid="stTextArea"] textarea:focus {
        border-color: #F1C40F !important;
        box-shadow: 0 0 15px rgba(241, 196, 15, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
        background-color: #1e1335 !important;
    }
    
    /* Shimmering Action & Download Buttons */
    div.stButton > button:first-child,
    div.stDownloadButton > button:first-child {
        background: linear-gradient(135deg, #FFE066 0%, #F1C40F 50%, #E67E22 100%) !important;
        background-size: 300% 300% !important;
        color: #130a24 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.9rem 2.2rem !important;
        font-size: 1.1rem !important;
        font-weight: 800 !important;
        font-family: 'Outfit', sans-serif !important;
        letter-spacing: 0.8px !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        box-shadow: 0 10px 25px -8px rgba(241, 196, 15, 0.4) !important;
        width: 100%;
        animation: buttonGlow 4s infinite alternate;
    }
    
    /* Force all inner text elements (spans, paragraphs) to inherit the dark amethyst color */
    div.stButton > button:first-child *,
    div.stDownloadButton > button:first-child * {
        color: #130a24 !important;
        font-weight: 800 !important;
    }
    
    @keyframes buttonGlow {
        0% { background-position: 0% 50%; box-shadow: 0 8px 20px -8px rgba(241, 196, 15, 0.35); }
        50% { background-position: 100% 50%; box-shadow: 0 12px 28px -4px rgba(243, 156, 18, 0.55); }
        100% { background-position: 0% 50%; box-shadow: 0 8px 20px -8px rgba(241, 196, 15, 0.35); }
    }
    
    div.stButton > button:first-child:hover,
    div.stDownloadButton > button:first-child:hover {
        box-shadow: 0 15px 35px -4px rgba(241, 196, 15, 0.6) !important;
        filter: brightness(1.08) !important;
    }
    
    div.stButton > button:first-child:hover *,
    div.stDownloadButton > button:first-child:hover * {
        color: #130a24 !important;
    }
    
    div.stButton > button:first-child:active,
    div.stDownloadButton > button:first-child:active {
        transform: scale(0.98) !important;
    }
    
    div.stButton > button:first-child:active *,
    div.stDownloadButton > button:first-child:active * {
        color: #130a24 !important;
    }
    
    /* Tabs customization to match glassmorphism */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(18, 12, 30, 0.45) !important;
        padding: 6px !important;
        border-radius: 0 0 12px 12px !important;
        border: 1px solid rgba(155, 89, 182, 0.2) !important;
        border-top: none !important;
        gap: 6px !important;
        width: 100%;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        border: none !important;
        color: #A5A5C7 !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.6rem !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #F8FAFC !important;
        background-color: rgba(255, 255, 255, 0.05) !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(241, 196, 15, 0.2) 0%, rgba(155, 89, 182, 0.2) 100%) !important;
        border: 1px solid rgba(241, 196, 15, 0.45) !important;
        color: #F1C40F !important;
        box-shadow: 0 4px 15px rgba(241, 196, 15, 0.15) !important;
    }
    
    /* Code output text styling */
    code {
        color: #F1C40F !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    p, li {
        line-height: 1.7;
        color: #D1D1E9;
    }
    
    /* Custom metric card system (Amethyst Amber Glow Theme) */
    .metrics-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 1rem;
        margin-top: 0.5rem;
    }
    @media (min-width: 480px) {
        .metrics-grid {
            grid-template-columns: repeat(3, 1fr);
        }
    }
    .metric-card {
        background: rgba(18, 12, 30, 0.65) !important;
        backdrop-filter: blur(20px);
        border: 1px solid rgba(155, 89, 182, 0.18) !important;
        border-radius: 16px;
        padding: 1.25rem;
        text-align: center;
        position: relative;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 3px;
        background: transparent;
        transition: all 0.4s ease;
    }
    .metrics-grid .metric-card:nth-child(1)::before {
        background: linear-gradient(90deg, #F1C40F, #F39C12);
    }
    .metrics-grid .metric-card:nth-child(2)::before {
        background: linear-gradient(90deg, #E84393, #D63031);
    }
    .metrics-grid .metric-card:nth-child(3)::before {
        background: linear-gradient(90deg, #2ECC71, #27AE60);
    }
    
    .metric-card:hover {
        transform: translateY(-8px);
        border-color: rgba(241, 196, 15, 0.35) !important;
    }
    .metrics-grid .metric-card:nth-child(1):hover {
        box-shadow: 0 15px 30px rgba(241, 196, 15, 0.15), 0 0 15px rgba(241, 196, 15, 0.05);
        border-color: rgba(241, 196, 15, 0.4) !important;
    }
    .metrics-grid .metric-card:nth-child(2):hover {
        box-shadow: 0 15px 30px rgba(232, 67, 147, 0.15), 0 0 15px rgba(232, 67, 147, 0.05);
        border-color: rgba(232, 67, 147, 0.4) !important;
    }
    .metrics-grid .metric-card:nth-child(3):hover {
        box-shadow: 0 15px 30px rgba(46, 204, 113, 0.15), 0 0 15px rgba(46, 204, 113, 0.05);
        border-color: rgba(46, 204, 113, 0.4) !important;
    }
    .metric-icon {
        font-size: 1.6rem;
        margin-bottom: 0.25rem;
    }
    .metric-label {
        font-size: 0.75rem;
        color: #A5A5C7;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        font-weight: 500;
    }
    .metric-value {
        font-size: 1.3rem;
        font-weight: 700;
        color: #F8FAFC;
        font-family: 'JetBrains Mono', monospace;
        margin-top: 0.25rem;
    }
    .metric-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.65rem;
        font-weight: 700;
        margin-top: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* INTERACTIVE ROBOT DRONE ANIMATIONS */
    .robot-box {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 1.5rem;
        background: rgba(18, 12, 30, 0.45) !important;
        border: 1px solid rgba(155, 89, 182, 0.2) !important;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
    }
    
    .floating-robot {
        animation: floatRobot 3.5s ease-in-out infinite;
    }
    
    @keyframes floatRobot {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-12px) rotate(1deg); }
        100% { transform: translateY(0px) rotate(0deg); }
    }
    
    .eye-blink {
        animation: blinkEye 5s infinite;
        transform-origin: 50% 50%;
    }
    
    @keyframes blinkEye {
        0%, 90%, 100% { transform: scaleY(1); }
        95% { transform: scaleY(0.1); }
    }
    
    .antenna-glow {
        animation: pulseAntenna 1.8s infinite alternate;
    }
    
    @keyframes pulseAntenna {
        0% { fill: #9B59B6; filter: drop-shadow(0 0 2px rgba(155, 89, 182, 0.5)); }
        100% { fill: #F1C40F; filter: drop-shadow(0 0 10px rgba(241, 196, 15, 0.9)); }
    }
    
    .hover-glow {
        animation: hoverPulse 0.9s infinite alternate;
        opacity: 0.8;
    }
    
    @keyframes hoverPulse {
        0% { rx: 11; ry: 4; fill: #9B59B6; opacity: 0.5; }
        100% { rx: 16; ry: 5.5; fill: #F1C40F; opacity: 0.9; filter: drop-shadow(0 0 8px rgba(241, 196, 15, 0.8)); }
    }
    
    /* Flying Letter Animation (Config to Terminal) */
    .animation-stage {
        width: 100%;
        height: 60px;
        position: relative;
        display: flex;
        justify-content: center;
        align-items: center;
        overflow: hidden;
        margin-top: 5px;
    }
    
    .flying-letter {
        font-size: 1.8rem;
        position: absolute;
        animation: sendLetter 2s cubic-bezier(0.25, 0.8, 0.25, 1) infinite;
        filter: drop-shadow(0 0 8px rgba(241, 196, 15, 0.6));
    }
    
    @keyframes sendLetter {
        0% { transform: translateX(-150px) translateY(-10px) scale(0.4) rotate(0deg); opacity: 0; }
        15% { opacity: 1; }
        85% { opacity: 1; }
        100% { transform: translateX(150px) translateY(10px) scale(1) rotate(360deg); opacity: 0; }
    }
    
    /* Flying Document Animation (Terminal to Workspace) */
    .flying-doc {
        font-size: 1.8rem;
        position: absolute;
        animation: receiveDoc 2s cubic-bezier(0.25, 0.8, 0.25, 1) infinite;
        filter: drop-shadow(0 0 8px rgba(46, 204, 113, 0.6));
    }
    
    @keyframes receiveDoc {
        0% { transform: translateX(-150px) translateY(10px) scale(0.4) rotate(0deg); opacity: 0; }
        15% { opacity: 1; }
        85% { opacity: 1; }
        100% { transform: translateX(150px) translateY(-10px) scale(1) rotate(-360deg); opacity: 0; }
    }
    
    /* Make the Left Config Column Sticky */
    [data-testid="column"]:nth-of-type(1) {
        position: -webkit-sticky !important;
        position: sticky !important;
        top: 2.5rem !important;
        align-self: start !important;
    }
    
    /* ROBOTS WORKFLOW LAYOUT & ANIMATIONS */
    .robots-workflow-container {
        display: flex;
        justify-content: space-around;
        align-items: center;
        padding: 1.5rem 1rem;
        background: rgba(18, 12, 30, 0.45) !important;
        border: 1px solid rgba(155, 89, 182, 0.2) !important;
        border-radius: 12px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
    }
    
    .robot-card {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100px;
        z-index: 2;
    }
    
    .robot-label {
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        font-family: 'Outfit', sans-serif;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
    }
    
    .workflow-connector {
        flex-grow: 1;
        height: 4px;
        background: rgba(255, 255, 255, 0.05);
        position: relative;
        margin: 0 15px;
        border-radius: 2px;
    }
    
    .connector-line-active {
        position: absolute;
        top: 0;
        left: 0;
        height: 100%;
        width: 100%;
        background: linear-gradient(90deg, #F1C40F, #9B59B6);
        box-shadow: 0 0 8px #F1C40F;
        animation: activePulse 2s infinite alternate;
    }
    
    @keyframes activePulse {
        0% { opacity: 0.6; }
        100% { opacity: 1; filter: drop-shadow(0 0 4px #F1C40F); }
    }
    
    /* Animations for active flying letters/documents */
    .letter-flow-1, .letter-flow-2, .letter-flow-brief, .letter-flow-finished {
        font-size: 1.5rem;
        position: absolute;
        top: 50%;
        left: 0;
        animation: flowAcross 1.8s linear infinite;
        z-index: 5;
    }
    
    .letter-flow-brief {
        filter: drop-shadow(0 0 6px #F1C40F);
    }
    .letter-flow-1 {
        filter: drop-shadow(0 0 6px #E84393);
    }
    .letter-flow-2 {
        filter: drop-shadow(0 0 6px #2ECC71);
    }
    .letter-flow-finished {
        filter: drop-shadow(0 0 6px #2ECC71);
        animation-iteration-count: 1 !important;
        animation-fill-mode: forwards !important;
    }
    
    @keyframes flowAcross {
        0% { left: 0%; transform: translateY(-50%) scale(0.6) rotate(0deg); opacity: 0; }
        15% { opacity: 1; }
        85% { opacity: 1; }
        100% { left: 100%; transform: translateY(-50%) scale(1.1) rotate(360deg); opacity: 0; }
    }
    
    /* Hide Streamlit text area helper hint watermark safely */
    div[data-testid="stTextAreaRootElement"] > div:nth-child(2) {
        display: none !important;
    }
    
    /* Force header background to be transparent and its buttons/icons to remain white/visible in all modes */
    header[data-testid="stHeader"], 
    .stAppHeader,
    header {
        background-color: transparent !important;
        background: transparent !important;
    }
    header[data-testid="stHeader"] button, 
    header[data-testid="stHeader"] svg, 
    .stAppHeader button, 
    .stAppHeader svg,
    header button,
    header svg {
        color: #F8FAFC !important;
        fill: #F8FAFC !important;
    }
    
    </style>
""", unsafe_allow_html=True)

# Context manager to redirect stdout (agent logs) to a Streamlit container
@contextlib.contextmanager
def st_stdout_redirect(placeholder):
    class StreamToStreamlit:
        def __init__(self, placeholder):
            self.placeholder = placeholder
            self.buffer = []
            self.ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

        def write(self, data):
            clean_data = self.ansi_escape.sub('', data)
            if clean_data.strip() and not clean_data.startswith("[CrewAIEventsBus]"):
                self.buffer.append(clean_data)
                logs = "".join(self.buffer[-25:])
                
                from streamlit.runtime.scriptrunner import get_script_run_ctx
                if get_script_run_ctx() is not None:
                    try:
                        self.placeholder.code(logs)
                    except Exception:
                        pass
                sys.__stdout__.write(data)

        def flush(self):
            sys.__stdout__.flush()

    old_stdout = sys.stdout
    sys.stdout = StreamToStreamlit(placeholder)
    try:
        yield
    finally:
        sys.stdout = old_stdout

# Robust Line-by-line Markdown Parser
def parse_sections(raw_text: str):
    # Normalize carriage returns
    raw_text = raw_text.replace('\r\n', '\n')
    
    # Strategy 1: Exact check for the new standard "# SECTION: <NAME>"
    lines = raw_text.split('\n')
    
    blog_lines = []
    linkedin_lines = []
    twitter_lines = []
    
    current_section = "blog"  # Default starts with blog
    
    for line in lines:
        stripped = line.strip()
        lower_line = stripped.lower()
        
        # Check if line indicates a section change
        is_header = False
        if (stripped.startswith('#') or 
            stripped.startswith('*') or 
            stripped.startswith('_') or 
            stripped.startswith('-') or 
            stripped.startswith('=')):
            is_header = True
            
        is_linkedin_marker = False
        is_twitter_marker = False
        is_blog_marker = False
        
        # Clean line to check for exact title matches
        clean_lower = lower_line.replace('#', '').replace('*', '').replace('_', '').replace(':', '').strip()
        
        if is_header or len(stripped) < 50:
            if "linkedin" in lower_line:
                if "section:" in lower_line or clean_lower in ["linkedin", "linkedin post", "linkedin status", "linkedin status update", "for linkedin"]:
                    is_linkedin_marker = True
            elif "twitter" in lower_line or "tweet" in lower_line or " x " in lower_line or lower_line.endswith(" x") or "thread" in lower_line:
                if "section:" in lower_line or clean_lower in ["twitter", "twitter thread", "tweets", "tweet thread", "x thread", "twitter/x thread", "twitter / x thread", "thread"]:
                    is_twitter_marker = True
            elif "blog" in lower_line:
                if "section:" in lower_line or clean_lower in ["blog", "blog post", "article", "blog article"]:
                    is_blog_marker = True
                        
        if is_linkedin_marker:
            current_section = "linkedin"
            continue
        elif is_twitter_marker:
            current_section = "twitter"
            continue
        elif is_blog_marker:
            current_section = "blog"
            continue
                
        # Append line to active section buffer
        if current_section == "blog":
            blog_lines.append(line)
        elif current_section == "linkedin":
            linkedin_lines.append(line)
        elif current_section == "twitter":
            twitter_lines.append(line)
            
    blog_content = "\n".join(blog_lines).strip()
    linkedin_content = "\n".join(linkedin_lines).strip()
    twitter_content = "\n".join(twitter_lines).strip()
    
    # Strategy 2: Fallback to Regex Split if linkedin or twitter content is still empty
    if not linkedin_content or not twitter_content:
        # Regex search for headers containing the keywords
        patterns = [
            r'(?:#+|\*\*)\s*(?:SECTION:\s*)?BLOG(?:\s*POST)?\s*(?:\*\*)?',
            r'(?:#+|\*\*)\s*(?:SECTION:\s*)?LINKEDIN(?:\s*POST)?\s*(?:\*\*)?',
            r'(?:#+|\*\*)\s*(?:SECTION:\s*)?TWITTER(?:\s*THREAD|\s*POST)?\s*(?:\*\*)?',
            r'(?:#+|\*\*)\s*(?:SECTION:\s*)?(?:TWEET|X)(?:\s*THREAD|\s*POST)?\s*(?:\*\*)?'
        ]
        
        matches = []
        for pat in patterns:
            for m in re.finditer(pat, raw_text, flags=re.IGNORECASE):
                matches.append((m.start(), m.end(), m.group(0)))
                
        if len(matches) >= 2:
            matches.sort(key=lambda x: x[0])
            
            sections = []
            last_end = 0
            for i in range(len(matches)):
                start, end, text = matches[i]
                sections.append((last_end, start, text))
                last_end = end
            sections.append((last_end, len(raw_text), "END"))
            
            # Temporary buffers
            temp_blog = []
            temp_linkedin = []
            temp_twitter = []
            
            # The part before the first match is blog
            first_start = matches[0][0]
            temp_blog.append(raw_text[0:first_start])
            
            for i in range(len(matches)):
                start, end, label = matches[i]
                next_start = sections[i+1][1]
                content = raw_text[end:next_start].strip()
                
                label_lower = label.lower()
                if "linkedin" in label_lower:
                    temp_linkedin.append(content)
                elif "twitter" in label_lower or "tweet" in label_lower or "x" in label_lower or "thread" in label_lower:
                    temp_twitter.append(content)
                elif "blog" in label_lower:
                    temp_blog.append(content)
                    
            # If the split was successful, update contents
            if temp_blog:
                blog_content = "\n\n".join(temp_blog).strip()
            if temp_linkedin:
                linkedin_content = "\n\n".join(temp_linkedin).strip()
            if temp_twitter:
                twitter_content = "\n\n".join(temp_twitter).strip()
                
    # Strategy 3: Individual tab check - do NOT replace successfully parsed text with warning text!
    if not blog_content.strip():
        blog_content = raw_text
    if not linkedin_content.strip():
        linkedin_content = "LinkedIn Post not auto-separated. Please copy it from the Raw Markdown tab."
    if not twitter_content.strip():
        twitter_content = "Twitter/X Thread not auto-separated. Please copy it from the Raw Markdown tab."
        
    return blog_content, linkedin_content, twitter_content

# Calculate API cost helper
def calculate_cost(prompt_tokens, completion_tokens, provider):
    pricing = {
        "Google Gemini": {"input": 0.075, "output": 0.30},      # Gemini 1.5 Flash rates per 1M tokens
        "OpenAI": {"input": 0.150, "output": 0.600},             # GPT-4o-mini rates per 1M tokens
        "Anthropic Claude": {"input": 0.80, "output": 4.00},     # Claude 3.5 Haiku rates per 1M tokens
        "Groq": {"input": 0.59, "output": 0.79}                  # Llama 3.1 70B rates per 1M tokens
    }
    rates = pricing.get(provider, {"input": 0.075, "output": 0.30})
    input_cost = (prompt_tokens / 1_000_000) * rates["input"]
    output_cost = (completion_tokens / 1_000_000) * rates["output"]
    return input_cost + output_cost

# Helper to generate animated Robot SVGs dynamically
# Helper to generate three-agent robot workflow SVG/HTML layout dynamically
def get_workflow_html(state: str) -> str:
    r_status = "sleeping"
    w_status = "sleeping"
    e_status = "sleeping"
    
    flow_brief = False
    flow_1 = False
    flow_2 = False
    flow_finished = False
    
    status_text = "Idle"
    status_color = "#A5A5C7"
    
    if state == "brief":
        r_status = "receiving"
        flow_brief = True
        status_text = "Ingesting brief and routing to Researcher..."
        status_color = "#F1C40F"
    elif state == "researching":
        r_status = "working"
        status_text = "Researcher is actively scanning the web..."
        status_color = "#F1C40F"
    elif state == "sending_to_writer":
        r_status = "finished"
        w_status = "receiving"
        flow_1 = True
        status_text = "Transmitting research findings to Content Writer..."
        status_color = "#E67E22"
    elif state == "writing":
        r_status = "finished"
        w_status = "working"
        status_text = "Content Writer is drafting posts..."
        status_color = "#E67E22"
    elif state == "sending_to_editor":
        r_status = "finished"
        w_status = "finished"
        e_status = "receiving"
        flow_2 = True
        status_text = "Transmitting draft to Editor Director..."
        status_color = "#2ECC71"
    elif state == "editing":
        r_status = "finished"
        w_status = "finished"
        e_status = "working"
        status_text = "Editor is proofreading and polishing..."
        status_color = "#2ECC71"
    elif state == "finished":
        r_status = "finished"
        w_status = "finished"
        e_status = "finished"
        flow_finished = True
        status_text = "Hub generated successfully! Outputting files..."
        status_color = "#2ECC71"
    else:
        status_text = "Ready to start content generation pipeline."
        status_color = "#A5A5C7"

    def make_robot_svg(eye_color, antenna_color, hover_color, mode):
        is_working = mode == "working" or mode == "receiving"
        is_finished = mode == "finished"
        
        float_class = "class='floating-robot'" if is_working else ""
        blink_class = "class='eye-blink'" if is_working else ""
        antenna_class = "class='antenna-glow'" if is_working else ""
        hover_class = "class='hover-glow'" if (is_working or is_finished) else ""
        
        stroke_color = eye_color if (is_working or is_finished) else "#334155"
        rect_fill = "#19102c"
        path_opacity = "1" if (is_working or is_finished) else "0.3"
        mouth_color = "#E2E8F0" if (is_working or is_finished) else "#475569"
        
        mouth_path = "M 43 58 Q 50 63 57 58" if not is_finished else "M 41 57 Q 50 65 59 57"
        
        return f"<div style='display:flex; justify-content:center; align-items:center;'><svg {float_class} viewBox='0 0 100 100' width='75' height='75'><line x1='50' y1='30' x2='50' y2='15' stroke='{stroke_color}' stroke-width='3'/><circle cx='50' cy='12' r='6' fill='{antenna_color}' {antenna_class}/><circle cx='20' cy='50' r='5' fill='{stroke_color}'/><circle cx='80' cy='50' r='5' fill='{stroke_color}'/><rect x='25' y='30' width='50' height='40' rx='15' fill='{rect_fill}' stroke='{stroke_color}' stroke-width='3'/><ellipse cx='41' cy='48' rx='5' ry='7' fill='{stroke_color}' {blink_class}/><ellipse cx='59' cy='48' rx='5' ry='7' fill='{stroke_color}' {blink_class}/><path d='{mouth_path}' fill='none' stroke='{mouth_color}' stroke-width='2.5' stroke-linecap='round' opacity='{path_opacity}'/><ellipse cx='50' cy='78' rx='12' ry='4.5' fill='{hover_color}' {hover_class}/></svg></div>"

    if r_status == "working" or r_status == "receiving":
        r_eye, r_ant, r_hov = "#F1C40F", "#9B59B6", "#F1C40F"
        r_lbl_style = "color:#F1C40F; text-shadow:0 0 8px rgba(241,196,15,0.6);"
    elif r_status == "finished":
        r_eye, r_ant, r_hov = "#2ECC71", "#2ECC71", "#2ECC71"
        r_lbl_style = "color:#2ECC71;"
    else:
        r_eye, r_ant, r_hov = "#334155", "#334155", "transparent"
        r_lbl_style = "color:#475569;"

    if w_status == "working" or w_status == "receiving":
        w_eye, w_ant, w_hov = "#E67E22", "#E84393", "#E67E22"
        w_lbl_style = "color:#E67E22; text-shadow:0 0 8px rgba(230,126,34,0.6);"
    elif w_status == "finished":
        w_eye, w_ant, w_hov = "#2ECC71", "#2ECC71", "#2ECC71"
        w_lbl_style = "color:#2ECC71;"
    else:
        w_eye, w_ant, w_hov = "#334155", "#334155", "transparent"
        w_lbl_style = "color:#475569;"

    if e_status == "working" or e_status == "receiving":
        e_eye, e_ant, e_hov = "#2ECC71", "#F1C40F", "#2ECC71"
        e_lbl_style = "color:#2ECC71; text-shadow:0 0 8px rgba(46,204,113,0.6);"
    elif e_status == "finished":
        e_eye, e_ant, e_hov = "#2ECC71", "#2ECC71", "#2ECC71"
        e_lbl_style = "color:#2ECC71;"
    else:
        e_eye, e_ant, e_hov = "#334155", "#334155", "transparent"
        e_lbl_style = "color:#475569;"

    c1_active = "connector-line-active" if (w_status != "sleeping" or flow_1) else ""
    c2_active = "connector-line-active" if (e_status != "sleeping" or flow_2) else ""
    
    html = []
    html.append("<div class='robots-workflow-container'>")
    
    # Brief ingestion connector (stable layout positioning)
    html.append(f"<div class='workflow-connector' style='max-width: 60px; min-width: 40px;'><div class=\"{'connector-line-active' if flow_brief else ''}\"></div>")
    if flow_brief:
        html.append("<div class='letter-flow-brief'>✉️</div>")
    html.append("</div>")
    
    # Researcher Robot
    html.append(f"<div class='robot-card'><div class='robot-label' style='{r_lbl_style}'>Researcher</div>{make_robot_svg(r_eye, r_ant, r_hov, r_status)}</div>")
    
    # Connector 1
    html.append(f"<div class='workflow-connector'><div class='{c1_active}'></div>")
    if flow_1:
        html.append("<div class='letter-flow-1'>📄</div>")
    html.append("</div>")
    
    # Writer Robot
    html.append(f"<div class='robot-card'><div class='robot-label' style='{w_lbl_style}'>Writer</div>{make_robot_svg(w_eye, w_ant, w_hov, w_status)}</div>")
    
    # Connector 2
    html.append(f"<div class='workflow-connector'><div class='{c2_active}'></div>")
    if flow_2:
        html.append("<div class='letter-flow-2'>📄</div>")
    html.append("</div>")
    
    # Editor Robot
    html.append(f"<div class='robot-card'><div class='robot-label' style='{e_lbl_style}'>Editor</div>{make_robot_svg(e_eye, e_ant, e_hov, e_status)}</div>")
    
    # Finished output connector (stable layout positioning)
    html.append(f"<div class='workflow-connector' style='max-width: 60px; min-width: 40px;'><div class=\"{'connector-line-active' if flow_finished else ''}\"></div>")
    if flow_finished:
        html.append("<div class='letter-flow-finished'>📄</div>")
    html.append("</div>")
    
    html.append("</div>")
    html.append(f"<div style='text-align:center; font-size:1.05rem; font-weight:600; color:{status_color}; margin-top:0.5rem;'>{status_text}</div>")
    
    return "".join(html)

# Helper to evaluate topic prompt quality
def evaluate_prompt(topic: str, provider: str, api_key: str) -> dict:
    import litellm
    
    provider_mapping = {
        "Google Gemini": "gemini/gemini-flash-latest",
        "OpenAI": "openai/gpt-4o-mini",
        "Anthropic Claude": "anthropic/claude-3-5-haiku-20241022",
        "Groq": "groq/llama-3.3-70b-versatile"
    }
    model_name = provider_mapping.get(provider, "gemini/gemini-flash-latest")
    
    prompt = f"""Evaluate the following content hub topic brief for detail, clarity, and suitability for content generation.
Rate it out of 10 (1 is extremely vague, e.g. "python"; 10 is highly detailed and contextual, e.g. "Advanced Python decorators for logging and rate-limiting in FastAPI").
Provide a short, constructive 1-sentence feedback message.

Return the output in this exact format:
RATING: [score]
FEEDBACK: [feedback]

Topic to evaluate: "{topic}" """
    
    try:
        response = litellm.completion(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            api_key=api_key,
            temperature=0.0
        )
        content = response.choices[0].message.content.strip()
        
        # Parse output
        rating = 5
        feedback = "Good start, try adding more context."
        
        for line in content.split("\n"):
            if line.startswith("RATING:"):
                rating_str = line.replace("RATING:", "").replace("/10", "").strip()
                try:
                    rating = int(float(rating_str))
                except ValueError:
                    pass
            elif line.startswith("FEEDBACK:"):
                feedback = line.replace("FEEDBACK:", "").strip()
                
        return {"rating": rating, "feedback": feedback}
    except Exception as e:
        return {"rating": None, "feedback": f"Could not evaluate: {e}"}

# 1. Main Page structure

st.markdown("<div class='title-banner'>GenAI Multi-Agent Content Studio</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle-banner'>Watch Researcher, Writer, and Editor AI Agents collaborate to produce high-value content hubs</div>", unsafe_allow_html=True)

# 2. Main Dual-Pane Columns
left_col, right_col = st.columns([1, 1.5], gap="large")

with left_col:
    st.markdown("<h3 style='margin-top:0;'>⚙️ Content Brief & Config</h3>", unsafe_allow_html=True)
    
    # Wrap settings in a clean visual container
    with st.container(border=True):
        # Dropdown to choose LLM Provider
        provider = st.selectbox(
            "Select LLM Provider:",
            ["Google Gemini", "OpenAI", "Anthropic Claude", "Groq"]
        )
        
        # Map provider to default environment variable names
        env_mapping = {
            "Google Gemini": "GOOGLE_API_KEY",
            "OpenAI": "OPENAI_API_KEY",
            "Anthropic Claude": "ANTHROPIC_API_KEY",
            "Groq": "GROQ_API_KEY"
        }
        
        env_var_name = env_mapping[provider]
        env_api_key = os.getenv(env_var_name)
        
        # Prompt for API Key (immediately after provider selection)
        if env_api_key:
            st.success(f"System {provider} API Key detected!")
            st.session_state["api_key"] = env_api_key
            
            # Allow optional override
            override_key = st.text_input(
                f"Override {provider} Key (Optional):",
                type="password",
                placeholder=f"Paste custom {provider} Key here..."
            )
            if override_key.strip():
                st.session_state["api_key"] = override_key.strip()
        else:
            st.info(f"Provide your {provider} API Key to enable the content studio.")
            user_key = st.text_input(
                f"{provider} API Key:",
                type="password",
                placeholder=f"Paste {provider} Key (starts with AIzaSy... or sk-...)"
            )
            if user_key.strip():
                st.session_state["api_key"] = user_key.strip()
            else:
                if "api_key" in st.session_state:
                    del st.session_state["api_key"]
                    
        # Check if API Key is present, and display warning directly under input fields
        has_api_key = "api_key" in st.session_state
        if not has_api_key:
            st.warning(f"⚠️ {provider} API Key Required. Please input your key above to enable.")
                    
        st.write("---")
        
        # Dropdown to choose Tone (Idea A)
        tone = st.selectbox(
            "Select Content Tone:",
            ["Technical & In-Depth", "Casual & Engaging", "Academic & Serious", "Short & Punchy"]
        )
        
        # Topic input box
        topic_input = st.text_area(
            "What topic would you like to build a content hub for?",
            placeholder="e.g., Python Decorators, FastAPI best practices...",
            height=100
        )
        
        # Disable the button if API key is not present
        has_api_key = "api_key" in st.session_state
        
        # Prompt strength evaluation UI
        if topic_input.strip() and has_api_key:
            state_topic = st.session_state.get("evaluated_topic")
            state_provider = st.session_state.get("evaluated_provider")
            
            if state_topic != topic_input or state_provider != provider:
                with st.spinner("🔍 Evaluating prompt strength..."):
                    eval_res = evaluate_prompt(topic_input, provider, st.session_state["api_key"])
                    st.session_state["prompt_rating"] = eval_res["rating"]
                    st.session_state["prompt_feedback"] = eval_res["feedback"]
                    st.session_state["evaluated_topic"] = topic_input
                    st.session_state["evaluated_provider"] = provider
                    
            rating = st.session_state.get("prompt_rating")
            feedback = st.session_state.get("prompt_feedback")
            
            if rating is not None:
                color = "#10B981" if rating >= 8 else ("#F59E0B" if rating >= 5 else "#EF4444")
                label = "Excellent" if rating >= 8 else ("Good" if rating >= 5 else "Needs Detail")
                st.markdown(
                    f"<div style='background-color:rgba(14, 19, 48, 0.3); border-left: 4px solid {color}; "
                    f"padding: 0.6rem 1rem; border-radius: 4px; margin-top: 5px; margin-bottom: 15px;'>"
                    f"<span style='font-weight:600; color:{color}; font-size:0.9rem;'>Prompt Efficiency Rating: {rating}/10 ({label})</span>"
                    f"<div style='font-size:0.85rem; color:#94A3B8; margin-top: 3px;'>{feedback}</div></div>", 
                    unsafe_allow_html=True
                )
            elif feedback:
                st.markdown(
                    f"<div style='background-color:rgba(14, 19, 48, 0.3); border-left: 4px solid #EF4444; "
                    f"padding: 0.6rem 1rem; border-radius: 4px; margin-top: 5px; margin-bottom: 15px;'>"
                    f"<span style='font-weight:600; color:#EF4444; font-size:0.9rem;'>Prompt Efficiency Evaluation Error</span>"
                    f"<div style='font-size:0.85rem; color:#94A3B8; margin-top: 3px;'>{feedback}</div></div>", 
                    unsafe_allow_html=True
                )
        
        generate_btn = st.button("Generate Content Hub", disabled=not has_api_key)
            
    # Metrics & Cost Tracking Dashboard (Idea B)
    if "raw_output" in st.session_state:
        st.write(" ")
        st.markdown("### 📊 Operational Tracker", unsafe_allow_html=True)
        billed_cost = 0.00000 if provider in ["Google Gemini", "Groq"] else st.session_state['est_cost']
        cost_status = "Free Tier" if provider in ["Google Gemini", "Groq"] else "Pay-as-you-go"
        cost_delta_color = "#34D399" if provider in ["Google Gemini", "Groq"] else "#60A5FA"
        
        st.markdown(f"""
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-icon">🪙</div>
                <div class="metric-label">Tokens Spent</div>
                <div class="metric-value">{st.session_state['total_tokens']:,}</div>
            </div>
            <div class="metric-card">
                <div class="metric-icon">📈</div>
                <div class="metric-label">Market Value</div>
                <div class="metric-value">${st.session_state['est_cost']:.5f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-icon">💳</div>
                <div class="metric-label">Billed Cost</div>
                <div class="metric-value">${billed_cost:.5f}</div>
                <div class="metric-badge" style="background-color: {cost_delta_color}22; color: {cost_delta_color};">{cost_status}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with right_col:
    st.markdown("<h3 style='margin-top:0;'>🚀 Production Workspace</h3>", unsafe_allow_html=True)
    
    # State A: Active generation
    if generate_btn:
        if not topic_input.strip():
            st.warning("Please type a topic first.")
        else:
            # macOS Title Bar for Active Run
            st.markdown("""
            <div class='mac-header'>
                <span class='mac-dot red'></span>
                <span class='mac-dot yellow'></span>
                <span class='mac-dot green'></span>
                <span class='mac-title'>AGENT RUNNING: LIVE STREAM</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Live updating workflow container
            workflow_placeholder = st.empty()
            workflow_placeholder.markdown(
                f"<div style='background-color:rgba(14, 19, 48, 0.45); border:1px solid rgba(139, 92, 246, 0.15); border-top:none; padding:1.5rem; margin-bottom: 1rem; border-radius: 0 0 12px 12px;'>{get_workflow_html('brief')}</div>", 
                unsafe_allow_html=True
            )
            
            # Pause briefly to allow user to see the brief-to-researcher transmission animation
            import time
            time.sleep(1.5)
            
            # Update to actively researching
            workflow_placeholder.markdown(
                f"<div style='background-color:rgba(14, 19, 48, 0.45); border:1px solid rgba(139, 92, 246, 0.15); border-top:none; padding:1.5rem; margin-bottom: 1rem; border-radius: 0 0 12px 12px;'>{get_workflow_html('researching')}</div>", 
                unsafe_allow_html=True
            )
            
            # Create execution progress status
            status_box = st.status(f"🎬 Crew is assembling... initializing agents via {provider} ({tone}).", expanded=True)
            
            with status_box:
                # Capture the current Streamlit context to pass down to callback threads
                from streamlit.runtime.scriptrunner import get_script_run_ctx, add_script_run_ctx
                import threading
                main_ctx = get_script_run_ctx()
                
                st.markdown("### 📈 Agent Progress Tracker")
                research_status = st.empty()
                write_status = st.empty()
                edit_status = st.empty()
                
                # Initialize agent progress indicators
                research_status.markdown("🔵 **Researcher Agent** is actively researching the web...")
                write_status.markdown("⚪ **Content Creator Agent** is waiting...")
                edit_status.markdown("⚪ **Editor Agent** is waiting...")
                
                st.write("---")
                
                # Collapsible expander for raw logs to keep UI clean and professional
                log_expander = st.expander("🛠️ View raw agent reasoning logs", expanded=False)
                with log_expander:
                    st.write("💬 **Live Agent Conversation Logs (updating in console & screen when thread-safe):**")
                    log_placeholder = st.empty()
                
                # Define safe update helper to bind Streamlit context to CrewAI's background threads
                def safe_update(element, text, unsafe_html=False):
                    if main_ctx:
                        try:
                            add_script_run_ctx(threading.current_thread())
                        except Exception:
                            pass
                    try:
                        element.markdown(text, unsafe_allow_html=unsafe_html)
                    except Exception:
                        pass
    
                # Define callbacks triggered when tasks are completed
                def on_research_complete():
                    safe_update(research_status, "✅ **Researcher Agent** has completed research!")
                    safe_update(write_status, "🔵 **Content Creator Agent** is drafting the blog & social posts...")
                    
                    # Animate data transmission from Researcher to Writer
                    safe_update(workflow_placeholder, f"<div style='background-color:rgba(14, 19, 48, 0.45); border:1px solid rgba(139, 92, 246, 0.15); border-top:none; padding:1.5rem; margin-bottom: 1rem; border-radius: 0 0 12px 12px;'>{get_workflow_html('sending_to_writer')}</div>", unsafe_html=True)
                    import time
                    time.sleep(1.5)
                    # Start writing
                    safe_update(workflow_placeholder, f"<div style='background-color:rgba(14, 19, 48, 0.45); border:1px solid rgba(139, 92, 246, 0.15); border-top:none; padding:1.5rem; margin-bottom: 1rem; border-radius: 0 0 12px 12px;'>{get_workflow_html('writing')}</div>", unsafe_html=True)
    
                def on_write_complete():
                    safe_update(write_status, "✅ **Content Creator Agent** has completed the drafts!")
                    safe_update(edit_status, "🔵 **Editor Agent** is proofreading and polishing content...")
                    
                    # Animate data transmission from Writer to Editor
                    safe_update(workflow_placeholder, f"<div style='background-color:rgba(14, 19, 48, 0.45); border:1px solid rgba(139, 92, 246, 0.15); border-top:none; padding:1.5rem; margin-bottom: 1rem; border-radius: 0 0 12px 12px;'>{get_workflow_html('sending_to_editor')}</div>", unsafe_html=True)
                    import time
                    time.sleep(1.5)
                    # Start editing
                    safe_update(workflow_placeholder, f"<div style='background-color:rgba(14, 19, 48, 0.45); border:1px solid rgba(139, 92, 246, 0.15); border-top:none; padding:1.5rem; margin-bottom: 1rem; border-radius: 0 0 12px 12px;'>{get_workflow_html('editing')}</div>", unsafe_html=True)
    
                def on_edit_complete():
                    safe_update(edit_status, "✅ **Editor Agent** has completed the review!")
                    safe_update(workflow_placeholder, f"<div style='background-color:rgba(14, 19, 48, 0.45); border:1px solid rgba(139, 92, 246, 0.15); border-top:none; padding:1.5rem; margin-bottom: 1rem; border-radius: 0 0 12px 12px;'>{get_workflow_html('finished')}</div>", unsafe_html=True)
    
                callbacks = {
                    "on_research_complete": on_research_complete,
                    "on_write_complete": on_write_complete,
                    "on_edit_complete": on_edit_complete
                }
                
                try:
                    # Redirect stdout and run crew dynamically
                    with st_stdout_redirect(log_placeholder):
                        run_result = run_content_studio(topic_input, provider, st.session_state["api_key"], tone, callbacks)
                    
                    final_output = run_result["output"]
                    prompt_tokens = run_result["prompt_tokens"]
                    completion_tokens = run_result["completion_tokens"]
                    total_tokens = run_result["total_tokens"]
                    
                    # Calculate estimated cost (Idea B)
                    est_cost = calculate_cost(prompt_tokens, completion_tokens, provider)
                    
                    # Split output into sections
                    blog_post, linkedin_post, twitter_thread = parse_sections(final_output)
                    
                    status_box.update(label="✨ Content Hub generated successfully!", state="complete", expanded=False)
                    
                    # Save results to session state
                    st.session_state["raw_output"] = final_output
                    st.session_state["blog"] = blog_post
                    st.session_state["linkedin"] = linkedin_post
                    st.session_state["twitter"] = twitter_thread
                    st.session_state["total_tokens"] = total_tokens
                    st.session_state["est_cost"] = est_cost
                    st.session_state["last_topic"] = topic_input
                    st.rerun()
                    
                except Exception as e:
                    status_box.update(label="❌ Pipeline execution failed", state="error", expanded=True)
                    st.error(f"Error during execution: {e}")
                    
    # State B: Display finished hub
    elif "raw_output" in st.session_state:
        # macOS Title Bar for Finished Output
        st.markdown("""
        <div class='mac-header'>
            <span class='mac-dot red'></span>
            <span class='mac-dot yellow'></span>
            <span class='mac-dot green'></span>
            <span class='mac-title'>PRODUCTION READY: CONTENT HUB</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Happy Success Robot Drone Container with workflow animation
        success_html = f"<div style='background-color:rgba(14, 19, 48, 0.45); border:1px solid rgba(139, 92, 246, 0.15); border-top:none; padding:1.5rem; margin-bottom: 1rem;'>{get_workflow_html('finished')}</div>"
        st.markdown(success_html, unsafe_allow_html=True)
        
        # Define tabs
        tab_blog, tab_linkedin, tab_twitter, tab_raw = st.tabs([
            "📝 Blog Post", 
            "💼 LinkedIn Post", 
            "🐦 Twitter/X Thread", 
            "📄 Raw Markdown"
        ])
        
        with tab_blog:
            st.markdown(st.session_state["blog"])
            
        with tab_linkedin:
            st.markdown("### LinkedIn Status Update")
            st.info("💡 Highlight and copy the text below to share on LinkedIn.")
            st.text_area("LinkedIn Post Text", value=st.session_state["linkedin"], height=350)
            
        with tab_twitter:
            st.markdown("### Twitter/X Thread")
            st.info("💡 Numbered posts ready to be copy-pasted as a thread.")
            st.text_area("Twitter Thread Text", value=st.session_state["twitter"], height=350)
            
        with tab_raw:
            st.info("💡 Full compiled markdown output containing all sections.")
            st.text_area("Complete Document", value=st.session_state["raw_output"], height=400)
            st.download_button(
                label="Download Complete Markdown",
                data=st.session_state["raw_output"],
                file_name=f"content_hub_{st.session_state.get('last_topic', 'hub').replace(' ', '_').lower()}.md",
                mime="text/markdown"
            )
            
    # State C: Default ready state
    else:
        # macOS Title Bar for Idle State
        st.markdown("""
        <div class='mac-header'>
            <span class='mac-dot red'></span>
            <span class='mac-dot yellow'></span>
            <span class='mac-dot green'></span>
            <span class='mac-title'>STUDIO STATUS: IDLE WORKSPACE</span>
        </div>
        """, unsafe_allow_html=True)
        
        idle_html = f"<div style='background-color:rgba(14, 19, 48, 0.45); border:1px solid rgba(139, 92, 246, 0.15); border-top:none; border-radius:0 0 12px 12px; padding:2rem 1.5rem; text-shadow:none; box-shadow:0 10px 30px -10px rgba(0, 0, 0, 0.5);'>{get_workflow_html('idle')}<div style='font-size:1.2rem; font-weight:600; color:#F8FAFC; margin-top:1.5rem; text-align:center; margin-bottom:0.5rem;'>Your Assistant Drone Team is Online</div><div style='font-size:0.95rem; color:#94A3B8; text-align:center;'>Fill in the content brief on the left and click <b>Generate Content Hub</b> to begin.<br>The drones will ingest your brief and coordinate the Researcher, Writer, and Editor.</div></div>"
        st.markdown(idle_html, unsafe_allow_html=True)
