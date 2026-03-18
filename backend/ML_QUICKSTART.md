# 🚀 Quick Start Guide - ML Desil Classifier

## Installation

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements_ml.txt
```

### 2. Verify Installation
```python
python -c "import tensorflow; print(f'TensorFlow {tensorflow.__version__}')"
python -c "import cv2; print(f'OpenCV {cv2.__version__}')"
```

---

## Quick Usage (Without Training)

### Manual Feature Analysis Only

```python
from ml_desil_classifier import HouseFeatureExtractor
from PIL import Image

# Load image
image = Image.open('house.jpg')

# Extract features
extractor = HouseFeatureExtractor()
processed = extractor.preprocess_image(image)
features = extractor.extract_all_features(processed)

# Print features
print(f"Color features: Red={features[0]:.2f}, Brown={features[1]:.2f}")
print(f"Texture: Edge Density={features[4]:.2f}")
print(f"Structural: Complexity={features[9]:.2f}")
```

### Run ML Web App (Feature-Based)

```bash
streamlit run streamlit_ml_app.py
```

Visit: `http://localhost:8501`

---

## Training with Your Data

### Step 1: Prepare Data

Create this folder structure:
```
data/
├── train/
│   ├── class_0/  (Desil 1-2: 100+ images)
│   ├── class_1/  (Desil 3-4: 100+ images)
│   ├── class_2/  (Desil 5-6: 100+ images)
│   ├── class_3/  (Desil 7-8: 100+ images)
│   └── class_4/  (Desil 9-10: 100+ images)
└── val/
    ├── class_0/  (10-20% of train data)
    ├── class_1/
    ├── class_2/
    ├── class_3/
    └── class_4/
```

### Step 2: Create Structure

```python
from train_desil_ml import create_example_structure
create_example_structure('data')  # Creates folders
# Then add your images to the class folders
```

### Step 3: Train Model

```python
from train_desil_ml import TrainingPipeline

# Create pipeline
pipeline = TrainingPipeline('data', 'desil_model.h5')

# Run training
pipeline.run_full_training(
    epochs=50,
    batch_size=32
)
```

### Step 4: Use Trained Model

```python
from ml_desil_classifier import DesilClassifierCNN
from PIL import Image
import tensorflow as tf

# Load model
classifier = DesilClassifierCNN()
classifier.model = tf.keras.models.load_model('desil_model.h5')

# Load & process image
image = Image.open('test_house.jpg')
processed = classifier.feature_extractor.preprocess_image(image)

# Predict
result = classifier.predict(processed)

print(f"Desil: {result['desil_range']}")
print(f"Class: {result['classification']}")
print(f"Confidence: {result['confidence_percentage']}%")
```

---

## API Integration

### Example: FastAPI Integration

```python
# api_desil.py
from fastapi import FastAPI, File, UploadFile
from PIL import Image
import json
from ml_desil_classifier import DesilClassifierCNN
import tensorflow as tf

app = FastAPI()

# Load model once
classifier = DesilClassifierCNN()
classifier.model = tf.keras.models.load_model('desil_model.h5')

@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    # Read image
    image = Image.open(file.file)
    
    # Process
    processed = classifier.feature_extractor.preprocess_image(image)
    
    # Predict
    result = classifier.predict(processed)
    
    return result

# Run: uvicorn api_desil:app --reload
```

---

## Methods Comparison

### Method 1: Manual Features Only (Fastest)
```python
from ml_desil_classifier import HouseFeatureExtractor

extractor = HouseFeatureExtractor()
processed = extractor.preprocess_image(image)
features = extractor.extract_all_features(processed)

# Manual scoring (see code)
score = (
    features[1] * 0.30 +  # brick
    features[4] * 0.25 +  # edges
    features[9] * 0.25 +  # complexity
    features[10] * 0.20   # brightness
)

if score < 0.25: desil = "1-2"
elif score < 0.40: desil = "3-4"
elif score < 0.55: desil = "5-6"
elif score < 0.70: desil = "7-8"
else: desil = "9-10"

print(f"Desil: {desil}, Score: {score:.2f}")
```

**Pros:** Fast, no training needed, interpretable
**Cons:** ~70-75% accuracy

---

### Method 2: CNN Only (Most Accurate)
```python
from ml_desil_classifier import DesilClassifierCNN
import tensorflow as tf

classifier = DesilClassifierCNN()
classifier.model = tf.keras.models.load_model('desil_model.h5')

result = classifier.predict(processed_image)

print(f"Desil: {result['desil_range']}")
print(f"Confidence: {result['confidence_percentage']}%")
```

