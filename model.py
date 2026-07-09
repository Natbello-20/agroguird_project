"""
Disease Detection Model Module
Handles loading and running the TensorFlow Lite model for maize disease detection.
"""

import os
import json
from typing import Tuple, Optional, Dict
import random
from pathlib import Path
from PIL import Image
import io

# Lazy imports
np = None
tf = None

# TensorFlow Lite availability
TFLITE_AVAILABLE = False

def _load_tensorflow_lite():
    """Lazy load TensorFlow Lite on first use"""
    global TFLITE_AVAILABLE, tf
    if TFLITE_AVAILABLE or tf is not None:
        return
    
    try:
        import tensorflow as tf_module
        tf = tf_module
        TFLITE_AVAILABLE = True
        print("✓ TensorFlow Lite loaded successfully")
    except (ImportError, Exception) as e:
        TFLITE_AVAILABLE = False
        print(f"⚠ TensorFlow Lite not available: {e}")
        print("  Using mock model for testing.")

def _ensure_numpy():
    """Lazy load numpy"""
    global np
    if np is None:
        import numpy as np_module
        np = np_module
    return np

# Maize disease class mapping (from labels.txt)
MAIZE_CLASSES = {
    0: "Corn___Healthy",
    1: "Corn___Common_Rust",
    2: "Corn___Northern_Leaf_Blight",
    3: "Corn___Gray_Leaf_Spot",
}

# Reverse mapping for checking if it's maize
MAIZE_CLASS_NAMES = set(MAIZE_CLASSES.values())

