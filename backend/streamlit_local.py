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
import json
import pandas as pd
import csv
from datetime import datetime
import subprocess
import platform

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
# LANGUAGE TRANSLATIONS
# ============================================

TRANSLATIONS = {
    "en": {
        "page_title": "House Socioeconomic Analyzer",
        "main_header": "🏠 House Socioeconomic Analyzer",
        "sub_header": "Upload house images to analyze the owner's socioeconomic status using AI",
        "about": "About This App",
        "description": """This AI analyzes house images to estimate the socioeconomic status of the owner based on:

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
- 🟢 High Income (Desil 9-10)""",
        "tips": "Tips for Best Results",
        "tips_content": """- Upload clear, well-lit photos
- Include multiple angles if possible
- Front view is most informative
- Interior photos add accuracy""",
        "api_status": "API Key Status",
        "api_success": "✅ Google API Key configured",
        "upload_header": "📤 Upload House Images",
        "choose_images": "Choose house images",
        "context_label": "Additional Context (Optional)",
        "context_placeholder": "E.g., 'This is a house in rural Java' or 'Front view of the house'",
        "uploaded_images": "📷 Uploaded Images",
        "results_header": "📊 Analysis Results",
        "analyze_button": "🔍 Analyze House",
        "analyzing": "Analyzing house images... This may take a moment.",
        "analyzing_image": "Analyzing image",
        "of": "of",
        "analysis_complete": "✅ Analysis Complete!",
        "analysis_error": "❌ Error during analysis:",
        "check_api": "Please check your API key and try again.",
        "upload_prompt": "👈 Upload house images on the left to start analysis",
        "footer": "all rights reserved © 2026 | built by Jaka Suryadi",
        "desil_1_2": "Low Income (Desil 1-2)",
        "desil_3_4": "Lower-Middle (Desil 3-4)",
        "desil_5_6": "Middle Income (Desil 5-6)",
        "desil_7_8": "Upper-Middle (Desil 7-8)",
        "desil_9_10": "High Income (Desil 9-10)",
        "analysis_summary": "Analysis Summary",
        "classification": "Classification",
        "desil": "Desil Range",
        "confidence": "Confidence",
        "observations": "Key Observations",
        "reasoning": "Detailed Reasoning",
        "atap": "Roof",
        "dinding": "Walls",
        "lantai": "Floor",
        "halaman": "Yard",
        "amenitas": "Amenities",
        "kondisi_umum": "Overall Condition",
        "download_csv": "📥 Download CSV",
        "copy_clipboard": "📋 Copy to Clipboard",
        "copied_success": "✅ Copied to clipboard!",
        "disclaimer": "This analysis is based solely on the provided image. An individual's or family's socioeconomic condition may differ. This AI is intended to aid analysis only. The displayed decile results are not based on official statistics from BPS or other institutions."
    },
    "id": {
        "page_title": "Penganalisis Sosioekonomi Rumah",
        "main_header": "🏠 Penganalisis Sosioekonomi Rumah",
        "sub_header": "Unggah foto rumah untuk menganalisis status sosioekonomi pemilik menggunakan AI",
        "about": "Tentang Aplikasi Ini",
        "description": """AI ini menganalisis foto rumah untuk memperkirakan status sosioekonomi pemilik berdasarkan:

- 🏗️ Struktur & konstruksi
- 🧱 Material bangunan
- 🪟 Kondisi & pemeliharaan
- 🌳 Sekitar rumah
- 🏠 Amenitas yang terlihat

**Kategori Klasifikasi:**
- 🔴 Miskin (Desil 1-2)
- 🟠 Bawah Menengah (Desil 3-4)
- 🟡 Menengah (Desil 5-6)
- 🔵 Atas Menengah (Desil 7-8)
- 🟢 Kaya (Desil 9-10)""",
        "tips": "Tips untuk Hasil Terbaik",
        "tips_content": """- Unggah foto yang jelas dan terang
- Sertakan beberapa sudut pandang
- Tampilan depan paling informatif
- Foto interior menambah akurasi""",
        "api_status": "Status API Key",
        "api_success": "✅ Google API Key dikonfigurasi",
        "upload_header": "📤 Unggah Foto Rumah",
        "choose_images": "Pilih foto rumah",
        "context_label": "Konteks Tambahan (Opsional)",
        "context_placeholder": "Contoh: 'Rumah di pedesaan Jawa' atau 'Tampilan depan rumah'",
        "uploaded_images": "📷 Foto yang Diunggah",
        "results_header": "📊 Hasil Analisis",
        "analyze_button": "🔍 Analisis Rumah",
        "analyzing": "Menganalisis foto rumah... Mohon tunggu sebentar.",
        "analyzing_image": "Menganalisis gambar",
        "of": "dari",
        "analysis_complete": "✅ Analisis Selesai!",
        "analysis_error": "❌ Kesalahan saat analisis:",
        "check_api": "Silakan periksa API key Anda dan coba lagi.",
        "upload_prompt": "👈 Unggah foto rumah di sebelah kiri untuk memulai analisis",
        "footer": "semua hak cipta © 2026 | dibuat oleh Jaka Suryadi",
        "desil_1_2": "Miskin (Desil 1-2)",
        "desil_3_4": "Bawah Menengah (Desil 3-4)",
        "desil_5_6": "Menengah (Desil 5-6)",
        "desil_7_8": "Atas Menengah (Desil 7-8)",
        "desil_9_10": "Kaya (Desil 9-10)",
        "analysis_summary": "Ringkasan Analisis",
        "classification": "Klasifikasi",
        "desil": "Rentang Desil",
        "confidence": "Kepercayaan",
        "observations": "Pengamatan Utama",
        "reasoning": "Penjelasan Detail",
        "atap": "Atap",
        "dinding": "Dinding",
        "lantai": "Lantai",
        "halaman": "Halaman",
        "amenitas": "Amenitas",
        "kondisi_umum": "Kondisi Umum",
        "download_csv": "📥 Download CSV",
        "copy_clipboard": "📋 Salin ke Clipboard",
        "copied_success": "✅ Berhasil disalin!",
        "disclaimer": "Hasil analisis ini berdasarkan gambar yang diberikan. Kondisi sosial ekonomi seseorang atau keluarga sangat mungkin berbeda. AI ini hanya dibuat untuk mempermudah pekerjaan untuk menganalisa. Hasil desil yang ditunjukan bukan berdasarkan hasil statistik BPS ataupun lembaga lainnya."
    }
}

