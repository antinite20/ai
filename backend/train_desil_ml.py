"""
Training Script for Desil Classifier
Demonstrates how to train the ML model with labeled data
"""

import os
import numpy as np
from pathlib import Path
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import matplotlib.pyplot as plt
from ml_desil_classifier import DesilClassifierCNN, HouseFeatureExtractor


class TrainingPipeline:
    """Complete training pipeline for desil classifier"""
    
    def __init__(self, data_dir: str, model_save_path: str = "desil_model.h5"):
        """
        Initialize training pipeline
        
        Args:
            data_dir: Directory containing train/val folders
            model_save_path: Path to save trained model
        """
        self.data_dir = data_dir
        self.model_save_path = model_save_path
        self.train_dir = os.path.join(data_dir, 'train')
        self.val_dir = os.path.join(data_dir, 'val')
        self.classifier = None
        self.history = None
        
    def validate_data_structure(self) -> bool:
        """Validate that data is organized correctly"""
        required_dirs = [
            self.train_dir,
            self.val_dir
        ]
        
        required_classes = [
            'class_0',  # Desil 1-2
            'class_1',  # Desil 3-4
            'class_2',  # Desil 5-6
            'class_3',  # Desil 7-8
            'class_4'   # Desil 9-10
        ]
        
        print("=" * 60)
        print("VALIDATING DATA STRUCTURE")
        print("=" * 60)
        
        for dir_path in required_dirs:
            if not os.path.exists(dir_path):
                print(f"❌ Missing directory: {dir_path}")
                return False
            print(f"✓ Found: {dir_path}")
            
            for class_dir in required_classes:
                class_path = os.path.join(dir_path, class_dir)
                if not os.path.exists(class_path):
                    print(f"  ❌ Missing class: {class_dir}")
                    return False
                
                num_images = len([f for f in os.listdir(class_path) 
                                 if f.endswith(('.jpg', '.jpeg', '.png'))])
                print(f"  ✓ {class_dir}: {num_images} images")
        
        print("✓ Data structure validated!\n")
        return True
    
    def create_data_generators(self, batch_size: int = 32):
        """Create data generators for training and validation"""
        
        print("=" * 60)
        print("CREATING DATA GENERATORS")
        print("=" * 60)
        
        # Training data generator with augmentation
        train_datagen = ImageDataGenerator(
            rescale=1./255,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            fill_mode='nearest'
        )
        
        # Validation data generator (no augmentation)
        val_datagen = ImageDataGenerator(rescale=1./255)
        
        # Load training data
        self.train_generator = train_datagen.flow_from_directory(
            self.train_dir,
            target_size=(224, 224),
            batch_size=batch_size,
            class_mode='categorical',
            shuffle=True
        )
        
        # Load validation data
        self.val_generator = val_datagen.flow_from_directory(
            self.val_dir,
            target_size=(224, 224),
            batch_size=batch_size,
            class_mode='categorical',
            shuffle=False
        )
        
        print(f"✓ Training generator: {len(self.train_generator)} batches")
        print(f"✓ Validation generator: {len(self.val_generator)} batches")
        print(f"✓ Batch size: {batch_size}\n")
        
        return self.train_generator, self.val_generator
    
    def build_and_compile_model(self, learning_rate: float = 1e-3):
        """Build and compile the model"""
        
        print("=" * 60)
        print("BUILDING MODEL")
        print("=" * 60)
        
        self.classifier = DesilClassifierCNN(
            input_shape=(224, 224, 3),
            num_classes=5
        )
        
        self.classifier.build_model()
        self.classifier.compile_model(learning_rate=learning_rate)
        
        # Print model summary
        print("\nModel Architecture:")
        self.classifier.model.summary()
        
        return self.classifier
    
    def train_model(self, epochs: int = 50, batch_size: int = 32):
        """Train the model"""
        
        print("\n" + "=" * 60)
        print("TRAINING MODEL")
        print("=" * 60 + "\n")
        
        # Prepare data generators
        self.create_data_generators(batch_size=batch_size)
        
        # Train
        self.history = self.classifier.model.fit(
            self.train_generator,
            validation_data=self.val_generator,
            epochs=epochs,
            verbose=1
        )
        
        return self.history
    
    def evaluate_model(self):
        """Evaluate model performance"""
        
        print("\n" + "=" * 60)
        print("EVALUATING MODEL")
        print("=" * 60)
        
        # Evaluate on validation set
        eval_result = self.classifier.model.evaluate(self.val_generator)
        
        print(f"\nValidation Loss: {eval_result[0]:.4f}")
        print(f"Validation Accuracy: {eval_result[1]:.4f}")
        print(f"Validation AUC: {eval_result[2]:.4f}")
        
        return eval_result
    
    def plot_training_history(self, save_path: str = "training_history.png"):
        """Plot training history"""
        
        if self.history is None:
            print("No training history available")
            return
        
        fig, axes = plt.subplots(1, 2, figsize=(15, 5))
        
        # Accuracy
        axes[0].plot(self.history.history['accuracy'], label='Train Accuracy')
        axes[0].plot(self.history.history['val_accuracy'], label='Val Accuracy')
        axes[0].set_title('Model Accuracy')
        axes[0].set_xlabel('Epoch')
        axes[0].set_ylabel('Accuracy')
        axes[0].legend()
        axes[0].grid(True)
        
        # Loss
        axes[1].plot(self.history.history['loss'], label='Train Loss')
        axes[1].plot(self.history.history['val_loss'], label='Val Loss')
        axes[1].set_title('Model Loss')
        axes[1].set_xlabel('Epoch')
        axes[1].set_ylabel('Loss')
        axes[1].legend()
        axes[1].grid(True)
        
        plt.tight_layout()
        plt.savefig(save_path)
        print(f"\n✓ Training history saved to {save_path}")
        
    def save_model(self):
        """Save trained model"""
        
        if self.classifier is None or self.classifier.model is None:
            print("No model to save")
            return
        
        self.classifier.model.save(self.model_save_path)
        print(f"\n✓ Model saved to {self.model_save_path}")
    
    def run_full_training(self, epochs: int = 50, batch_size: int = 32):
        """Run complete training pipeline"""
        
        # Validate data
        if not self.validate_data_structure():
            print("Data validation failed. Please check your data directory.")
            return False
        
        # Build model
        self.build_and_compile_model()
        
        # Train
        self.train_model(epochs=epochs, batch_size=batch_size)
        
        # Evaluate
        self.evaluate_model()
        
        # Plot history
        self.plot_training_history()
        
        # Save
        self.save_model()
        
        print("\n" + "=" * 60)
        print("✓ TRAINING COMPLETE!")
        print("=" * 60)
        
        return True