# Legacy disease class mapping (for fallback/mock)
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
    Disease Detection Model for maize leaves using TensorFlow Lite.
    Supports both real TFLite models and mock predictions.
    """
    
    def __init__(self, model_path: Optional[str] = None, use_mock: bool = False):
        """
        Initialize the disease detection model.
        
        Args:
            model_path: Path to the TFLite model file (.tflite)
            use_mock: Force use of mock model even if TensorFlow is available
        """
        self.interpreter = None
        self.input_details = None
        self.output_details = None
        self.use_mock = use_mock
        self.model_loaded = False
        self.image_size = (224, 224)  # Standard input size for most models
        self.labels = MAIZE_CLASSES
        self.disease_info = {}
        
        # Load disease information
        self._load_disease_info()
        
        # Only try to load real model if not forced to mock
        if not self.use_mock:
            # Auto-detect model if not specified
            if model_path is None:
                model_path = "mobile_assets/maize_model.tflite"
            
            if model_path and os.path.exists(model_path):
                self.load_model(model_path)
            else:
                print(f"⚠ Model file not found: {model_path if model_path else 'None'}")
                print("  Using mock model for testing.")
                self.use_mock = True
    
    def _load_disease_info(self):
        """Load disease information from JSON file"""
        try:
            info_path = Path("mobile_assets/disease_info.json")
            if info_path.exists():
                with open(info_path, 'r', encoding='utf-8') as f:
                    self.disease_info = json.load(f)
                print(f"✓ Loaded disease info for {len(self.disease_info)} conditions")
        except Exception as e:
            print(f"⚠ Could not load disease info: {e}")
    
    def load_model(self, model_path: str) -> bool:
        """
        Load a TensorFlow Lite model.
        
        Args:
            model_path: Path to the .tflite model file
        
        Returns:
            True if model loaded successfully, False otherwise
        """
        try:
            # Lazy load TensorFlow Lite
            _load_tensorflow_lite()
            
            if not TFLITE_AVAILABLE:
                print("⚠ TensorFlow Lite not available, cannot load model")
                self.use_mock = True
                return False
            
            if not os.path.exists(model_path):
                print(f"⚠ Model file not found: {model_path}")
                self.use_mock = True
                return False
            
            # Load TFLite model and allocate tensors
            self.interpreter = tf.lite.Interpreter(model_path=model_path)
            self.interpreter.allocate_tensors()
            
            # Get input and output details
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            
            # Update image size from model input shape
            input_shape = self.input_details[0]['shape']
            self.image_size = (input_shape[1], input_shape[2])
            
            self.model_loaded = True
            print(f"✓ TFLite model loaded from {model_path}")
            print(f"  Input shape: {input_shape}")
            print(f"  Output shape: {self.output_details[0]['shape']}")
            return True
        
        except Exception as e:
            print(f"✗ Error loading model: {e}")
            self.model_loaded = False
            self.use_mock = True
            return False
    
    def preprocess_image(self, image) -> object:
        """
        Preprocess image for model input.
        
        Args:
            image: Input image (numpy array or PIL Image)
        
        Returns:
            Preprocessed image array
        """
        try:
            np_module = _ensure_numpy()
            
            # Convert to PIL Image if it's a numpy array
            if isinstance(image, np_module.ndarray):
                # Assume it's RGB format from reading the file
                pil_image = Image.fromarray(image.astype('uint8'))
            elif isinstance(image, Image.Image):
                pil_image = image
            else:
                print(f"[ERROR] Unsupported image type: {type(image)}")
                return None
            
            # Convert to RGB if needed (in case of RGBA or grayscale)
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Resize to model input size
            resized = pil_image.resize(self.image_size, Image.Resampling.BILINEAR)
            
            # Convert to numpy array
            img_array = np_module.array(resized)
            
            # Normalize pixel values to [0, 1]
            normalized = img_array.astype('float32') / 255.0
            
            # Add batch dimension
            batch = np_module.expand_dims(normalized, axis=0)
            
            print(f"[DEBUG] Preprocessed batch shape: {batch.shape}")
            return batch
        
        except Exception as e:
            print(f"[ERROR] Error preprocessing image: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def predict(self, image) -> Tuple[Optional[str], float, float, float]:
        """
        Predict disease class and confidence from an image.
        
        Args:
            image: Input image (numpy array or PIL Image)
        
        Returns:
            Tuple of (disease_class, confidence_score, entropy, confidence_gap)
        """
        print(f"[DEBUG] predict() called - image is None: {image is None}, use_mock: {self.use_mock}, model_loaded: {self.model_loaded}")
        
        if image is None:
            print("[DEBUG] Image is None, returning None")
            return None, 0.0, 0.0, 0.0
        
        if self.use_mock or not self.model_loaded:
            print("[DEBUG] Using mock prediction")
            result = self._mock_predict()
            return result[0], result[1], 0.5, 0.3  # Add dummy entropy and gap for mock
        
        try:
            np_module = _ensure_numpy()
            
            # Preprocess image
            processed = self.preprocess_image(image)
            
            if processed is None:
                print("[DEBUG] Preprocessing failed, returning None")
                return None, 0.0
            
            # Set the input tensor
            self.interpreter.set_tensor(self.input_details[0]['index'], processed)
            
            # Run inference
            self.interpreter.invoke()
            
            # Get the output tensor
            output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
            
            # Get prediction results
            confidence = float(np_module.max(output_data[0]))
            class_idx = int(np_module.argmax(output_data[0]))
            
            disease_class = self.labels.get(class_idx, "Unknown")
            
            # Calculate prediction entropy (measure of uncertainty)
            # High entropy = uncertain = likely non-maize
            # Low entropy = confident = likely maize
            probs = output_data[0]
            entropy = -np_module.sum(probs * np_module.log(probs + 1e-10))
            
            # Calculate gap between top 2 predictions
            sorted_probs = np_module.sort(probs)[::-1]
            confidence_gap = float(sorted_probs[0] - sorted_probs[1])
            
            print(f"[DEBUG] Model output: {output_data[0]}")
            print(f"[DEBUG] Predicted: {disease_class} with confidence: {confidence:.4f}")
            print(f"[DEBUG] Entropy: {entropy:.4f} (lower = more certain)")
            print(f"[DEBUG] Confidence gap: {confidence_gap:.4f} (higher = more decisive)")
            print(f"[DEBUG] All class confidences: {[f'{self.labels[i]}: {output_data[0][i]:.4f}' for i in range(len(output_data[0]))]}")
            
            return disease_class, confidence, entropy, confidence_gap
        
        except Exception as e:
            print(f"Error during prediction: {e}")
            import traceback
            traceback.print_exc()
            return None, 0.0, 0.0, 0.0
    
    def is_maize_leaf(self, image_bytes) -> bool:
        """Return True if the predicted class corresponds to a maize leaf (Corn)."""
        disease, _ = self.predict(image_bytes)
        return disease is not None and disease.startswith('Corn___')
    
    def get_disease_info(self, disease_class: str) -> Dict:
        """
        Get detailed disease information.
        
        Args:
            disease_class: Disease class name (e.g., "Corn___Healthy")
        
        Returns:
            Dictionary with disease details or empty dict
        """
        # Extract the disease key from class name (e.g., "Corn___Healthy" -> "healthy")
        if "___" in disease_class:
            disease_key = disease_class.split("___")[1].lower().replace("_", "_")
        else:
            disease_key = disease_class.lower()
        
        return self.disease_info.get(disease_key, {})
    
    def _mock_predict(self) -> Tuple[str, float]:
        """
        Mock prediction for testing purposes.
        Simulates maize detection with ~20% chance of rejecting non-maize images.
        
        Returns:
            Disease class and confidence (or None for non-maize)
        """
        # 20% chance to simulate non-maize leaf detection
        if random.random() < 0.2:
            # Return low confidence to trigger rejection
            return random.choice(list(MAIZE_CLASSES.values())), random.uniform(0.15, 0.45)
        
        # 80% chance of valid maize prediction
        disease_class = random.choice(list(MAIZE_CLASSES.values()))
        confidence = random.uniform(0.75, 0.98)
        return disease_class, round(confidence, 2)
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