# ============================================
# HELPER FUNCTIONS
# ============================================

def copy_to_clipboard(text: str):
    """
    Copy text to clipboard (cross-platform)
    """
    try:
        if platform.system() == 'Windows':
            import subprocess
            process = subprocess.Popen(['clip'], stdin=subprocess.PIPE)
            process.communicate(text.encode('utf-8'))
        elif platform.system() == 'Darwin':  # macOS
            import subprocess
            process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
            process.communicate(text.encode('utf-8'))
        else:  # Linux and other
            import subprocess
            # Try xclip, then xsel as fallback
            try:
                process = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE)
                process.communicate(text.encode('utf-8'))
            except FileNotFoundError:
                process = subprocess.Popen(['xsel', '--clipboard', '--input'], stdin=subprocess.PIPE)
                process.communicate(text.encode('utf-8'))
        return True
    except Exception as e:
        st.warning(f"Gagal menyalin: {str(e)}")
        return False

def generate_csv_data(result_data: dict) -> str:
    """
    Generate CSV content from analysis result
    """
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Ringkasan Analisis'])
    writer.writerow([])
    
    # Write main info
    writer.writerow(['Klasifikasi', result_data.get('klasifikasi', 'N/A')])
    writer.writerow(['Rentang Desil', result_data.get('rentang_desil', 'N/A')])
    writer.writerow(['Kepercayaan', f"{result_data.get('kepercayaan', 'N/A')} ({result_data.get('persentase_kepercayaan', 0)}%)"])
    writer.writerow([])
    
    # Write categories
    pengamatan_kategori = result_data.get('pengamatan_kategori', {})
    kategori_mapping = {
        "atap": "Atap Rumah",
        "dinding": "Dinding Rumah",
        "lantai": "Lantai Rumah",
        "halaman": "Halaman Rumah",
        "amenitas": "Amenitas Rumah",
        "kondisi_umum": "Kondisi Umum"
    }
    
    for kategori, label in kategori_mapping.items():
        if kategori in pengamatan_kategori and pengamatan_kategori[kategori]:
            writer.writerow([label])
            for obs in pengamatan_kategori[kategori]:
                writer.writerow(['', obs])
    
    writer.writerow([])
    writer.writerow(['Penjelasan Detail'])
    writer.writerow([result_data.get('penjelasan_detail', '')])
    writer.writerow([])
    writer.writerow([f'Dianalisis pada: {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}'])
    
    return output.getvalue()

