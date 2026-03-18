# 🌐 Language Toggle & Analysis Table Feature

## 📝 Perubahan yang Ditambahkan

### 1. ✅ Language Toggle (Indonesia/English)
**Lokasi:** Top-right corner header

**Fitur:**
- Klik tombol 🇮🇩/🇺🇸 untuk switch bahasa
- Semua UI text berubah sesuai bahasa pilihan
- State tersimpan saat navigasi
- Support 2 bahasa: Bahasa Indonesia dan English

**Elemen yang Diterjemahkan:**
- Header & sub-header
- Labels form
- Button text
- Sidebar content
- Tabel headers
- Messages & notifikasi
- Footer

### 2. ✅ Analysis Results in Table Format
**Lokasi:** Right column, Analysis Results section

**Features:**
- **Per-Image Summary Table**: Ringkasan hasil analisis setiap photo
  - Classification (Klasifikasi)
  - Desil Range (Rentang Desil)
  - Confidence Level (Level Kepercayaan)

- **Detailed Breakdown**:
  - Key Observations (Pengamatan Utama)
  - Detailed Reasoning (Penjelasan Detail)
  - Color-coded badges per Desil level

- **Overall Summary Table**: Ringkasan total untuk semua images
  - Filename
  - Classification
  - Desil Range
  - Confidence Percentage

---

## 🎨 UI Layout Baru

```
┌─────────────────────────────────────────────────────────────┐
│  🏠 Title          🇮🇩 Language Toggle  🌙 Theme Toggle      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────┬──────────────────────────────────┐
│ LEFT (Upload)           │ RIGHT (Results)                  │
│                         │                                  │
│ • Upload form           │ • Per-image results             │
│ • File uploader         │ • Summary table                 │
│ • Image previews        │ • Classification badge          │
│                         │ • Observations list             │
│                         │ • Detailed reasoning            │
│                         │ • Overall summary table         │
└─────────────────────────┴──────────────────────────────────┘
```

---

## 💻 Code Structure

### Language System
```python
TRANSLATIONS = {
    "en": { ... },
    "id": { ... }
}

# Usage:
get_text("key_name")  # Returns translated text
```

### JSON Parsing Function
```python
def parse_analysis_json(analysis_text: str) -> dict:
    """
    Parse JSON output from Gemini AI
    - Handles markdown code blocks
    - Extracts JSON from text
    - Returns structured data
    """
```

### Table Generation
```python
# Per-image table
df_summary = pd.DataFrame(table_data.items())
st.dataframe(df_summary, use_container_width=True)

# Overall summary
df_all = pd.DataFrame(summary_data)
st.dataframe(df_all, use_container_width=True)
```

---

## 🔄 How It Works

### Language Toggle Flow:
```
Click Language Button
    ↓
Toggle st.session_state.language
    ↓
Rerun Streamlit script
    ↓
All text uses get_text() function
    ↓
UI displays in selected language
```

### Analysis Table Flow:
```
Upload Image(s)
    ↓
Click "Analyze House"
    ↓
Gemini AI returns JSON
    ↓
parse_analysis_json() extracts data
    ↓
Create summary table (per-image)
    ↓
Display classification badge
    ↓
Show observations & reasoning
    ↓
Collect data from all images
    ↓
Create overall summary table
```

---

## 📊 Table Examples

### Per-Image Summary Table (Bahasa Indonesia):
| Klasifikasi | Rentang Desil | Kepercayaan |
|-------------|---------------|------------|
| Menengah | 5-6 | Tinggi (85%) |

### Per-Image Summary Table (English):
| Classification | Desil Range | Confidence |
|---|---|---|
| Middle Income | 5-6 | High (85%) |

### Overall Summary Table:
| File | Classification | Desil | Confidence |
|------|---|---|---|
| rumah1.jpg | Middle Income | 5-6 | 85% |
| rumah2.jpg | Upper-Middle | 7-8 | 92% |
| rumah3.jpg | Low Income | 1-2 | 78% |

---

## 🎯 Supported Languages

### Bahasa Indonesia (ID) 🇮🇩
- Default language
- Full translation of all UI elements
- Regional relevant terminology

