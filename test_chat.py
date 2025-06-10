from src.core.chat_manager import ChatManager
from src.core.profile_manager import ProfileManager, UserProfile, UserData

# Create test data
pm = ProfileManager()
profile = UserProfile(
    name="Sarah Johnson",
    age=28,
    gender="female",
    height_cm=165.0,
    weight_kg=68.0,
    exercise_frequency="3-4_times_week",
    goal="I want to lose 15 pounds and tone up for summer"
)

user_id = pm.create_user_id(profile.name)
user_data = UserData(user_id=user_id, profile=profile)

# Test the chat flow
cm = ChatManager()
print("=== STARTING CHAT ===")
response = cm.start_chat_session(user_data)
print("COACH:", response)

print("\n=== USER SAYS: 'workout' ===")
response = cm.process_user_message(user_id, "workout")
print("COACH:", response)

print("\n=== USER SAYS: 'I have a gym membership' ===")
response = cm.process_user_message(user_id, "I have a gym membership")
print("COACH:", response)

print("\n=== USER SAYS: 'I have a bad knee' ===")
response = cm.process_user_message(user_id, "I have a bad knee")
print("COACH:", response)

print("\n=== CHECK ONBOARDING DATA ===")
onboarding = cm.get_onboarding_data(user_id)
if onboarding:
    print("Focus:", onboarding.focus_area)
    print("Specific:", onboarding.specific_question_answer)
    print("Additional:", onboarding.additional_info)