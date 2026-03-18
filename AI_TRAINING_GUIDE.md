# Panduan Melatih AI untuk Klasifikasi Desil & Kondisi Ekonomi

## 📋 Ringkasan Perubahan

Sistem prompt telah diupgrade dari deskripsi umum menjadi **kriteria terukur dan spesifik** untuk setiap Desil level (1-10).

---

## 🎯 Metode Pelatihan AI (3 Pendekatan)

### **1. PROMPT ENGINEERING (SUDAH DITERAPKAN) ✅**

**Apa yang dilakukan:**
- ✅ Diupdate semua sistem prompt dengan kriteria terukur untuk setiap Desil
- ✅ Format output JSON yang ketat (bukan free-form text)
- ✅ Kriteria visual yang spesifik (ukuran rumah, material, amenities, dll)

**File yang diupdate:**
- [streamlit_local.py](streamlit_local.py) - Local development version
- [server.py](server.py) - Production API
- [streamlit_app.py](streamlit_app.py) - Streamlit cloud version

**Keuntungan:** Langsung bekerja, murah, cepat
**Kelemahan:** Terbatas pada kemampuan model dasar

---

### **2. FINE-TUNING DENGAN DATA TRAINING (RECOMMENDED)**

Jika ingin akurasi lebih tinggi, bisa melakukan fine-tuning Google Gemini dengan data training custom:

#### **Langkah-langkah Fine-tuning:**

```bash
# 1. Install Google AI SDK
pip install google-generativeai

# 2. Siapkan training data (CSV dengan format):
# image_base64, classification, desil_range, confidence, reasoning
```

**Format dataset training yang diperlukan:**
```json
[
  {
    "image_url": "https://example.com/rumah1.jpg",
    "classification": "Low Income",
    "desil_range": "1-2",
    "features": {
      "materials": "wood, bamboo",
      "roof_condition": "tin with leaks",
      "house_size_m2": 20,
      "has_electricity_meter": false,
      "has_water_tank": false
    }
  },
  // ... lebih banyak examples
]
```

**Minimal dataset yang direkomendasikan:**
- **50-100 images per Desil level** (untuk akurasi baik)
- **500+ total images** (untuk fine-tuning optimal)
- **Variety:** berbagai kondisi rumah, lokasi, cuaca, sudut pengambilan

#### **Script Fine-tuning (Contoh):**

```python
import google.generativeai as genai
import json

# Configure API
genai.configure(api_key="YOUR_API_KEY")

# Upload training data
def upload_training_data(file_path):
    files = []
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    for item in data:
        # Upload setiap image ke Gemini
        file = genai.upload_file(item['image_url'])
        files.append({
            'file': file,
            'label': item['classification']
        })
    
    return files

# Start fine-tuning
training_data = upload_training_data('training_data.json')

operation = genai.create_tuned_model(
    display_name="House Socioeconomic Analyzer v2",
    source_model="models/gemini-2.5-flash",
    training_data=[
        {'file_data': file['file'], 'media_type': 'image/jpeg'}
        for file in training_data
    ],
    hyperparameters={
        'batch_size': 4,
        'learning_rate': 0.001,
        'epoch_count': 10,
    }
)

print(f"Fine-tuning started: {operation.name}")
```

**Biaya:** ~$1-5 per fine-tuning (tergantung jumlah data)
**Waktu:** 1-2 jam untuk 500 images

---

### **3. CUSTOM SCORING FUNCTION (BEST ACCURACY)**

Buat scoring function yang menghitung "ekonomic score" berdasarkan features:

```python
def calculate_economic_score(image_analysis: dict) -> dict:
    """
    Calculate economic score based on detected features
    Score: 0-100 (0=poorest, 100=richest)
    """
    score = 0
    factors = {}
    
    # Structure/Size scoring (0-15 points)
    size = image_analysis.get('estimated_size_m2', 0)
    if size < 25:
        factors['structure'] = 2
    elif size < 50:
        factors['structure'] = 5
    elif size < 100:
        factors['structure'] = 8
    elif size < 150:
        factors['structure'] = 12
    else:
        factors['structure'] = 15
    
    # Materials scoring (0-20 points)
    materials = image_analysis.get('materials', [])
    material_score = 0
    for material in materials:
        if material in ['wood', 'bamboo', 'plastic']:
            material_score += 2
        elif material in ['brick', 'tin']:
            material_score += 5
        elif material in ['concrete', 'ceramic']:
            material_score += 10
        elif material in ['marble', 'stone', 'imported']:
            material_score += 15
    factors['materials'] = min(material_score, 20)
    
    # Amenities scoring (0-25 points)
    amenities = image_analysis.get('amenities', [])
    amenities_score = 0
    amenity_weights = {
        'electricity_meter': 5,
        'water_tank': 5,
        'ac_unit': 8,
        'security_system': 7,
        'solar_panels': 10,
        'modern_gate': 5,
        'driveway': 8,
    }
    for amenity, weight in amenity_weights.items():
        if amenity in amenities:
            amenities_score += weight
    factors['amenities'] = min(amenities_score, 25)
    
    # Condition scoring (0-20 points)
    condition = image_analysis.get('condition', 'poor')
    condition_score = {
        'poor': 2,
        'fair': 8,
        'good': 15,
        'excellent': 20,
        'luxury': 20,
    }
    factors['condition'] = condition_score.get(condition, 5)
    
    # Yard/Fencing (0-20 points)
    yard = image_analysis.get('yard_condition', 'none')
    yard_score = {
        'dirt': 0,
        'paved': 5,
        'fenced': 10,
        'landscaped': 15,
        'professional_landscaping': 20,
    }
    factors['yard'] = yard_score.get(yard, 0)
    
    # Calculate total score
    total_score = sum(factors.values())
    
    # Map score to Desil
    desil_mapping = {
        'Low Income': (0, 20, '1-2'),
        'Lower-Middle': (21, 35, '3-4'),
        'Middle Income': (36, 55, '5-6'),
        'Upper-Middle': (56, 75, '7-8'),
        'High Income': (76, 100, '9-10'),
    }
    
    classification = None
    for cls, (min_s, max_s, desil) in desil_mapping.items():
        if min_s <= total_score <= max_s:
            classification = cls
            break
    
    return {
        'economic_score': total_score,
        'classification': classification,
        'desil_range': desil,
        'confidence_percentage': min(total_score * 1.5, 100),  # Higher score = higher confidence
        'factors': factors
    }
```

