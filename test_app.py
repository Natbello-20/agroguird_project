"""Test FastAPI app integration"""
from fastapi.testclient import TestClient
import main

print("Testing FastAPI App Integration...")
print("=" * 60)

client = TestClient(main.app)

print("✓ FastAPI app loaded successfully")
print(f"✓ Model initialized: mock={main.model.use_mock}")
print(f"✓ Total routes: {len([r for r in main.app.routes if hasattr(r, 'path')])}")

# Check predict endpoint exists
routes = [r.path for r in main.app.routes if hasattr(r, 'path')]
print(f"✓ /predict endpoint exists: {'/predict' in routes}")
print(f"✓ /superadmin/dashboard exists: {'/superadmin/dashboard' in routes}")

print("\n" + "=" * 60)
print("App Integration Test Complete!")
print("=" * 60)
