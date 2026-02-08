"""
Initialize AgroGuard database with Ghana regions and districts
Run this script once after database creation to populate location data
"""

from database import SessionLocal, init_db
from database import Region, District
from datetime import datetime

# Ghana's 16 regions with approximate coordinates
GHANA_REGIONS = [
    {"name": "Ahafo", "code": "AF", "lat": 6.500, "lng": -2.300},
    {"name": "Ashanti", "code": "AR", "lat": 6.600, "lng": -1.600},
    {"name": "Bono", "code": "BO", "lat": 7.500, "lng": -2.200},
    {"name": "Bono East", "code": "BE", "lat": 7.600, "lng": -0.700},
    {"name": "Central Region", "code": "CR", "lat": 5.150, "lng": -1.300},
    {"name": "Eastern Region", "code": "ER", "lat": 6.200, "lng": -0.900},
    {"name": "Greater Accra", "code": "GA", "lat": 5.600, "lng": -0.200},
    {"name": "North East Region", "code": "NE", "lat": 10.700, "lng": -0.500},
    {"name": "Northern Region", "code": "NR", "lat": 9.500, "lng": -0.900},
    {"name": "Oti Region", "code": "OT", "lat": 8.600, "lng": 0.900},
    {"name": "Savannah Region", "code": "SA", "lat": 10.950, "lng": -1.600},
    {"name": "Upper East Region", "code": "UE", "lat": 10.800, "lng": -1.400},
    {"name": "Upper West Region", "code": "UW", "lat": 10.500, "lng": -2.500},
    {"name": "Volta Region", "code": "VR", "lat": 7.100, "lng": 0.800},
    {"name": "Western North Region", "code": "WN", "lat": 5.900, "lng": -2.800},
    {"name": "Western Region", "code": "WR", "lat": 5.200, "lng": -2.400},
]

# Districts by region (subset - can be expanded)
DISTRICTS_BY_REGION = {
    "Ashanti": [
        {"name": "Kumasi Metropolitan", "lat": 6.627, "lng": -1.620},
        {"name": "Afigya-Kwabre", "lat": 6.400, "lng": -1.800},
        {"name": "Atwima Mponua", "lat": 6.550, "lng": -1.500},
        {"name": "Bosomtwe", "lat": 6.800, "lng": -1.300},
    ],
    "Bono": [
        {"name": "Sunyani Municipal", "lat": 6.340, "lng": -2.325},
        {"name": "Dormaa", "lat": 7.400, "lng": -2.700},
    ],
    "Greater Accra": [
        {"name": "Accra Metropolitan", "lat": 5.630, "lng": -0.200},
        {"name": "Ledzokuku-Krowor", "lat": 5.650, "lng": -0.150},
    ],
    "Central Region": [
        {"name": "Cape Coast Metropolitan", "lat": 5.107, "lng": -1.248},
        {"name": "Sekondi-Takoradi Metropolitan", "lat": 4.900, "lng": -1.740},
    ],
    "Eastern Region": [
        {"name": "Koforidua", "lat": 6.084, "lng": -0.271},
        {"name": "Akyem", "lat": 6.200, "lng": -0.500},
    ],
    "Northern Region": [
        {"name": "Tamale Metropolitan", "lat": 9.400, "lng": -0.840},
        {"name": "Savelugu-Nanton", "lat": 9.650, "lng": -0.650},
    ],
    "Volta Region": [
        {"name": "Ho Municipal", "lat": 6.913, "lng": 0.479},
        {"name": "Hohoe", "lat": 6.818, "lng": 0.494},
    ],
    "Western Region": [
        {"name": "Sekondi-Takoradi Metropolitan", "lat": 4.900, "lng": -1.740},
        {"name": "Juaso", "lat": 5.950, "lng": -1.550},
    ],
    "Upper East Region": [
        {"name": "Bolgatanga Municipal", "lat": 10.789, "lng": -1.524},
        {"name": "Navrongo", "lat": 10.897, "lng": -1.095},
    ],
}


def init_ghana_locations():
    """Initialize database with Ghana regions and districts"""
    db = SessionLocal()
    
    try:
        # Clear existing data
        db.query(District).delete()
        db.query(Region).delete()
        db.commit()
        print("✓ Cleared existing regions and districts")
        
        # Insert regions
        regions_dict = {}
        for region_data in GHANA_REGIONS:
            region = Region(
                name=region_data["name"],
                region_code=region_data["code"],
                lat=region_data["lat"],
                lng=region_data["lng"],
            )
            db.add(region)
            regions_dict[region_data["name"]] = region
        
        db.commit()
        print(f"✓ Added {len(GHANA_REGIONS)} regions")
        
        # Insert districts
        total_districts = 0
        for region_name, districts_list in DISTRICTS_BY_REGION.items():
            region = regions_dict.get(region_name)
            if region:
                for district_data in districts_list:
                    district = District(
                        name=district_data["name"],
                        region_id=region.id,
                        lat=district_data.get("lat"),
                        lng=district_data.get("lng"),
                    )
                    db.add(district)
                    total_districts += 1
        
        db.commit()
        print(f"✓ Added {total_districts} districts")
        
        print("\n✓✓✓ Ghana location data initialized successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"✗ Error initializing location data: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    print("Initializing AgroGuard database...")
    print("=" * 60)
    
    # Create tables first
    init_db()
    
    # Then populate Ghana locations
    init_ghana_locations()
