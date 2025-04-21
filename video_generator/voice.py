import os
import random
from elevenlabs.client import ElevenLabs
from elevenlabs import play

from config import ELEVENLABS_API_KEY, VOICES

from moviepy import AudioFileClip 

client = ElevenLabs(
  api_key=ELEVENLABS_API_KEY,
)

class Voice:
    def __init__(self, voice_name, text, file_name, save_folder="temp"):
        self._output_path = save_folder+"/"+file_name
        self.save_folder = save_folder  
        self.files_saved = []
        if voice_name == "random":
            self._get_random_voice()
        else:
            self.voice_name = voice_name
        self._generate_voice(text, file_name)
        self._audio_clip = AudioFileClip(self._output_path)

    @property
    def duration(self):
        return self._audio_clip.duration

    @property
    def output_path(self):
        return self._output_path

    @property
    def audio_clip(self):
        return self._audio_clip

    def _get_random_voice(self):
        self.voice_name = random.choice(list(VOICES.keys()))
        print(f"Selected voice for {self._output_path}: {self.voice_name}")

    def _generate_voice(self, text, file_name):
        response = client.text_to_speech.convert(
            text=text,
            voice_id=VOICES[self.voice_name],
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
        )
        self._save_audio(response, self._output_path)

    def _save_audio(self, response, output_path):
        with open(output_path, "wb") as f:
            for chunk in response:
                if chunk:
                    f.write(chunk)
        self.files_saved.append(output_path)
        print(f"Voice generated and saved to {self._output_path}")

    def delete(self):
        self._audio_clip.close()
        #os.remove(self._output_path)
        print(f"Deleted audio file: {self._output_path}")

if __name__ == "__main__":
    voice = Voice("default", "output_audio")
    voice.generate_voice("The first move is what sets everything in motion.")