from openai import OpenAI
from typing import List, Optional
from config.settings import OPENAI_API_KEY, OPENAI_MODEL
from src.core.profile_manager import UserData, OnboardingAnswers
from src.core.chat_manager import ChatMessage
from src.core.prompt_builder import PromptBuilder

class HealthAIEngine:
    """Core AI engine for health coaching responses"""
    
    def __init__(self):
        """Initialize the AI engine with OpenAI client"""
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        # Initialize OpenAI client (new v1.0+ format)
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
        self.prompt_builder = PromptBuilder()
        
        # Response settings
        self.max_tokens = 800  # Reasonable length for coaching responses
        self.temperature = 0.7  # Balanced creativity and consistency
    
    def generate_coaching_response(self, 
                                 user_data: UserData,
                                 onboarding: OnboardingAnswers, 
                                 chat_history: List[ChatMessage],
                                 user_message: str) -> str:
        """Generate a personalized coaching response"""
        
        try:
            # Build the comprehensive prompt
            prompt = self.prompt_builder.build_coaching_prompt(
                user_data=user_data,
                onboarding=onboarding,
                chat_history=chat_history,
                user_message=user_message
            )
            
            # Generate response using OpenAI (new v1.0+ format)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                presence_penalty=0.1,  # Slightly encourage new topics
                frequency_penalty=0.1   # Slightly reduce repetition
            )
            
            # Extract and return the response
            ai_response = response.choices[0].message.content.strip()
            return ai_response
            
        except Exception as e:
            if "rate_limit" in str(e).lower():
                return self._get_rate_limit_response()
            elif "invalid" in str(e).lower():
                return f"I apologize, but I encountered an issue processing your request: {str(e)}"
            else:
                print(f"AI Engine Error: {e}")
                return self._get_fallback_response(user_data, user_message)
    
    def generate_quick_response(self, user_message: str, coach_style: str = "normal") -> str:
        """Generate a quick response without full context (for testing)"""
        
        try:
            personality = self.prompt_builder.base_coach_personality[coach_style]
            
            simple_prompt = f"""You are a health coach with this personality:
{personality['personality']}
Tone: {personality['tone']}

Respond to this message: "{user_message}"

Keep it helpful, brief, and in character."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": simple_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Quick response error: {e}")
            return "I'm here to help with your health and fitness goals! What would you like to know?"
    
    def _get_rate_limit_response(self) -> str:
        """Response when hitting API rate limits"""
        return (
            "I'm getting a lot of requests right now! Please wait a moment and try again. "
            "In the meantime, remember that consistency is key to reaching your health goals! 💪"
        )
    
    def _get_fallback_response(self, user_data: UserData, user_message: str) -> str:
        """Fallback response when AI fails"""
        name = user_data.profile.name.split()[0]
        focus = getattr(user_data, 'onboarding', {}).get('focus_area', 'health')
        
        return (
            f"Hi {name}! I'm having a technical moment, but I'm still here to help with your {focus} goals. "
            f"Could you try rephrasing your question? I want to make sure I give you the best advice possible!"
        )
    
    def test_api_connection(self) -> bool:
        """Test if OpenAI API is working"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            return True
        except Exception as e:
            print(f"API connection test failed: {e}")
            return False