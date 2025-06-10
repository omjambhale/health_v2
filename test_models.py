from src.core.profile_manager import ProfileManager, UserProfile, OnboardingAnswers

# Test the models
pm = ProfileManager()

# Create a test profile
profile = UserProfile(
    name="john doe",
    age=28,
    gender="male", 
    height_cm=175.0,
    weight_kg=75.0,
    exercise_frequency="3-4_times_week",
    goal="I want to lose 10 pounds and build muscle"
)

print("Profile created:", profile.name)  # Should be "John Doe" (auto-formatted)
print("Data valid:", profile.dict())

# Add this to your test_models.py to see validation in action
print("\n--- Testing Validation ---")

try:
    # This should fail - invalid age
    bad_profile = UserProfile(
        name="Test User",
        age=5,  # Too young!
        gender="male",
        height_cm=175.0,
        weight_kg=75.0,
        exercise_frequency="daily",
        goal="Get fit"
    )
except Exception as e:
    print("Age validation caught:", e)

try:
    # This should fail - invalid name
    bad_profile = UserProfile(
        name="123",  # Numbers not allowed!
        age=25,
        gender="female",
        height_cm=165.0,
        weight_kg=65.0,
        exercise_frequency="never",
        goal="Lose weight"
    )
except Exception as e:
    print("Name validation caught:", e)

print("Validation tests complete!")