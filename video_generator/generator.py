from video_generator.video import Video
from video_generator.voice import Voice
from video_generator.audio import Audio
from video_generator.captions import Captions

import os
import tempfile
import glob
import concurrent.futures
from functools import partial
import time

# Create temp directory if it doesn't exist
temp_dir = os.path.abspath("temp")
os.makedirs(temp_dir, exist_ok=True)
print(f"Setting MOVIEPY_TEMP_DIR to: {temp_dir}")

# Set environment variable for MoviePy temp directory
os.environ['MOVIEPY_TEMP_DIR'] = temp_dir
os.environ['TMPDIR'] = temp_dir

# Print current working directory for debugging
print(f"Current working directory: {os.getcwd()}")

def generate_video(main_text, 
        title_text, 
        video_output_path, 
        background_clips_folder="assets/backgrounds/minecraft/parkour1/", 
        temp_voices_folder="temp/voices", 
        temp_audio_folder="temp/audio",
        capitalize=False,
        audio_temp_name="temp.mp3",
        pause_duration=1,
        background_audio_path="",
        voice_name="random",
        voice_title_output_name="title.mp3",
        voice_text_output_name="text.mp3",
        label_name="label_1",
        font_path="assets/fonts/roboto.ttf",
        font_size=36,
        color='white',
        position=('center'),
        caption_box_width=864,
        video_name = "video",
        max_workers=4,  # Number of parallel workers
        fast_mode=True  # Enable fast mode for maximum speed
    ):
    print("-"*30, video_name, "-"*30)
    print("Generating video with title: ", title_text)
    
    # Ensure directories exist
    os.makedirs(temp_voices_folder, exist_ok=True)
    os.makedirs(temp_audio_folder, exist_ok=True)
    os.makedirs(os.path.dirname(video_output_path) or "output", exist_ok=True)
    
    # Ensure video_output_path starts with output/ directory
    if not video_output_path.startswith("output/") and not os.path.dirname(video_output_path):
        video_output_path = os.path.join("output", video_output_path)
        print(f"Updated video output path to: {video_output_path}")
    
    # Keep track of all temp files created
    temp_files_to_clean = []
    
    # Generate voices in parallel
    print("Generating voices in parallel...")
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit voice generation tasks
        title_voice_future = executor.submit(
            Voice, voice_name, title_text, voice_title_output_name, temp_voices_folder
        )
        text_voice_future = executor.submit(
            Voice, voice_name, main_text, voice_text_output_name, temp_voices_folder
        )
        
        # Wait for completion and get results
        title_voice = title_voice_future.result()
        text_voice = text_voice_future.result()
    print(f"Voice generation completed in {time.time() - start_time:.2f} seconds")
    
    audio = Audio(
        voices_clips=[title_voice.audio_clip, text_voice.audio_clip],
        audio_path=background_audio_path,
        pause_duration=pause_duration, 
        audio_temp_name=audio_temp_name, 
        folder=temp_audio_folder
    )

    # Create a full path for the intermediate file with proper directory
    without_captions_path = video_output_path.split(".")[0]+"_without_captions.mp4"
    if not os.path.dirname(without_captions_path):
        without_captions_path = os.path.join("output", without_captions_path)
    temp_files_to_clean.append(without_captions_path)
    
    # Optimize video generation - preload clips in parallel
    print("Preparing video clips...")
    video = Video(
        video_output_path=without_captions_path, 
        background_folder=background_clips_folder, 
        audio=audio.audio_clip,
        parallel_processing=True,
        max_workers=max_workers
    )

    video.add_label(label_name, 
        title_text, 
        title_voice.duration
    )
    
    # Start timer for video generation
    video_start_time = time.time()
    video.save_video()
    print(f"Initial video generation took {time.time() - video_start_time:.2f} seconds")

    video.close_clips()
    title_voice.delete()
    text_voice.delete()
    audio.delete()

    # Create captions with optimized processing
    print("Generating captions...")
    captions_start_time = time.time()
    video_with_captions = Captions(without_captions_path, 
                                audio.output_path, 
                                video_output_path, 
                                capitalize=capitalize,
                                parallel_processing=True,
                                max_workers=max_workers
    )

    video_with_captions.clear_title_captions()
    video_with_captions.add_captions_to_video(
                font_path=font_path,
                font_size=font_size,
                color=color,
                position=position,
                caption_box_width=caption_box_width
            )

    video_with_captions.save()
    print(f"Caption generation took {time.time() - captions_start_time:.2f} seconds")
    video_with_captions.close()
    
    # Clean up all temporary files
    cleanup_files = [
        without_captions_path,
        os.path.join(temp_voices_folder, voice_title_output_name),
        os.path.join(temp_voices_folder, voice_text_output_name),
        os.path.join(temp_audio_folder, audio_temp_name)
    ]
    
    print("Cleaning up temporary files...")
    for temp_file in cleanup_files:
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
                print(f"Removed {temp_file}")
        except Exception as e:
            print(f"Error removing {temp_file}: {e}")

    # Additional cleanup for any temp files that match our pattern in the current directory
    for pattern in ["*TEMP_MPY*", "*temp*", "*_without_captions*"]:
        for file in glob.glob(pattern):
            if os.path.isfile(file) and not file.startswith(("output/", "temp/", "assets/")):
                try:
                    os.remove(file)
                    print(f"Removed temporary file: {file}")
                except Exception as e:
                    print(f"Error removing {file}: {e}")

    total_time = time.time() - start_time
    print("Cleared temp files")
    print(f"Final video saved to: {video_output_path}")
    print(f"Total video generation time: {total_time:.2f} seconds")
    print("-"*30, video_name, "-"*30)
    
    return video_output_path

if __name__ == "__main__":
    generate_video(
        main_text="The Craigslist Ad That Shook Me For The Rest Of My Life...",
        title_text="The Craigslist Ad That Shook Me For The Rest Of My Life...",
        video_output_path="output/something.mp4",
        background_clips_folder="assets/backgrounds/minecraft/parkour1/",
        temp_voices_folder="temp/voices", 
        temp_audio_folder="temp/audio",
        capitalize=False,
        audio_temp_name="temp.mp3",
        pause_duration=1,
        background_audio_path="",
        voice_name="random",
        voice_title_output_name="title.mp3",
        voice_text_output_name="text.mp3",
        label_name="label_1",
        font_path="assets/fonts/roboto.ttf",
        font_size=36,
        color='white',
        position=('center'),
        caption_box_width=864
    )