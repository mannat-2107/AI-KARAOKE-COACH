import streamlit as st
import requests
import json
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Set page config with music theme
st.set_page_config(
    page_title="🎤 AI Vocal Master",
    page_icon="🎵",
    layout="centered"
)
vocal_range = "Soprano"  # Default vocal range

# Music-themed background
def set_background():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("https://as2.ftcdn.net/jpg/03/32/75/25/1000_F_332752512_3gCvPg3CS8LjY7EAxC7Nawr2oKS8M8PF.webp");
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
        }}
        .main .block-container {{
            background-color: rgba(0, 0, 0, 0.8);
            border-radius: 15px;
            padding: 2rem;
            margin-top: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 0 20px rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        .stChatMessage {{
            background-color: rgba(20, 20, 20, 0.9) !important;
            border-radius: 15px !important;
            padding: 1.5rem !important;
            margin: 1rem 0 !important;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2) !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_background()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "🎶 Welcome to Vocal Master! 🎤\n\nAsk me about:\n- 🎵 Vocal warm-ups\n- 🎼 Pitch correction\n- 🎧 Song selection\n- 🎤 Stage techniques\n\nLet's improve your singing!"
    }]
# Configure sidebar
# Configure sidebar
with st.sidebar:
    st.title("⚙️ Vocal Settings")
    api_key = st.text_input("🔑 OpenRouter API Key", type="password")
    st.markdown("[Get API Key](https://openrouter.ai/keys)")
    
    # Initialize vocal_range in session state
    if 'vocal_range' not in st.session_state:
        st.session_state.vocal_range = "Soprano"  # Default value
    
    # Model selection with vocal range
    model_name = st.selectbox(
        "🤖 Choose Model",
        ("google/palm-2-chat-bison",),
        index=0
    )
    
    # Vocal range selector
    st.session_state.vocal_range = st.selectbox(
        "🎚️ Your Vocal Range",
        ["Soprano", "Alto", "Tenor", "Baritone", "Bass"],
        index=0
    )
    
    # Advanced settings
    with st.expander("🎛️ Advanced Settings"):
        temperature = st.slider(
            "🎭 Response Style", 
            0.0, 1.0, 0.7,
            help="0 = Strict technical advice, 1 = Creative suggestions"
        )
    
    if st.button("🧹 Clear Session"):
        st.session_state.messages = [{
            "role": "assistant",
            "content": "🎤 Session cleared! Ask me vocal questions!"
        }]
# Main interface
st.title("🎤 AI Vocal Coach Pro")
st.caption("Your personal singing instructor with real-time feedback analysis")
st.caption("Vocal Master | By Reg. no :12316464")

# Chat display with music formatting
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        content = message["content"]
        # Enhance musical notation
        content = content.replace("C4", "C₄").replace("A3", "A₃")
        content = content.replace("- ", "🎵 ")
        st.markdown(content)

# Handle vocal queries
if prompt := st.chat_input("Ask about singing techniques..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    if not api_key:
        with st.chat_message("assistant"):
            st.error("🔐 API key required! Check sidebar.")
        st.stop()

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        with st.spinner("🎶 Composing response..."):
            try:
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://vocal-coach.streamlit.app",
                        "X-Title": "AI Vocal Master"
                    },
                    json={
                        "model": model_name,
                        "messages": [{
                            "role": "system",
                            "content": f"""You are a professional vocal coach. Follow these rules only and handle irrelevant responses:
1. Use music emojis (🎵🎤🎶)
2. Structure responses with:
   • 🎯 Technique Breakdown
   • 🎼 Exercise Steps
   • 💡 Pro Tips
   • 🎧 Song Examples
3. Include vocal notation (C₄, A₃)
4. Current vocal range: {vocal_range}
5. Always suggest practical exercises"""
                        }] + st.session_state.messages[-4:],
                        "temperature": temperature
                    },
                    timeout=20
                )

                response.raise_for_status()
                raw = response.json()['choices'][0]['message']['content']
                
                # Enhance musical formatting
                processed = raw.replace("- ", "🎵 ").replace("Step", "🎼 Step")
                processed = processed.replace("Tip:", "💡 Tip:").replace("Example:", "🎧 Example:")
                
                # Add animated typing
                for word in processed.split():
                    full_response += word + " "
                    response_placeholder.markdown(full_response + " ▌")
                    time.sleep(0.04)
                response_placeholder.markdown(full_response)
                
            except Exception as e:
                logging.error(f"Vocal Error: {str(e)}")
                full_response = f"🎤 Technical difficulty! Error: {str(e)}"
                response_placeholder.error(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})