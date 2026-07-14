"""
Test script to verify rejection logic with different scenarios
"""

def test_rejection_logic(confidence, entropy, confidence_gap, scenario_name):
    """Test the rejection logic with given metrics"""
    
    CONFIDENCE_THRESHOLD = 0.50
    ENTROPY_THRESHOLD = 1.1
    GAP_THRESHOLD = 0.25
    
    rejection_count = 0
    rejection_reasons = []
    
    if confidence < CONFIDENCE_THRESHOLD:
        rejection_count += 1
        rejection_reasons.append(f"low confidence ({confidence:.2f} < {CONFIDENCE_THRESHOLD})")
    if entropy > ENTROPY_THRESHOLD:
        rejection_count += 1
        rejection_reasons.append(f"high uncertainty (entropy: {entropy:.2f} > {ENTROPY_THRESHOLD})")
    if confidence_gap < GAP_THRESHOLD:
        rejection_count += 1
        rejection_reasons.append(f"unclear prediction (gap: {confidence_gap:.2f} < {GAP_THRESHOLD})")
    
    is_likely_non_maize = rejection_count >= 2
    
    print(f"\n{scenario_name}:")
    print(f"  Confidence: {confidence:.2f}, Entropy: {entropy:.2f}, Gap: {confidence_gap:.2f}")
    print(f"  Rejection count: {rejection_count}/3")
    print(f"  Reasons: {', '.join(rejection_reasons) if rejection_reasons else 'None'}")
    print(f"  Result: {'❌ REJECTED' if is_likely_non_maize else '✅ ACCEPTED'}")
    
    return is_likely_non_maize

# Test scenarios
print("=" * 60)
print("REJECTION LOGIC TEST")
print("=" * 60)

# Real maize leaves (should be ACCEPTED)
print("\n🌾 REAL MAIZE LEAVES (Should be ACCEPTED):")
test_rejection_logic(0.75, 0.65, 0.45, "Healthy maize - High confidence")
test_rejection_logic(0.68, 0.85, 0.38, "Diseased maize - Good confidence")
test_rejection_logic(0.55, 0.95, 0.28, "Maize - Moderate confidence")
test_rejection_logic(0.52, 1.05, 0.26, "Maize - Lower confidence (edge case)")

# Non-maize objects (should be REJECTED)
print("\n🚫 NON-MAIZE OBJECTS (Should be REJECTED):")
test_rejection_logic(0.35, 1.35, 0.08, "Hand - Low conf, high entropy, low gap")
test_rejection_logic(0.28, 1.42, 0.05, "Table - All criteria failed")
test_rejection_logic(0.42, 1.25, 0.12, "Face - 2/3 criteria failed")
test_rejection_logic(0.38, 1.15, 0.22, "Sky - Low conf + high entropy")

# Edge cases
print("\n⚠️ EDGE CASES:")
test_rejection_logic(0.48, 1.08, 0.23, "Edge case - Just below threshold")
test_rejection_logic(0.51, 1.12, 0.26, "Edge case - Just above threshold")
test_rejection_logic(0.50, 1.10, 0.25, "Exactly at thresholds")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