---

## 🔄 Workflow Rekomendasi

### **Phase 1: Validasi Prompt (Minggu 1)**
1. Test dengan 10-20 foto rumah berbeda
2. Lihat apakah output JSON konsisten
3. Cek akurasi klasifikasi manual
4. Adjust prompt jika perlu

**Test Command:**
```python
import google.generativeai as genai
from PIL import Image

genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel('gemini-2.5-flash')

image = Image.open("rumah_test.jpg")
response = model.generate_content([
    SYSTEM_PROMPT,  # dari file Anda
    "Analyze this house image",
    image
])

print(response.text)
```

### **Phase 2: Kumpulkan Training Data (Minggu 2-3)**
1. Ambil/kumpulkan 50-100 foto per Desil level
2. Label manual untuk ground truth
3. Upload ke dataset training

### **Phase 3: Fine-tune Model (Minggu 4)**
1. Run fine-tuning script
2. Test dengan data validation
3. Measure accuracy

### **Phase 4: Deploy Fine-tuned Model (Minggu 5)**
1. Update code untuk gunakan tuned model
2. Monitor performance di production

---

## 📊 KPI untuk Evaluasi

Gunakan metrik ini untuk mengukur progress training:

```python
from sklearn.metrics import confusion_matrix, accuracy_score

def evaluate_model(predictions, ground_truth):
    """
    predictions: ["Low Income", "Middle Income", ...]
    ground_truth: ["Low Income", "Middle Income", ...]
    """
    
    # Accuracy
    accuracy = accuracy_score(predictions, ground_truth)
    print(f"Accuracy: {accuracy:.2%}")
    
    # Confusion Matrix
    cm = confusion_matrix(predictions, ground_truth)
    print("Confusion Matrix:")
    print(cm)
    
    # Per-class accuracy (Precision & Recall)
    from sklearn.metrics import classification_report
    print(classification_report(predictions, ground_truth))
    
    return {
        'accuracy': accuracy,
        'confusion_matrix': cm
    }
```

**Target KPI:**
- Accuracy: > 80% (sebelum fine-tuning)
- Accuracy: > 92% (setelah fine-tuning dengan 500+ images)

---

## 💡 Tips Optimasi

### **1. Improve Prompt (No Cost)**
- ✅ Sudah diterapkan di file Anda
- Tambah contoh visual untuk setiap Desil
- Tambah negative examples ("bukan Desil 5-6")

### **2. Better Image Input**
- Pastikan image clear dan well-lit
- Multiple angles per rumah (depan, samping, belakang)
- Include interior shots jika possible

### **3. Post-processing Logic**
```python
# Jika confidence < 50%, ask for more context
if response['confidence_percentage'] < 50:
    # Request additional images
    # Or ask user for manual input
    pass

# Jika hasil inconsistent across images, average
if len(results) > 1:
    avg_score = sum([r['confidence_percentage'] for r in results]) / len(results)
    final_classification = results[np.argmax([r['confidence_percentage'] for r in results])]['classification']
```

---

## 🚀 Next Steps

### **Immediate (Today):**
1. ✅ Test updated system prompt dengan test image
2. ✅ Verify JSON output parsing works

### **This Week:**
1. ⬜ Collect 50-100 training images per Desil
2. ⬜ Create labeling spreadsheet
3. ⬜ Document classification criteria dengan photos

### **Next Month:**
1. ⬜ Run fine-tuning
2. ⬜ Evaluate improved model
3. ⬜ Deploy to production

---

## 📞 Support Resources

- **Google Gemini API:** https://aistudio.google.com/
- **Fine-tuning Guide:** https://ai.google.dev/docs/tuning
- **Training Data Format:** https://ai.google.dev/docs/models/customize

---

**Created:** Jan 31, 2026
**Status:** System Prompt Optimized ✅
