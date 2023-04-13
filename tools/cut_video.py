from utilities import cut_first_n_sec, cut_last_n_sec
from moviepy.editor import *

clip = VideoFileClip("./templates/template_empty.mp4")

clip_short = cut_first_n_sec(clip, 3)

# clip_short = clip.subclip(0, 5)

clip_short.write_videofile("closing_empty.mp4", codec="libx264", audio_codec="aac")

# last_5 = cut_last_n_sec(clip, 5)
# last_5.write_videofile("last_5.mp4", codec="libx264", audio_codec="aac")

