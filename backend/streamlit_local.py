"""
House Socioeconomic Classification App (Local Version)
Analyze house images to determine owner's socioeconomic status
Built with Streamlit + Google Gemini Vision AI

This version works on your local laptop!
"""

import streamlit as st
import base64
import os
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
import io

# Load environment variables
load_dotenv()

# ============================================
# CONFIGURATION
# ============================================
# Get your API key from: https://aistudio.google.com/apikey
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# Configure Google AI
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# System prompt for house analysis
SYSTEM_PROMPT = """You are an expert socioeconomic analyst specializing in housing assessment in Indonesia.

Your task is to analyze house images and determine the likely socioeconomic status of the owner based on visual indicators.

When analyzing a house, evaluate these factors:
1. **Structure & Size**: House dimensions, number of floors, overall footprint
2. **Construction Materials**: Wood, brick, cement, quality of materials
3. **Roof Condition**: Type (tin, tile, concrete), condition, maintenance
4. **Wall Condition**: Paint, cracks, weathering, finishing quality
5. **Windows & Doors**: Quality, material, security features
6. **Surroundings**: Yard condition, fencing, landscaping
7. **Visible Amenities**: Garage, water tank, satellite dish, AC units
8. **Interior (if visible)**: Furniture, flooring, cleanliness

Based on Indonesian socioeconomic standards (Desil), classify into:
- **Low Income (Miskin)** - Desil 1-2: Basic construction, minimal amenities, signs of poverty
- **Lower-Middle Income** - Desil 3-4: Simple but maintained housing
- **Middle Income** - Desil 5-6: Standard housing with basic modern amenities
- **Upper-Middle Income** - Desil 7-8: Well-maintained, quality construction, good amenities
- **High Income (Kaya)** - Desil 9-10: Luxury construction, premium materials, extensive amenities

Always provide:
1. **Classification**: The socioeconomic category
2. **Confidence Level**: Low/Medium/High
3. **Detailed Reasoning**: Explain what visual indicators led to your conclusion
4. **Key Observations**: Bullet points of important features noticed

Be objective and base your analysis solely on visible evidence in the images."""


# ============================================
# HELPER FUNCTIONS
# ============================================

def analyze_house_image(image_data, additional_context: str = "") -> str:
    """
    Analyze house image using Google Gemini Vision AI
    """
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = f"{SYSTEM_PROMPT}\n\nPlease analyze this house image and determine the socioeconomic status of the owner."
        if additional_context:
            prompt += f"\n\nAdditional context: {additional_context}"
        
        response = model.generate_content([prompt, image_data])
        
        if response and response.text:
            return response.text
        else:
            return "No response from AI"
        
    except Exception as e:
        return f"Error analyzing image: {str(e)}"


# ============================================
# STREAMLIT UI
# ============================================

# Page configuration
st.set_page_config(
    page_title="House Socioeconomic Analyzer",
    page_icon="🏠",
    layout="wide"
)

# Initialize theme in session state
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'  # Default to light theme

# Toggle theme function
def toggle_theme():
    if st.session_state.theme == 'light':
        st.session_state.theme = 'dark'
    else:
        st.session_state.theme = 'light'

