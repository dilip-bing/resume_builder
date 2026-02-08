"""
Test Character Limit Integration with AI Optimizer
Verifies that the Gemini optimizer respects character limits
"""

import json
from char_limiter import get_limiter
from gemini_optimizer import GeminiATSOptimizer

def test_char_limit_calculation():
    """Test that character limits are calculated correctly"""
    
    # Sample resume content
    resume_data = {
        "professional_summary": "Experienced software engineer with 5+ years in full-stack development",
        "experience": [
            {
                "title": "Senior Software Engineer",
                "company": "Tech Corp",
                "bullet_1": "Led development of microservices architecture serving 1M+ users",
                "bullet_2": "Improved system performance by 40% through optimization"
            }
        ],
        "technical_skills": "Python, JavaScript, React, Node.js, Docker, Kubernetes",
        "languages": "Java, Python, C++, JavaScript, TypeScript, Go",
        "frameworks": "React, Angular, Vue.js, Express, Django, Flask"
    }
    
    # Create a mock optimizer (without API key)
    class MockOptimizer(GeminiATSOptimizer):
        def __init__(self):
            # Skip API initialization
            pass
    
    optimizer = MockOptimizer()
    
    # Calculate character limits
    char_limits = optimizer._calculate_char_limits(resume_data)
    
    print("=" * 70)
    print("CHARACTER LIMIT CALCULATION TEST")
    print("=" * 70)
    
    for field, limit in char_limits.items():
        print(f"\n{field}:")
        print(f"  Max characters: {limit}")
        
        # Get current text length
        if field == "professional_summary":
            current_len = len(resume_data["professional_summary"])
        elif field.startswith("experience_"):
            parts = field.split("_")
            exp_idx = int(parts[1])
            bullet_key = "_".join(parts[2:])
            current_len = len(resume_data["experience"][exp_idx][bullet_key])
        elif field in ["technical_skills", "languages", "frameworks"]:
            current_len = len(resume_data[field])
        else:
            current_len = 0
        
        print(f"  Current length: {current_len}")
        print(f"  Remaining: {limit - current_len} characters")
        
        if current_len > limit:
            print(f"  ⚠️ VIOLATION: Exceeds limit by {current_len - limit} chars!")
        elif current_len > limit * 0.9:
            print(f"  ⚠️ WARNING: Near limit (90%+)")
        else:
            print(f"  ✅ OK")
    
    print("\n" + "=" * 70)
    return char_limits


def test_validation():
    """Test character limit validation"""
    
    # Create mock optimizer
    class MockOptimizer(GeminiATSOptimizer):
        def __init__(self):
            pass
    
    optimizer = MockOptimizer()
    
    # Test data with violations
    optimized_content = {
        "professional_summary": "A" * 500,  # Too long!
        "technical_skills": "Python, JavaScript",  # OK
    }
    
    char_limits = {
        "professional_summary": 200,  # Limit is 200
        "technical_skills": 100,  # Limit is 100
    }
    
    print("\n" + "=" * 70)
    print("VALIDATION TEST")
    print("=" * 70)
    
    validation = optimizer._validate_char_limits(optimized_content, char_limits)
    
    print(f"\nValidation Results:")
    print(f"  Is Valid: {validation['is_valid']}")
    print(f"  Violations: {len(validation['violations'])}")
    print(f"  Warnings: {len(validation['warnings'])}")
    
    if validation['violations']:
        print("\n❌ Violations:")
        for v in validation['violations']:
            print(f"  • {v}")
    
    if validation['warnings']:
        print("\n⚠️ Warnings:")
        for w in validation['warnings']:
            print(f"  • {w}")
    
    print("\n" + "=" * 70)
    
    return validation


if __name__ == "__main__":
    print("\n🧪 Testing Character Limit Integration\n")
    
    # Test 1: Character limit calculation
    print("Test 1: Character Limit Calculation")
    char_limits = test_char_limit_calculation()
    
    # Test 2: Validation logic
    print("\n\nTest 2: Validation Logic")
    validation = test_validation()
    
    print("\n\n✅ All tests completed!")
    print("\n💡 Next steps:")
    print("1. Paste your Gemini API key in .streamlit/secrets.toml")
    print("2. Run: streamlit run enhanced_app.py")
    print("3. Go to '🤖 G. AI Optimization' tab")
    print("4. Test with a job description")
    print("5. Verify character limits are respected!")
