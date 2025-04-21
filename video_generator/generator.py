from video_generator.video import Video
from video_generator.voice import Voice
from video_generator.audio import Audio
from video_generator.captions import Captions

import os

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
        video_name = "video"
    ):
    print("-"*30, video_name, "-"*30)
    print("Generating video with title: ", title_text)
    title_voice = Voice(voice_name, title_text, voice_title_output_name, save_folder=temp_voices_folder)
    text_voice = Voice(voice_name, main_text, voice_text_output_name, save_folder=temp_voices_folder)

    audio = Audio(
        voices_clips=[title_voice.audio_clip, text_voice.audio_clip],
        audio_path=background_audio_path,
        pause_duration=pause_duration, 
        audio_temp_name=audio_temp_name, 
        folder=temp_audio_folder
    )

    video = Video(
        video_output_path=video_output_path.split(".")[0]+"_without_captions.mp4", 
        background_folder=background_clips_folder, 
        audio=audio.audio_clip
    )

    video.add_label(label_name, 
        title_text, 
        title_voice.duration
    )
    video.save_video()

    video.close_clips()
    title_voice.delete()
    text_voice.delete()
    audio.delete()

    video_with_captions = Captions(video_output_path.split(".")[0]+"_without_captions.mp4", 
                                audio.output_path, 
                                video_output_path, 
                                capitalize=capitalize
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
    video_with_captions.close()
    os.remove(video_output_path.split(".")[0]+"_without_captions.mp4")

    print("Cleared temp files")
    print("-"*30, video_name, "-"*30)

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