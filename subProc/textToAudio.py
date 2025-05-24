from openai import OpenAI

client = OpenAI()
def text_to_audio(text_input, output_file, model="tts-1", voice="alloy"):
    
    with client.audio.speech.with_streaming_response.create(
        model=model,
        voice=voice,
        input=text_input
    ) as response:
        response.stream_to_file(output_file)

    print(f"Audio saved to {output_file}")