# Theme-based CSS
if st.session_state.theme == 'dark':
    st.markdown("""
    <style>
        /* Dark Theme */
        .stApp {
            background-color: #1a1a2e;
            color: #ffffff;
        }
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #4ade80;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        .sub-header {
            font-size: 1.1rem;
            color: #9ca3af;
            text-align: center;
            margin-bottom: 2rem;
        }
        .result-box {
            background-color: #2d2d44;
            border-left: 5px solid #4ade80;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
            color: #e5e7eb;
        }
        .info-box {
            background-color: #2d2d44;
            border-left: 5px solid #fbbf24;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            color: #e5e7eb;
        }
        .classification-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            margin: 5px 0;
        }
        .low-income { background-color: #ef4444; color: white; }
        .lower-middle { background-color: #f97316; color: white; }
        .middle-income { background-color: #eab308; color: black; }
        .upper-middle { background-color: #3b82f6; color: white; }
        .high-income { background-color: #22c55e; color: white; }
        
        .stTextArea textarea {
            background-color: #2d2d44 !important;
            color: #ffffff !important;
            border-color: #4b5563 !important;
        }
        .stFileUploader {
            background-color: #2d2d44;
            border-radius: 10px;
        }
        section[data-testid="stSidebar"] {
            background-color: #16213e;
        }
        section[data-testid="stSidebar"] * {
            color: #e5e7eb !important;
        }
        .stButton>button {
            background-color: #4ade80;
            color: #1a1a2e;
            font-weight: bold;
        }
        .stButton>button:hover {
            background-color: #22c55e;
        }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        /* Light Theme */
        .stApp {
            background-color: #ffffff;
            color: #1f2937;
        }
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #059669;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        .sub-header {
            font-size: 1.1rem;
            color: #6b7280;
            text-align: center;
            margin-bottom: 2rem;
        }
        .result-box {
            background-color: #f0fdf4;
            border-left: 5px solid #059669;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
            color: #1f2937;
        }
        .info-box {
            background-color: #fffbeb;
            border-left: 5px solid #f59e0b;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            color: #1f2937;
        }
        .classification-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            margin: 5px 0;
        }
        .low-income { background-color: #fecaca; color: #991b1b; border: 2px solid #ef4444; }
        .lower-middle { background-color: #fed7aa; color: #9a3412; border: 2px solid #f97316; }
        .middle-income { background-color: #fef08a; color: #854d0e; border: 2px solid #eab308; }
        .upper-middle { background-color: #bfdbfe; color: #1e40af; border: 2px solid #3b82f6; }
        .high-income { background-color: #bbf7d0; color: #166534; border: 2px solid #22c55e; }
        
        section[data-testid="stSidebar"] {
            background-color: #f3f4f6;
        }
        .stButton>button {
            background-color: #059669;
            color: white;
            font-weight: bold;
        }
        .stButton>button:hover {
            background-color: #047857;
        }
    </style>
    """, unsafe_allow_html=True)

# Header with theme toggle
col_title, col_toggle = st.columns([6, 1])

with col_title:
    st.markdown('<p class="main-header">🏠 House Socioeconomic Analyzer</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Upload house images to analyze the owner\'s socioeconomic status using AI</p>', unsafe_allow_html=True)

with col_toggle:
    theme_icon = "🌙" if st.session_state.theme == 'light' else "☀️"
    theme_label = "Dark" if st.session_state.theme == 'light' else "Light"
    if st.button(f"{theme_icon} {theme_label}", key="theme_toggle", on_click=toggle_theme):
        pass

# Check API Key
if not GOOGLE_API_KEY:
    st.error("⚠️ Google API Key not found! Please set GOOGLE_API_KEY in your .env file")
    st.info("Get your free API key at: https://aistudio.google.com/apikey")
    st.stop()

