from moviepy.video.io.VideoFileClip import VideoFileClip
from typing import Union
import os

def cut_video(clip: str, start_time: int, end_time: int, write_to_file: bool = True, output_path: str = "output.mp4") -> Union[None, VideoFileClip]:
    # Load the video clip
    video = VideoFileClip(clip)

    # Subclip from start_time to end_time
    subclip = video.subclip(start_time, end_time)

    # Write the output to a file or return the VideoFileClip object
    if write_to_file:
        subclip.write_videofile(output_path)
        return None
    else:
        return write_to_file

if __name__ == '__main__':
    current_dir = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(current_dir, "test.mp4")
    
    cut_video(path, 3, 5, True)
