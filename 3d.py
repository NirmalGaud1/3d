import streamlit as st
import google.generativeai as genai
import os
import io
from gtts import gTTS
import time
import speech_recognition as sr  # Corrected import

# --- Configuration ---
try:
    genai.configure(api_key="AIzaSyBfxXXypKxT0-SOzncW5m153D75r-kLRLA")
except Exception as e:
    st.error(f"Failed to configure Google Generative AI. Error: {e}")
    st.stop()

# --- Streamlit App UI ---
st.set_page_config(page_title="Talking Aria", page_icon="🤖")

st.markdown(
    """
    <style>
        .stButton>button {
            background-color: #4A90E2;
            color: white;
            border-radius: 12px;
            border: none;
            padding: 12px 24px;
            font-size: 1.1rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #357ABD;
            transform: scale(1.02);
        }
        .stTextInput>div>div>input, .stTextArea>div>div>textarea {
            border-radius: 12px;
            padding: 12px;
            border: 1px solid #ddd;
            font-size: 1rem;
        }
        .title-text {
            font-size: 2.5em;
            color: #2c3e50;
            text-align: center;
            margin-bottom: 20px;
        }
        .header-text {
            font-size: 1.8em;
            color: #34495e;
            margin-top: 20px;
            margin-bottom: 15px;
        }
        .aria-visual-container {
            display: flex;
            justify-content: center;
            margin-bottom: 20px;
        }
        .aria-image {
            max-width: 300px;
            height: auto;
            border-radius: 15px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        }
        .chat-message {
            padding: 10px;
            margin: 5px;
            border-radius: 8px;
            font-size: 1rem;
        }
        .user-message {
            background-color: #e6f3ff;
            border: 1px solid #4A90E2;
        }
        .aria-message {
            background-color: #f0f0f0;
            border: 1px solid #34495e;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<h1 class='title-text'>🌟 Talking Aria (Streamlit) 🌟</h1>", unsafe_allow_html=True)
st.write("Interact with Aria using voice commands. Listen to her intelligent replies!")

# --- Session State Initialization ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "aria_animation_state" not in st.session_state:
    st.session_state.aria_animation_state = 'idle'  # 'idle', 'listening', 'thinking', 'speaking'
if "spoken_text" not in st.session_state:
    st.session_state.spoken_text = ""
if "aria_says" not in st.session_state:
    st.session_state.aria_says = ""
if "listening" not in st.session_state:
    st.session_state.listening = False

# --- AI Model Initialization ---
try:
    model = genai.GenerativeModel('gemini-1.5-flash')  # Updated to a stable model
    chat = model.start_chat(history=st.session_state.chat_history)
except Exception as e:
    st.error(f"Error initializing Gemini model. Please check your API key and network connection. Error: {e}")
    st.stop()

# --- Functions ---
def get_ai_response(user_input):
    """Sends user input to Gemini AI and returns Aria's response."""
    try:
        response = chat.send_message(user_input)
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.chat_history.append({"role": "aria", "content": response.text})
        return response.text
    except Exception as e:
        st.error(f"Error getting response from Gemini AI: {e}")
        return "Sorry, I'm having trouble connecting to my brain right now. Please try again."

def speak_text_and_animate(text):
    """Generates audio for Aria speaking using gTTS and updates her visual state."""
    st.session_state.aria_says = text
    st.session_state.aria_animation_state = 'speaking'

    try:
        tts = gTTS(text=text, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        st.audio(fp, format='audio/mp3', start_time=0)
    except Exception as e:
        st.error(f"Error generating Aria's voice: {e}")
        st.session_state.aria_says = "Sorry, I couldn't generate voice output."
    finally:
        st.session_state.aria_animation_state = 'idle'

def listen_for_command():
    """Listens to the microphone, converts speech to text, and processes the command."""
    if st.session_state.listening:
        return  # Prevent multiple simultaneous listens

    st.session_state.listening = True
    st.session_state.aria_animation_state = 'listening'
    st.session_state.spoken_text = "Aria is listening..."

    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            try:
                audio = r.listen(source, timeout=5, phrase_time_limit=5)
                st.session_state.aria_animation_state = 'thinking'
                st.session_state.spoken_text = "Processing your command..."

                command_text = r.recognize_google(audio)
                st.session_state.spoken_text = f"You said: {command_text}"

                ai_response_text = get_ai_response(command_text)
                speak_text_and_animate(ai_response_text)
            except sr.WaitTimeoutError:
                st.session_state.spoken_text = "No speech detected. Please try again."
            except sr.UnknownValueError:
                st.session_state.spoken_text = "Could not understand audio. Please speak more clearly."
            except sr.RequestError as e:
                st.session_state.spoken_text = f"Speech service error: {e}. Please check your internet connection."
            except Exception as e:
                st.session_state.spoken_text = f"An unexpected error occurred: {e}"
    except Exception as e:
        st.session_state.spoken_text = f"Microphone error: {e}. Please ensure a microphone is connected."
    finally:
        st.session_state.aria_animation_state = 'idle'
        st.session_state.listening = False

# --- Display Aria's Visual ---
aria_idle_image_url = "https://placehold.co/300x400/87CEEB/FFFFFF?text=Aria+Idle"
aria_listening_image_url = "https://placehold.co/300x400/FFD700/000000?text=Aria+Listening"
aria_thinking_image_url = "https://placehold.co/300x400/FFA07A/000000?text=Aria+Thinking"
aria_speaking_image_url = "https://placehold.co/300x400/98FB98/000000?text=Aria+Speaking"

if st.session_state.aria_animation_state == 'listening':
    current_aria_image = aria_listening_image_url
elif st.session_state.aria_animation_state == 'thinking':
    current_aria_image = aria_thinking_image_url
elif st.session_state.aria_animation_state == 'speaking':
    current_aria_image = aria_speaking_image_url
else:
    current_aria_image = aria_idle_image_url

st.markdown(f"""
    <div class="aria-visual-container">
        <img src="{current_aria_image}" class="aria-image">
    </div>
""", unsafe_allow_html=True)

# --- Voice Input Button ---
if st.button("🎙️ Start Listening"):
    listen_for_command()

# --- Display Current Interaction ---
if st.session_state.spoken_text:
    st.markdown("<h3 class='header-text'>You Said:</h3>", unsafe_allow_html=True)
    st.text_area("Your Input", st.session_state.spoken_text, height=50, key="spoken_output_display", disabled=True)

if st.session_state.aria_says:
    st.markdown("<h3 class='header-text'>Aria Says:</h3>", unsafe_allow_html=True)
    st.text_area("Aria's Response", st.session_state.aria_says, height=150, key="aria_output_display", disabled=True)

# --- Display Chat History ---
if st.session_state.chat_history:
    st.markdown("<h3 class='header-text'>Chat History:</h3>", unsafe_allow_html=True)
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"<div class='chat-message user-message'>You: {message['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-message aria-message'>Aria: {message['content']}</div>", unsafe_allow_html=True)

# --- Limitations and Next Steps ---
st.markdown("---")
st.markdown(
    """
    <h3 class='header-text'>Important Notes for Streamlit:</h3>
    <p>
    Direct real-time 3D character animation (like in Three.js) and
    browser-native Web Speech API for voice input are not
    natively supported within Streamlit's core framework without <a href="https://docs.streamlit.io/library/components/create" target="_blank">Streamlit Custom Components</a>.
    </p>

    <h3 class='header-text'>Next Steps for Enhancing this Streamlit App:</h3>
    <ul>
        <li><b>Provide Actual Animated Visuals:</b> Replace the placeholder image URLs with actual animated GIFs or videos.</li>
        <li><b>True 3D Visuals:</b> Use a Streamlit Custom Component for interactive 3D character control (e.g., GLTF models).</li>
        <li><b>Enhanced Voice Control:</b> Explore advanced TTS services like Google Cloud Text-to-Speech for better voice options.</li>
        <li><b>Microphone Permissions:</b> Add checks for microphone availability and user permissions.</li>
    </ul>
    """,
    unsafe_allow_html=True
)
