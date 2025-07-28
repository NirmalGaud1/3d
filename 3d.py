import streamlit as st
import google.generativeai as genai
import os
import io
from gtts import gTTS
import time
import SpeechRecognition as sr # Library for Speech-to-Text

# --- Configuration ---
try:
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
        /* Style for text areas */
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
    st.session_state.aria_animation_state = 'idle' # 'idle', 'listening', 'thinking', 'speaking'
if "spoken_text" not in st.session_state:
    st.session_state.spoken_text = ""
if "aria_says" not in st.session_state:
    st.session_state.aria_says = ""
if "last_command_time" not in st.session_state:
    st.session_state.last_command_time = time.time() # To manage the 5-second delay


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

    try:
        # gTTS default voice for English is typically female-sounding
        tts = gTTS(text=text, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)

        # Display and play audio
        st.audio(fp, format='audio/mp3', start_time=0)

    except Exception as e:
        st.error(f"Error generating Aria's voice: {e}")
        st.session_state.aria_says = "Sorry, I couldn't generate voice output."
    finally:
        # Revert to idle animation state after speaking, will update on next rerun
        st.session_state.aria_animation_state = 'idle'

def listen_for_command():
    """Listens to the microphone, converts speech to text, and processes the command."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.session_state.aria_animation_state = 'listening'
        st.session_state.spoken_text = "Aria is listening..."
        st.markdown(f"""
            <div class="aria-visual-container">
                <img src="{aria_listening_image_url}" class="aria-image">
            </div>
        """, unsafe_allow_html=True)
        st.write("Please speak now...")
        st.stop() # Stop the script until audio is heard and processed. This is crucial for microphone input in Streamlit.

        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=5) # Listen for up to 5 seconds
            st.session_state.spoken_text = "Processing your command..."
            st.session_state.aria_animation_state = 'thinking'
            st.experimental_rerun() # Rerun to update visual state to 'thinking' and show processing message

            # Introduce the 5-second delay here, after listening but before AI response
            time.sleep(5)

            # Use Google Web Speech API for recognition (free, online)
            command_text = r.recognize_google(audio)
            st.session_state.spoken_text = f"You said: {command_text}"

            # Get AI response
            ai_response_text = get_ai_response(command_text)

            # Speak the text and update animation state
            speak_text_and_animate(ai_response_text)

        except sr.WaitTimeoutError:
            st.session_state.spoken_text = "No speech detected. Please try again."
            st.session_state.aria_animation_state = 'idle'
            st.experimental_rerun()
        except sr.UnknownValueError:
            st.session_state.spoken_text = "Could not understand audio. Please speak more clearly."
            st.session_state.aria_animation_state = 'idle'
            st.experimental_rerun()
        except sr.RequestError as e:
            st.session_state.spoken_text = f"Speech service error; {e}. Please check your internet connection."
            st.session_state.aria_animation_state = 'idle'
            st.experimental_rerun()
        except Exception as e:
            st.session_state.spoken_text = f"An unexpected error occurred: {e}"
            st.session_state.aria_animation_state = 'idle'
            st.experimental_rerun()


# --- Display Aria's Visual (Simulated 3D Animated Girl) ---
# **IMPORTANT:** Replace these URLs with actual links to animated GIFs or video files
# of your 3D animated girl in idle, listening, and speaking states.
# You can find free animated GIFs on websites like GIPHY or create your own.
# Example: https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOWUzMDBhZWQ1YjZkMjZlZTBjYWI4Zjc4ZDgyNjI0ZGRlMjExYjNiNiZlcD12MV9pbnRlcm5hbF9naWZzX2dpZklkJmN0PWc/oBPOP4cgwV4C4/giphy.gif
aria_idle_image_url = "https://placehold.co/300x400/87CEEB/FFFFFF?text=Aria+Idle"
aria_listening_image_url = "https://placehold.co/300x400/FFD700/000000?text=Aria+Listening"
aria_thinking_image_url = "https://placehold.co/300x400/FFA07A/000000?text=Aria+Thinking"
aria_speaking_image_url = "https://placehold.co/300x400/98FB98/000000?text=Aria+Speaking"


# Determine which image to display based on Aria's current state
if st.session_state.aria_animation_state == 'listening':
    current_aria_image = aria_listening_image_url
elif st.session_state.aria_animation_state == 'thinking':
    current_aria_image = aria_thinking_image_url
elif st.session_state.aria_animation_state == 'speaking':
    current_aria_image = aria_speaking_image_url
else: # idle
    current_aria_image = aria_idle_image_url

st.markdown(f"""
    <div class="aria-visual-container">
        <img src="{current_aria_image}" class="aria-image">
    </div>
""", unsafe_allow_html=True)


# --- Voice Input Button ---
st.button("🎙️ Start Listening", on_click=listen_for_command)


# Display current spoken text (user input)
if st.session_state.spoken_text: # Check if it's not empty
    st.markdown(f"<h3 class='header-text'>You Said:</h3>", unsafe_allow_html=True)
    st.text_area("Your Input", st.session_state.spoken_text, height=50, key="spoken_output_display", disabled=True)

# Display Aria's response
if st.session_state.aria_says: # Check if it's not empty
    st.markdown(f"<h3 class='header-text'>Aria Says:</h3>", unsafe_allow_html=True)
    st.text_area("Aria's Response", st.session_state.aria_says, height=150, key="aria_output_display", disabled=True)


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
        <li><b>Provide Actual Animated Visuals:</b> Replace the placeholder `aria_idle_image_url`, `aria_listening_image_url`, `aria_thinking_image_url`, and `aria_speaking_image_url` with actual URLs to animated GIFs or short video files of your 3D animated girl.</li>
        <li><b>True 3D Visuals:</b> For a truly interactive 3D character (e.g., controlling a GLTF model), explore creating a Streamlit Custom Component. This is a more advanced topic but offers full 3D control directly within your Streamlit app.</li>
        <li><b>Chat History Display:</b> Display the full conversation history for a better user experience.</li>
        <li><b>More Voice Control:</b> For more nuanced voice control (e.g., specific voices, speaking styles), explore
            other TTS services like Google Cloud Text-to-Speech, which offer more options than gTTS.</li>
    </ul>
    """,
    unsafe_allow_html=True
)
