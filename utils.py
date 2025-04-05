import os
import azure.cognitiveservices.speech as speechsdk
import streamlit as st
import openai


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


def get_keywords_openai(text, model):
    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant that can pick out keywords from a transcription. As a comma separated string, output the relevant keywords (if any) given the transcript. You can only choose between 'cannot-talk', 'explain', 'food', 'pain', 'sleep'.",
                },
                {
                    "role": "user",
                    "content": f"Find the keywords in the text: {text}",
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


# Recognize from the microphone
def recognize_from_microphone():
    # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_config = speechsdk.SpeechConfig(
        subscription=os.environ.get("SPEECH_KEY"),
        region=os.environ.get("SPEECH_REGION"),
    )
    speech_config.speech_recognition_language = "en-US"

    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, audio_config=audio_config
    )

    print("Speak into your microphone.")
    speech_recognition_result = speech_recognizer.recognize_once_async().get()

    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(speech_recognition_result.text))
        return speech_recognition_result.text
    elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        print(
            "No speech could be recognized: {}".format(
                speech_recognition_result.no_match_details
            )
        )
    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_recognition_result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")
