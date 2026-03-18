# 🧠 ML-Based Desil Classifier - Technical Documentation

## Overview

Sistem klasifikasi berbasis Machine Learning untuk menentukan level desil ekonomi rumah berdasarkan analisis gambar visual.

---

## 📂 File Structure

```
backend/
├── ml_desil_classifier.py      # Core ML model & feature extraction
├── train_desil_ml.py           # Training pipeline
├── streamlit_ml_app.py         # Interactive web interface
└── requirements_ml.txt         # Dependencies
```

---

## 🏗️ Architecture Components

### 1. **HouseFeatureExtractor** (ml_desil_classifier.py)

Ekstraksi fitur visual dari gambar rumah:

#### Color Distribution
```python
# Analisis distribusi warna untuk menentukan material
- red_ratio: Batu bata/tanah
- brown_ratio: Material berkualitas
- green_ratio: Vegetasi/landscaping
- gray_ratio: Beton/semen
```

#### Texture Features
```python
# Analisis tekstur permukaan
- edge_density: Densitas tepi (maintenance level)
  High edge = well-maintained, Low edge = neglected
- texture_variance: Kompleksitas tekstur
  High variance = complex, Low variance = simple
```

#### Structural Features
```python
# Analisis struktur bangunan
- corner_density: Detail arsitektur
- horizontal_lines: Garis horizontal bangunan
- vertical_lines: Garis vertikal bangunan
- structural_complexity: Kombinasi
```

#### Brightness & Contrast
```python
- mean_brightness: Tingkat pencahayaan
- brightness_std: Variasi pencahayaan
- contrast: Kontras keseluruhan
```

**Output:** Vektor fitur 13-dimensi (normalized 0-1)

---

### 2. **DesilClassifierCNN** (ml_desil_classifier.py)

Arsitektur Convolutional Neural Network:

```
Input (224x224x3)
  ↓
[Data Augmentation]
  - RandomFlip
  - RandomRotation (±10°)
  - RandomZoom (±10%)
  ↓
[Normalization Layer]
  ↓
[Conv Block 1]
  - Conv2D(32, 3x3) → ReLU
  - Conv2D(32, 3x3) → ReLU
  - BatchNorm → MaxPool(2x2) → Dropout(0.25)
  ↓
[Conv Block 2]
  - Conv2D(64, 3x3) → ReLU
  - Conv2D(64, 3x3) → ReLU
  - BatchNorm → MaxPool(2x2) → Dropout(0.25)
  ↓
[Conv Block 3]
  - Conv2D(128, 3x3) → ReLU
  - Conv2D(128, 3x3) → ReLU
  - BatchNorm → MaxPool(2x2) → Dropout(0.25)
  ↓
[Conv Block 4]
  - Conv2D(256, 3x3) → ReLU
  - Conv2D(256, 3x3) → ReLU
  - BatchNorm → MaxPool(2x2) → Dropout(0.25)
  ↓
[Global Average Pooling]
  ↓
[Dense Layers]
  - Dense(512) → ReLU → BatchNorm → Dropout(0.5)
  - Dense(256) → ReLU → BatchNorm → Dropout(0.5)
  - Dense(128) → ReLU → BatchNorm → Dropout(0.3)
  ↓
[Output Layer]
  - Dense(5, softmax) → 5 Desil Classes
```

**Parameters:**
- Total: ~15-20 juta parameters
- Optimizer: Adam (lr=0.001)
- Loss: Categorical Crossentropy
- Metrics: Accuracy, AUC

---

### 3. **HybridDesilClassifier** (ml_desil_classifier.py)

Kombinasi CNN + Manual Features:

```
Input Image
  ↓
Split into two paths:

Path 1 (60% weight):        Path 2 (40% weight):
  ↓                           ↓
CNN Model              Manual Feature Extraction
  ↓                           ↓
Softmax Probabilities   Feature-based Scoring
  ↓                           ↓
Desil Prediction        Desil Ranking
  ↓                           ↓
Weighted Average ← Combine Results
  ↓
Final Desil Classification + Confidence
```

**Weighted Voting:**
```python
final_score = (CNN_confidence × 0.6) + (Manual_score × 0.4)
```

---

## 🎯 Classification Levels

