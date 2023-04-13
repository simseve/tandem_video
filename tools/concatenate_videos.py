from typing import List, Union
from moviepy.editor import VideoFileClip, concatenate_videoclips
import os

def concatenate_videos(video_paths: List[str], write_to_file: bool = True, output_path: str = "output.mp4") -> Union[None, VideoFileClip]:
    # Load all videos into VideoFileClip objects
    video_clips = [VideoFileClip(path) for path in video_paths]

    # Concatenate the clips into one video
    concatenated_clip = concatenate_videoclips(video_clips)

    # Write the output to a file or return the VideoFileClip object
    if write_to_file:
        concatenated_clip.write_videofile(output_path)
        return None
    else:
        return concatenated_clip

if __name__ == '__main__':

    # Concatenate three videos and write the output to a file
    current_dir = os.path.abspath(os.path.dirname(__file__))
    video_names = ["video1.mp4", "video2.mp4", "video3.mp4"]
    video_paths = []

    for name in video_names:
        path = os.path.join(current_dir, name)
        video_paths.append(path)

    concatenate_videos(video_paths)
    

    # # Concatenate three videos and return the VideoFileClip object
    # video_paths = ["video1.mp4", "video2.mp4", "video3.mp4"]
    # output_clip = concatenate_videos(video_paths, write_to_file=False)
