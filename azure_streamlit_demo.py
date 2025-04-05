import streamlit as st
import azure.cognitiveservices.speech as speechsdk
import os
import tempfile
import openai
from elevenlabs import stream
from elevenlabs.client import ElevenLabs
import utils

# Initialize session state for persistent data
if "original_text" not in st.session_state:
    st.session_state.original_text = ""
if "processed_text" not in st.session_state:
    st.session_state.processed_text = ""
if "option" not in st.session_state:
    st.session_state.option = "Original"
if "show_results" not in st.session_state:
    st.session_state.show_results = False

# Setup clients
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY", "")
openai_api_key = os.getenv("OPENAI_API_KEY", "")
eleven_client = ElevenLabs(api_key=elevenlabs_api_key)
openai.api_key = openai_api_key

# Use fixed models to avoid reloading
llm_model = "gpt-4o-mini"
voice_id = "JBFqnCBsd6RMkjVDRZzb"
tts_model = "eleven_multilingual_v2"


# Functions to handle state changes without page reload
def update_option(value):
    st.session_state.option = value


def start_transcription():
    with st.spinner("Processing speech..."):
        text = utils.recognize_from_microphone()
        if text:
            st.session_state.original_text = text

            st.info("Processing text with AI...")
            processed_text = utils.process_with_openai(text, llm_model)
            keywords = utils.get_keywords_openai(text, llm_model)
            st.session_state.processed_text = processed_text
            st.session_state.show_results = True
            st.success("Processing complete!")
            st.text(f"Keywords: {keywords}")
            if keywords != "":
                for k in keywords.split(","):
                    st.image(f"icons/{k}.png")

        else:
            st.error("No speech detected or error in speech recognition.")


def play_audio():
    with st.spinner("Converting text to speech..."):
        text_to_convert = st.session_state.processed_text

        audio_stream = utils.text_to_speech(
            text_to_convert, voice_id, tts_model, eleven_client
        )
        if audio_stream:
            # Return the audio stream to be played
            return audio_stream
    return None


# App title
st.title("Speech Processing Demo")

# Create container for the transcribe button
transcribe_container = st.container()
with transcribe_container:
    # Use on_click to prevent page reload
    transcribe = st.button("Start Transcribing", on_click=start_transcription)

# Only show results if transcription has been done
if st.session_state.show_results:
    results_container = st.container()
    with results_container:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Original Transcription")
            st.text_area(
                "", st.session_state.original_text, height=200, key="original_text_area"
            )

        with col2:
            st.subheader("Processed Transcription")
            st.text_area(
                "",
                st.session_state.processed_text,
                height=200,
                key="processed_text_area",
            )
    audio_stream = play_audio()
    stream(audio_stream)

    # options_container = st.container()
    # with options_container:
    #     col1, col2 = st.columns(2)

    #     # Use radio with on_change callback
    #     option = col1.radio(
    #         "Choose text to convert",
    #         ["Original", "Processed"],
    #         index=0 if st.session_state.option == "Original" else 1,
    #         key="text_option",
    #         on_change=update_option,
    #         args=(st.session_state.option,),
    #     )

    #     # Store the selection directly to prevent reload issues
    #     st.session_state.option = option

    #     # Play audio button with callback
    #     if col2.button("Play Audio", type="primary", key="play_button"):
    #         audio_stream = play_audio()
    #         if audio_stream:
    #             # For streaming via speakers
    #             stream(audio_stream)