def extract_material_and_condition(observation_text: str) -> tuple:
    """
    Extract material dan kondisi dari pengamatan
    Contoh: "Seng berkarat, usang, dan tampak rusak" -> ("Seng", "Rusak")
    """
    if not observation_text or observation_text == 'N/A':
        return ('N/A', 'N/A')
    
    # Keywords untuk kondisi
    kondisi_keywords = {
        'Baik': ['baik', 'bagus', 'sempurna', 'baru', 'terawat', 'mantap', 'excellent', 'good'],
        'Cukup': ['cukup', 'lumayan', 'sedang', 'standard', 'medium', 'reasonable'],
        'Tidak Baik': ['rusak', 'berkarat', 'bocor', 'pecah', 'retak', 'sobek', 'jebol', 'bad', 'poor', 'damaged', 'worn'],
        'Sangat Rusak': ['sangat rusak', 'ekstrim', 'parah', 'critical', 'severe'],
    }
    
    text_lower = observation_text.lower()
    
    # Ambil kata pertama sebagai material
    words = observation_text.split()
    material = words[0] if words else 'N/A'
    
    # Deteksi kondisi dari keywords
    kondisi = 'N/A'
    for condition, keywords in kondisi_keywords.items():
        if any(kw in text_lower for kw in keywords):
            kondisi = condition
            break
    
    return (material, kondisi)

def generate_structured_csv_data(parsed: dict, filename: str) -> str:
    """
    Generate structured CSV for database (simpel dan efisien)
    Format: Nama File | Klasifikasi | Desil | Kepercayaan | 
            Atap | Kondisi Atap | Lantai | Kondisi Lantai | Dinding | Kondisi Dinding | Timestamp
    """
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Extract data
    classification = parsed.get('klasifikasi', 'N/A')
    desil_range = parsed.get('rentang_desil', 'N/A')
    confidence = parsed.get('kepercayaan', 'N/A')
    confidence_pct = parsed.get('persentase_kepercayaan', 0)
    pengamatan_kategori = parsed.get('pengamatan_kategori', {})
    
    # Convert confidence to detailed level
    if confidence_pct >= 95:
        confidence_level = 'Sangat Tinggi'
    elif confidence_pct >= 75:
        confidence_level = 'Tinggi'
    elif confidence_pct >= 50:
        confidence_level = 'Sedang'
    else:
        confidence_level = 'Rendah'
    
    # Extract desil number (from "1-2" to "1")
    desil_num = desil_range.split('-')[0] if desil_range != 'N/A' else 'N/A'
    
    # Function to extract first mention or primary material
    def get_primary_material(observations_list):
        if observations_list and len(observations_list) > 0:
            return observations_list[0]
        return 'N/A'
    
    # Extract material dan kondisi dari kategori
    atap_obs = get_primary_material(pengamatan_kategori.get('atap', []))
    atap_material, atap_condition = extract_material_and_condition(atap_obs)
    
    lantai_obs = get_primary_material(pengamatan_kategori.get('lantai', []))
    lantai_material, lantai_condition = extract_material_and_condition(lantai_obs)
    
    dinding_obs = get_primary_material(pengamatan_kategori.get('dinding', []))
    dinding_material, dinding_condition = extract_material_and_condition(dinding_obs)
    
    halaman_obs = get_primary_material(pengamatan_kategori.get('halaman', []))
    halaman_material, halaman_condition = extract_material_and_condition(halaman_obs)
    
    amenitas_obs = get_primary_material(pengamatan_kategori.get('amenitas', []))
    amenitas_material, amenitas_condition = extract_material_and_condition(amenitas_obs)
    
    kondisi_umum_obs = get_primary_material(pengamatan_kategori.get('kondisi_umum', []))
    kondisi_umum_material, kondisi_umum_condition = extract_material_and_condition(kondisi_umum_obs)
    
    # Write headers
    writer.writerow(['Nama File', 'Klasifikasi', 'Desil', 'Kepercayaan', 'Atap', 'Kondisi Atap', 'Lantai', 'Kondisi Lantai', 'Dinding', 'Kondisi Dinding', 'Halaman', 'Amenitas', 'Timestamp'])
    
    # Write data
    writer.writerow([
        filename,
        classification,
        desil_num,
        f"{confidence_level} ({confidence_pct}%)",
        atap_material,
        atap_condition,
        lantai_material,
        lantai_condition,
        dinding_material,
        dinding_condition,
        halaman_material,
        amenitas_material,
        datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    ])
    
    return output.getvalue()