### English (EN) 🇺🇸
- International language
- Full translation of all UI elements
- Standard terminology

---

## 🔧 Configuration

### Language State:
```python
if 'language' not in st.session_state:
    st.session_state.language = 'id'  # Default: Indonesian
```

### Language Toggle Function:
```python
def toggle_language():
    if st.session_state.language == 'en':
        st.session_state.language = 'id'
    else:
        st.session_state.language = 'en'
```

### Get Text Function:
```python
def get_text(key: str) -> str:
    lang = st.session_state.language
    return TRANSLATIONS[lang].get(key, TRANSLATIONS['en'].get(key, key))
```

---

## 📋 Translation Keys Available

### Header & Navigation:
- `main_header` - Main application title
- `sub_header` - Subtitle
- `about` - About section title
- `tips` - Tips section title
- `api_status` - API key status section

### Form Labels:
- `upload_header` - Upload section title
- `choose_images` - File uploader label
- `context_label` - Context input label
- `context_placeholder` - Context placeholder text
- `uploaded_images` - Uploaded images section

### Results:
- `results_header` - Results section title
- `analyze_button` - Analyze button text
- `analysis_summary` - Summary section title
- `analysis_complete` - Success message
- `classification` - Classification label
- `desil` - Desil range label
- `confidence` - Confidence label
- `observations` - Observations label
- `reasoning` - Reasoning label

### Messages:
- `analyzing` - Loading spinner text
- `analyzing_image` - Per-image analysis text
- `analysis_error` - Error message
- `check_api` - API error hint
- `upload_prompt` - Upload prompt text

---

## ✨ Features & Benefits

✅ **Multi-language Support**
- Easy to understand for Indonesian & English users
- Can be expanded to more languages

✅ **Structured Results**
- Clear table format for easy understanding
- Per-image and overall summary tables
- Color-coded badges for visual clarity

✅ **Better Data Presentation**
- JSON parsing ensures reliable data extraction
- Organized display of observations and reasoning
- Professional table layout

✅ **User Experience**
- Language persists during session
- Theme toggle still available
- Responsive layout on all screen sizes

---

## 🚀 How to Use

### 1. Change Language:
```
1. Click 🇮🇩 or 🇺🇸 button in top-right
2. UI updates immediately to selected language
3. Language preference persists until changed
```

### 2. View Analysis Results:
```
1. Upload house image(s)
2. Click "🔍 Analyze House" / "🔍 Analisis Rumah"
3. AI analyzes images
4. Results displayed in:
   - Per-image summary table
   - Classification badge
   - Observations list
   - Detailed reasoning
   - Overall summary table
```

### 3. Interpret Results:
```
Classification → Desil level (1-2, 3-4, 5-6, 7-8, 9-10)
Confidence → High/Medium/Low + percentage
Observations → Key features noticed
Reasoning → Detailed explanation
```

---

## 📚 Files Modified

**File:** `backend/streamlit_local.py`

**Changes:**
1. Added imports: `json`, `pandas`
2. Added `TRANSLATIONS` dictionary with full translations
3. Added `parse_analysis_json()` function
4. Added language state management & toggle function
5. Updated all UI elements to use `get_text()`
6. Added table generation with pandas
7. Replaced analysis badge logic with colored badges
8. Added overall summary table
9. Enhanced layout with language toggle button

---

## 🔍 Testing

### Test Language Toggle:
1. Run: `streamlit run backend/streamlit_local.py`
2. Click language button → UI should change language
3. Upload image → Click analyze
4. Results should display in selected language

### Test Table Display:
1. Upload single image → Analyze
2. Check per-image summary table appears
3. Upload multiple images → Analyze
4. Check overall summary table appears with all images

---

## 🎯 Next Steps

### Possible Enhancements:
- [ ] Add more languages (Javanese, Sundanese, etc.)
- [ ] Export results to CSV/PDF
- [ ] Store analysis history with language preferences
- [ ] Add language preference to user profile
- [ ] Translate system prompt to match selected language

---

**Version:** 1.0  
**Date:** January 31, 2026  
**Status:** ✅ Complete & Tested
