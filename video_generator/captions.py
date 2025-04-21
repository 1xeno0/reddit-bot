from moviepy import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip
from openai import OpenAI

from config import OPENAI_API_KEY

from pprint import pprint
import os
import traceback

client = OpenAI(api_key=OPENAI_API_KEY)

class Captions:
    def __init__(self, video_path, audio_path, output_path, capitalize=False):
        self.video_path = video_path
        self.audio_path = audio_path
        self.output_path = output_path
        self._open_video()
        transcript = self._get_transcript()
        timestamps = self._get_timestamps(transcript)
        self.final_captions = self._concatenate_timestamps(timestamps, capitalize=capitalize)
        pprint(self.final_captions)

        self.created_text_clips = []

    def _open_video(self):
        self.video = VideoFileClip(self.video_path)

    def close(self):
        self.video.close()
        print("original video closed")

        self._close_all_text_clips()
        print("closed all text clips")

    def _get_audio_file(self):
        audio_file = open(self.audio_path, "rb")
        return audio_file

    def _get_transcript(self):
        transcription = client.audio.transcriptions.create(
            file=self._get_audio_file(),
            model="whisper-1",
            response_format="verbose_json",
            timestamp_granularities=["word"]
        )
        return transcription

    def _get_timestamps(self, transcript):
        timestamps = []
        for word in transcript.words:
            timestamps.append({
                "word": word.word,
                "start": round(float(word.start), 2),
                "end": round(float(word.end), 2)
            })
        return timestamps

    def _concatenate_timestamps(self, word_timestamps, max_words=3, max_gap=0.05, capitalize=False):
        sentences = []
        current_chunk_words = []
        current_chunk_start_time = None
        current_chunk_last_word_end_time = None

        for i, word_data in enumerate(word_timestamps):
            word = word_data['word']
            start_time = word_data['start']
            end_time = word_data['end']

            if i == 0:
                current_chunk_words = [word]
                current_chunk_start_time = start_time
                current_chunk_last_word_end_time = end_time
                continue
                
            gap = start_time - current_chunk_last_word_end_time
            
            is_max_words_reached = len(current_chunk_words) >= max_words
            is_gap_exceeded = gap > max_gap

            if is_max_words_reached or is_gap_exceeded:
                sentence_text = " ".join(current_chunk_words)
                if capitalize:
                    sentence_text = sentence_text.upper()
                sentences.append({
                    'start': current_chunk_start_time,
                    'end': current_chunk_last_word_end_time,
                    'text': sentence_text
                })
                
                current_chunk_words = [word]
                current_chunk_start_time = start_time
                current_chunk_last_word_end_time = end_time
            else:
                current_chunk_words.append(word)
                current_chunk_last_word_end_time = end_time

        if current_chunk_words:
            sentence_text = " ".join(current_chunk_words)
            sentences.append({
                'start': current_chunk_start_time,
                'end': current_chunk_last_word_end_time,
                'text': sentence_text
            })

        return sentences

    def _create_text_clip(self, text, start, end, font_path, font_size, color, bg_color, position, caption_box_width):
        text_clip = TextClip(font_path, 
            text, 
            font_size=font_size, 
            color=color, 
            bg_color=bg_color,
            size=(caption_box_width, 50),
            method="caption"
        )
        text_clip = text_clip.with_position(position, relative=True).with_start(start).with_duration(end - start)
        self.created_text_clips.append(text_clip)
        print(f"created text clip with \"{text}\" from {start} to {end}")
        return text_clip

    def _add_text_clip_to_video(self, text_clip):
        self.video = CompositeVideoClip([self.video, text_clip])
        self.created_text_clips.append(text_clip)

    def clear_title_captions(self):
        for i, caption in enumerate(self.final_captions):
            print(f"caption {i}: {caption['end']} - {self.final_captions[i+1]['start']}")
            if self.final_captions[i+1]['start'] - caption['end'] >= 0.99:
                self.final_captions = self.final_captions[i+1:]
                break

    def add_captions_to_video(self, font_path, font_size, color, bg_color=None, position=('center', 0.85), caption_box_width=864):
        for caption in self.final_captions:
            text_clip = self._create_text_clip(caption['text'], caption['start'], caption['end'], font_path, font_size, color, bg_color, position, caption_box_width)
            self._add_text_clip_to_video(text_clip)
            print(f"added text clip with \"{caption['text']}\" from {caption['start']} to {caption['end']}")
        print("added all text clips to video")
    
    def _close_all_text_clips(self):
        for text_clip in self.created_text_clips:
            text_clip.close()
        print("closed all text clips")

    def save(self):
        print(f"saving video to {self.output_path}")
        audio = AudioFileClip(self.audio_path)
        self.video.audio = audio
        print("added audio to video")
        self.video.write_videofile(self.output_path, 
            codec='libx264', audio_codec='aac',
            logger="bar")
        print("saved video")
        audio.close()
        print("closed audio")

if __name__ == "__main__":
    video = Captions("output/something.mp4", "temp/temp.mp3", "output/something_captions.mp4")
    video.clear_title_captions()
    success = video.add_captions_to_video(
                font_path="assets/fonts/roboto.ttf",
                font_size=36,
                color='white',
                position=('center'), # 85% down
                caption_box_width=int(video.video.w * 0.8),
                capitalize=True # Use 80% width
            )
    video.save()
    video.close()