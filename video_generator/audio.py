import numpy as np
from moviepy import AudioFileClip, concatenate_audioclips, AudioClip
import os

class Audio:
    def __init__(self, voices_clips=[], audio_path="", pause_duration=1, audio_temp_name="temp.mp3", folder="temp"):
        self._output_path = folder+"/"+audio_temp_name
        self.audio_path = audio_path
        self.voices_clips = voices_clips

        self.voices_clips.insert(1, self._create_silence_audio_clip(pause_duration))
        print("Inserted silence clip")
        self._conconate_voices()
        self._save_audio()
        self._audio_clip = AudioFileClip(self._output_path)

    @property
    def audio_clip(self):
        return self._audio_clip

    @property
    def output_path(self):
        return self._output_path

    def _create_silence_audio_clip(self, duration: float, fps=30, nchannels: int = 1) -> AudioClip:
        make_frame_silence = lambda t: [0] * nchannels
        silence_clip = AudioClip(make_frame_silence, duration=duration, fps=fps)
        print(f"Silence clip created")
        return silence_clip

    def _conconate_voices(self):
        self.final_clip = concatenate_audioclips(self.voices_clips)
        print(f"Final audio clip was concantenated: {self._output_path}")

    def _save_audio(self):
        self.final_clip.write_audiofile(self._output_path, codec='mp3')
        self.final_clip.close()
        print(f"Saved final audio to: {self._output_path}")

    def delete(self):
        self._audio_clip.close()
        #os.remove(self._output_path)
        print(f"Deleted audio file: {self._output_path}")