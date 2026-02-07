"""Test multi-line detection"""
from char_limiter import get_limiter

limiter = get_limiter()

# Test with long leadership bullet
text = "Led and mentored a cross-functional team of 10 engineers in Android development and automation, driving project delivery via Agile methodologies while fostering technical growth through code reviews and performance evaluations."

print("="*80)
print("MULTI-LINE DETECTION TEST")
print("="*80)

print(f"\nText: {text[:80]}...")
print(f"Text length: {len(text)} chars")

info = limiter.get_adaptive_limit("• ", text, text)

print(f"\nResults:")
print(f"  Detected lines: {info['num_lines']}")
print(f"  Total pixels available: {info['total_pixels']} ({info['num_lines']} x 755)")
print(f"  Pixels used: {info['pixels_used']}")
print(f"  Percentage used: {info['percentage_used']:.1f}%")
print(f"  Remaining chars: {info['remaining']}")
print(f"  Is at limit: {info['is_at_limit']}")
print(f"  Current limit: {info['current_limit']}")

if info['num_lines'] > 1:
    print(f"\n✅ Multi-line field detected! Allowing {info['num_lines']} lines.")
else:
    print(f"\n❌ Single line field")

print("="*80)
