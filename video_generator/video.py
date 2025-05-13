from moviepy import VideoFileClip, concatenate_videoclips, ImageClip, CompositeVideoClip
import os
import random
import time
import concurrent.futures
from functools import partial
import multiprocessing

from video_generator.label import generate_label_image

class Video:
    def __init__(self, video_output_path, audio=None, background_folder="assets/backgrounds/minecraft/parkour1/", length=10, parallel_processing=False, max_workers=4):
        self.video_output_path = video_output_path
        self.clips = []
        self.parallel_processing = parallel_processing
        self.max_workers = max_workers
        
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

    def _load_clip(self, file_path):
        try:
            return VideoFileClip(file_path)
        except Exception as e:
            print(f"Error loading clip {file_path}: {e}")
            return None

    def _get_clips(self):
        if self.parallel_processing:
            # Get list of potential clips first
            potential_clips = []
            for file in os.listdir(self.background_folder):
                if ".ds_store" not in file.lower():
                    potential_clips.append(os.path.join(self.background_folder, file))
            
            random.shuffle(potential_clips)  # Randomize the order
            
            # Load clips in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_clip = {executor.submit(self._load_clip, clip_path): clip_path 
                                 for clip_path in potential_clips[:10]}  # Start with first 10 clips
                
                for future in concurrent.futures.as_completed(future_to_clip):
                    clip_path = future_to_clip[future]
                    try:
                        clip = future.result()
                        if clip is not None:
                            if self._get_clips_duration() + clip.duration > self.length:
                                # Need to trim the clip
                                self.clips.append(clip.subclipped(0, self.length - self._get_clips_duration()))
                                break
                            else:
                                self.clips.append(clip)
                                
                            if self._get_clips_duration() >= self.length:
                                break
                    except Exception as e:
                        print(f"Error processing clip {clip_path}: {e}")
        else:
            # Original sequential method
            while (self._get_clips_duration() < self.length):
                clip = self._get_random_clip()
                print(clip.duration, self.length - self._get_clips_duration())
                if clip.duration > self.length - self._get_clips_duration():
                    self.clips.append(clip.subclipped(0, self.length - self._get_clips_duration()))
                else:
                    self.clips.append(clip)
                    
        print(f"Got clips for video with total duration {self._get_clips_duration()}")

    def _conconate_clips(self):
        # Use multiprocessing for faster concatenation if available
        if hasattr(concatenate_videoclips, "multiprocessing") and self.parallel_processing:
            self.background_video = concatenate_videoclips(self.clips, method="compose", 
                                                          multiprocessing=True, 
                                                          threads=self.max_workers)
        else:
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
        # Ensure the output directory exists
        output_dir = os.path.dirname(self.video_output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Create a dedicated temp dir for this specific operation
        temp_dir = os.path.abspath("temp/video_processing")
        os.makedirs(temp_dir, exist_ok=True)
        print(f"Using temp directory for video processing: {temp_dir}")
        
        # Use CPU count for optimal encoding performance
        cpu_count = multiprocessing.cpu_count()
        optimal_threads = min(cpu_count, 8)  # Use up to 8 threads or available CPUs
        
        # Optimize first-pass video encoding
        print(f"Starting initial video encoding with {optimal_threads} threads...")
        start_time = time.time()
        
        try:
            # Use optimized encoding settings for faster generation
            self.background_video.write_videofile(
                self.video_output_path, 
                audio_codec="aac",
                fps=30,
                threads=optimal_threads,  # Use multiple CPU cores for encoding
                logger="bar",
                temp_audiofile=os.path.join(temp_dir, "temp_audio.m4a"),
                remove_temp=True,
                preset="ultrafast",  # Use fastest preset
                ffmpeg_params=["-crf", "28"]  # Reduce quality for speed
            )
            encoding_time = time.time() - start_time
            print(f"First-pass video encoding completed in {encoding_time:.2f} seconds")
        except Exception as e:
            print(f"Error during first-pass encoding: {e}")
            # Use fallback method with safer settings
            print("Using fallback encoding method...")
            self.background_video.write_videofile(
                self.video_output_path, 
                audio_codec="aac",
                fps=30,
                threads=optimal_threads,
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
        length=3,
        parallel_processing=True,
        max_workers=4
    )
    video.add_label("label_1", "title", 1)
    video.save_video()