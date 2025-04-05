import streamlit as st
import azure.cognitiveservices.speech as speechsdk
import os
import tempfile
import openai
from elevenlabs import stream
from elevenlabs.client import ElevenLabs
import utils

# Setup clients
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY", "")
openai_api_key = os.getenv("OPENAI_API_KEY", "")
eleven_client = ElevenLabs(api_key=elevenlabs_api_key)
openai.api_key = openai_api_key

llm_model = "gpt-4o-mini"
voice_id = "JBFqnCBsd6RMkjVDRZzb"
tts_model = "eleven_multilingual_v2"


st.title("Speech Processing Demo")

transcribe = st.button("Start Transcribing")
if transcribe:
    with st.spinner("Processing speech..."):
        text = utils.recognize_from_microphone()
        st.session_state.original_text = text

        st.info("Processing text with AI...")
        processed_text = utils.process_with_openai(text, llm_model)
        st.session_state.processed_text = processed_text
        st.success("Processing complete!")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Original Transcription")
        st.text_area("", st.session_state.original_text, height=200)
    with col2:
        st.subheader("Processed Transcription")
        st.text_area("", st.session_state.processed_text, height=200)

    option = col1.radio("Choose text to convert", ["Original", "Processed"])
    play_button = col2.button("Play Audio", type="primary")

    if play_button:
        with st.spinner("Converting text to speech..."):
            text_to_convert = (
                st.session_state.original_text
                if option == "Original"
                else st.session_state.processed_text
            )

            audio_stream = utils.text_to_speech(
                text_to_convert, voice_id, tts_model, eleven_client
            )
            if audio_stream:
                # st.audio(audio_stream.content, format="audio/mp3")
                stream(audio_stream)
