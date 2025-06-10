from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
from datetime import datetime
import json
import os
from config.settings import USER_DATA_FILE, STORAGE_DIR

class UserProfile(BaseModel):
    """User's basic health profile information"""
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=13, le=120)  # Age between 13-120
    gender: Literal["male", "female", "other"] = Field(...)
    height_cm: float = Field(..., ge=100, le=250)  # Height in cm
    weight_kg: float = Field(..., ge=30, le=300)   # Weight in kg
    exercise_frequency: Literal[
        "never", "rarely", "1-2_times_week", 
        "3-4_times_week", "5-6_times_week", "daily"
    ] = Field(...)
    goal: str = Field(..., min_length=5, max_length=500)
    
    @validator('name')
    def validate_name(cls, v):
        """Ensure name contains only letters, spaces, and basic punctuation"""
        if not v.replace(' ', '').replace('-', '').replace("'", '').isalpha():
            raise ValueError('Name should contain only letters, spaces, hyphens, and apostrophes')
        return v.strip().title()

class OnboardingAnswers(BaseModel):
    """User's answers to the 3 onboarding questions"""
    focus_area: Literal["food", "workout"] = Field(...)
    specific_question_answer: str = Field(..., min_length=3, max_length=1000)
    additional_info: Optional[str] = Field(None, max_length=1000)
    
    # Track which specific question was asked based on focus_area
    specific_question: str = Field(...)

class CoachStyle(BaseModel):
    """Coach personality settings"""
    style: Literal["normal", "david_goggins"] = Field(default="normal")

class UserData(BaseModel):
    """Complete user data structure"""
    user_id: str = Field(...)  # Simple string ID for now
    profile: UserProfile
    onboarding: Optional[OnboardingAnswers] = None
    coach_style: CoachStyle = Field(default_factory=CoachStyle)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class ProfileManager:
    """Handles all user profile operations and JSON storage"""
    
    def __init__(self):
        """Initialize profile manager and ensure storage directory exists"""
        os.makedirs(STORAGE_DIR, exist_ok=True)
    
    def save_user_data(self, user_data: UserData) -> bool:
        """Save user data to JSON file"""
        try:
            # Update the timestamp
            user_data.updated_at = datetime.now()
            
            # Load existing data or create new structure
            all_users = self._load_all_users()
            all_users[user_data.user_id] = user_data.dict()
            
            # Save to file
            with open(USER_DATA_FILE, 'w') as f:
                json.dump(all_users, f, indent=2, default=str)
            
            return True
        except Exception as e:
            print(f"Error saving user data: {e}")
            return False
    
    def load_user_data(self, user_id: str) -> Optional[UserData]:
        """Load user data from JSON file"""
        try:
            all_users = self._load_all_users()
            if user_id in all_users:
                return UserData(**all_users[user_id])
            return None
        except Exception as e:
            print(f"Error loading user data: {e}")
            return None
    
    def _load_all_users(self) -> dict:
        """Load all users from JSON file"""
        try:
            if os.path.exists(USER_DATA_FILE):
                with open(USER_DATA_FILE, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading users file: {e}")
            return {}
    
    def create_user_id(self, name: str) -> str:
        """Create a simple user ID based on name and timestamp"""
        # Simple ID generation - in production you'd use UUID or similar
        clean_name = name.lower().replace(' ', '_').replace('-', '_')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{clean_name}_{timestamp}"
    
    def update_onboarding(self, user_id: str, onboarding: OnboardingAnswers) -> bool:
        """Update user's onboarding answers"""
        user_data = self.load_user_data(user_id)
        if user_data:
            user_data.onboarding = onboarding
            return self.save_user_data(user_data)
        return False
    
    def update_coach_style(self, user_id: str, style: str) -> bool:
        """Update user's coach style preference"""
        user_data = self.load_user_data(user_id)
        if user_data:
            user_data.coach_style.style = style
            return self.save_user_data(user_data)
        return False