| Desil | Class | Ukuran | Material | Amenitas | Kondisi |
|-------|-------|--------|----------|----------|---------|
| 1-2 | Miskin | <25m² | Kayu/bamboo | Tidak ada | Rusak |
| 3-4 | Bawah Menengah | 25-50m² | Kayu+bata | Listrik | Biasa |
| 5-6 | Menengah | 50-100m² | Bata berkualitas | Listrik+air | Terawat |
| 7-8 | Atas Menengah | 100-150m² | Beton | AC | Premium |
| 9-10 | Kaya | >150m² | Material import | Multiple | Mewah |

---

## 📊 Manual Scoring Algorithm

```python
score = (
    brick_ratio × 0.30 +           # Material quality
    condition_score × 0.25 +       # Maintenance
    complexity_score × 0.25 +      # Structural
    brightness_score × 0.20        # Lighting
)

# Map score to Desil:
if score < 0.25:     → Desil 1-2
elif score < 0.40:   → Desil 3-4
elif score < 0.55:   → Desil 5-6
elif score < 0.70:   → Desil 7-8
else:                → Desil 9-10
```

---

## 🚀 Training & Deployment

### Setup Requirements

```bash
pip install -r requirements_ml.txt
```

**requirements_ml.txt:**
```
tensorflow==2.13.0
keras==2.13.0
numpy==1.24.0
opencv-python==4.8.0
pillow==10.0.0
scikit-learn==1.3.0
streamlit==1.28.0
matplotlib==3.7.0
```

### Data Preparation

**Directory Structure:**
```
data/
├── train/
│   ├── class_0/  (Desil 1-2: 500+ images)
│   ├── class_1/  (Desil 3-4: 500+ images)
│   ├── class_2/  (Desil 5-6: 500+ images)
│   ├── class_3/  (Desil 7-8: 500+ images)
│   └── class_4/  (Desil 9-10: 500+ images)
└── val/
    ├── class_0/
    ├── class_1/
    ├── class_2/
    ├── class_3/
    └── class_4/
```

**Image Requirements:**
- Format: JPG, PNG, WebP
- Size: Any (resized to 224×224)
- Quality: Clear, well-lit
- Angles: Front, side, interior, yard
- Total: 2500-5000 images recommended

### Training Pipeline

**Step 1: Create Directory Structure**
```python
from train_desil_ml import create_example_structure
create_example_structure('data')
```

**Step 2: Add Images to Classes**
```
Place house images in appropriate class folders
based on known/verified desil level
```

**Step 3: Run Training**
```python
from train_desil_ml import TrainingPipeline

pipeline = TrainingPipeline('data', 'desil_model.h5')
pipeline.run_full_training(
    epochs=50,
    batch_size=32
)
```

**Step 4: Monitor Training**
```
- Accuracy should reach 80-90% on validation
- Loss should decrease smoothly
- Training history saved to training_history.png
```

---

## 💻 Usage Examples

### Example 1: Manual Feature Analysis Only

```python
from ml_desil_classifier import HouseFeatureExtractor
import cv2

# Load image
image = cv2.imread('house.jpg')
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Extract features
extractor = HouseFeatureExtractor()
processed = extractor.preprocess_image(image)
features = extractor.extract_all_features(processed)

print(f"Features: {features}")
# [0.15, 0.32, 0.08, 0.25, 0.45, 0.12, ...]
```

### Example 2: CNN Prediction

```python
from ml_desil_classifier import DesilClassifierCNN

# Load model
classifier = DesilClassifierCNN()
classifier.model = keras.models.load_model('desil_model.h5')

# Predict
result = classifier.predict(processed_image)

print(result)
# {
#   'desil_range': '5-6',
#   'classification': 'Menengah',
#   'confidence': 'Tinggi',
#   'confidence_percentage': 85,
#   'all_probabilities': {...}
# }
```

### Example 3: Hybrid Prediction

```python
from ml_desil_classifier import HybridDesilClassifier

# Initialize
hybrid = HybridDesilClassifier()

# Load trained model
hybrid.cnn_model.model = keras.models.load_model('desil_model.h5')

# Predict
result = hybrid.predict_hybrid(processed_image)

print(result)
# {
#   'method': 'hybrid',
#   'desil_range': '5-6',
#   'classification': 'Menengah',
#   'confidence': 'Tinggi',
#   'confidence_percentage': 84,
#   'cnn_prediction': {...},
#   'manual_score': 0.58
# }
```

