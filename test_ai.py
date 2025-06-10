from src.core.health_ai_engine import HealthAIEngine
from src.core.profile_manager import ProfileManager, UserProfile, UserData, OnboardingAnswers

# Test API connection first
print("=== TESTING API CONNECTION ===")
ai_engine = HealthAIEngine()
if ai_engine.test_api_connection():
    print("✅ OpenAI API connection successful!")
else:
    print("❌ API connection failed - check your .env file")
    exit()

# Test quick response
print("\n=== TESTING QUICK RESPONSE (NORMAL) ===")
response = ai_engine.generate_quick_response(
    "I want to lose weight but I hate running", 
    "normal"
)
print("NORMAL COACH:", response)

print("\n=== TESTING QUICK RESPONSE (DAVID GOGGINS) ===")
response = ai_engine.generate_quick_response(
    "I want to lose weight but I hate running", 
    "david_goggins"
)
print("GOGGINS COACH:", response)

print("\n=== TESTING FULL CONTEXT RESPONSE ===")
# Create test user data
pm = ProfileManager()
profile = UserProfile(
    name="Mike Chen",
    age=32,
    gender="male",
    height_cm=180.0,
    weight_kg=85.0,
    exercise_frequency="rarely",
    goal="I want to build muscle and get stronger"
)

user_id = pm.create_user_id(profile.name)
user_data = UserData(user_id=user_id, profile=profile)

# Create onboarding data
onboarding = OnboardingAnswers(
    focus_area="workout",
    specific_question_answer="I have a gym membership but I'm intimidated",
    additional_info="I have never really lifted weights before",
    specific_question="Do you have access to a gym?"
)

# Test full coaching response
response = ai_engine.generate_coaching_response(
    user_data=user_data,
    onboarding=onboarding,
    chat_history=[],
    user_message="What's the best workout routine for a complete beginner?"
)

print("FULL CONTEXT COACH:", response)