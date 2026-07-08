"""Test script for model integration"""
import model
import numpy as np

print("=" * 60)
print("Testing Model Integration")
print("=" * 60)

# Test 1: Model initialization with mock
print("\n1. Testing mock model initialization...")
m = model.DiseaseDetectionModel(use_mock=True)
print(f"   ✓ Model initialized (mock={m.use_mock})")
print(f"   ✓ Labels loaded: {len(m.labels)} classes")
print(f"   ✓ Disease info loaded: {len(m.disease_info)} conditions")

# Test 2: Mock prediction
print("\n2. Testing mock prediction...")
img = np.zeros((224, 224, 3), dtype=np.uint8)
disease, conf = m.predict(img)
print(f"   ✓ Prediction: {disease}")
print(f"   ✓ Confidence: {conf}")
print(f"   ✓ Is maize: {disease.startswith('Corn___') if disease else False}")

# Test 3: Disease info retrieval
print("\n3. Testing disease info retrieval...")
if disease:
    info = m.get_disease_info(disease)
    print(f"   ✓ Disease name: {info.get('name', 'N/A')}")
    print(f"   ✓ Symptoms count: {len(info.get('symptoms', []))}")
    print(f"   ✓ Management steps: {len(info.get('management', []))}")

# Test 4: All disease classes
print("\n4. Testing all disease classes...")
for idx, disease_name in m.labels.items():
    print(f"   {idx}: {disease_name}")

# Test 5: Try loading real model (may fail if TF not available)
print("\n5. Testing real TFLite model loading...")
try:
    m_real = model.DiseaseDetectionModel(model_path="mobile_assets/maize_model.tflite")
    if m_real.model_loaded:
        print(f"   ✓ Real model loaded successfully!")
        print(f"   ✓ Input size: {m_real.image_size}")
    else:
        print(f"   ⚠ Model loading failed, using mock")
except Exception as e:
    print(f"   ⚠ Could not load real model: {e}")

print("\n" + "=" * 60)
print("Test Complete!")
print("=" * 60)
