from moviepy import VideoFileClip, concatenate_videoclips, ImageClip, CompositeVideoClip
import os
import random
import time

from video_generator.label import generate_label_image

class Video:
    def __init__(self, video_output_path, audio=None, background_folder="assets/backgrounds/minecraft/parkour1/", length=10):
        self.video_output_path = video_output_path
        self.clips = []
        if not audio.duration:
            self.length = length
        else:
            self.length = audio.duration
        print(f"length: {self.length}")
        print(f"audio duration: {audio.duration}")
        self.background_folder = background_folder
        self.audio = audio

        self._get_clips()
        self._conconate_clips()
        self._add_audio()

    @property
    def duration(self):
        return self.background_video.duration

    @property
    def video(self):
        return self.background_video

    def _get_random_clip(self):
        while True:
            clip = random.choice(os.listdir(self.background_folder))
            if clip not in self.clips and ".ds_store" not in clip.lower():
                print(f"Got clip: {clip}")
                return VideoFileClip(os.path.join(self.background_folder, clip))

    def _get_clips_duration(self):
        return sum([clip.duration for clip in self.clips])

    def _get_clips(self):
        while (self._get_clips_duration() < self.length):
            clip = self._get_random_clip()
            print(clip.duration, self.length - self._get_clips_duration())
            if clip.duration > self.length - self._get_clips_duration():
                self.clips.append(clip.subclipped(0, self.length - self._get_clips_duration()))
            else:
                self.clips.append(clip)
        print(f"Got clips for video with total duration {self._get_clips_duration()}")

    def _conconate_clips(self):
        self.background_video = concatenate_videoclips(self.clips)
        print(f"Concatenated clips for video with total duration {self.background_video.duration}")

    def _add_audio(self):
        self.background_video.audio = self.audio
        print("Added audio to video")

    def add_label(self, label_name, title, duration):
        generate_label_image(label_name, title)

        self.label_image_clip = ImageClip(
            f"labels/outputs/{label_name}.png", 
            duration=duration
        ).with_position("center").resized(0.8)

        self.background_video = CompositeVideoClip([self.background_video, self.label_image_clip])
        
        print("Added label to video")

    def save_video(self):
        self.background_video.write_videofile(
            self.video_output_path, 
            audio_codec="aac",
            fps=30,
            threads=4,
            logger="bar"
        )
        print(f"Saved video to {self.video_output_path}")

    def close_clips(self):
        self.label_image_clip.close()
        for clip in self.clips:
            clip.close()
        self.background_video.close()
        print("All used clips closed")


if __name__ == "__main__":
    video = Video(
        video_output_path="video.mp4", 
        background_folder="assets/backgrounds/minecraft/parkour1/",
        length=3
    )
    video.add_label("label_1", "title", 1)
    video.save_video()