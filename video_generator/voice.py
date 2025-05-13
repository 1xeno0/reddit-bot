import os
import random
import time
from elevenlabs.client import ElevenLabs
from elevenlabs import play

from config import ELEVENLABS_API_KEY, VOICES

from moviepy import AudioFileClip 

client = ElevenLabs(
  api_key=ELEVENLABS_API_KEY,
)

# Cache directory for storing generated voices to avoid regenerating the same ones
VOICE_CACHE_DIR = "temp/voice_cache"
os.makedirs(VOICE_CACHE_DIR, exist_ok=True)

class Voice:
    def __init__(self, voice_name, text, file_name, save_folder="temp"):
        self._output_path = os.path.join(save_folder, file_name)
        self.save_folder = save_folder  
        self.files_saved = []
        
        # Use random voice if specified
        if voice_name == "random":
            self._get_random_voice()
        else:
            self.voice_name = voice_name
            
        # Generate a unique cache key based on text content and voice
        self.cache_key = f"{self.voice_name}_{hash(text)}"
        self.cache_path = os.path.join(VOICE_CACHE_DIR, f"{self.cache_key}.mp3")
        
        # Check cache first
        if os.path.exists(self.cache_path):
            print(f"Using cached voice audio: {self.cache_path}")
            # Copy from cache to output path
            self._copy_from_cache()
        else:
            # Generate new audio if not cached
            print(f"Generating new voice audio for {file_name}")
            self._generate_voice(text, file_name)
            # Save to cache for future use
            self._save_to_cache()
            
        # Load the audio clip
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
        start_time = time.time()
        response = client.text_to_speech.convert(
            text=text,
            voice_id=VOICES[self.voice_name],
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
        )
        self._save_audio(response, self._output_path)
        print(f"Voice generation took {time.time() - start_time:.2f} seconds")

    def _save_audio(self, response, output_path):
        with open(output_path, "wb") as f:
            for chunk in response:
                if chunk:
                    f.write(chunk)
        self.files_saved.append(output_path)
        print(f"Voice generated and saved to {self._output_path}")
        
    def _copy_from_cache(self):
        """Copy the cached audio file to the output path"""
        import shutil
        os.makedirs(os.path.dirname(self._output_path), exist_ok=True)
        shutil.copy2(self.cache_path, self._output_path)
        self.files_saved.append(self._output_path)
        print(f"Copied cached voice from {self.cache_path} to {self._output_path}")
        
    def _save_to_cache(self):
        """Save the generated audio to the cache directory"""
        import shutil
        shutil.copy2(self._output_path, self.cache_path)
        print(f"Saved voice to cache: {self.cache_path}")

    def delete(self):
        self._audio_clip.close()
        #os.remove(self._output_path)
        print(f"Deleted audio file: {self._output_path}")

if __name__ == "__main__":
    voice = Voice("default", "The first move is what sets everything in motion.", "output_audio.mp3")
    print(f"Duration: {voice.duration} seconds")
    voice.delete()