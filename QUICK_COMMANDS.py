#!/usr/bin/env python3
"""
QUICK COMMANDS REFERENCE
Perintah-perintah siap pakai untuk testing dan training AI
"""

# =============================================================================
# 1. TEST SISTEM PROMPT DENGAN PHOTO SENDIRI
# =============================================================================

"""
COMMAND:
$ python test_updated_prompt.py

EDIT DULU:
Buka test_updated_prompt.py dan ubah:
- image_path = "path/to/your/image.jpg"
- test_name = "Deskripsi rumah Anda"

EXPECTED OUTPUT:
{
    "classification": "Low Income|Lower-Middle|Middle|Upper-Middle|High Income",
    "desil_range": "1-2|3-4|5-6|7-8|9-10",
    "confidence": "Low|Medium|High",
    "confidence_percentage": 75
    ...
}
"""

# =============================================================================
# 2. TEST DENGAN STREAMLIT (LOCAL)
# =============================================================================

"""
COMMAND:
$ cd backend
$ streamlit run streamlit_local.py

BUKA:
http://localhost:8501

GUNAKAN:
- Upload foto rumah
- Klik "Analyze House"
- Lihat JSON output di result
- Check apakah classification sesuai Desil
"""

# =============================================================================
# 3. SETUP PYTHON ENVIRONMENT
# =============================================================================

"""
COMMAND (Windows):
$ pip install -r backend/requirements.txt

COMMAND (Linux/Mac):
$ pip install -r backend/requirements.txt

KEY PACKAGES:
- google-generativeai
- streamlit
- pillow
- dotenv
"""

# =============================================================================
# 4. KONFIGURASI API KEY
# =============================================================================

"""
1. DAPATKAN API KEY:
   https://aistudio.google.com/apikey

2. CREATE FILE: backend/.env
   GOOGLE_API_KEY=your_key_here

3. TEST CONNECTION:
"""

import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GOOGLE_API_KEY")
print(f"API Key configured: {bool(api_key)}")

# =============================================================================
# 5. MANUAL TESTING CODE
# =============================================================================

"""
Gunakan script ini untuk test prompt dengan foto:
"""

# COPY-PASTE KE PYTHON:

import google.generativeai as genai
from PIL import Image
import json
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()
api_key = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# Load image
image = Image.open("path/to/your/image.jpg")

# System prompt dari streamlit_local.py
SYSTEM_PROMPT = """You are an expert socioeconomic analyst...
[Gunakan prompt dari backend/streamlit_local.py]
"""

# Generate analysis
model = genai.GenerativeModel('gemini-2.5-flash')
response = model.generate_content([
    SYSTEM_PROMPT,
    "Analyze this house image and provide ONLY JSON output.",
    image
])

# Parse JSON
try:
    result = json.loads(response.text)
    print(f"Classification: {result['classification']}")
    print(f"Desil: {result['desil_range']}")
    print(f"Confidence: {result['confidence_percentage']}%")
except json.JSONDecodeError:
    print("Failed to parse JSON")
    print(response.text)

# =============================================================================
# 6. BATCH TESTING MULTIPLE IMAGES
# =============================================================================

"""
Untuk test 10+ images sekaligus:
"""

import glob
from pathlib import Path

# Prepare
images_folder = "path/to/test_images"
results = []

# Process
for image_file in glob.glob(f"{images_folder}/*.jpg"):
    image = Image.open(image_file)
    response = model.generate_content([SYSTEM_PROMPT, "Analyze", image])
    
    try:
        result = json.loads(response.text)
        results.append({
            'file': Path(image_file).name,
            'classification': result['classification'],
            'desil': result['desil_range'],
            'confidence': result['confidence_percentage']
        })
    except:
        results.append({'file': Path(image_file).name, 'error': 'Parse failed'})

# Summary
print("\nSUMMARY:")
print(f"Total: {len(results)}")
for r in results:
    if 'error' not in r:
        print(f"{r['file']}: {r['classification']} (Desil {r['desil']}) - {r['confidence']}%")

# =============================================================================
# 7. ACCURACY MEASUREMENT
# =============================================================================

"""
Measure accuracy vs ground truth
"""

