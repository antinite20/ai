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
    
    Args:
        image_data: PIL Image object
        additional_context: Optional additional context about the image
    
    Returns:
        Analysis result as string
    """
    try:
        # Initialize the model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Build the prompt
        prompt = f"{SYSTEM_PROMPT}\n\nPlease analyze this house image and determine the socioeconomic status of the owner."
        if additional_context:
            prompt += f"\n\nAdditional context: {additional_context}"
        
        # Generate response with image
        response = model.generate_content([prompt, image_data])
        
        return response.text
        
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

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A5F;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .result-box {
        background-color: #f0f7ff;
        border-left: 5px solid #1E88E5;
        padding: 20px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .info-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .stButton>button {
        background-color: #1E88E5;
        color: white;
        font-size: 1.1rem;
        padding: 0.5rem 2rem;
        border-radius: 5px;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #1565C0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">🏠 House Socioeconomic Analyzer</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Upload house images to analyze the owner\'s socioeconomic status using AI</p>', unsafe_allow_html=True)

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
    - Low Income (Desil 1-2)
    - Lower-Middle (Desil 3-4)
    - Middle Income (Desil 5-6)
    - Upper-Middle (Desil 7-8)
    - High Income (Desil 9-10)
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
    
    # File uploader - multiple files
    uploaded_files = st.file_uploader(
        "Choose house images",
        type=['png', 'jpg', 'jpeg', 'webp'],
        accept_multiple_files=True,
        help="Upload one or more images of the house (front, side, interior)"
    )
    
    # Optional context input
    additional_context = st.text_area(
        "Additional Context (Optional)",
        placeholder="E.g., 'This is a house in rural Java' or 'Front view of the house'",
        help="Provide any additional information about the images"
    )
    
    # Display uploaded images
    if uploaded_files:
        st.subheader("📷 Uploaded Images")
        # Create columns for image display
        img_cols = st.columns(min(len(uploaded_files), 3))
        for idx, file in enumerate(uploaded_files):
            with img_cols[idx % 3]:
                st.image(file, caption=file.name, use_container_width=True)

with col2:
    st.subheader("📊 Analysis Results")
    
    # Analyze button
    if uploaded_files:
        if st.button("🔍 Analyze House", type="primary", use_container_width=True):
            with st.spinner("Analyzing house images... This may take a moment."):
                try:
                    all_results = []
                    
                    for idx, uploaded_file in enumerate(uploaded_files):
                        st.info(f"Analyzing image {idx + 1}/{len(uploaded_files)}: {uploaded_file.name}")
                        
                        # Open image with PIL
                        image = Image.open(uploaded_file)
                        
                        # Get context including filename
                        context = f"Image: {uploaded_file.name}"
                        if additional_context:
                            context += f". {additional_context}"
                        
                        # Run analysis
                        result = analyze_house_image(image, context)
                        all_results.append({
                            "filename": uploaded_file.name,
                            "analysis": result
                        })
                    
                    # Display results
                    st.success("✅ Analysis Complete!")
                    
                    for result in all_results:
                        st.markdown(f"### 📄 {result['filename']}")
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
st.markdown("""
<p style="text-align: center; color: #888; font-size: 0.9rem;">
    Built with Streamlit + Google Gemini Vision AI | For Educational Purposes
    <br>
    <small>⚠️ This is a demo app. Classifications are AI estimates based on visual indicators only.</small>
</p>
""", unsafe_allow_html=True)