### Example 4: Multiple Image Analysis

```python
import os
from PIL import Image
import numpy as np

# Analyze multiple images
images_dir = 'house_photos/'
results = []

for img_file in os.listdir(images_dir):
    img_path = os.path.join(images_dir, img_file)
    image = Image.open(img_path)
    
    # Process
    processed = extractor.preprocess_image(image)
    result = classifier.predict(processed)
    result['image'] = img_file
    results.append(result)

# Aggregate results (voting)
desil_votes = [r['desil_range'] for r in results]
final_desil = max(set(desil_votes), key=desil_votes.count)
print(f"Final Desil (voting): {final_desil}")
```

---

## 📈 Performance Metrics

### Expected Accuracy by Method

| Method | Accuracy | Training Time | Hardware |
|--------|----------|---------------|----------|
| Manual Features Only | 70-75% | <1 min | CPU |
| CNN (trained) | 85-90% | 2-3 hours | GPU |
| Hybrid (optimized) | 82-88% | 2-3 hours | GPU |

### Training Hardware Recommendations

**Minimum:**
- CPU: 4 cores
- RAM: 8GB
- Storage: 10GB

**Recommended:**
- GPU: NVIDIA (CUDA 11.8+) or Apple Silicon
- RAM: 16GB+
- Storage: 50GB SSD

**High-End:**
- GPU: RTX 3090 / A100
- RAM: 32GB+
- Storage: 100GB+ NVMe

---

## 🔧 Configuration & Hyperparameters

### CNN Training

```python
# Default hyperparameters
learning_rate = 0.001      # Adam optimizer
batch_size = 32             # Images per batch
epochs = 50                 # Training iterations
dropout_rate = 0.25-0.5     # Regularization

# Early stopping
patience = 10               # Epochs without improvement
restore_best_weights = True

# Learning rate reduction
factor = 0.5                # Reduce by 50%
lr_patience = 5             # Epochs to wait
min_lr = 1e-7               # Minimum learning rate
```

### Manual Scoring Weights

```python
# Feature importance (can be tuned)
material_weight = 0.30      # Brick/concrete ratio
condition_weight = 0.25     # Maintenance & edges
complexity_weight = 0.25    # Structural details
brightness_weight = 0.20    # Lighting quality
```

---

## 🎛️ Advanced: Custom Model Modification

### Add Custom Layers

```python
class CustomDesilCNN(DesilClassifierCNN):
    def build_model(self):
        model = keras.Sequential([
            # ... existing layers ...
            
            # Add custom attention layer
            layers.AdditiveAttention(),
            
            # ... rest of model ...
        ])
        self.model = model
        return model
```

### Use Transfer Learning

```python
# Use pre-trained ResNet50
base_model = keras.applications.ResNet50(
    weights='imagenet',
    include_top=False,
    input_shape=(224, 224, 3)
)

model = keras.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dense(256, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(5, activation='softmax')
])
```

---

## 🚨 Troubleshooting

### Model Overfitting
- Increase dropout rates
- Add L1/L2 regularization
- Use more data augmentation
- Reduce model complexity

### Slow Training
- Use GPU acceleration
- Reduce image resolution (to 128×128)
- Use smaller batch size
- Use transfer learning

### Poor Accuracy
- Check data quality & balance
- Verify class distribution
- Add more training data
- Tune hyperparameters

### Memory Issues
- Reduce batch size
- Use gradient checkpointing
- Split data into smaller chunks
- Use mixed precision training

---

## 📚 References

- TensorFlow/Keras: https://www.tensorflow.org
- CNN Architectures: https://github.com/tensorflow/models
- Image Processing: https://docs.opencv.org
- Best Practices: https://keras.io/guides/

---

## 📝 License & Attribution

Development code for house socioeconomic classification system.

---

## 🤝 Support

For issues or improvements:
1. Check troubleshooting section
2. Review training logs
3. Validate data structure
4. Test on sample images

---

**Last Updated:** February 2026
**Status:** Production Ready