def generate_batch_summary_csv(all_results_list: list) -> str:
    """
    Generate summary CSV for all analyzed images (simplified format)
    """
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow(['No', 'Nama File', 'Klasifikasi', 'Desil', 'Kepercayaan', 'Atap', 'Kondisi Atap', 'Lantai', 'Kondisi Lantai', 'Dinding', 'Kondisi Dinding'])
    
    # Write data
    for idx, item in enumerate(all_results_list, 1):
        writer.writerow([
            idx,
            item['filename'],
            item['classification'],
            item['desil'],
            item['confidence_level'],
            item['atap'],
            item['atap_condition'],
            item['lantai'],
            item['lantai_condition'],
            item['dinding'],
            item['dinding_condition']
        ])
    
    return output.getvalue()

def analyze_house_image(image_data, additional_context: str = "") -> str:
    """
    Analyze house image using Google Gemini Vision AI
    """
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"{SYSTEM_PROMPT}\n\nAnalisis gambar rumah ini dan tentukan status sosioekonomi pemiliknya. Kategorikan pengamatan Anda berdasarkan elemen rumah: atap, dinding, lantai, halaman, amenitas, dan kondisi umum."
        if additional_context:
            prompt += f"\n\nKonteks tambahan: {additional_context}"
        
        response = model.generate_content([prompt, image_data])
        
        if response and response.text:
            return response.text
        else:
            return "Tidak ada respons dari AI"
        
    except Exception as e:
        return f"Kesalahan menganalisis gambar: {str(e)}"

def parse_analysis_json(analysis_text: str) -> dict:
    """
    Parse JSON from analysis text with support for categorized observations
    """
    import json
    try:
        # Try direct JSON parsing
        result = json.loads(analysis_text)
        return result
    except:
        try:
            # Try to extract JSON from markdown code blocks
            if '```json' in analysis_text:
                json_str = analysis_text.split('```json')[1].split('```')[0].strip()
            elif '```' in analysis_text:
                json_str = analysis_text.split('```')[1].split('```')[0].strip()
            else:
                # Try to find JSON in the text
                start = analysis_text.find('{')
                end = analysis_text.rfind('}') + 1
                if start >= 0 and end > start:
                    json_str = analysis_text[start:end]
                else:
                    return None
            
            result = json.loads(json_str)
            return result
        except:
            return None


# ============================================
# STREAMLIT UI
# ============================================

# Page configuration
st.set_page_config(
    page_title="House Socioeconomic Analyzer",
    page_icon="🏠",
    layout="wide"
)

