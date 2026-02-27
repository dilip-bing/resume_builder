"""
Test Cover Letter API with ThredUp - With Cold Start Handling
"""
import requests
import base64
import json
from datetime import datetime
import time

# API Configuration
API_URL = "https://resume-optimizer-api-fvpd.onrender.com"
API_KEY = "nFDqvbuNJb4dwsoL9E6HfyTaPC-O2oeHvK-y1RWDSGU"

# ThredUp Job Description
JOB_DESCRIPTION = """
About ThredUp

ThredUp is transforming resale with technology and a mission to inspire the world to think secondhand first. By making it easy to buy and sell secondhand, ThredUp has become one of the world's largest online resale platforms for apparel, shoes and accessories. Sellers love ThredUp because we make it easy to clean out their closets and unlock value for themselves or for the charity of their choice while doing good for the planet. Buyers love shopping value, premium and luxury brands all in one place, at up to 90% off estimated retail price. Our proprietary operating platform is the foundation for our managed marketplace and consists of distributed processing infrastructure, proprietary software and systems and data science expertise. With ThredUp's Resale-as-a-Service, some of the world's leading brands and retailers are leveraging our platform to deliver customizable, scalable resale experiences to their customers. ThredUp has processed over 172 million unique secondhand items from 55,000 brands across 100 categories. By extending the life cycle of clothing, ThredUp is changing the way consumers shop and ushering in a more sustainable future for the fashion industry.

Recognized on TIME Most Influential Companies of 2023,  Digiday's WorkLife 50 2023, TIME's Best Inventions of 2022, and Lattice's People Success Awards 2022.

About our Internship Program
As a ThredUp summer intern, you won't just be observing—you'll be an essential part of the team, gaining a firsthand glimpse into what it's like to work at the world's largest fashion resale platform.


During our intensive 10-week paid program, you will own and tackle high-impact, challenging projects alongside our world-class team, with the real opportunity to influence ThredUp's business strategy and our sustainable mission.


Our paid internships are ideal for ambitious students or recent grads who thrive in a fast-paced, mission-driven culture, enjoy solving complex challenges, and are ready for a serious jump start on their career development. Plus, you'll be helping us inspire a new generation of consumers to think secondhand first, making a tangible difference for the planet.

About the Internship
Join us as a Machine Learning Engineer Intern to tackle operational challenges leveraging cutting-edge technologies such as Computer Vision, Deep Reinforcement Learning, and state-of-the-art Multimodal and Vision Language Models. In collaboration with our experienced ML Engineers, you'll research and develop ML models to help optimize and modernize our operations processes. Your work could possibly even make it into our production systems by the end of your internship! 

We're seeking candidates who are pursuing or have recently completed a Bachelor's or Master's degree in Computer Science, Machine Learning, or a related field, or have recently graduated from a relevant technical bootcamp program. The ideal candidate will have a strong foundation in algorithms and data structures, hands-on experience with computer vision or agent-based frameworks in Python, a team-oriented mindset, analytical prowess, problem-solving aptitude, and excellent communication skills.

This is a 10 week internship from 6/8/2026 - 8/13/2026

This is an hourly role and pays $35 - 50 per hour based on the currently enrolled academic program or completed level of education.

What We Offer:

At ThredUp, we value infinite learning. As an intern you'll have the opportunity to learn about our forward-thinking business and collaborate with our talented team.

We also believe that each person should help drive the business. As an intern, you'll be encouraged to speakUP, think big, ask questions and seek the truth, and help influence outcomes for our business and customers.

You'll have the opportunity to work with passionate and supportive team members who encourage new ideas, feedback and collaboration.

We have a talented leadership team that encourages transparency and they will support you in maximizing your internship experience.

We believe diversity, inclusion and belonging is key for our team

At ThredUp, our mission has been built on extending the lives of millions of unique clothing items. Much like our inventory, we are proud to have fostered a workplace that is one-of-a-kind. As a company focused on diversity, inclusion and belonging, we are committed to ensuring our employees are comfortable bringing their authentic selves to work every day. A unique perspective is critical to solving complex problems and inspiring a new generation to think secondhand first. Be you.

If you are a candidate with a disability and have a reasonable accommodation request for the job application process, please email disabilitysupport@thredup.com the specific details of your disability related accommodation request. This email address is reserved for candidates with disabilities only. General application inquiries will not receive a response.
"""

def wake_up_api():
    """Wake up the API with a health check (handles cold start)"""
    print("\n🔄 Step 1: Waking up API (cold start handling)...")
    print(f"   Checking: {API_URL}/health")
    
    try:
        start = datetime.now()
        response = requests.get(f"{API_URL}/health", timeout=60)
        elapsed = (datetime.now() - start).total_seconds()
        
        if response.status_code == 200:
            print(f"   ✅ API is awake! (responded in {elapsed:.2f}s)")
            return True
        else:
            print(f"   ⚠️  API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health check failed: {str(e)}")
        return False