# Sidebar with information
with st.sidebar:
    st.header("ℹ️ About This App")
    st.markdown("""
    This AI analyzes house images to estimate the socioeconomic status of the owner based on:
    
    - 🏗️ Structure & construction
    - 🧱 Building materials
    - 🪟 Condition & maintenance
    - 🌳 Surroundings
    - 🏠 Visible amenities
    
    **Classification Categories:**
    - 🔴 Low Income (Desil 1-2)
    - 🟠 Lower-Middle (Desil 3-4)
    - 🟡 Middle Income (Desil 5-6)
    - 🔵 Upper-Middle (Desil 7-8)
    - 🟢 High Income (Desil 9-10)
    """)
    
    st.divider()
    
    st.header("📝 Tips for Best Results")
    st.markdown("""
    - Upload clear, well-lit photos
    - Include multiple angles if possible
    - Front view is most informative
    - Interior photos add accuracy
    """)
    
    st.divider()
    
    st.header("🔑 API Key Status")
    st.success("✅ Google API Key configured")

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📤 Upload House Images")
    
    uploaded_files = st.file_uploader(
        "Choose house images",
        type=['png', 'jpg', 'jpeg', 'webp'],
        accept_multiple_files=True,
        help="Upload one or more images of the house (front, side, interior)"
    )
    
    additional_context = st.text_area(
        "Additional Context (Optional)",
        placeholder="E.g., 'This is a house in rural Java' or 'Front view of the house'",
        help="Provide any additional information about the images"
    )
    
    if uploaded_files:
        st.subheader("📷 Uploaded Images")
        img_cols = st.columns(min(len(uploaded_files), 3))
        for idx, file in enumerate(uploaded_files):
            with img_cols[idx % 3]:
                st.image(file, caption=file.name, use_container_width=True)

with col2:
    st.subheader("📊 Analysis Results")
    
    if uploaded_files:
        if st.button("🔍 Analyze House", type="primary", use_container_width=True):
            with st.spinner("Analyzing house images... This may take a moment."):
                try:
                    all_results = []
                    
                    for idx, uploaded_file in enumerate(uploaded_files):
                        st.info(f"Analyzing image {idx + 1}/{len(uploaded_files)}: {uploaded_file.name}")
                        
                        image = Image.open(uploaded_file)
                        
                        context = f"Image: {uploaded_file.name}"
                        if additional_context:
                            context += f". {additional_context}"
                        
                        result = analyze_house_image(image, context)
                        all_results.append({
                            "filename": uploaded_file.name,
                            "analysis": result
                        })
                    
                    st.success("✅ Analysis Complete!")
                    
                    for result in all_results:
                        st.markdown(f"### 📄 {result['filename']}")
                        
                        # Detect classification for badge
                        analysis_text = result['analysis'].lower()
                        if 'low income' in analysis_text or 'desil 1-2' in analysis_text:
                            badge_class = "low-income"
                            badge_text = "🔴 Low Income (Desil 1-2)"
                        elif 'lower-middle' in analysis_text or 'desil 3-4' in analysis_text:
                            badge_class = "lower-middle"
                            badge_text = "🟠 Lower-Middle (Desil 3-4)"
                        elif 'upper-middle' in analysis_text or 'desil 7-8' in analysis_text:
                            badge_class = "upper-middle"
                            badge_text = "🔵 Upper-Middle (Desil 7-8)"
                        elif 'high income' in analysis_text or 'desil 9-10' in analysis_text:
                            badge_class = "high-income"
                            badge_text = "🟢 High Income (Desil 9-10)"
                        else:
                            badge_class = "middle-income"
                            badge_text = "🟡 Middle Income (Desil 5-6)"
                        
                        st.markdown(f'<span class="classification-badge {badge_class}">{badge_text}</span>', unsafe_allow_html=True)
                        
                        st.markdown(f"""
                        <div class="result-box">
                        {result['analysis']}
                        </div>
                        """, unsafe_allow_html=True)
                        st.divider()
                    
                except Exception as e:
                    st.error(f"❌ Error during analysis: {str(e)}")
                    st.info("Please check your API key and try again.")
    else:
        st.markdown("""
        <div class="info-box">
        👈 Upload house images on the left to start analysis
        </div>
        """, unsafe_allow_html=True)

# Footer
st.divider()
st.markdown(f"""
<p style="text-align: center; color: {'#9ca3af' if st.session_state.theme == 'dark' else '#6b7280'}; font-size: 0.9rem;">
    Built with Streamlit + Google Gemini Vision AI | For Educational Purposes
    <br>
    <small>⚠️ This is a demo app. Classifications are AI estimates based on visual indicators only.</small>
</p>
""", unsafe_allow_html=True)
