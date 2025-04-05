from elevenlabs import stream
from elevenlabs.client import ElevenLabs
import os

client = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY"),
)

# audio_stream = client.text_to_speech.convert_as_stream(
#     text="We are helping Aphasia patients regain their independence",
#     voice_id="JBFqnCBsd6RMkjVDRZzb",
#     model_id="eleven_multilingual_v2",
# )

# stream(audio_stream)


# speech to text

# text = client.speech_to_text.convert(
#     file=os.path.join("audio", "aphasia-1-speaker.mp3"),
#     model_id="scribe_v1",
# )
# print(text)

file_path = os.path.join("audio", "aphasia-1-speaker.mp3")
file_data = open(file_path, "rb")
result = client.speech_to_text.convert(
    model_id="scribe_v1",
    file=file_data,
)
print(result)