from sklearn.metrics import confusion_matrix, accuracy_score, classification_report

# Data
predictions = ["Low Income", "Middle Income", "High Income", ...]  # AI results
ground_truth = ["Low Income", "Middle Income", "High Income", ...]  # Manual labels

# Calculate
accuracy = accuracy_score(predictions, ground_truth)
print(f"Accuracy: {accuracy:.2%}")

# Per-class
print(classification_report(predictions, ground_truth))

# =============================================================================
# 8. PREPARE TRAINING DATA FOR FINE-TUNING
# =============================================================================

"""
Format data untuk fine-tuning Google Gemini
"""

import json
import csv

# OPTION 1: CSV FORMAT
def prepare_training_csv(image_folder):
    """
    Create CSV: image_path, classification, desil_range, features
    """
    data = []
    
    # Manual loop through images
    for img_file in os.listdir(image_folder):
        # MANUAL LABELING:
        # 1. Look at image
        # 2. Determine: classification, desil_range, key features
        # 3. Add to list
        
        data.append({
            'image_path': os.path.join(image_folder, img_file),
            'classification': 'Low Income',  # FROM YOUR JUDGMENT
            'desil_range': '1-2',  # FROM YOUR JUDGMENT
            'features': 'wood, tin roof, <25m2'
        })
    
    # Write CSV
    with open('training_data.csv', 'w') as f:
        writer = csv.DictWriter(f, fieldnames=['image_path', 'classification', 'desil_range', 'features'])
        writer.writeheader()
        writer.writerows(data)

# OPTION 2: JSON FORMAT
def prepare_training_json(image_folder):
    """
    Create JSON for Google AI fine-tuning
    """
    data = {
        "training_data": []
    }
    
    # Manual labeling
    data["training_data"].append({
        "image_url": "gs://bucket/rumah_desil_5.jpg",
        "classification": "Middle Income",
        "desil_range": "5-6",
        "features": {
            "size_m2": 75,
            "materials": ["brick", "concrete"],
            "roof": "ceramic tiles",
            "amenities": ["electricity_meter", "water_tank"]
        }
    })
    
    # Write JSON
    with open('training_data.json', 'w') as f:
        json.dump(data, f, indent=2)

# =============================================================================
# 9. GOOGLE AI STUDIO FINE-TUNING STEPS
# =============================================================================

"""
MANUAL STEPS in Google AI Studio:

1. Go to: https://aistudio.google.com/
2. Click: "Tune a Model"
3. Select: "gemini-2.5-flash"
4. Upload: training_data.csv or training_data.json
5. Set:
   - Learning rate: 0.001
   - Batch size: 4
   - Epochs: 5-10
6. Click: "Start tuning"
7. Wait: 1-2 hours
8. Get: New model ID (e.g., tuned-gemini-xxxxx)
9. Copy: Model ID untuk update code
"""

# =============================================================================
# 10. UPDATE CODE DENGAN TUNED MODEL
# =============================================================================

"""
Setelah fine-tuning selesai:

1. COPY model ID dari Google AI Studio
   Format: projects/123/locations/us-central1/endpoints/456

2. UPDATE streamlit_local.py:
   
   # OLD:
   model = genai.GenerativeModel('gemini-2.5-flash')
   
   # NEW:
   model = genai.GenerativeModel('projects/YOUR_PROJECT_ID/locations/us-central1/endpoints/YOUR_ENDPOINT')

3. TEST dengan foto yang sama
4. MEASURE accuracy improvement
5. DEPLOY ke production
"""

# =============================================================================
# 11. CUSTOM SCORING ENGINE (OPTIONAL)
# =============================================================================

"""
Implementasi scoring function untuk higher accuracy:
"""

