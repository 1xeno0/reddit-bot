import os
import math
import argparse
from moviepy import VideoFileClip

video = VideoFileClip("mc_parkour.mp4")

for i in range(0, int(video.duration), 10):
    new_clip = video.subclipped(i, i+10)
    new_clip.write_videofile(f"assets/backgrounds/minecraft/parkour1/mc_parkour_{i}.mp4", audio=False)

video.close()