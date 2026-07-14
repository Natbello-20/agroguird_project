"""
Check if the real TensorFlow model is loading correctly
"""
import os
from dotenv import load_dotenv
load_dotenv()

print("=" * 60)
print("MODEL LOADING CHECK")
print("=" * 60)

# Check environment variable
USE_REAL_MODEL = os.getenv("USE_REAL_MODEL", "false").lower() == "true"
print(f"\n1. Environment Variable:")
print(f"   USE_REAL_MODEL = {os.getenv('USE_REAL_MODEL', 'NOT SET')}")
print(f"   Parsed as: {USE_REAL_MODEL}")

# Check model file exists
model_path = "mobile_assets/maize_model.tflite"
model_exists = os.path.exists(model_path)
print(f"\n2. Model File:")
print(f"   Path: {model_path}")
print(f"   Exists: {'✅ YES' if model_exists else '❌ NO'}")
if model_exists:
    size_mb = os.path.getsize(model_path) / (1024 * 1024)
    print(f"   Size: {size_mb:.2f} MB")

# Try to load the model
print(f"\n3. Loading Model:")
try:
    from model import DiseaseDetectionModel
    
    # Initialize with real model
    print(f"   Initializing with use_mock={not USE_REAL_MODEL}...")
    model = DiseaseDetectionModel(use_mock=not USE_REAL_MODEL)
    
    print(f"\n4. Model Status:")
    print(f"   use_mock: {model.use_mock}")
    print(f"   model_loaded: {model.model_loaded}")
    print(f"   interpreter: {model.interpreter is not None}")
    
    if model.use_mock:
        print(f"\n   ⚠️  WARNING: Using MOCK model!")
        print(f"   This means predictions are RANDOM!")
    else:
        if model.model_loaded:
            print(f"\n   ✅ Real model loaded successfully!")
            print(f"   Input size: {model.image_size}")
            print(f"   Classes: {list(model.labels.values())}")
        else:
            print(f"\n   ❌ Real model FAILED to load!")
            print(f"   Falling back to mock mode")
    
    # Test a prediction
    print(f"\n5. Test Prediction:")
    try:
        import numpy as np
        from PIL import Image
        
        # Create a dummy image
        dummy_img = Image.new('RGB', (224, 224), color='green')
        
        result = model.predict(dummy_img)
        disease, confidence, entropy, gap = result
        
        print(f"   Disease: {disease}")
        print(f"   Confidence: {confidence:.4f}")
        print(f"   Entropy: {entropy:.4f}")
        print(f"   Gap: {gap:.4f}")
        
        if model.use_mock:
            print(f"\n   ⚠️  These are RANDOM values (mock mode)!")
        else:
            print(f"\n   ✅ These are REAL predictions from TensorFlow!")
            
    except Exception as e:
        print(f"   ❌ Prediction failed: {e}")
        import traceback
        traceback.print_exc()

except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("CHECK COMPLETE")
print("=" * 60)
