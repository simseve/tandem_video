from moviepy.editor import *
from moviepy.video.fx import speedx


# Load the input video
input_video = VideoFileClip("original.mp4")

# Get the size (dimensions) of the video
width, height = input_video.size

print(f"Video size: {width}x{height}")

# Remove the audio from the video
video_without_audio = input_video.set_audio(None)

# Set the start time for the overlay (in seconds)
start_time = 4  # Replace this with your desired start time

# Cut the input video into two parts: before and after the start time
header = video_without_audio.subclip(0, start_time)
template = video_without_audio.subclip(start_time + 1)

# # Set the slowdown factor (higher values result in a slower video)
# slowdown_factor = 2  # Adjust this value to set the desired slowdown factor

# # Slow down the video
# slowed_header = header.fx(speedx, 1 / slowdown_factor)

# Write the header clip out
header.write_videofile("header.mp4", codec="libx264", audio_codec="aac")
template.write_videofile("template.mp4", codec="libx264", audio_codec="aac")