**Pros:** ~85-90% accuracy
**Cons:** Requires training data

---

### Method 3: Hybrid (Best Balance)
```python
from ml_desil_classifier import HybridDesilClassifier
import tensorflow as tf

hybrid = HybridDesilClassifier()
hybrid.cnn_model.model = tf.keras.models.load_model('desil_model.h5')

result = hybrid.predict_hybrid(processed_image)

print(f"Desil: {result['desil_range']}")
print(f"Confidence: {result['confidence_percentage']}%")
# Shows both CNN and manual scores
```

**Pros:** ~82-88% accuracy, balanced
**Cons:** Requires trained model

---

## Testing & Validation

### Test with Sample Image

```python
import cv2
from ml_desil_classifier import HouseFeatureExtractor

# Load test image
img = cv2.imread('test_house.jpg')
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# Extract features
extractor = HouseFeatureExtractor()
processed = extractor.preprocess_image(img_rgb)

# Show detailed features
color_features = extractor.extract_color_distribution(processed)
texture_features = extractor.extract_texture_features(processed)
struct_features = extractor.extract_structural_features(processed)
brightness_features = extractor.extract_brightness_contrast(processed)

print("Color Features:")
for k, v in color_features.items():
    print(f"  {k}: {v:.4f}")

print("\nTexture Features:")
for k, v in texture_features.items():
    print(f"  {k}: {v:.4f}")

print("\nStructural Features:")
for k, v in struct_features.items():
    print(f"  {k}: {v:.4f}")

print("\nBrightness Features:")
for k, v in brightness_features.items():
    print(f"  {k}: {v:.4f}")
```

### Validate Model Performance

```python
from train_desil_ml import TrainingPipeline

pipeline = TrainingPipeline('data', 'desil_model.h5')

# Create data generators
train_gen, val_gen = pipeline.create_data_generators(batch_size=32)

# Evaluate on validation set
pipeline.classifier = pipeline.build_and_compile_model()
pipeline.classifier.model = tf.keras.models.load_model('desil_model.h5')

loss, accuracy, auc = pipeline.classifier.model.evaluate(val_gen)

print(f"Validation Loss: {loss:.4f}")
print(f"Validation Accuracy: {accuracy:.4f}")
print(f"Validation AUC: {auc:.4f}")
```

---

## Performance Tips

### Speed Up Feature Extraction
```python
# For batch processing
import numpy as np

images = [img1, img2, img3]
all_features = []

for img in images:
    processed = extractor.preprocess_image(img)
    features = extractor.extract_all_features(processed)
    all_features.append(features)

# More efficient with pre-processing
all_features = np.array(all_features)
```

### Use GPU for Training
```python
import tensorflow as tf

# Check GPU availability
print(f"GPU Available: {tf.config.list_physical_devices('GPU')}")

# Force GPU usage
with tf.device('/GPU:0'):
    pipeline.train_model(epochs=50)
```

### Batch Processing for Inference
```python
# Process multiple images at once
images = [img1, img2, img3, ...]
processed_images = np.array([
    classifier.feature_extractor.preprocess_image(img) 
    for img in images
])

# Predict batch
predictions = classifier.model.predict(processed_images)
```

---

## Troubleshooting

### Out of Memory
```python
# Reduce batch size
pipeline.train_model(epochs=50, batch_size=16)  # was 32

# Or use gradient checkpointing
# See ML_DOCUMENTATION.md for advanced options
```

### Poor Results
```python
# 1. Check data quality
# 2. Verify data distribution
# 3. Increase training epochs
# 4. Use more data augmentation
# 5. Tune hyperparameters
```

### Import Errors
```bash
# Reinstall all packages
pip install --upgrade -r requirements_ml.txt

# Check versions
python -c "import tensorflow; print(tensorflow.__version__)"
```

---

## Next Steps

1. ✅ Install dependencies
2. ✅ Try manual feature extraction
3. ✅ Prepare training data (optional)
4. ✅ Train CNN model (optional)
5. ✅ Deploy API or Streamlit app
6. ✅ Integrate into production

---

## Documentation

- **ML_DOCUMENTATION.md** - Complete technical docs
- **README.md** - General project info
- **Code comments** - Inline documentation

---

## Support

For issues:
1. Check error messages carefully
2. Review ML_DOCUMENTATION.md
3. Validate data structure
4. Test with sample images

Good luck! 🚀
