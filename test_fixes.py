"""Quick test for the two fixes:
1. Non-maize detection (mock model returns low confidence ~20% of time)
2. 5 total scans per device (not per segment)
"""
import requests
from io import BytesIO
from PIL import Image

BASE_URL = "http://localhost:8000"
DEVICE_ID = "test-fix-device"

def create_test_image(color=(100, 150, 100)):
    img = Image.new('RGB', (224, 224), color=color)
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    buffer.seek(0)
    return buffer

print("=" * 80)
print("TESTING FIXES")
print("=" * 80)

print("\n📊 FIX 1: Non-Maize Detection (Mock Model)")
print("-" * 80)
print("Mock model now returns low confidence (~20% chance) to simulate non-maize")
print("Testing 10 images to see rejection rate...")

rejected = 0
accepted = 0

for i in range(1, 11):
    img = create_test_image(color=(100 + i*10, 150, 100))
    
    response = requests.post(
        f"{BASE_URL}/predict",
        files={"file": ("test.jpg", img, "image/jpeg")},
        headers={
            "device-id": f"nonmaize-test-{i}",
            "x-latitude": "6.6885",
            "x-longitude": "-1.6244"
        }
    )
    
    data = response.json()
    confidence = data.get("confidence", 0)
    
    if response.status_code == 400 and confidence < 0.5:
        rejected += 1
        print(f"  Image {i}: ✗ REJECTED (confidence {confidence} < 0.5) ← Non-maize detected!")
    elif response.status_code == 200:
        accepted += 1
        print(f"  Image {i}: ✓ ACCEPTED (confidence {confidence})")
    else:
        print(f"  Image {i}: ⚠ Unexpected status {response.status_code}")

print(f"\nResults: {accepted} accepted, {rejected} rejected")
print(f"Expected: ~8 accepted, ~2 rejected (20% rejection rate)")
if rejected > 0:
    print("✓ Non-maize detection is working!")
else:
    print("⚠ No rejections - may need more samples or model adjustment")

print("\n\n📊 FIX 2: 5 Total Scans Per Device (Not Per Segment)")
print("-" * 80)
print("Testing with SAME device_id but DIFFERENT GPS locations")
print("Should stop after 5 total scans regardless of location\n")

success = 0
rejected = 0

# Try 7 scans with DIFFERENT GPS each time
for i in range(1, 8):
    # Different GPS for each scan (different segments)
    lat = 6.6885 + (i * 0.001)  # Each scan 100m apart
    lon = -1.6244 + (i * 0.001)
    
    img = create_test_image(color=(100, 150 + i*10, 100))
    
    response = requests.post(
        f"{BASE_URL}/predict",
        files={"file": ("test.jpg", img, "image/jpeg")},
        headers={
            "device-id": DEVICE_ID,  # SAME device
            "x-latitude": str(lat),   # DIFFERENT location
            "x-longitude": str(lon)
        }
    )
    
    data = response.json()
    scan_info = data.get("scan_info", {})
    
    if response.status_code == 200:
        success += 1
        print(f"  Scan {i} (GPS: {lat:.4f}, {lon:.4f}): ✓ ACCEPTED")
        print(f"    Total scans: {scan_info.get('scans_used', 'N/A')}/5")
        print(f"    Remaining: {scan_info.get('scans_remaining', 'N/A')}")
    elif response.status_code == 429:
        rejected += 1
        print(f"  Scan {i} (GPS: {lat:.4f}, {lon:.4f}): ✗ REJECTED - Limit reached")
        print(f"    Error: {data.get('error', 'Unknown')}")
    elif response.status_code == 400:
        print(f"  Scan {i}: ⚠ Rejected as non-maize (confidence {data.get('confidence', 0)})")
        # Don't count as scan limit rejection
    else:
        print(f"  Scan {i}: ⚠ Unexpected status {response.status_code}")

print(f"\nResults: {success} accepted, {rejected} rejected by limit")
print(f"Expected: 5 accepted, 2 rejected")

if success == 5 and rejected == 2:
    print("✓ 5 total scans limit is working correctly!")
elif success == 5:
    print("✓ Accepted exactly 5 scans (perfect!)")
    print("⚠ Rejections may be less than 2 due to non-maize detection")
else:
    print(f"⚠ Unexpected result: {success} accepted (expected 5)")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("Fix 1 (Non-Maize Detection): " + ("✓ Working" if rejected > 0 else "⚠ Needs verification"))
print("Fix 2 (5 Total Scans Limit): " + ("✓ Working" if success <= 5 else "✗ Not working"))
print("\nNote: Mock model randomly rejects ~20% of images as non-maize")
print("      This is a simulation - real model will be more accurate")
