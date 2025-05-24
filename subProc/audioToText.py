from openai import OpenAI

def audio_to_text(audio_file_path):
    
    client = OpenAI()
    with open(audio_file_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    
    return transcription.text