def calculate_economic_score(image_analysis):
    """
    Calculate economic score 0-100 based on features
    """
    score = 0
    
    # Size scoring
    size = image_analysis.get('estimated_size_m2', 0)
    if size < 25:
        score += 2
    elif size < 50:
        score += 5
    elif size < 100:
        score += 8
    else:
        score += 12
    
    # Materials scoring
    materials = image_analysis.get('materials', [])
    material_score = 0
    for material in materials:
        if material in ['wood', 'bamboo']:
            material_score += 2
        elif material in ['brick']:
            material_score += 5
        elif material in ['concrete', 'ceramic']:
            material_score += 10
        elif material in ['marble', 'stone']:
            material_score += 15
    score += min(material_score, 20)
    
    # Amenities scoring
    amenities = image_analysis.get('amenities', [])
    if 'electricity_meter' in amenities:
        score += 5
    if 'water_tank' in amenities:
        score += 5
    if 'ac_unit' in amenities:
        score += 10
    if 'solar_panel' in amenities:
        score += 15
    
    # Map to Desil
    if score < 20:
        return 'Low Income', '1-2'
    elif score < 35:
        return 'Lower-Middle', '3-4'
    elif score < 55:
        return 'Middle Income', '5-6'
    elif score < 75:
        return 'Upper-Middle', '7-8'
    else:
        return 'High Income', '9-10'

# =============================================================================
# 12. MONITORING & METRICS
# =============================================================================

"""
Track performance metrics:
"""

def calculate_metrics(predictions, ground_truth):
    """
    Calculate comprehensive metrics
    """
    accuracy = accuracy_score(predictions, ground_truth)
    cm = confusion_matrix(predictions, ground_truth)
    
    print(f"Accuracy: {accuracy:.2%}")
    print(f"Confusion Matrix:\n{cm}")
    
    # Per-Desil accuracy
    from sklearn.metrics import precision_recall_fscore_support
    precision, recall, f1, support = precision_recall_fscore_support(
        ground_truth, predictions, average='weighted'
    )
    
    print(f"Precision: {precision:.2%}")
    print(f"Recall: {recall:.2%}")
    print(f"F1-Score: {f1:.2%}")

# =============================================================================
# 13. DEPLOYMENT TO PRODUCTION
# =============================================================================

"""
Deploy updated model:

1. Update model ID di:
   - backend/streamlit_local.py
   - backend/server.py
   - backend/streamlit_app.py

2. Test lokally:
   $ streamlit run backend/streamlit_local.py

3. Deploy ke production:
   $ git commit -am "Update to fine-tuned model"
   $ git push

4. Monitor:
   - Watch error rates
   - Track confidence scores
   - Log classifications
"""

# =============================================================================
# 14. TROUBLESHOOTING
# =============================================================================

"""
PROBLEM: JSON parse error
SOLUTION: Check model output, ensure no text before/after JSON

PROBLEM: Low confidence (<50%)
SOLUTION: 
  - Provide better image (clearer, multiple angles)
  - Add context information
  - Request fine-tuned model

PROBLEM: Wrong classification
SOLUTION:
  - Review Desil criteria in DESIL_QUICK_REFERENCE.md
  - Check image quality
  - Consider fine-tuning with more data

PROBLEM: Slow processing
SOLUTION:
  - Use batch processing
  - Implement caching
  - Upgrade to faster model
"""

# =============================================================================
# 15. NEXT STEPS
# =============================================================================

"""
WEEK 1:
[1] Run test_updated_prompt.py dengan 10+ images
[2] Measure accuracy vs manual labels
[3] Document results

WEEK 2-3:
[4] Collect 50 images per Desil level (250+ total)
[5] Label dengan classification, desil, features
[6] Prepare training CSV/JSON

WEEK 4:
[7] Upload to Google AI Studio
[8] Run fine-tuning
[9] Test new model

WEEK 5:
[10] Deploy to production
[11] Monitor performance
[12] Iterate improvements
"""

# =============================================================================

if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║         QUICK COMMANDS REFERENCE - READY TO USE             ║
    ╚════════════════════════════════════════════════════════════╝
    
    See sections above for:
    1. Testing with photos
    2. Using Streamlit interface
    3. Setup environment
    4. Configure API key
    5. Manual testing code
    6. Batch testing
    7. Accuracy measurement
    8. Prepare training data
    9. Fine-tuning steps
    10. Update with tuned model
    11. Custom scoring
    12. Monitoring metrics
    13. Production deployment
    14. Troubleshooting
    15. Next steps
    
    START: python test_updated_prompt.py
    """)