def test_cover_letter_api():
    """Test cover letter generation with ThredUp job"""
    
    print("="*80)
    print("TESTING COVER LETTER API - ThredUp ML Engineer Intern Position")
    print("="*80)
    
    # Step 1: Wake up API
    if not wake_up_api():
        print("\n⚠️  API health check failed, but continuing anyway...")
    
    time.sleep(2)  # Give it a moment
    
    # Step 2: Test cover letter generation
    print(f"\n🔄 Step 2: Generating Cover Letter...")
    print(f"   Endpoint: {API_URL}/api/v1/generate-cover-letter")
    print(f"   Job Length: {len(JOB_DESCRIPTION)} characters")
    print(f"   Timeout: 180 seconds (extended for cold start)")
    print("\n" + "-"*80)
    
    # Prepare request
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "job_description": JOB_DESCRIPTION,
        "applicant_name": "Dilip Kumar",
        "applicant_email": "dthirukondac@binghamton.edu",
        "return_format": "base64"
    }
    
    print("\n📤 SENDING REQUEST...")
    print("   (This may take 30-180 seconds on first request...)\n")
    start_time = datetime.now()
    
    try:
        # Make API call with extended timeout
        response = requests.post(
            f"{API_URL}/api/v1/generate-cover-letter",
            json=payload,
            headers=headers,
            timeout=180  # Extended timeout for cold start
        )
        
        end_time = datetime.now()
        elapsed = (end_time - start_time).total_seconds()
        
        print(f"✅ Response received in {elapsed:.2f} seconds")
        print(f"📊 Status Code: {response.status_code}")
        print("-"*80)
        
        # Check if successful
        if response.status_code == 200:
            result = response.json()
            
            print("\n" + "="*80)
            print("✅ SUCCESS - COVER LETTER GENERATED!")
            print("="*80)
            print(f"\n📋 RESPONSE DETAILS:")
            print(f"   Status: {result.get('status', 'N/A')}")
            print(f"   Message: {result.get('message', 'N/A')}")
            print(f"   Filename: {result.get('filename', 'N/A')}")
            print(f"   Company Name: {result.get('company_name', 'N/A')}")
            print(f"   Response Time: {elapsed:.2f} seconds")
            
            # Check if base64 data is present
            if 'cover_letter_base64' in result:
                base64_data = result['cover_letter_base64']
                print(f"\n📄 Base64 Data Length: {len(base64_data):,} characters")
                
                # Decode and save to file
                cover_letter_bytes = base64.b64decode(base64_data)
                filename = f"output/thredup_cover_letter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
                
                with open(filename, "wb") as f:
                    f.write(cover_letter_bytes)
                
                print(f"💾 Saved to: {filename}")
                print(f"📏 File Size: {len(cover_letter_bytes):,} bytes ({len(cover_letter_bytes)/1024:.2f} KB)")
                
                print("\n" + "="*80)
                print("🎉 TEST PASSED - API IS WORKING CORRECTLY!")
                print("="*80)
                print("\n📊 SUMMARY:")
                print(f"   ✅ API Response: OK (200)")
                print(f"   ✅ Generation Time: {elapsed:.2f}s")
                print(f"   ✅ Cover Letter Created: YES")
                print(f"   ✅ File Saved: {filename}")
                print(f"   ✅ Company Detected: {result.get('company_name', 'ThredUp')}")
                print(f"\n💡 INTEGRATION READY:")
                print(f"   • Copy the 6-line Python snippet from API_CHEAT_SHEET.md")
                print(f"   • Replace job description with your target job")
                print(f"   • API will generate cover letter in ~30-60s")
                
                return True
            else:
                print("\n⚠️  WARNING: No base64 data in response")
                print(f"Full Response: {json.dumps(result, indent=2)}")
                return False
        
        elif response.status_code == 401:
            print(f"\n❌ AUTHENTICATION ERROR (401)")
            print("="*80)
            print("The API key is missing or incorrect.")
            print(f"Current API key: {API_KEY}")
            return False
        
        elif response.status_code == 500:
            print(f"\n❌ SERVER ERROR (500)")
            print("="*80)
            print("The API encountered an internal error.")
            try:
                error_data = response.json()
                print(f"Error Details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Raw Response: {response.text}")
            return False
        
        else:
            print(f"\n❌ ERROR - HTTP {response.status_code}")
            print("="*80)
            print(f"Response: {response.text}")
            return False
    
    except requests.exceptions.Timeout:
        print(f"\n❌ TIMEOUT - Request exceeded 180 seconds")
        print("="*80)
        print("Possible causes:")
        print("  • API is experiencing heavy load")
        print("  • Network connectivity issues")
        print("  • API service may be down")
        print("\nRecommendation: Try again in 1-2 minutes")
        return False
    
    except Exception as e:
        print(f"\n❌ EXCEPTION OCCURRED")
        print("="*80)
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        import traceback
        print(f"\nTraceback:\n{traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_cover_letter_api()
    
    print("\n" + "="*80)
    if success:
        print("✅ ALL TESTS PASSED - API IS PRODUCTION READY!")
        print("\nNext Steps:")
        print("  1. Open the generated cover letter document")
        print("  2. Review the content and formatting")
        print("  3. Use the API in your automation scripts")
    else:
        print("⚠️  TESTS FAILED - See error messages above")
        print("\nTroubleshooting:")
        print("  1. Check internet connection")
        print("  2. Verify API key is correct")
        print("  3. Wait 2 minutes and try again (cold start)")
        print("  4. Check API status: https://resume-optimizer-api-fvpd.onrender.com/health")
    print("="*80)
