from video_generator.generator import generate_video as generate_video_as_function
from reddit_scraper import RedditScraper

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

import json
import os
import glob
import shutil
import re

class Config:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = self._get_config()

    def _get_config(self):
        with open(self.config_path, 'r') as f:
            return json.load(f)

    def save_config(self, config_path, config):
        with open(config_path, 'w') as f:
            json.dump(config, f)
        self.config = self._get_config()

    def update_config_by_key(self, key, value):
        self.config[key] = value
        self.save_config(self.config_path, self.config)

    def delete_config(self, config_path):
        os.remove(config_path)

class VideoConfig(Config):
    def __init__(self, config_path):
        super().__init__(config_path)

    def update_config(self, main_text="The Craigslist Ad That Shook Me For The Rest Of My Life...", 
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
    ):
        config = {
            "main_text": main_text,
            "title_text": title_text,
            "video_output_path": video_output_path,
            "background_clips_folder": background_clips_folder,
            "temp_voices_folder": temp_voices_folder, 
            "temp_audio_folder": temp_audio_folder,
            "capitalize": capitalize,
            "audio_temp_name": audio_temp_name,
            "pause_duration": pause_duration,
            "background_audio_path": background_audio_path,
            "voice_name": voice_name,
            "voice_title_output_name": voice_title_output_name,
            "voice_text_output_name": voice_text_output_name,
            "label_name": label_name,
            "font_path": font_path,
            "font_size": font_size,
            "color": color,
            "position": position,
            "caption_box_width": caption_box_width
        }

        self.save_config(self.config_path, config)

class StoryConfig(Config):
    def __init__(self, config_path):
        super().__init__(config_path)

    def update_config(self, 
        title="Breaking up with someone because of lifestyle differences?",
        url="https://reddit.com/r/Advice/comments/1jnqrla/breaking_up_with_someone_because_of_lifestyle/",
        subreddit="Advice",
        timestamp="2025-03-31T02:22:43",
        score="36",
        author="Electronic_Lime_z459",
        num_comments="33",
        content="I've been seeing a guy for a few months, someone who I've had a huge crush on from afar for the last few years. I was very happy that we finally connected, but now, I see that we are so not compatible. \n\nI have trouble with voicing my feelings... I know it's valid to stop seeing someone for any reason at all, but I'm not sure how to word *why* I want us to stop seeing each other. \n\nFor background, my siblings and I are breaking the generational curse of drugs and alcohol in our family. We all have very good jobs, keep our noses clean, and are focused. Addiction is heavy in our family... from our father, his siblings, and some of our cousins. \n\n1. He spends every night at the bar. \n2. He works a job that he he makes very little at, but doesn't try to find anything better... Even though in our area it wouldn't be difficult. \n3. Does/buys hard drugs on \"special occasions\", but then will complain about how little he makes at job. \n\nThe reason that really did it for me was telling me that I'm \"blessed\" because things fall into place for me. I work 40+ hours at my company to get recognition, I consciously make good decisions, and I have goals with milestones I try to reach. \n\nI don't want to insult him, but do want to make it clear why I don't want to see each other any longer.  ",
        scrape_date="2025-03-31T15:44:32.352779"
    ):
        config = {
            "title": title,
            "url": url,
            "subreddit": subreddit,
            "timestamp": timestamp,
            "score": score,
            "author": author,
            "num_comments": num_comments,
            "content": content,
            "scrape_date": scrape_date
        }

        self.save_config(self.config_path, config)

app = Flask(__name__)
CORS(app)
reddit = RedditScraper("reddit_config.json")

@app.route('/get_stories', methods=['GET'])
def get_stories():
    stories = []
    for file in os.listdir("story_configs"):
        try:
            with open(os.path.join("story_configs", file), "r", encoding="utf-8") as f:
                story = json.load(f)
                stories.append(
                    {
                        "filename": file,
                        "config": story
                    }
                )
        except (UnicodeDecodeError, json.JSONDecodeError):
            # Skip corrupted files
            continue
    return jsonify(stories)

@app.route('/get_story/<story_filename>', methods=['GET'])
def get_story(story_filename):
    with open(os.path.join("story_configs", story_filename), "r") as f:
        story = json.load(f)
        return jsonify(story)
    return jsonify({"error": "Story not found"})

