from typing import List, Optional
from src.core.profile_manager import UserData, OnboardingAnswers
from src.core.chat_manager import ChatMessage

class PromptBuilder:
    """Builds context-rich prompts for the AI health coach"""
    
    def __init__(self):
        self.base_coach_personality = {
            "normal": {
                "tone": "friendly, encouraging, and supportive",
                "style": "Give practical, science-based advice with a warm, motivational tone",
                "personality": "You're a knowledgeable but approachable health coach"
            },
            "david_goggins": {
                "tone": "intense, direct, and no-nonsense", 
                "style": "Challenge them with tough love, push them beyond comfort zones",
                "personality": "You're David Goggins - mental toughness, discipline, embrace the suck"
            }
        }
    
    def build_system_prompt(self, user_data: UserData, onboarding: OnboardingAnswers) -> str:
        """Create the main system prompt with full user context"""
        
        # Get coach style
        coach_style = user_data.coach_style.style
        personality = self.base_coach_personality[coach_style]
        
        # Build comprehensive context
        user_context = self._build_user_context(user_data, onboarding)
        coaching_guidelines = self._get_coaching_guidelines(coach_style)
        response_format = self._get_response_format(onboarding.focus_area)
        
        system_prompt = f"""You are an expert AI health coach with the following personality and approach:

COACH PERSONALITY & TONE:
{personality['personality']}
Tone: {personality['tone']}
Style: {personality['style']}

USER PROFILE & CONTEXT:
{user_context}

COACHING GUIDELINES:
{coaching_guidelines}

RESPONSE FORMAT & FOCUS:
{response_format}

Remember: Always be helpful, evidence-based, and tailored to this specific user's context."""

        return system_prompt
    
    def _build_user_context(self, user_data: UserData, onboarding: OnboardingAnswers) -> str:
        """Build detailed user context section"""
        profile = user_data.profile
        
        # Calculate BMI for context
        height_m = profile.height_cm / 100
        bmi = profile.weight_kg / (height_m ** 2)
        bmi_category = self._get_bmi_category(bmi)
        
        context = f"""
Name: {profile.name}
Age: {profile.age} years old
Gender: {profile.gender}
Height: {profile.height_cm}cm ({self._cm_to_feet(profile.height_cm)})
Weight: {profile.weight_kg}kg ({self._kg_to_lbs(profile.weight_kg)}lbs)
BMI: {bmi:.1f} ({bmi_category})
Exercise Frequency: {profile.exercise_frequency.replace('_', ' ')}
Primary Goal: "{profile.goal}"

ONBOARDING RESPONSES:
Focus Area: {onboarding.focus_area}
{onboarding.specific_question}
Answer: "{onboarding.specific_question_answer}"
Additional Context: "{onboarding.additional_info}"
"""
        return context
    
    def _get_coaching_guidelines(self, coach_style: str) -> str:
        """Get style-specific coaching guidelines"""
        if coach_style == "david_goggins":
            return """
• Push them beyond their comfort zone - growth happens in discomfort
• Use direct, sometimes harsh language to break through mental barriers
• Emphasize mental toughness, discipline, and taking ownership
• Challenge excuses and weak mindset thinking
• Focus on doing the hard things that others won't do
• Remind them that pain is temporary but quitting lasts forever
• Make them accountable for their choices and results
• Reference overcoming obstacles and pushing through when it sucks
"""
        else:  # normal
            return """
• Be encouraging and supportive while maintaining honesty
• Provide practical, actionable advice they can implement today
• Break down complex goals into manageable steps
• Celebrate small wins and progress along the way
• Address challenges with empathy and problem-solving
• Use positive reinforcement and motivation
• Focus on sustainable, long-term habit changes
• Make advice accessible and realistic for their lifestyle
"""
    
    def _get_response_format(self, focus_area: str) -> str:
        """Get focus-area specific response formatting"""
        if focus_area == "workout":
            return """
WORKOUT RESPONSES SHOULD INCLUDE:
• Specific exercises with sets/reps/duration when relevant
• Progression suggestions (how to advance over time)
• Form cues and safety considerations
• Equipment alternatives if needed
• Recovery and rest day guidance
• Adaptation for any mentioned limitations

FORMAT: Use clear structure with exercise names, specific numbers, and practical tips.
"""
        else:  # food
            return """
NUTRITION RESPONSES SHOULD INCLUDE:
• Specific food suggestions and meal ideas
• Portion guidance when relevant
• Timing recommendations (when to eat what)
• Practical prep tips and shortcuts
• Substitutions for dietary restrictions
• Hydration and supplement guidance when appropriate

FORMAT: Use clear meal/snack suggestions with specific foods and practical implementation tips.
"""
    
    def build_conversation_context(self, chat_history: List[ChatMessage], max_messages: int = 10) -> str:
        """Build conversation context from recent chat history"""
        if not chat_history:
            return "This is the start of your conversation."
        
        # Get recent messages (excluding system/onboarding messages)
        recent_messages = chat_history[-max_messages:] if len(chat_history) > max_messages else chat_history
        
        # Filter to actual conversation (skip onboarding flow)
        conversation_messages = [
            msg for msg in recent_messages 
            if not any(keyword in msg.content.lower() for keyword in 
                      ['question 1 of 3', 'question 2 of 3', 'final question', 'perfect! 🎯'])
        ]
        
        if not conversation_messages:
            return "This is the beginning of your coaching conversation."
        
        context = "RECENT CONVERSATION:\n"
        for msg in conversation_messages[-5:]:  # Last 5 actual conversation messages
            role = "USER" if msg.role == "user" else "COACH"
            context += f"{role}: {msg.content}\n"
        
        return context
    
    def build_coaching_prompt(self, user_data: UserData, onboarding: OnboardingAnswers, 
                            chat_history: List[ChatMessage], user_message: str) -> str:
        """Build the complete prompt for a coaching response"""
        
        system_prompt = self.build_system_prompt(user_data, onboarding)
        conversation_context = self.build_conversation_context(chat_history)
        
        full_prompt = f"""{system_prompt}

{conversation_context}

USER'S CURRENT MESSAGE: "{user_message}"

Provide a helpful, personalized response as their health coach. Be specific, actionable, and tailored to their profile and goals."""

        return full_prompt
    
    # Helper methods for formatting
    def _get_bmi_category(self, bmi: float) -> str:
        """Categorize BMI for context"""
        if bmi < 18.5:
            return "underweight"
        elif bmi < 25:
            return "normal weight"
        elif bmi < 30:
            return "overweight"
        else:
            return "obese"
    
    def _cm_to_feet(self, cm: float) -> str:
        """Convert cm to feet and inches"""
        inches = cm / 2.54
        feet = int(inches // 12)
        remaining_inches = int(inches % 12)
        return f"{feet}'{remaining_inches}\""
    
    def _kg_to_lbs(self, kg: float) -> int:
        """Convert kg to pounds"""
        return int(kg * 2.20462)