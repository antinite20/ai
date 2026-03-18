"""
Machine Learning-based Desil Classification Model
Uses CNN + Dense layers for house socioeconomic classification
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import cv2
from PIL import Image
import joblib
from typing import Tuple, Dict, List
import json
import base64
from io import BytesIO


# ============================================
# FEATURE EXTRACTION
# ============================================

class HouseFeatureExtractor:
    """Extract visual features from house images"""
    
    def __init__(self):
        self.image_size = (224, 224)
        self.color_ranges = {
            'red': ([0, 0, 100], [10, 100, 255]),
            'brown': ([80, 80, 100], [120, 150, 180]),
            'green': ([50, 100, 0], [100, 180, 100]),
            'gray': ([80, 80, 80], [150, 150, 150]),
            'black': ([0, 0, 0], [50, 50, 50]),
        }
    
    def extract_color_distribution(self, image: np.ndarray) -> Dict[str, float]:
        """Extract color histogram features (0-1 normalized)"""
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        
        features = {}
        features['red_ratio'] = np.sum(np.logical_and(
            hsv[:,:,0] >= 0, hsv[:,:,0] <= 10
        )) / hsv.size
        
        features['brown_ratio'] = np.sum(np.logical_and(
            hsv[:,:,0] >= 10, hsv[:,:,0] <= 20
        )) / hsv.size
        
        features['green_ratio'] = np.sum(np.logical_and(
            hsv[:,:,0] >= 40, hsv[:,:,0] <= 80
        )) / hsv.size
        
        features['gray_ratio'] = np.sum(np.logical_and(
            hsv[:,:,1] < 30, hsv[:,:,2] > 100
        )) / hsv.size
        
        return features
    
    def extract_texture_features(self, image: np.ndarray) -> Dict[str, float]:
        """Extract texture features using edge detection"""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Edge detection
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        # Laplacian variance (texture complexity)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        texture_variance = np.var(laplacian)
        
        features = {
            'edge_density': min(edge_density, 1.0),
            'texture_variance': min(texture_variance / 10000, 1.0),  # normalized
        }
        
        return features
    
    def extract_structural_features(self, image: np.ndarray) -> Dict[str, float]:
        """Extract structural features (lines, corners, etc.)"""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Detect corners (Harris corners)
        corners = cv2.cornerHarris(gray, 2, 3, 0.04)
        corner_density = np.sum(corners > 0.01) / corners.size
        
        # Horizontal/vertical lines detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Count horizontal lines
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 1))
        h_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, horizontal_kernel)
        h_line_count = np.sum(h_lines > 0) / h_lines.size
        
        # Count vertical lines
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 30))
        v_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, vertical_kernel)
        v_line_count = np.sum(v_lines > 0) / v_lines.size
        
        features = {
            'corner_density': corner_density,
            'horizontal_lines': h_line_count,
            'vertical_lines': v_line_count,
            'structural_complexity': (h_line_count + v_line_count) / 2
        }
        
        return features
    
    def extract_brightness_contrast(self, image: np.ndarray) -> Dict[str, float]:
        """Extract lighting and contrast features"""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        features = {
            'mean_brightness': np.mean(gray) / 255.0,
            'brightness_std': np.std(gray) / 255.0,
            'contrast': np.max(gray) - np.min(gray) / 255.0
        }
        
        return features
    
    def extract_all_features(self, image: np.ndarray) -> np.ndarray:
        """Extract all features and return as vector"""
        color_features = self.extract_color_distribution(image)
        texture_features = self.extract_texture_features(image)
        structural_features = self.extract_structural_features(image)
        brightness_features = self.extract_brightness_contrast(image)
        
        # Combine all features in order
        feature_vector = [
            color_features['red_ratio'],
            color_features['brown_ratio'],
            color_features['green_ratio'],
            color_features['gray_ratio'],
            texture_features['edge_density'],
            texture_features['texture_variance'],
            structural_features['corner_density'],
            structural_features['horizontal_lines'],
            structural_features['vertical_lines'],
            structural_features['structural_complexity'],
            brightness_features['mean_brightness'],
            brightness_features['brightness_std'],
            brightness_features['contrast']
        ]
        
        return np.array(feature_vector, dtype=np.float32)
    
    def preprocess_image(self, image_path_or_array):
        """Load and preprocess image"""
        if isinstance(image_path_or_array, str):
            image = Image.open(image_path_or_array).convert('RGB')
            image = np.array(image)
        else:
            image = image_path_or_array
        
        # Resize
        image = cv2.resize(image, self.image_size)
        
        # Normalize to 0-1
        image = image.astype(np.float32) / 255.0
        
        return image


# ============================================
# CNN MODEL ARCHITECTURE
# ============================================

class DesilClassifierCNN:
    """CNN-based classifier for desil levels"""
    
    def __init__(self, input_shape=(224, 224, 3), num_classes=5):
        """
        Initialize CNN model
        Args:
            input_shape: Input image shape
            num_classes: Number of desil categories (5: 1-2, 3-4, 5-6, 7-8, 9-10)
        """
        self.input_shape = input_shape
        self.num_classes = num_classes
        self.model = None
        self.feature_extractor = HouseFeatureExtractor()
        self.scaler = None
        
    def build_model(self):
        """Build CNN architecture"""
        model = keras.Sequential([
            # Input layer
            layers.Input(shape=self.input_shape),
            
            # Data augmentation
            layers.RandomFlip("horizontal"),
            layers.RandomRotation(0.1),
            layers.RandomZoom(0.1),
            
            # Normalization
            layers.Normalization(),
            
            # Block 1
            layers.Conv2D(32, 3, padding='same', activation='relu'),
            layers.Conv2D(32, 3, padding='same', activation='relu'),
            layers.BatchNormalization(),
            layers.MaxPooling2D(2),
            layers.Dropout(0.25),
            
            # Block 2
            layers.Conv2D(64, 3, padding='same', activation='relu'),
            layers.Conv2D(64, 3, padding='same', activation='relu'),
            layers.BatchNormalization(),
            layers.MaxPooling2D(2),
            layers.Dropout(0.25),
            
            # Block 3
            layers.Conv2D(128, 3, padding='same', activation='relu'),
            layers.Conv2D(128, 3, padding='same', activation='relu'),
            layers.BatchNormalization(),
            layers.MaxPooling2D(2),
            layers.Dropout(0.25),
            
            # Block 4
            layers.Conv2D(256, 3, padding='same', activation='relu'),
            layers.Conv2D(256, 3, padding='same', activation='relu'),
            layers.BatchNormalization(),
            layers.MaxPooling2D(2),
            layers.Dropout(0.25),
            
            # Global pooling
            layers.GlobalAveragePooling2D(),
            
            # Dense layers
            layers.Dense(512, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.5),
            
            layers.Dense(256, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.5),
            
            layers.Dense(128, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            # Output
            layers.Dense(self.num_classes, activation='softmax')
        ])
        
        self.model = model
        return model
    
    def compile_model(self, learning_rate=1e-3):
        """Compile the model"""
        optimizer = keras.optimizers.Adam(learning_rate=learning_rate)
        self.model.compile(
            optimizer=optimizer,
            loss='categorical_crossentropy',
            metrics=['accuracy', keras.metrics.AUC()]
        )
    
    def train(self, X_train, y_train, X_val, y_val, epochs=50, batch_size=32):
        """Train the model"""
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-7
            )
        ]
        
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        return history
    
    def predict(self, image_array) -> Dict:
        """
        Predict desil level for image
        
        Args:
            image_array: Preprocessed image array
        
        Returns:
            Dictionary with prediction results
        """
        # Add batch dimension if needed
        if len(image_array.shape) == 3:
            image_array = np.expand_dims(image_array, axis=0)
        
        # Predict
        predictions = self.model.predict(image_array, verbose=0)
        prediction = predictions[0]
        
        desil_map = {
            0: "1-2",
            1: "3-4",
            2: "5-6",
            3: "7-8",
            4: "9-10"
        }
        
        classification_map = {
            0: "Miskin",
            1: "Bawah Menengah",
            2: "Menengah",
            3: "Atas Menengah",
            4: "Kaya"
        }
        
        predicted_class = np.argmax(prediction)
        confidence = float(prediction[predicted_class])
        
        # Determine confidence level
        if confidence > 0.7:
            confidence_level = "Tinggi"
        elif confidence > 0.4:
            confidence_level = "Sedang"
        else:
            confidence_level = "Rendah"
        
        return {
            "desil_range": desil_map[predicted_class],
            "classification": classification_map[predicted_class],
            "confidence": confidence_level,
            "confidence_percentage": int(confidence * 100),
            "all_probabilities": {
                "desil_1_2": float(prediction[0]),
                "desil_3_4": float(prediction[1]),
                "desil_5_6": float(prediction[2]),
                "desil_7_8": float(prediction[3]),
                "desil_9_10": float(prediction[4])
            }
        }


# ============================================
# HYBRID APPROACH: CNN + MANUAL FEATURES
# ============================================

class HybridDesilClassifier:
    """Combines CNN predictions with manual feature-based scoring"""
    
    def __init__(self):
        self.cnn_model = DesilClassifierCNN()
        self.feature_extractor = HouseFeatureExtractor()
        self.weights = {
            'cnn': 0.6,           # 60% weight on CNN
            'manual_features': 0.4 # 40% weight on manual features
        }
    
    def manual_scoring(self, features: Dict[str, float]) -> Tuple[int, float]:
        """
        Manual scoring based on extracted features
        
        Returns:
            (desil_index, score)
        """
        # Size indicator (from color distribution)
        # More brick/brown = better construction
        brick_score = features.get('brown_ratio', 0)
        wood_score = features.get('red_ratio', 0)
        
        # Material quality
        if brick_score > 0.3:
            material_score = 0.8  # Brick = better
        elif wood_score > 0.3:
            material_score = 0.4  # Wood = worse
        else:
            material_score = 0.6
        
        # Texture & maintenance (edge density = maintenance level)
        edge_density = features.get('edge_density', 0)
        if edge_density > 0.5:
            condition_score = 0.7  # Complex = maintained
        else:
            condition_score = 0.4  # Simple = neglected
        
        # Structural complexity
        structural = features.get('structural_complexity', 0)
        if structural > 0.6:
            complexity_score = 0.8  # Complex = wealthy
        else:
            complexity_score = 0.4  # Simple = poor
        
        # Brightness (well-lit = better maintained)
        brightness = features.get('mean_brightness', 0)
        if brightness > 0.6:
            brightness_score = 0.8
        else:
            brightness_score = 0.4
        
        # Weighted score
        total_score = (
            material_score * 0.3 +
            condition_score * 0.25 +
            complexity_score * 0.25 +
            brightness_score * 0.2
        )
        
        # Map score to desil
        if total_score < 0.25:
            desil_idx = 0  # 1-2
        elif total_score < 0.40:
            desil_idx = 1  # 3-4
        elif total_score < 0.55:
            desil_idx = 2  # 5-6
        elif total_score < 0.70:
            desil_idx = 3  # 7-8
        else:
            desil_idx = 4  # 9-10
        
        return desil_idx, total_score
    
    def predict_hybrid(self, image_array) -> Dict:
        """
        Hybrid prediction combining CNN and manual features
        """
        # CNN prediction
        cnn_result = self.cnn_model.predict(image_array)
        cnn_probs = cnn_result['all_probabilities']
        cnn_pred_idx = np.argmax([
            cnn_probs['desil_1_2'],
            cnn_probs['desil_3_4'],
            cnn_probs['desil_5_6'],
            cnn_probs['desil_7_8'],
            cnn_probs['desil_9_10']
        ])
        
        # Manual feature extraction
        features = self.feature_extractor.extract_all_features(image_array)
        features_dict = {
            'red_ratio': features[0],
            'brown_ratio': features[1],
            'green_ratio': features[2],
            'gray_ratio': features[3],
            'edge_density': features[4],
            'texture_variance': features[5],
            'mean_brightness': features[10]
        }
        
        manual_idx, manual_score = self.manual_scoring(features_dict)
        
        # Combine predictions (weighted average)
        combined_prob = (
            self.weights['cnn'] * cnn_result['confidence_percentage'] / 100 +
            self.weights['manual_features'] * manual_score
        )
        
        # Final prediction - average of both methods
        final_idx = int(round(
            self.weights['cnn'] * cnn_pred_idx +
            self.weights['manual_features'] * manual_idx
        ))
        
        desil_map = ["1-2", "3-4", "5-6", "7-8", "9-10"]
        classification_map = ["Miskin", "Bawah Menengah", "Menengah", "Atas Menengah", "Kaya"]
        
        return {
            "method": "hybrid",
            "desil_range": desil_map[final_idx],
            "classification": classification_map[final_idx],
            "confidence": "Tinggi" if combined_prob > 0.7 else ("Sedang" if combined_prob > 0.4 else "Rendah"),
            "confidence_percentage": int(combined_prob * 100),
            "cnn_prediction": cnn_result,
            "manual_features": features_dict,
            "manual_score": float(manual_score)
        }


# ============================================
# UTILITY FUNCTIONS
# ============================================

def save_model(model: DesilClassifierCNN, path: str):
    """Save trained model"""
    model.model.save(path)
    print(f"Model saved to {path}")


def load_model(path: str) -> DesilClassifierCNN:
    """Load trained model"""
    classifier = DesilClassifierCNN()
    classifier.model = keras.models.load_model(path)
    return classifier


def predict_from_base64(image_base64: str, model: DesilClassifierCNN) -> Dict:
    """Predict from base64 encoded image"""
    # Decode base64
    image_data = base64.b64decode(image_base64)
    image = Image.open(BytesIO(image_data)).convert('RGB')
    image_array = np.array(image)
    
    # Preprocess
    feature_extractor = HouseFeatureExtractor()
    processed_image = feature_extractor.preprocess_image(image_array)
    
    # Predict
    result = model.predict(processed_image)
    
    return result


# ============================================
# EXAMPLE TRAINING CODE
# ============================================

def example_training():
    """
    Example of how to train the model
    Requires: labeled training data in format
    - train_images/: folder with images
    - train_labels.csv: CSV with columns [image_name, desil_class]
    """
    
    print("=" * 60)
    print("DESIL CLASSIFIER - ML MODEL TRAINING EXAMPLE")
    print("=" * 60)
    
    # Initialize
    classifier = DesilClassifierCNN(num_classes=5)
    classifier.build_model()
    classifier.compile_model()
    
    print("\n✓ Model architecture built successfully!")
    print(f"  - Input shape: {classifier.input_shape}")
    print(f"  - Output classes: {classifier.num_classes}")
    print(f"  - Total parameters: {classifier.model.count_params():,}")
    
    print("\n" + "=" * 60)
    print("TRAINING DATA REQUIREMENTS:")
    print("=" * 60)
    print("""
    1. Create labeled dataset:
       - Desil 1-2 (Miskin): ~500 images
       - Desil 3-4 (Bawah Menengah): ~500 images
       - Desil 5-6 (Menengah): ~500 images
       - Desil 7-8 (Atas Menengah): ~500 images
       - Desil 9-10 (Kaya): ~500 images
       Total: ~2500 images
    
    2. Organize as:
       data/
       ├── train/
       │   ├── class_0/  (Desil 1-2)
       │   ├── class_1/  (Desil 3-4)
       │   ├── class_2/  (Desil 5-6)
       │   ├── class_3/  (Desil 7-8)
       │   └── class_4/  (Desil 9-10)
       └── val/
           ├── class_0/
           ├── class_1/
           ├── class_2/
           ├── class_3/
           └── class_4/
    
    3. Training code:
       from keras.preprocessing.image import ImageDataGenerator
       
       train_datagen = ImageDataGenerator(
           rescale=1./255,
           rotation_range=20,
           width_shift_range=0.2,
           height_shift_range=0.2,
           zoom_range=0.2
       )
       
       train_generator = train_datagen.flow_from_directory(
           'data/train',
           target_size=(224, 224),
           batch_size=32,
           class_mode='categorical'
       )
       
       val_generator = train_datagen.flow_from_directory(
           'data/val',
           target_size=(224, 224),
           batch_size=32,
           class_mode='categorical'
       )
       
       history = classifier.train(
           train_generator,
           val_generator,
           epochs=50,
           batch_size=32
       )
    """)


if __name__ == "__main__":
    example_training()
