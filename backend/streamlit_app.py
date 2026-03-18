"""
House Socioeconomic Classification App
Analyze house images to determine owner's socioeconomic status
Built with Streamlit + Gemini Vision AI
"""

import streamlit as st
import base64
import asyncio
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# ============================================
# CONFIGURATION
# ============================================
# System prompt for house analysis
SYSTEM_PROMPT = """Anda adalah seorang analis sosioekonomi ahli yang berspesialisasi dalam penilaian perumahan di Indonesia.

Tugas Anda adalah menganalisis gambar rumah dan mengklasifikasikan status ekonomi pemilik HANYA berdasarkan kriteria visual di bawah ini.
ANDA HARUS mengeluarkan HANYA JSON yang valid, dalam BAHASA INDONESIA, tanpa penjelasan sebelum atau sesudah.

Format JSON WAJIB:
{
    "klasifikasi": "Miskin|Bawah Menengah|Menengah|Atas Menengah|Kaya",
    "rentang_desil": "1-2|3-4|5-6|7-8|9-10",
    "kepercayaan": "Rendah|Sedang|Tinggi",
    "persentase_kepercayaan": number_0_to_100,
    "pengamatan_kategori": {
        "atap": ["pengamatan1", "pengamatan2"],
        "dinding": ["pengamatan1", "pengamatan2"],
        "lantai": ["pengamatan1", "pengamatan2"],
        "halaman": ["pengamatan1"],
        "amenitas": ["pengamatan1", "pengamatan2"],
        "kondisi_umum": ["pengamatan1"]
    },
    "penjelasan_detail": "string"
}

=== DESIL 1-2 (MISKIN) ===
HARUS memiliki mayoritas dari ini:
- Struktur: Rumah sangat kecil (<25m²), 1 lantai, ruang terbatas
- Material: Kayu, bambu, plastik, tanah, batu bata berkualitas rendah
- Atap: Seng berkarat/bocor, plastik, bagian hilang, rusak
- Dinding: Tidak dicat, retak dalam, berbasis tanah, mengelupas
- Kondisi: Tanda-tanda neglect, kerusakan ekstrim, potensi masalah struktural
- Halaman: Tanah kotor, tanpa pagar, sampah, rumput liar
- Amenitas: TIDAK ada meter listrik, TIDAK ada tangki air, TIDAK ada antena
- Keseluruhan: Indikator kemiskinan ekstrim

=== DESIL 3-4 (BAWAH MENENGAH) ===
HARUS memiliki mayoritas dari ini:
- Struktur: Rumah kecil (25-50m²), 1 lantai
- Material: Campuran kayu dan batu bata sederhana, blok dasar
- Atap: Seng atau asbes dasar, beberapa celah perawatan
- Dinding: Sebagian dicat, retak minor, finishing dasar
- Kondisi: Dirawat tapi menunjukkan keausan, perawatan rata-rata
- Halaman: Paved/tanah sederhana dengan pagar dasar
- Amenitas: Listrik dasar ada, tangki air mungkin ada
- Keseluruhan: Kelas pekerja, tingkat subsistensi

=== DESIL 5-6 (MENENGAH) ===
HARUS memiliki mayoritas dari ini:
- Struktur: Rumah menengah (50-100m²), 1-1.5 lantai
- Material: Batu bata berkualitas/blok beton standar
- Atap: Ubin keramik atau beton, terawat dengan baik
- Dinding: Dicat dengan baik, retak minimal, finishing bagus
- Kondisi: Terawat dengan baik, penampilan bersih
- Halaman: Pagar yang tepat, tanah beraspal, sedikit landscaping
- Amenitas: Meter listrik, tangki air, mungkin satelit dish
- Keseluruhan: Hidup kelas menengah yang stabil

=== DESIL 7-8 (ATAS MENENGAH) ===
HARUS memiliki mayoritas dari ini:
- Struktur: Rumah besar (100-150m²+), 2 lantai minimum
- Material: Beton bertulang, batu bata berkualitas, finishing profesional
- Atap: Ubin keramik premium atau beton, kondisi sempurna
- Dinding: Pengecatan profesional, tanpa retak terlihat, finishing berkualitas
- Kondisi: Perawatan sempurna, penampilan modern
- Halaman: Pagar dekoratif, landscaping, desain tepat
- Amenitas: Unit AC terlihat, gerbang modern, pencahayaan outdoor bagus
- Interior: Furnitur berkualitas, lantai bagus (jika terlihat)
- Keseluruhan: Kelas profesional/pemilik bisnis

=== DESIL 9-10 (KAYA) ===
HARUS memiliki mayoritas dari ini:
- Struktur: Rumah besar (150m²+), 2+ lantai, desain luas
- Material: Material impor premium, elemen marmer/batu
- Atap: Keramik mewah atau material impor, kondisi sempurna
- Dinding: Desain arsitektur profesional, kondisi sempurna
- Kondisi: Finishing mewah, perawatan sempurna
- Halaman: Landscaping profesional, elemen dekoratif, pagar berkualitas tinggi
- Amenitas: Beberapa unit AC, panel surya, sistem keamanan, carport
- Interior: Furnitur mewah, lantai marmer, fixture modern (jika terlihat)
- Keseluruhan: Indikator kekayaan, gaya hidup mewah

Instructions:
1. Periksa SEMUA detail yang terlihat dengan hati-hati
2. Cocokkan dengan kriteria di atas - harus cocok MAYORITAS tanda untuk setiap level
3. Jika bukti tercampur, beri kepercayaan SEDANG
4. Jika bukti jelas dan cocok dengan banyak kriteria, beri kepercayaan TINGGI
5. ORGANISIR pengamatan berdasarkan KATEGORI: atap, dinding, lantai, halaman, amenitas, kondisi_umum
6. Keluarkan HANYA JSON - tidak ada teks sebelum atau sesudah
7. GUNAKAN BAHASA INDONESIA untuk semua teks dalam JSON"""


# ============================================
# HELPER FUNCTIONS
# ============================================

def encode_image_to_base64(uploaded_file):
    """Convert uploaded file to base64 string"""
    bytes_data = uploaded_file.getvalue()
    return base64.b64encode(bytes_data).decode('utf-8')


async def analyze_house_image(image_base64: str, additional_context: str = "") -> str:
    """Analyze a house image using Google Gemini Vision AI."""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = SYSTEM_PROMPT
        if additional_context:
            prompt += f"\n\nKonteks tambahan: {additional_context}"

        response = model.generate_content([prompt, image_base64])
        return response.text if response and response.text else "Tidak ada respons dari AI"
    except Exception as e:
        return f"Kesalahan menganalisis gambar: {str(e)}"


def run_async(coro):
    """Run async function in Streamlit"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


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
                    # Combine all images into one analysis
                    # For now, we'll analyze the first image
                    # (Multi-image analysis can be added later)
                    
                    all_results = []
                    
                    for idx, uploaded_file in enumerate(uploaded_files):
                        st.info(f"Analyzing image {idx + 1}/{len(uploaded_files)}: {uploaded_file.name}")
                        
                        # Encode image to base64
                        image_base64 = encode_image_to_base64(uploaded_file)
                        
                        # Get context including filename
                        context = f"Image: {uploaded_file.name}"
                        if additional_context:
                            context += f". {additional_context}"
                        
                        # Run analysis
                        result = run_async(analyze_house_image(image_base64, context))
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
    Built with Streamlit + Gemini Vision AI | For Educational Purposes
    <br>
    <small>⚠️ This is a demo app. Classifications are AI estimates based on visual indicators only.</small>
</p>
""", unsafe_allow_html=True)
