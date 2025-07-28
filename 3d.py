import streamlit as st
import google.generativeai as genai
import os # For accessing environment variables for API key
import io # Required for gTTS audio
from gtts import gTTS # Google Text-to-Speech library
import time # Import the time module for delays

# --- Configuration ---
try:
    # IMPORTANT: For production, use Streamlit Secrets (st.secrets) or environment variables
    # instead of hardcoding your API key directly in the script for security.
    # Example for st.secrets: genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    genai.configure(api_key="AIzaSyBfxXXypKxT0-SOzncW5m153D75r-kLRLA")
except Exception as e:
    st.error(f"Failed to configure Google Generative AI. Please ensure your API key is set correctly. Error: {e}")
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
        .stTextInput>div>div>input {
            border-radius: 12px;
            padding: 12px;
            border: 1px solid #ddd;
            font-size: 1rem;
        }
        .stTextArea>div>div>textarea {
            border-radius: 12px;
            padding: 12px;
            border: 1px solid #ddd;
            min-height: 150px;
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
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<h1 class='title-text'>🌟 Talking Aria (Streamlit) 🌟</h1>", unsafe_allow_html=True)
st.write("Interact with Aria using text commands. Get intelligent responses and hear her voice!")

# Initialize chat history and animation state in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "aria_animation_state" not in st.session_state:
    st.session_state.aria_animation_state = 'idle' # 'idle' or 'speaking'

# --- AI Model Initialization ---
try:
    model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')
    chat = model.start_chat(history=st.session_state.chat_history)
except Exception as e:
    st.error(f"Error initializing Gemini model. Please check your API key and network connection. Error: {e}")
    st.stop()

# --- Functions ---
def get_ai_response(user_input):
    """Sends user input to Gemini AI and returns Aria's response."""
    try:
        response = chat.send_message(user_input)
        return response.text
    except Exception as e:
        st.error(f"Error getting response from Gemini AI: {e}")
        return "Sorry, I'm having trouble connecting to my brain right now. Please try again."

def speak_text_and_animate(text):
    """
    Generates audio for Aria speaking using gTTS and updates her visual state.
    """
    st.session_state.aria_says = text
    st.session_state.aria_animation_state = 'speaking'
    st.experimental_rerun() # Rerun to show speaking animation immediately

    try:
        tts = gTTS(text=text, lang='en') # Default English voice is generally female-sounding
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0) # Rewind the buffer to the beginning

        # Display and play audio
        st.audio(fp, format='audio/mp3', start_time=0, key="aria_audio_player")

        # After audio plays (requires user interaction to re-trigger, or a custom component)
        # For a more dynamic flow without full custom component, you'd need JavaScript on frontend.
        # Here, we'll revert to idle after the Streamlit rerun cycle completes.
        # A more advanced approach would be to wait for the audio to finish playing.

    except Exception as e:
        st.error(f"Error generating Aria's voice: {e}")
        st.session_state.aria_says = "Sorry, I couldn't generate voice output."
    finally:
        # Revert to idle animation after speaking is initiated.
        # Note: In pure Streamlit, there's no direct 'audio finished' callback.
        # The animation will revert on the next user interaction or rerun.
        st.session_state.aria_animation_state = 'idle'
        st.experimental_rerun()


# --- Display Aria's Visual (Simulated 3D Animated Girl) ---
aria_idle_image_url = "https://placehold.co/300x400/87CEEB/FFFFFF?text=Aria+Idle" # Placeholder for idle girl
aria_speaking_image_url = "https://placehold.co/300x400/98FB98/000000?text=Aria+Speaking" # Placeholder for speaking girl

# You can replace these with actual GIFs or images of a 3D animated girl
# Example: "https://your-domain.com/aria_idle.gif" or "https://your-domain.com/aria_speaking.gif"

current_aria_image = aria_speaking_image_url if st.session_state.aria_animation_state == 'speaking' else aria_idle_image_url

st.markdown(f"""
    <div class="aria-visual-container">
        <img src="{current_aria_image}" class="aria-image">
    </div>
""", unsafe_allow_html=True)


# --- Main Interaction Loop ---
user_command = st.text_input("Type your command here:", key="user_input_text")

if st.button("Send Command"):
    if user_command:
        st.session_state.spoken_text = user_command
        st.session_state.aria_says = "Aria is thinking..."
        st.session_state.aria_animation_state = 'idle' # Ensure idle while thinking
        st.experimental_rerun() # Rerun to show "Aria is thinking..." immediately

# Display current spoken text (user input)
if "spoken_text" in st.session_state:
    st.markdown(f"<h3 class='header-text'>You Said:</h3>", unsafe_allow_html=True)
    st.text_area("Your Input", st.session_state.spoken_text, height=50, key="spoken_output_display", disabled=True)

# Display Aria's response and trigger speaking
if "aria_says" in st.session_state:
    st.markdown(f"<h3 class='header-text'>Aria Says:</h3>", unsafe_allow_html=True)
    st.text_area("Aria's Response", st.session_state.aria_says, height=150, key="aria_output_display", disabled=True)

    # If Aria just finished thinking, get the actual AI response and speak it
    if st.session_state.aria_says == "Aria is thinking...":
        # Introduce a 5-second delay before getting the AI response
        time.sleep(5) # This will pause the execution for 5 seconds
        ai_response_text = get_ai_response(st.session_state.spoken_text)
        speak_text_and_animate(ai_response_text)
        # Note: speak_text_and_animate handles st.experimental_rerun() internally


# --- Limitations and Next Steps ---
st.markdown("---")
st.markdown(
    """
    <h3 class='header-text'>Important Notes for Streamlit:</h3>
    <p>
    While this Streamlit app now includes voice output and a visual simulation,
    direct real-time 3D character animation (like in Three.js) and
    browser-native Web Speech API for voice input are not
    natively supported within Streamlit's core framework.
    </p>

    <h3 class='header-text'>Next Steps for Enhancing this Streamlit App:</h3>
    <ul>
        <li><b>Real 3D Visuals:</b> For a truly interactive 3D character, consider using a <a href="https://docs.streamlit.io/library/components/create" target="_blank">Streamlit Custom Component</a>
            that embeds Three.js or a similar JavaScript 3D library on the front-end. This is more complex but offers full 3D control.</li>
        <li><b>Better Visuals:</b> Replace the placeholder images for Aria with actual images or animated GIFs of a 3D animated girl
            in 'idle' and 'speaking' states.</li>
        <li><b>Voice Input:</b> Integrate a dedicated Speech-to-Text library (e.g., Google Cloud Speech-to-Text API, AssemblyAI)
            on the Python backend to enable voice commands in Streamlit.</li>
        <li><b>More Voice Control:</b> For more nuanced voice control (e.g., specific voices, speaking styles), explore
            other TTS services like Google Cloud Text-to-Speech, which offer more options than gTTS.</li>
        <li><b>Chat History Display:</b> Display the full conversation history for a better user experience.</li>
    </ul>
    """,
    unsafe_allow_html=True
