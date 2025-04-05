import streamlit as st
import os
import tempfile
import openai
from elevenlabs import stream
from elevenlabs.client import ElevenLabs

# Set page configuration
st.set_page_config(page_title="Speech Processing Demo", layout="wide")

# Initialize session state for storing app state
if "processed_text" not in st.session_state:
    st.session_state.processed_text = ""
if "original_text" not in st.session_state:
    st.session_state.original_text = ""

# App title and description
st.title("Speech Processing Demo")
st.markdown(
    "Upload an audio file for speech-to-text, then process it and convert back to speech."
)

# Sidebar for API keys
with st.sidebar:
    st.header("API Configuration")
    elevenlabs_api_key = st.text_input(
        "ElevenLabs API Key", type="password", value=os.getenv("ELEVENLABS_API_KEY", "")
    )
    openai_api_key = st.text_input(
        "OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", "")
    )

    # Voice selection
    st.header("Voice Settings")
    voice_id = st.selectbox(
        "Select Voice",
        [
            "JBFqnCBsd6RMkjVDRZzb",
            "21m00Tcm4TlvDq8ikWAM",
            "AZnzlk1XvdvUeBnXmlld",
            "EXAVITQu4vr4xnSDxMaL",
        ],
        format_func=lambda x: {
            "JBFqnCBsd6RMkjVDRZzb": "Rachel (Female)",
            "21m00Tcm4TlvDq8ikWAM": "Adam (Male)",
            "AZnzlk1XvdvUeBnXmlld": "Nicole (Female)",
            "EXAVITQu4vr4xnSDxMaL": "Josh (Male)",
        }.get(x, x),
    )

    tts_model = st.selectbox(
        "Text-to-Speech Model",
        ["eleven_multilingual_v2", "eleven_monolingual_v1"],
        index=0,
    )

    stt_model = st.selectbox(
        "Speech-to-Text Model", ["scribe_v1", "scribe_v2"], index=0
    )

    # OpenAI model selection
    llm_model = st.selectbox("OpenAI Model", ["gpt-4o-mini"], index=0)


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
def speech_to_text(file_path, model_id, client):
    try:
        with open(file_path, "rb") as file_data:
            result = client.speech_to_text.convert(
                model_id=model_id,
                file=file_data,
            )
        return result
    except Exception as e:
        st.error(f"Speech-to-text error: {e}")
        return None


# Function to process text with OpenAI
def process_with_openai(text, model):
    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that cleans up transcribed speech. Remove filler words like 'um', 'uh', 'like', etc. Fix grammar issues. Just output the text as-is with no headings or styling.",
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
tab1, tab2 = st.tabs(["Upload & Process", "Results"])

with tab1:
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload audio file", type=["mp3", "wav", "m4a", "ogg"]
    )

    col1, col2 = st.columns(2)

    # Process button
    process_button = col1.button(
        "Process Audio", type="primary", disabled=uploaded_file is None
    )

    if process_button and uploaded_file is not None:
        with st.spinner("Processing audio..."):
            # Initialize clients
            eleven_client = initialize_clients()

            # Save uploaded file to temp file
            with tempfile.NamedTemporaryFile(
                delete=False, suffix="." + uploaded_file.name.split(".")[-1]
            ) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_filepath = tmp_file.name

            # Speech to text
            st.info("Converting speech to text...")
            transcription = speech_to_text(tmp_filepath, stt_model, eleven_client)

            if transcription:
                st.session_state.original_text = transcription

                # Process with OpenAI
                st.info("Processing text with AI...")
                processed_text = process_with_openai(transcription, llm_model)

                if processed_text:
                    st.session_state.processed_text = processed_text
                    st.success("Processing complete! Go to Results tab.")

            # Clean up temp file
            os.unlink(tmp_filepath)

with tab2:
    # Display original and processed text
    if st.session_state.original_text:
        st.subheader("Original Transcription")
        st.text_area("", st.session_state.original_text, height=150)

        st.subheader("Processed Text")
        st.text_area("", st.session_state.processed_text, height=150)

        # Text to speech section
        st.subheader("Text to Speech")
        col1, col2 = st.columns(2)

        option = col1.radio("Choose text to convert", ["Original", "Processed"])
        play_button = col2.button("Play Audio", type="primary")

        if play_button:
            with st.spinner("Converting text to speech..."):
                eleven_client = initialize_clients()
                text_to_convert = (
                    st.session_state.original_text
                    if option == "Original"
                    else st.session_state.processed_text
                )

                audio_stream = text_to_speech(
                    text_to_convert, voice_id, tts_model, eleven_client
                )
                if audio_stream:
                    # st.audio(audio_stream.content, format="audio/mp3")
                    stream(audio_stream)

# Footer
st.markdown("---")
st.caption("Speech Processing Demo using ElevenLabs and OpenAI")