# ============================================
# USAGE EXAMPLE
# ============================================

def example_directory_structure():
    """Print example directory structure"""
    
    print("""
    EXPECTED DATA DIRECTORY STRUCTURE:
    
    data/
    ├── train/
    │   ├── class_0/          (Desil 1-2: Miskin)
    │   │   ├── image1.jpg
    │   │   ├── image2.jpg
    │   │   └── ...
    │   ├── class_1/          (Desil 3-4: Bawah Menengah)
    │   │   ├── image1.jpg
    │   │   └── ...
    │   ├── class_2/          (Desil 5-6: Menengah)
    │   │   ├── image1.jpg
    │   │   └── ...
    │   ├── class_3/          (Desil 7-8: Atas Menengah)
    │   │   ├── image1.jpg
    │   │   └── ...
    │   └── class_4/          (Desil 9-10: Kaya)
    │       ├── image1.jpg
    │       └── ...
    │
    └── val/
        ├── class_0/
        │   ├── image1.jpg
        │   └── ...
        ├── class_1/
        │   └── ...
        ├── class_2/
        │   └── ...
        ├── class_3/
        │   └── ...
        └── class_4/
            └── ...
    
    RECOMMENDED DATA DISTRIBUTION:
    - Each class: 500-1000 images
    - Train/Val split: 80/20
    - Total images: 2500-5000
    
    IMAGE REQUIREMENTS:
    - Format: JPG, PNG
    - Size: Any (will be resized to 224x224)
    - Quality: Clear, well-lit
    - Content: House fronts, interiors, surroundings
    """)


def create_example_structure(base_dir: str = "data"):
    """Create example directory structure"""
    
    print(f"Creating example data structure in {base_dir}...")
    
    classes = ['class_0', 'class_1', 'class_2', 'class_3', 'class_4']
    
    for split in ['train', 'val']:
        for class_dir in classes:
            path = os.path.join(base_dir, split, class_dir)
            os.makedirs(path, exist_ok=True)
            print(f"✓ Created {path}")
    
    print(f"✓ Directory structure created!\n")
    print("Next steps:")
    print(f"1. Add house images to {base_dir}/train/class_*/")
    print(f"2. Add house images to {base_dir}/val/class_*/")
    print("3. Run training with: pipeline.run_full_training()\n")


# ============================================
# MAIN EXECUTION
# ============================================

if __name__ == "__main__":
    
    print("\n" + "=" * 60)
    print("DESIL CLASSIFIER - TRAINING SCRIPT")
    print("=" * 60 + "\n")
    
    # Show example structure
    example_directory_structure()
    
    print("\n" + "=" * 60)
    print("QUICK START")
    print("=" * 60 + "\n")
    
    print("Option 1: Create directory structure")
    print("  from train_desil_ml import create_example_structure")
    print("  create_example_structure('data')\n")
    
    print("Option 2: Run training (if data exists)")
    print("  from train_desil_ml import TrainingPipeline")
    print("  pipeline = TrainingPipeline('data', 'desil_model.h5')")
    print("  pipeline.run_full_training(epochs=50, batch_size=32)\n")
    
    print("Option 3: Train with custom parameters")
    print("""
  pipeline = TrainingPipeline('data', 'my_model.h5')
  
  # Validate
  if pipeline.validate_data_structure():
      # Build
      pipeline.build_and_compile_model(learning_rate=1e-3)
      
      # Train
      pipeline.train_model(epochs=100, batch_size=16)
      
      # Evaluate
      pipeline.evaluate_model()
      
      # Save
      pipeline.save_model()
    """)
    
    # Uncomment below to create example structure:
    # create_example_structure('data')
