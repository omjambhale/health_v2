from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from src.core.profile_manager import OnboardingAnswers, UserData

class ChatState(Enum):
    """Tracks which stage of onboarding we're in"""
    WELCOME = "welcome"
    ASKING_FOCUS = "asking_focus"  # Question 1: food or workout?
    ASKING_SPECIFIC = "asking_specific"  # Question 2: gym access or daily food
    ASKING_ADDITIONAL = "asking_additional"  # Question 3: anything else?
    ONBOARDING_COMPLETE = "onboarding_complete"  # Ready for main chat
    MAIN_CHAT = "main_chat"  # Normal conversation mode

class ChatMessage(BaseModel):
    """Represents a single chat message"""
    role: str  # "assistant" or "user"
    content: str
    timestamp: str

class ChatSession(BaseModel):
    """Manages the entire chat session state"""
    user_id: str
    state: ChatState = ChatState.WELCOME
    messages: List[ChatMessage] = []
    
    # Temporary storage for onboarding answers
    focus_area: Optional[str] = None
    specific_answer: Optional[str] = None
    additional_info: Optional[str] = None

class ChatManager:
    """Handles chat flow logic and state management"""
    
    def __init__(self):
        self.sessions: Dict[str, ChatSession] = {}
    
    def start_chat_session(self, user_data: UserData) -> str:
        """Initialize a new chat session for a user"""
        session = ChatSession(user_id=user_data.user_id)
        self.sessions[user_data.user_id] = session
        
        # Generate welcome message
        welcome_msg = self._generate_welcome_message(user_data)
        self._add_message(session, "assistant", welcome_msg)
        
        # Move to first question
        session.state = ChatState.ASKING_FOCUS
        focus_question = self._get_focus_question()
        self._add_message(session, "assistant", focus_question)
        
        return focus_question
    
    def process_user_message(self, user_id: str, message: str) -> str:
        """Process user input and return appropriate response"""
        session = self.sessions.get(user_id)
        if not session:
            return "Session not found. Please start over."
        
        # Add user message to history
        self._add_message(session, "user", message)
        
        # Process based on current state
        if session.state == ChatState.ASKING_FOCUS:
            return self._handle_focus_question(session, message)
        elif session.state == ChatState.ASKING_SPECIFIC:
            return self._handle_specific_question(session, message)
        elif session.state == ChatState.ASKING_ADDITIONAL:
            return self._handle_additional_question(session, message)
        elif session.state == ChatState.ONBOARDING_COMPLETE:
            return self._handle_onboarding_complete(session)
        else:
            return "I'm not sure how to help with that right now."
    
    def _generate_welcome_message(self, user_data: UserData) -> str:
        """Create personalized welcome message"""
        name = user_data.profile.name.split()[0]  # First name only
        return (
            f"Hey {name}! 👋 Great to meet you!\n\n"
            f"I'm your AI health coach, and I'm here to help you with your goal: "
            f'"{user_data.profile.goal}"\n\n'
            f"Before we dive in, I'd like to ask you a few quick questions to "
            f"give you the best possible guidance. Sound good?"
        )
    
    def _get_focus_question(self) -> str:
        """Question 1: What's their focus area?"""
        return (
            "**Question 1 of 3:**\n\n"
            "What would you like help with today?\n"
            "• **Food** - Nutrition, meal planning, diet optimization\n"
            "• **Workout** - Exercise routines, training plans, fitness strategies\n\n"
            "Just type 'food' or 'workout' (or tell me in your own words!)"
        )
    
    def _handle_focus_question(self, session: ChatSession, message: str) -> str:
        """Process answer to focus question"""
        message_lower = message.lower()
        
        # Try to detect intent
        if any(word in message_lower for word in ['food', 'eat', 'diet', 'nutrition', 'meal']):
            session.focus_area = "food"
            focus_detected = "food"
        elif any(word in message_lower for word in ['workout', 'exercise', 'gym', 'fitness', 'training']):
            session.focus_area = "workout" 
            focus_detected = "workout"
        else:
            # Unclear response - ask for clarification
            clarification = (
                "I want to make sure I understand! Are you looking for help with:\n"
                "• **Food** (nutrition, meals, diet)\n"
                "• **Workout** (exercise, training, fitness)\n\n"
                "Could you clarify which one interests you most?"
            )
            self._add_message(session, "assistant", clarification)
            return clarification
        
        # Move to specific question
        session.state = ChatState.ASKING_SPECIFIC
        specific_question = self._get_specific_question(focus_detected)
        self._add_message(session, "assistant", specific_question)
        return specific_question
    
    def _get_specific_question(self, focus_area: str) -> str:
        """Question 2: Specific follow-up based on their choice"""
        if focus_area == "workout":
            return (
                "**Question 2 of 3:**\n\n"
                "Do you have access to a gym, or will you be working out at home?\n\n"
                "This helps me recommend the right exercises and equipment for your situation!"
            )
        else:  # food
            return (
                "**Question 2 of 3:**\n\n"
                "What do you usually eat in a typical day? Don't worry about being perfect - "
                "just give me a rough idea!\n\n"
                "For example: 'Cereal for breakfast, sandwich for lunch, pasta for dinner' "
                "or whatever feels normal for you."
            )
    
    def _handle_specific_question(self, session: ChatSession, message: str) -> str:
        """Process answer to the specific follow-up question"""
        session.specific_answer = message
        
        # Move to final question
        session.state = ChatState.ASKING_ADDITIONAL
        final_question = self._get_final_question()
        self._add_message(session, "assistant", final_question)
        return final_question
    
    def _get_final_question(self) -> str:
        """Question 3: Any additional context"""
        return (
            "**Final question (3 of 3):**\n\n"
            "Is there anything else I should know to give you the best advice? \n\n"
            "Things like:\n"
            "• Injuries or physical limitations\n"
            "• Dietary restrictions or preferences\n" 
            "• Time constraints\n"
            "• Past experiences with diet/exercise\n\n"
            "Or just type 'nothing else' if you're all set!"
        )
    
    def _handle_additional_question(self, session: ChatSession, message: str) -> str:
        """Process final onboarding question"""
        session.additional_info = message
        session.state = ChatState.ONBOARDING_COMPLETE
        
        completion_msg = (
            "Perfect! 🎯 I have everything I need.\n\n"
            "Based on your profile and answers, I'm ready to be your personal health coach. "
            "Let's start with your first question or goal - what would you like to work on?"
        )
        self._add_message(session, "assistant", completion_msg)
        return completion_msg
    
    def _handle_onboarding_complete(self, session: ChatSession) -> str:
        """Handle the transition to main chat"""
        session.state = ChatState.MAIN_CHAT
        return "I'm ready to help! What's your first question?"
    
    def get_onboarding_data(self, user_id: str) -> Optional[OnboardingAnswers]:
        """Extract completed onboarding data"""
        session = self.sessions.get(user_id)
        if not session or not all([session.focus_area, session.specific_answer]):
            return None
        
        # Determine which specific question was asked
        if session.focus_area == "workout":
            specific_question = "Do you have access to a gym, or will you be working out at home?"
        else:
            specific_question = "What do you usually eat in a typical day?"
        
        return OnboardingAnswers(
            focus_area=session.focus_area,
            specific_question_answer=session.specific_answer,
            additional_info=session.additional_info or "No additional information provided",
            specific_question=specific_question
        )
    
    def is_onboarding_complete(self, user_id: str) -> bool:
        """Check if user has completed onboarding"""
        session = self.sessions.get(user_id)
        return session and session.state in [ChatState.ONBOARDING_COMPLETE, ChatState.MAIN_CHAT]
    
    def get_chat_history(self, user_id: str) -> List[ChatMessage]:
        """Get full chat history for a user"""
        session = self.sessions.get(user_id)
        return session.messages if session else []
    
    def _add_message(self, session: ChatSession, role: str, content: str):
        """Add a message to the session history"""
        from datetime import datetime
        message = ChatMessage(
            role=role,
            content=content,
            timestamp=datetime.now().isoformat()
        )
        session.messages.append(message)