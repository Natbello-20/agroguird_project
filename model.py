"""
Disease Detection Model Module
Handles loading and running the TensorFlow model for crop disease detection.
"""

import os
import cv2 as cv2_module
from typing import Tuple, Optional
import random

# Lazy imports
np = None

# TensorFlow is imported lazily to avoid startup delays
TENSORFLOW_AVAILABLE = False
keras = None

def _load_tensorflow():
    """Lazy load TensorFlow on first use"""
    global TENSORFLOW_AVAILABLE, keras
    if TENSORFLOW_AVAILABLE:
        return
    
    try:
        import tensorflow as tf
        from tensorflow import keras as tf_keras
        keras = tf_keras
        TENSORFLOW_AVAILABLE = True
    except (ImportError, Exception) as e:
        TENSORFLOW_AVAILABLE = False
        print("TensorFlow not available. Using mock model for testing.")

def _ensure_numpy():
    """Lazy load numpy"""
    global np
    if np is None:
        import numpy as np_module
        np = np_module
    return np

# Disease class mapping
DISEASE_CLASSES = {
    0: "Tomato___Early_blight",
    1: "Tomato___Late_blight",
    2: "Tomato___Leaf_Mold",
    3: "Tomato___Healthy",
    4: "Corn___Leaf_Spot",
    5: "Corn___Healthy",
    6: "Potato___Early_Blight",
    7: "Potato___Healthy",
    8: "Cassava___Brown_Leaf_Spot",
    9: "Cassava___Healthy",
    10: "Rice___Leaf_Blast",
    11: "Rice___Healthy",
    12: "Cocoa___Frosty_Pod",
    13: "Cocoa___Healthy",
}

class DiseaseDetectionModel:
    """
    Disease Detection Model for crop leaves.
    Supports both real TensorFlow models and mock predictions.
    """
    
    def __init__(self, model_path: Optional[str] = None, use_mock: bool = False):
        """
        Initialize the disease detection model.
        
        Args:
            model_path: Path to the pre-trained model (.h5 or SavedModel format)
            use_mock: Force use of mock model even if TensorFlow is available
        """
        self.model = None
        self.use_mock = use_mock or not TENSORFLOW_AVAILABLE
        self.model_loaded = False
        self.image_size = (224, 224)  # Standard input size for most models
        
        if not self.use_mock and model_path:
            self.load_model(model_path)
    
    def load_model(self, model_path: str) -> bool:
        """
        Load a pre-trained TensorFlow model.
        
        Args:
            model_path: Path to the model file
        
        Returns:
            True if model loaded successfully, False otherwise
        """
        try:
            # Lazy load TensorFlow
            _load_tensorflow()
            
            if not TENSORFLOW_AVAILABLE:
                print("TensorFlow not available, cannot load model")
                return False
            
            if not os.path.exists(model_path):
                print(f"Model file not found: {model_path}")
                return False
            
            self.model = keras.models.load_model(model_path)
            self.model_loaded = True
            print(f"Model loaded successfully from {model_path}")
            return True
        
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model_loaded = False
            return False
    
    def preprocess_image(self, image) -> object:
        """
        Preprocess image for model input.
        
        Args:
            image: Input image (OpenCV format)
        
        Returns:
            Preprocessed image array
        """
        try:
            np_module = _ensure_numpy()
            
            # Resize to model input size
            resized = cv2_module.resize(image, self.image_size)
            
            # Normalize pixel values to [0, 1] or [-1, 1]
            normalized = resized.astype('float32') / 255.0
            
            # Add batch dimension
            batch = np_module.expand_dims(normalized, axis=0)
            
            return batch
        
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return None
    
    def is_maize_leaf(self, image_bytes) -> bool:
        """Return True if the predicted class corresponds to a maize leaf (Corn)."""
        disease, _ = self.predict(image_bytes)
        return disease.startswith('Corn___')

        """
        Predict disease class and confidence from an image.
        
        Args:
            image: Input image (OpenCV format)
        
        Returns:
            Tuple of (disease_class, confidence_score)
        """
        if image is None:
            return None, 0.0
        
        if self.use_mock:
            return self._mock_predict()
        
        try:
            np_module = _ensure_numpy()
            
            # Preprocess image
            processed = self.preprocess_image(image)
            
            if processed is None:
                return None, 0.0
            
            # Make prediction
            predictions = self.model.predict(processed, verbose=0)
            confidence = float(np_module.max(predictions[0]))
            class_idx = int(np_module.argmax(predictions[0]))
            
            disease_class = DISEASE_CLASSES.get(class_idx, "Unknown")
            
            return disease_class, confidence
        
        except Exception as e:
            print(f"Error during prediction: {e}")
            return None, 0.0
    
    def _mock_predict(self) -> Tuple[str, float]:
        """
        Mock prediction for testing purposes.
        
        Returns:
            Random disease class and confidence
        """
        disease_class = random.choice(list(DISEASE_CLASSES.values()))
        confidence = random.uniform(0.80, 0.99)
        return disease_class, round(confidence, 2)
    
    def batch_predict(self, images) -> Tuple[list, list]:
        """
        Predict multiple images at once.
        
        Args:
            images: Batch of images
        
        Returns:
            Lists of disease classes and confidences
        """
        diseases = []
        confidences = []
        
        for image in images:
            disease, confidence = self.predict(image)
            diseases.append(disease)
            confidences.append(confidence)
        
        return diseases, confidences


# Global model instance
_model_instance = None

def get_model(model_path: Optional[str] = None, use_mock: bool = False) -> DiseaseDetectionModel:
    """
    Get or create a global model instance.
    
    Args:
        model_path: Path to model file
        use_mock: Force mock model
    
    Returns:
        DiseaseDetectionModel instance
    """
    global _model_instance
    
    if _model_instance is None:
        _model_instance = DiseaseDetectionModel(model_path=model_path, use_mock=use_mock)
    
    return _model_instance

def reset_model():
    """Reset the global model instance."""
    global _model_instance
    _model_instance = None
