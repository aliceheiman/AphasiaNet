import streamlit as st
import os
import tempfile
import openai
from elevenlabs import stream
from elevenlabs.client import ElevenLabs

# Set page configuration
st.set_page_config(page_title="Speech Processing Demo", layout="wide")


# Setup clients
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY", "")
openai_api_key = os.getenv("OPENAI_API_KEY", "")
eleven_client = ElevenLabs(api_key=elevenlabs_api_key)
openai.api_key = openai_api_key

# Use fixed models to avoid reloading
llm_model = "gpt-4o-mini"
voice_id = "JBFqnCBsd6RMkjVDRZzb"
tts_model = "eleven_multilingual_v2"
stt_model = "scribe_v1"

# App title and description
st.title("Speech Processing Demo")
st.markdown(
    "Upload an audio file for speech-to-text, then process it and convert back to speech."
)


# Function to initialize API clients
def initialize_clients():
    # ElevenLabs client
    if elevenlabs_api_key:
        eleven_client = ElevenLabs(api_key=elevenlabs_api_key)
    else:
        st.error("Please provide your ElevenLabs API key")
        st.stop()

    # OpenAI client
    if openai_api_key:
        openai.api_key = openai_api_key
    else:
        st.error("Please provide your OpenAI API key")
        st.stop()

    return eleven_client


# Function for text-to-speech
def text_to_speech(text, voice_id, model_id, client):
    try:
        audio_stream = client.text_to_speech.convert_as_stream(
            text=text,
            voice_id=voice_id,
            model_id=model_id,
        )
        return audio_stream
    except Exception as e:
        st.error(f"Text-to-speech error: {e}")
        return None


# Function for speech-to-text
def speech_to_text(file_data, model_id, client):
    try:
        result = client.speech_to_text.convert(
            model_id=model_id,
            file=file_data,
        )
        return result
    except Exception as e:
        st.error(f"Speech-to-text error: {e}")
        return None


# Function to process text with OpenAI
def process_with_openai(text, model, fluent=False):
    if not fluent:
        prompt = "You are a helpful assistant that cleans up transcribed speech. Remove filler words like 'um', 'uh', 'like', etc. Fix grammar issues. Just output the text as-is with no headings or styling."
    else:
        prompt = """
        I'll give you some conversations or monologue from aphasia patients. For each piece of text, do the following:
        Check if there's more than one person talking. If so, only keep the words of aphasia patients.
        Determine whether it's Broca's aphasia or Wernicke's aphasia:
        For Broca's aphasia, make the words into grammarly correct, coherent, concise sentences that fully covers what they’re trying to say.
        For Wernicke's aphasia, guess what is the actual meaning of the patient, and turn that into logical, meaningful sentences that others could understand.
        Generate the output with only the converted text and nothing else.    
        """

    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": prompt,
                },
                {
                    "role": "user",
                    "content": f"Clean up and summarize this transcribed speech: {text}",
                },
            ],
            temperature=0.3,
            max_tokens=1024,
        )

        # Extract the content from the response
        cleaned_text = response.choices[0].message.content
        return cleaned_text
    except Exception as e:
        st.error(f"OpenAI API error: {e}")
        return None


# Main app layout
tab1, tab2 = st.tabs(["Demo", ""])

with tab1:
    st.video("https://www.youtube.com/watch?v=JWC-cVQmEmY&ab_channel=tactustherapy")

    # File uploader
    # uploaded_file = st.file_uploader("Audio file", type=["mp3", "wav", "m4a", "ogg"])

    col1, col2 = st.columns(2)

    # Process button
    fluent_option = st.selectbox("Fluent?", options=["Not Fluent", "Fluent"])
    process_button = col1.button("Process Audio", type="primary")

    if process_button:
        with st.spinner("Processing audio..."):
            # Initialize clients
            eleven_client = initialize_clients()

            # Speech to text
            st.info("Converting speech to text...")

            file_data = open("audio/aphasia-1-speaker.mp3", "rb")
            transcription = speech_to_text(file_data, stt_model, eleven_client)

            if transcription:
                st.session_state["original_text"] = transcription

                # Process with OpenAI
                st.info("Processing text with AI...")
                fluent_bool = fluent_option == "Fluent"
                print("Using", fluent_bool)
                processed_text = process_with_openai(
                    transcription, llm_model, fluent_bool
                )

                st.subheader("Original Transcription")
                st.text_area("", st.session_state["original_text"], height=150)

                st.subheader("Processed Text")
                st.text_area("", processed_text, height=150)

                with st.spinner("Converting text to speech..."):
                    eleven_client = initialize_clients()
                    text_to_convert = processed_text

                    audio_stream = text_to_speech(
                        text_to_convert, voice_id, tts_model, eleven_client
                    )
                    if audio_stream:
                        # st.audio(audio_stream.content, format="audio/mp3")
                        stream(audio_stream)


# Footer
st.markdown("---")
st.caption("Speech Processing Demo using ElevenLabs and OpenAI")
