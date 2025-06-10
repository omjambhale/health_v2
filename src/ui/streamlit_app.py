import streamlit as st
from datetime import datetime
import sys
import os

# Add the project root to the path so we can import our modules
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..', '..')
sys.path.append(project_root)

from src.core.profile_manager import ProfileManager, UserProfile, UserData
from src.core.chat_manager import ChatManager
from src.core.health_ai_engine import HealthAIEngine
from config.settings import APP_TITLE

# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="💪",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize session state
def init_session_state():
    """Initialize all session state variables"""
    if 'step' not in st.session_state:
        st.session_state.step = 'profile'  # profile -> chat
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None
    if 'chat_manager' not in st.session_state:
        st.session_state.chat_manager = ChatManager()
    if 'ai_engine' not in st.session_state:
        st.session_state.ai_engine = HealthAIEngine()
    if 'profile_manager' not in st.session_state:
        st.session_state.profile_manager = ProfileManager()

def render_header():
    """Render the app header"""
    st.title("💪 Health Coach V2")
    st.markdown("---")

def render_profile_form():
    """Render the user profile collection form"""
    st.header("👋 Let's Get Started!")
    st.write("First, tell me a bit about yourself so I can give you personalized advice.")
    
    with st.form("profile_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("What's your name?", placeholder="e.g., John Smith")
            age = st.number_input("Age", min_value=13, max_value=120, value=25)
            gender = st.selectbox("Gender", ["male", "female", "other"])
        
        with col2:
            height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=170.0, step=0.5)
            weight = st.number_input("Weight (kg)", min_value=30.0, max_value=300.0, value=70.0, step=0.5)
            exercise_freq = st.selectbox("How often do you exercise?", [
                "never", "rarely", "1-2_times_week", 
                "3-4_times_week", "5-6_times_week", "daily"
            ], format_func=lambda x: x.replace('_', ' ').title())
        
        goal = st.text_area(
            "What's your main health/fitness goal?", 
            placeholder="e.g., I want to lose 10 pounds and build muscle for summer",
            height=100
        )
        
        # Coach style selection
        st.subheader("🎯 Choose Your Coach Style")
        coach_style = st.radio(
            "How would you like me to coach you?",
            ["normal", "david_goggins"],
            format_func=lambda x: "Normal (Supportive & Encouraging)" if x == "normal" 
                                 else "David Goggins Mode (Intense & No-Nonsense)",
            horizontal=True
        )
        
        submit_button = st.form_submit_button("Start Coaching! 🚀", type="primary")
        
        if submit_button:
            if name and goal:
                try:
                    # Create user profile
                    profile = UserProfile(
                        name=name,
                        age=age,
                        gender=gender,
                        height_cm=height,
                        weight_kg=weight,
                        exercise_frequency=exercise_freq,
                        goal=goal
                    )
                    
                    # Create user data
                    user_id = st.session_state.profile_manager.create_user_id(name)
                    user_data = UserData(user_id=user_id, profile=profile)
                    user_data.coach_style.style = coach_style
                    
                    # Save user data
                    if st.session_state.profile_manager.save_user_data(user_data):
                        st.session_state.user_data = user_data
                        
                        # Start chat session
                        welcome_msg = st.session_state.chat_manager.start_chat_session(user_data)
                        
                        # Move to chat step
                        st.session_state.step = 'chat'
                        st.success("Profile created! Starting chat...")
                        
                except Exception as e:
                    st.error(f"Please check your information: {str(e)}")
            else:
                st.error("Please fill in your name and goal to continue.")

def render_chat_interface():
    """Render the chat interface"""
    user_data = st.session_state.user_data
    chat_manager = st.session_state.chat_manager
    
    # Header with user info
    st.header(f"💬 Hey {user_data.profile.name.split()[0]}!")
    
    # Show coach style
    style_emoji = "🔥" if user_data.coach_style.style == "david_goggins" else "😊"
    style_name = "David Goggins Mode" if user_data.coach_style.style == "david_goggins" else "Normal Coach"
    st.caption(f"{style_emoji} Coach Style: {style_name}")
    
    # Chat container
    chat_container = st.container()
    
    # Display chat history
    with chat_container:
        messages = chat_manager.get_chat_history(user_data.user_id)
        
        for message in messages:
            if message.role == "assistant":
                with st.chat_message("assistant", avatar="🤖"):
                    st.write(message.content)
            else:
                with st.chat_message("user", avatar="👤"):
                    st.write(message.content)
    
    # Chat input
    if user_input := st.chat_input("Type your message here..."):
        # Display user message immediately
        with st.chat_message("user", avatar="👤"):
            st.write(user_input)
        
        # Process the message
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                # Check if onboarding is complete
                if chat_manager.is_onboarding_complete(user_data.user_id):
                    # Generate AI response
                    onboarding_data = chat_manager.get_onboarding_data(user_data.user_id)
                    chat_history = chat_manager.get_chat_history(user_data.user_id)
                    
                    ai_response = st.session_state.ai_engine.generate_coaching_response(
                        user_data=user_data,
                        onboarding=onboarding_data,
                        chat_history=chat_history,
                        user_message=user_input
                    )
                    
                    # Add AI message to chat manager
                    from src.core.chat_manager import ChatMessage
                    ai_message = ChatMessage(
                        role="assistant",
                        content=ai_response,
                        timestamp=datetime.now().isoformat()
                    )
                    chat_manager.sessions[user_data.user_id].messages.append(ai_message)
                    
                    st.write(ai_response)
                else:
                    # Handle onboarding flow
                    response = chat_manager.process_user_message(user_data.user_id, user_input)
                    st.write(response)
                    
                    # Save onboarding data when complete
                    if chat_manager.is_onboarding_complete(user_data.user_id):
                        onboarding_data = chat_manager.get_onboarding_data(user_data.user_id)
                        if onboarding_data:
                            st.session_state.profile_manager.update_onboarding(
                                user_data.user_id, onboarding_data
                            )
    
    # Sidebar with user info
    with st.sidebar:
        st.header("📊 Your Profile")
        st.write(f"**Name:** {user_data.profile.name}")
        st.write(f"**Age:** {user_data.profile.age}")
        st.write(f"**Goal:** {user_data.profile.goal}")
        st.write(f"**Coach Style:** {style_name}")
        
        st.markdown("---")
        
        if st.button("🔄 Start Over"):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]

def main():
    """Main app function"""
    init_session_state()
    render_header()
    
    if st.session_state.step == 'profile':
        render_profile_form()
    elif st.session_state.step == 'chat':
        render_chat_interface()

if __name__ == "__main__":
    main()