# Initialize language in session state
if 'language' not in st.session_state:
    st.session_state.language = 'id'  # Default to Indonesian

# Initialize theme in session state
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'  # Default to dark theme

# Initialize analysis results storage in session state
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = []

# Initialize batch summary in session state
if 'batch_summary' not in st.session_state:
    st.session_state.batch_summary = []

def toggle_language():
    if st.session_state.language == 'en':
        st.session_state.language = 'id'
    else:
        st.session_state.language = 'en'

def get_text(key: str) -> str:
    """Get translated text based on current language"""
    lang = st.session_state.language
    return TRANSLATIONS[lang].get(key, TRANSLATIONS['en'].get(key, key))

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
col_title, col_lang, col_toggle = st.columns([5, 1, 1])

with col_title:
    st.markdown(f'<p class="main-header">{get_text("main_header")}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">{get_text("sub_header")}</p>', unsafe_allow_html=True)
    # Disclaimer note
    st.markdown(f'<div class="info-box">{get_text("disclaimer")}</div>', unsafe_allow_html=True)

with col_lang:
    lang_icon = "🇮🇩" if st.session_state.language == 'id' else "🇺🇸"
    lang_label = "English" if st.session_state.language == 'id' else "Bahasa"
    if st.button(f"{lang_icon}", key="language_toggle", on_click=toggle_language, help=lang_label):
        pass

with col_toggle:
    theme_icon = "🌙" if st.session_state.theme == 'light' else "☀️"
    theme_label = "Dark" if st.session_state.theme == 'light' else "Light"
    if st.button(f"{theme_icon}", key="theme_toggle", on_click=toggle_theme, help=theme_label):
        pass

# Check API Key
if not GOOGLE_API_KEY:
    st.error("⚠️ Google API Key not found! Please set GOOGLE_API_KEY in your .env file")
    st.info("Get your free API key at: https://aistudio.google.com/apikey")
    st.stop()

# Sidebar with information
with st.sidebar:
    st.header(get_text("about"))
    st.markdown(get_text("description"))
    
    st.divider()
    
    st.header(get_text("tips"))
    st.markdown(get_text("tips_content"))
    
    st.divider()
    
    st.header(get_text("api_status"))
    st.success(get_text("api_success"))

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader(get_text("upload_header"))
    
    uploaded_files = st.file_uploader(
        get_text("choose_images"),
        type=['png', 'jpg', 'jpeg', 'webp'],
        accept_multiple_files=True,
        help=get_text("context_label")
    )
    
    additional_context = st.text_area(
        get_text("context_label"),
        placeholder=get_text("context_placeholder"),
        help=get_text("context_label")
    )
    
    if uploaded_files:
        st.subheader(get_text("uploaded_images"))
        img_cols = st.columns(min(len(uploaded_files), 3))
        for idx, file in enumerate(uploaded_files):
            with img_cols[idx % 3]:
                st.image(file, caption=file.name, use_container_width=True)

