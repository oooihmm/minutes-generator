import os
import openai
from dotenv import load_dotenv


class MinuteGenerator:
    def __init__(self):
        load_dotenv()
        self._api_key = os.getenv("OPENAI_API_KEY", "")

    def generate_minute(self, file_name):
        openai.api_key = self._api_key

        try:
            audio_file = open(file_name, "rb")
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
            text = transcript['text']
            return text
        except:
            return False

    def summary_minute(self, text):
        openai.api_key = self._api_key

        try:
            completion = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo", 
            messages = [{"role": "user", "content": "Summarize the following sentence in five lines with only the key points." + text}]
            )
            summary = completion["choices"][0]["message"]["content"]
            return summary
        except:
            return False
