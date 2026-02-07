"""
Demo: Adaptive Character Limiter
=================================

Demonstrates how the character limiter adapts based on actual text content.
"""

from char_limiter import AdaptiveCharLimiter


def demo():
    limiter = AdaptiveCharLimiter()
    
    print("\n" + "="*80)
    print("ADAPTIVE CHARACTER LIMITER DEMONSTRATION")
    print("="*80)
    print(f"\nLine width: {limiter.LINE_WIDTH_PIXELS} pixels")
    print(f"Font: Times New Roman {limiter.FONT_SIZE}pt")
    print(f"Widest character width: {limiter.widest_char_width:.1f}px")
    print(f"Average character width: {limiter.avg_char_width:.1f}px")
    
    # Example 1: Languages field
    print("\n" + "-"*80)
    print("EXAMPLE 1: Languages Field")
    print("-"*80)
    
    prefix = "Languages: "
    
    # Initial state
    initial = limiter.get_initial_limit(prefix)
    print(f"\nPrefix: '{prefix}'")
    print(f"Initial conservative limit: {initial} characters")
    print(f"  → User sees: '{initial} characters remaining'")
    
    # User types narrow characters
    text1 = "Java, Python, C++"
    info1 = limiter.get_adaptive_limit(prefix, text1)
    print(f"\n✏️  User types: '{text1}' ({len(text1)} chars)")
    print(f"   Pixels used: {info1['pixels_used']}/{info1['total_pixels']} ({info1['percentage_used']:.1f}%)")
    print(f"   NEW limit: {info1['current_limit']} characters")
    print(f"   Remaining: {info1['remaining']} characters")
    print(f"   ✨ BONUS: +{info1['efficiency_gain']} chars from efficient typing!")
    
    # User types more
    text2 = "Java, Python, C++, C, Kotlin, Swift, JavaScript, PHP"
    info2 = limiter.get_adaptive_limit(prefix, text2)
    print(f"\n✏️  User continues: '{text2}' ({len(text2)} chars)")
    print(f"   Pixels used: {info2['pixels_used']}/{info2['total_pixels']} ({info2['percentage_used']:.1f}%)")
    print(f"   NEW limit: {info2['current_limit']} characters")
    print(f"   Remaining: {info2['remaining']} characters")
    if info2['is_near_limit']:
        print(f"   ⚠️  WARNING: Getting close to limit!")
    
    # Example 2: Project bullet point
    print("\n" + "-"*80)
    print("EXAMPLE 2: Project Bullet Point")
    print("-"*80)
    
    bullet_prefix = "• "
    
    initial_bullet = limiter.get_initial_limit(bullet_prefix)
    print(f"\nPrefix: '{bullet_prefix}'")
    print(f"Initial conservative limit: {initial_bullet} characters")
    
    bullet_text = "Developed a scalable web application using React and Node.js"
    bullet_info = limiter.get_adaptive_limit(bullet_prefix, bullet_text)
    print(f"\n✏️  User types: '{bullet_text}' ({len(bullet_text)} chars)")
    print(f"   Pixels used: {bullet_info['pixels_used']}/{bullet_info['total_pixels']} ({bullet_info['percentage_used']:.1f}%)")
    print(f"   Remaining: {bullet_info['remaining']} characters")
    print(f"   ✨ BONUS: +{bullet_info['efficiency_gain']} chars")
    
    # Example 3: Comparison of narrow vs wide characters
    print("\n" + "-"*80)
    print("EXAMPLE 3: Narrow vs Wide Characters")
    print("-"*80)
    
    # Same character count, different widths
    narrow_text = "iiiiiiiiiiiiiiiiiii"  # 19 i's (narrow)
    wide_text = "WWWWWWWWWWWWWWWWWWW"  # 19 W's (wide)
    
    narrow_info = limiter.get_adaptive_limit("", narrow_text)
    wide_info = limiter.get_adaptive_limit("", wide_text)
    
    print(f"\nBoth texts have {len(narrow_text)} characters:")
    print(f"\n  Narrow text (i's):")
    print(f"    Pixels used: {narrow_info['pixels_used']}px")
    print(f"    Remaining chars: {narrow_info['remaining']}")
    print(f"    Efficiency gain: +{narrow_info['efficiency_gain']}")
    
    print(f"\n  Wide text (W's):")
    print(f"    Pixels used: {wide_info['pixels_used']}px")
    print(f"    Remaining chars: {wide_info['remaining']}")
    print(f"    Efficiency gain: +{wide_info['efficiency_gain']}")
    
    print(f"\n  📊 Difference: {narrow_info['remaining'] - wide_info['remaining']} extra chars for narrow text!")
    
    # Summary
    print("\n" + "="*80)
    print("KEY BENEFITS")
    print("="*80)
    print("""
✅ SAFE: Starts with conservative limit (using widest character)
✅ ADAPTIVE: Expands dynamically as user types
✅ EFFICIENT: Rewards typing narrow characters (i, l, t vs W, M, @)
✅ ACCURATE: Measures actual pixel width, not just character count
✅ VISUAL: Shows remaining characters with color-coded warnings
✅ SMART: Displays efficiency bonus to encourage smart typing

How it works:
1. Start: Calculate conservative limit using widest character (14px)
2. User types: Measure actual pixel width of their text
3. Adapt: Calculate remaining space and update limit
4. Display: Show remaining characters with visual feedback
    - Green (✅): Plenty of space remaining
    - Orange (⚠️): Less than 10 characters remaining
    - Red (🚫): At or over limit

This prevents text overflow while maximizing flexibility!
""")
    print("="*80 + "\n")


if __name__ == "__main__":
    demo()