with col2:
    st.subheader(get_text("results_header"))
    
    if uploaded_files:
        if st.button(get_text("analyze_button"), type="primary", use_container_width=True):
            with st.spinner(get_text("analyzing")):
                try:
                    all_results = []
                    
                    for idx, uploaded_file in enumerate(uploaded_files):
                        st.info(f"{get_text('analyzing_image')} {idx + 1}/{len(uploaded_files)}: {uploaded_file.name}")
                        
                        image = Image.open(uploaded_file)
                        
                        context = f"Image: {uploaded_file.name}"
                        if additional_context:
                            context += f". {additional_context}"
                        
                        result = analyze_house_image(image, context)
                        all_results.append({
                            "filename": uploaded_file.name,
                            "analysis": result
                        })
                    
                    st.success(get_text("analysis_complete"))
                    
                    # Create summary table
                    summary_data = []
                    
                    for result in all_results:
                        st.markdown(f"### 📄 {result['filename']}")
                        
                        # Parse JSON from analysis
                        parsed = parse_analysis_json(result['analysis'])
                        
                        if parsed:
                            # Get classification and determine badge
                            classification = parsed.get('klasifikasi', 'Tidak Diketahui')
                            desil_range = parsed.get('rentang_desil', 'N/A')
                            confidence = parsed.get('kepercayaan', 'N/A')
                            confidence_pct = parsed.get('persentase_kepercayaan', 0)
                            pengamatan_kategori = parsed.get('pengamatan_kategori', {})
                            penjelasan_detail = parsed.get('penjelasan_detail', '')
                            
                            # Determine badge style
                            analysis_text = classification.lower()
                            if 'miskin' in analysis_text or '1-2' in desil_range:
                                badge_class = "low-income"
                                emoji = "🔴"
                            elif 'bawah' in analysis_text or '3-4' in desil_range:
                                badge_class = "lower-middle"
                                emoji = "🟠"
                            elif 'atas' in analysis_text or '7-8' in desil_range:
                                badge_class = "upper-middle"
                                emoji = "🔵"
                            elif 'kaya' in analysis_text or '9-10' in desil_range:
                                badge_class = "high-income"
                                emoji = "🟢"
                            else:
                                badge_class = "middle-income"
                                emoji = "🟡"
                            
                            # Display badge
                            st.markdown(f'<span class="classification-badge {badge_class}">{emoji} {classification}</span>', unsafe_allow_html=True)
                            
                            # Create comprehensive summary table for this image
                            st.subheader(get_text("analysis_summary"))
                            
                            # Build comprehensive summary rows
                            summary_rows = [
                                [get_text("classification"), classification],
                                [get_text("desil"), desil_range],
                                [get_text("confidence"), f"{confidence} ({confidence_pct}%)"],
                            ]
                            
                            # Add category observations to summary
                            kategori_mapping = {
                                "atap": "🏠 Atap Rumah",
                                "dinding": "🧱 Dinding Rumah",
                                "lantai": "📐 Lantai Rumah",
                                "halaman": "🌳 Halaman Rumah",
                                "amenitas": "💡 Amenitas Rumah",
                                "kondisi_umum": "🏘️ Kondisi Umum"
                            }
                            
                            # Add observations to summary rows
                            for kategori, kategori_label in kategori_mapping.items():
                                if kategori in pengamatan_kategori and pengamatan_kategori[kategori]:
                                    # Join observations with comma, limit to reasonable length
                                    obs_text = ", ".join(pengamatan_kategori[kategori][:2])  # First 2 observations
                                    if len(pengamatan_kategori[kategori]) > 2:
                                        obs_text += f" (+{len(pengamatan_kategori[kategori])-2} lebih)"
                                    summary_rows.append([kategori_label, obs_text])
                            
                            # Create and display summary dataframe
                            df_summary = pd.DataFrame(summary_rows, columns=['', 'Value'])
                            st.dataframe(df_summary, use_container_width=True, hide_index=True)
                            
                            # Display brief reasoning (penjelasan detail)
                            st.subheader(get_text("reasoning"))
                            st.write(penjelasan_detail)
                            
                            # Add Download CSV and Copy buttons
                            st.divider()
                            col_download, col_copy = st.columns(2)
                            
                            # Prepare structured CSV data (database-ready format)
                            structured_csv = generate_structured_csv_data(parsed, result['filename'])
                            filename_structured = f"analisis_{result['filename'].rsplit('.', 1)[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                            
                            with col_download:
                                st.download_button(
                                    label=get_text("download_csv"),
                                    data=structured_csv,
                                    file_name=filename_structured,
                                    mime="text/csv",
                                    use_container_width=True,
                                    key=f"download_{result['filename']}"
                                )
                            
                            with col_copy:
                                if st.button(get_text("copy_clipboard"), use_container_width=True, key=f"copy_{result['filename']}"):
                                    if copy_to_clipboard(structured_csv):
                                        st.success(get_text("copied_success"))
                                    else:
                                        st.error("Gagal menyalin ke clipboard")
                            
                            # Store in session state untuk prevent data loss on refresh
                            result_item = {
                                'filename': result['filename'],
                                'classification': parsed.get('klasifikasi', 'N/A'),
                                'desil': parsed.get('rentang_desil', 'N/A').split('-')[0],
                                'confidence_pct': parsed.get('persentase_kepercayaan', 0),
                                'confidence': parsed.get('kepercayaan', 'N/A'),
                                'pengamatan_kategori': pengamatan_kategori,
                                'penjelasan_detail': penjelasan_detail,
                                'parsed': parsed
                            }
                            
                            # Calculate confidence level
                            conf_pct = result_item['confidence_pct']
                            if conf_pct >= 95:
                                result_item['confidence_level'] = 'Sangat Tinggi'
                            elif conf_pct >= 75:
                                result_item['confidence_level'] = 'Tinggi'
                            elif conf_pct >= 50:
                                result_item['confidence_level'] = 'Sedang'
                            else:
                                result_item['confidence_level'] = 'Rendah'
                            
                            # Add material info
                            def get_primary(obs_list):
                                return obs_list[0] if obs_list else 'N/A'
                            
                            result_item['atap'] = get_primary(pengamatan_kategori.get('atap', []))
                            result_item['lantai'] = get_primary(pengamatan_kategori.get('lantai', []))
                            result_item['dinding'] = get_primary(pengamatan_kategori.get('dinding', []))
                            result_item['halaman'] = get_primary(pengamatan_kategori.get('halaman', []))
                            result_item['amenitas'] = get_primary(pengamatan_kategori.get('amenitas', []))
                            result_item['kondisi_umum'] = get_primary(pengamatan_kategori.get('kondisi_umum', []))
                            
                            st.session_state.analysis_results.append(result_item)
                            st.session_state.batch_summary.append({
                                'filename': result_item['filename'],
                                'classification': result_item['classification'],
                                'desil': result_item['desil'],
                                'confidence_level': result_item['confidence_level'],
                                'atap': result_item['atap'],
                                'lantai': result_item['lantai'],
                                'dinding': result_item['dinding']
                            })
                            
                            # Add to summary data
                            summary_data.append({
                                'File': result['filename'],
                                'Klasifikasi': classification,
                                'Desil': desil_range,
                                'Kepercayaan': f"{confidence_pct}%"
                            })
                        else:
                            # If JSON parsing fails, show raw analysis
                            st.markdown(f"""
                            <div class="result-box">
                            {result['analysis']}
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.divider()
                    
                    # Show overall summary table
                    if summary_data:
                        st.subheader("📋 Ringkasan Keseluruhan")
                        df_all = pd.DataFrame(summary_data)
                        st.dataframe(df_all, use_container_width=True, hide_index=True)
                        
                        # Add batch export button
                        if st.session_state.batch_summary:
                            st.divider()
                            col_batch_export, col_batch_copy = st.columns(2)
                            
                            batch_csv = generate_batch_summary_csv(st.session_state.batch_summary)
                            
                            with col_batch_export:
                                st.download_button(
                                    label="📥 Download Ringkasan (CSV)",
                                    data=batch_csv,
                                    file_name=f"ringkasan_analisis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                    mime="text/csv",
                                    use_container_width=True
                                )
                            
                            with col_batch_copy:
                                if st.button("📋 Salin Ringkasan", use_container_width=True, key="copy_batch"):
                                    if copy_to_clipboard(batch_csv):
                                        st.success("✅ Ringkasan berhasil disalin!")
                    
                except Exception as e:
                    st.error(f"{get_text('analysis_error')} {str(e)}")
                    st.info(get_text("check_api"))
    else:
        st.markdown(f"""
        <div class="info-box">
        {get_text('upload_prompt')}
        </div>
        """, unsafe_allow_html=True)

# Footer
st.divider()
st.markdown(f"""
<p style="text-align: center; color: {'#9ca3af' if st.session_state.theme == 'dark' else '#6b7280'}; font-size: 0.9rem;">
    {get_text('footer')}
</p>
""", unsafe_allow_html=True)
