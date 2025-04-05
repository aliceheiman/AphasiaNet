import streamlit as st
import os
import threading
import time
import wave
import struct
from pvrecorder import PvRecorder

# Set page config
st.set_page_config(page_title="Real-time Audio Recorder", layout="wide")

# Initialize session state
if "is_recording" not in st.session_state:
    st.session_state["is_recording"] = False
if "audio_frames" not in st.session_state:
    st.session_state["audio_frames"] = []
if "thread" not in st.session_state:
    st.session_state["thread"] = None
if "recording_status" not in st.session_state:
    st.session_state["recording_status"] = ""

# App title and description
st.title("Real-time Audio Recorder")
st.markdown(
    "Start and stop live recording from your microphone. Audio will be saved as a WAV file."
)


# Recording logic
def record_audio():
    recorder = PvRecorder(device_index=-1, frame_length=512)
    st.session_state["audio_frames"] = []

    try:
        recorder.start()
        while st.session_state["is_recording"]:
            frame = recorder.read()
            st.session_state["audio_frames"].extend(frame)
        recorder.stop()
    finally:
        recorder.delete()


def save_audio():
    os.makedirs("audio", exist_ok=True)
    audio = st.session_state["audio_frames"]
    with wave.open("audio/test.wav", "w") as f:
        f.setparams((1, 2, 16000, 0, "NONE", "NONE"))
        f.writeframes(struct.pack("h" * len(audio), *audio))
    st.session_state["recording_status"] = "Audio saved as `audio/test.wav`."


# Layout: Two columns for start/stop buttons
col1, col2 = st.columns(2)

with col1:
    if st.button("Start Recording", disabled=st.session_state["is_recording"]):
        st.session_state["is_recording"] = True
        st.session_state["recording_status"] = "Recording in progress..."
        st.session_state["thread"] = threading.Thread(target=record_audio)
        st.session_state["thread"].start()

with col2:
    if st.button("Stop Recording", disabled=not st.session_state["is_recording"]):
        st.session_state["is_recording"] = False
        st.session_state["thread"].join()
        save_audio()

# Feedback / status
if st.session_state["recording_status"]:
    st.info(st.session_state["recording_status"])

# Optionally play audio (if available)
if os.path.exists("audio/test.wav"):
    st.audio("audio/test.wav", format="audio/wav")

# Footer
st.markdown("---")
st.caption("Audio Recorder Demo using PvRecorder and Streamlit")