@app.route('/update_story/<story_filename>', methods=['POST'])
def update_story(story_filename):
    data = request.json
    story_config = StoryConfig(os.path.join("story_configs", story_filename))
    story_config.update_config(
        title=data["title"], 
        url=data["url"], 
        subreddit=data["subreddit"], 
        timestamp=data["timestamp"], 
        score=data["score"], 
        author=data["author"], 
        num_comments=data["num_comments"], 
        content=data["content"], 
        scrape_date=data["scrape_date"]
    )
    return jsonify({"message": "Story updated successfully"})

@app.route('/delete_story/<story_filename>', methods=['DELETE'])
def delete_story(story_filename):
    os.remove(os.path.join("story_configs", story_filename))
    return jsonify({"message": "Story deleted successfully"})

@app.route('/get_video_configs', methods=['GET'])
def get_video_configs():
    video_configs = []
    for file in os.listdir("video_configs"):
        with open(os.path.join("video_configs", file), "r") as f:
            video_config = json.load(f)
            video_configs.append({
                "filename": file,
                "config": video_config
            })
    return jsonify(video_configs)

@app.route('/get_video_config/<video_config_filename>', methods=['GET'])
def get_video_config(video_config_filename):
    with open(os.path.join("video_configs", video_config_filename), "r") as f:
        video_config = json.load(f)
        return jsonify(video_config)
    return jsonify({"error": "Video config not found"})

@app.route('/update_video_config/<video_config_filename>', methods=['POST'])
def update_video_config(video_config_filename):
    data = request.json
    video_config = VideoConfig(os.path.join("video_configs", video_config_filename))
    video_config.update_config(
        main_text=data["main_text"], 
        title_text=data["title_text"], 
        video_output_path="output/" + data["video_output_path"] if "output/" not in data["video_output_path"] else data["video_output_path"], 
        background_clips_folder=data["background_clips_folder"], 
        temp_voices_folder=data["temp_voices_folder"], 
        temp_audio_folder=data["temp_audio_folder"], 
        capitalize=data["capitalize"], 
        audio_temp_name=data["audio_temp_name"], 
        pause_duration=data["pause_duration"], 
        background_audio_path=data["background_audio_path"], 
        voice_name=data["voice_name"], 
        voice_title_output_name=data["voice_title_output_name"], 
        voice_text_output_name=data["voice_text_output_name"], 
        label_name=data["label_name"], 
        font_path=data["font_path"], 
        font_size=data["font_size"], 
        color=data["color"], 
        position=data["position"], 
        caption_box_width=data["caption_box_width"]
    )
    return jsonify({"message": "Video config updated successfully"})

@app.route('/delete_video_config/<video_config_filename>', methods=['DELETE'])
def delete_video_config(video_config_filename):
    os.remove(os.path.join("video_configs", video_config_filename))
    return jsonify({"message": "Video config deleted successfully"})

@app.route('/get_video/<path:video_output_path>', methods=['GET'])
def get_video(video_output_path):
    app.logger.info(f"Requested video: {video_output_path}")
    if os.path.exists(video_output_path):
        return send_file(video_output_path, mimetype='video/mp4')
    else:
        app.logger.error(f"Video not found: {video_output_path}")
        return jsonify({"error": f"Video file not found: {video_output_path}"}), 404

def cleanup_temp_files():
    """Clean up temporary files that might be created in the main directory."""
    # Check for temp files in main directory and move them to temp folder
    temp_patterns = [
        "*TEMP_MPY*", "*temp*", "*_without_captions*", 
        "*.mpy", "*.m4a", "*_TEMP_*", "*.wav.tmp*",
        "*.wav", "*.mp3.tmp*", "*_*_*_*-*-*-"
    ]
    
    print("Cleaning up temporary files...")
    cleanup_dir = os.path.join("temp", "cleanup")
    os.makedirs(cleanup_dir, exist_ok=True)
    
    # Current working directory files that match patterns
    for pattern in temp_patterns:
        for file in glob.glob(pattern):
            try:
                if os.path.isfile(file) and not file.startswith(("output/", "temp/", "assets/")):
                    target_path = os.path.join(cleanup_dir, os.path.basename(file))
                    print(f"Moving temporary file {file} to {target_path}")
                    # If the file is in use, this might fail, so we try a copy+delete approach
                    try:
                        shutil.move(file, target_path)
                    except:
                        try:
                            shutil.copy2(file, target_path)
                            try:
                                os.remove(file)
                            except:
                                print(f"Couldn't delete {file}, will try again later")
                        except Exception as e:
                            print(f"Couldn't copy {file}: {e}")
            except Exception as e:
                print(f"Error handling {file}: {e}")
    
    print("Cleanup completed")

