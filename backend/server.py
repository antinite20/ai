"""
House Socioeconomic Classification API
Backend for analyzing house images
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import base64
import asyncio
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# ============================================
# CONFIGURATION
# ============================================
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)


def analyze_house_image(image_base64: str, additional_context: str = "") -> str:
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
# FASTAPI APP
# ============================================
app = FastAPI(title="House Socioeconomic Analyzer API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalysisResult(BaseModel):
    classification: str
    desil_range: str
    confidence: str
    confidence_percentage: int
    key_observations: List[str]
    detailed_reasoning: str


class AnalysisResponse(BaseModel):
    success: bool
    filename: str
    result: Optional[str] = None
    error: Optional[str] = None


# ============================================
# API ENDPOINTS
# ============================================

@app.get("/api/")
def root():
    return {"message": "House Socioeconomic Analyzer API is running!"}


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "api_key_configured": bool(GOOGLE_API_KEY)}


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_house(
    file: UploadFile = File(...),
    context: Optional[str] = Form(None)
):
    """
    Analyze a house image and return socioeconomic classification
    """
    try:
        # Validate file type
        allowed_types = ["image/png", "image/jpeg", "image/jpg", "image/webp"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: PNG, JPG, JPEG, WEBP"
            )
        
        # Read and encode image
        contents = await file.read()
        image_base64 = base64.b64encode(contents).decode('utf-8')
        
        # Analyze using Google Gemini Vision AI
        result_text = analyze_house_image(image_base64, context or "")

        return AnalysisResponse(
            success=True,
            filename=file.filename,
            result=result_text
        )
        
    except Exception as e:
        return AnalysisResponse(
            success=False,
            filename=file.filename if file else "unknown",
            error=str(e)
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