@app.route('/generate_video', methods=['POST'])
def generate_video():
    try:
        # Set up temp directory environment variable 
        # (must be set each time because Flask may create a new process)
        temp_dir = os.path.abspath("temp")
        os.makedirs(temp_dir, exist_ok=True)
        os.environ['MOVIEPY_TEMP_DIR'] = temp_dir
        os.environ['TMPDIR'] = temp_dir
        
        # First clean up any temp files from previous runs
        cleanup_temp_files()
        
        data = request.json
        story_filename = data["story_filename"]
        video_filename = data["video_filename"]
        
        # Get CPU count for optimal parallel processing
        import multiprocessing
        cpu_count = multiprocessing.cpu_count()
        max_workers = min(cpu_count, 8)  # Use up to 8 workers or available CPUs, whichever is less
        print(f"Using {max_workers} workers for parallel processing (from {cpu_count} available CPUs)")
        
        # Check if fast mode is requested
        fast_mode = data.get("fast_mode", True)  # Default to True for maximum speed
        print(f"Fast mode is {'enabled' if fast_mode else 'disabled'}")
        
        story_config = StoryConfig(os.path.join("story_configs", story_filename))
        video_config = VideoConfig(os.path.join("video_configs", video_filename))

        # Make sure output directory exists
        os.makedirs("output", exist_ok=True)
        
        output_filename = data["story_filename"].split(".")[0] + ".mp4"
        video_output_path = os.path.join("output", output_filename)
        
        video_config.update_config_by_key("main_text", story_config.config["content"])
        video_config.update_config_by_key("title_text", story_config.config["title"])
        video_config.update_config_by_key("video_output_path", video_output_path)

        # Start time for performance measurement
        import time
        start_time = time.time()
        
        generate_video_as_function(
            video_config.config["main_text"],
            video_config.config["title_text"],
            video_config.config["video_output_path"],
            video_config.config["background_clips_folder"],
            video_config.config["temp_voices_folder"],
            video_config.config["temp_audio_folder"],
            video_config.config["capitalize"],
            video_config.config["audio_temp_name"],
            video_config.config["pause_duration"],
            video_config.config["background_audio_path"],
            video_config.config["voice_name"],
            video_config.config["voice_title_output_name"],
            video_config.config["voice_text_output_name"],
            video_config.config["label_name"],
            video_config.config["font_path"],
            video_config.config["font_size"],
            video_config.config["color"],
            video_config.config["position"],
            video_config.config["caption_box_width"],
            max_workers=max_workers,  # Pass the optimal number of workers
            fast_mode=fast_mode       # Pass fast mode setting
        )
        
        # Calculate and log the time taken
        elapsed_time = time.time() - start_time
        print(f"Video generation completed in {elapsed_time:.2f} seconds")
        
        # Clean up again after generation
        cleanup_temp_files()

        return jsonify({
            "message": "Video generated successfully", 
            "video_output_path": video_config.config["video_output_path"],
            "generation_time": f"{elapsed_time:.2f} seconds"
        })
    except Exception as e:
        # Clean up on error too
        cleanup_temp_files()
        app.logger.error(f"Error generating video: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/get_all_videos', methods=['GET'])
def get_all_videos():
    videos = []
    for file in os.listdir("output"):
        videos.append("output/" + file)
    return jsonify(videos)

@app.route('/get_new_stories', methods=['POST'])
def get_new_stories():
    data = request.json
    reddit.get_posts_from_subreddit(data["subreddit"])
    return jsonify({"message": "New stories fetched successfully"})

if __name__ == '__main__':
    app.run(debug=True)