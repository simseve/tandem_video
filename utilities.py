from moviepy.editor import *
import qrcode
from PIL import Image, ImageDraw, ImageFont
from logger_config import setup_logger
import configparser
import numpy as np
import json
import datetime

logger = setup_logger()

# Read the configuration file
config = configparser.ConfigParser()
config.read('config.ini')

tmp_directory = config.get('constants', 'tmp_directory')

empty_body = config.getboolean('constants', 'EMPTY_BODY')
empty_header = config.getboolean('constants', 'EMPTY_HEADER')
empty_closing = config.getboolean('constants', 'EMPTY_CLOSING')
new_width = config.getint('constants', 'NEW_LOGO_WIDTH')
font_size = config.getint('constants', 'FONT_SIZE')
passenger_font_size = config.getint('constants', 'PASSENGER_FONT_SIZE')
line_spacing = config.getint('constants', 'LINE_SPACING')
slogan_font_size = config.getint('constants', 'SLOGAN_FONT_SIZE')
fade_out_duration = config.getint('constants', 'FADE_OUT_DURATION')
padding = config.getint('constants', 'PADDING')
default_audio_volume = config.get('constants', 'DEFAULT_AUDIO_VOLUME')

name = config.get('text_overlay', 'name')
website = config.get('text_overlay', 'website')
ph_number = config.get('text_overlay', 'ph_number')
email = config.get('text_overlay', 'email')
line_1 = config.get('text_overlay', 'line_1')
line_2 = config.get('text_overlay', 'line_2')

transition_duration = config.getint('io', 'TRANSITION_DURATION')

  

def cut_last_n_sec(input_video: VideoFileClip, duration: int) -> VideoFileClip:

    # Calculate the new end time
    new_end_time = input_video.duration - duration
    logger.info(f"cut_last_n_sec -> new_end_time = {new_end_time}")

    # Create a new subclip without the last n seconds
    trimmed_video = input_video.subclip(new_end_time, input_video.duration)
    logger.info(f"cut_last_n_sec succesfully trimmed")
    # Save the result
    return trimmed_video


def cut_first_n_sec(input_video: VideoFileClip, duration: int) -> VideoFileClip:
    logger.info(f"cut_first_n_sec -> duration = {duration}")
    # Create a new subclip without the first n seconds
    trimmed_video = input_video.subclip(0, duration)

    logger.info(f"cut_first_n_sec succesfully trimmed")
    # Save the result
    return trimmed_video

def _extend_video(input_video: VideoFileClip, duration: int) -> VideoFileClip:

    # Define the desired duration in seconds
    desired_duration = duration

    logger.info(f"extend_video -> extended duration = {duration}")
    # If the input video is shorter than the desired duration, loop and trim as needed
    if input_video.duration < desired_duration:
        num_loops = int(desired_duration // input_video.duration)
        last_loop_duration = desired_duration % input_video.duration

        clips = [input_video] * num_loops
        if last_loop_duration > 0:
            clips.append(input_video.subclip(0, last_loop_duration))

        output_video = concatenate_videoclips(clips)

    # If the input video is longer than the desired duration, trim it
    elif input_video.duration > desired_duration:
        output_video = input_video.subclip(0, desired_duration)

    # If the input video has the desired duration, use it as is
    else:
        output_video = input_video

    logger.info(f"extend_video ->job completed")
    # Save the result
    return output_video


def _text_overlay(text: str, input_video: VideoFileClip, position: str, font_size: int, font_type: str = "./fonts/kollektif/Kollektif-Bold.ttf") -> VideoFileClip:
    """
    Apply a text over a clip.

    :param text: The text to overlay.
    :param input_video: The target video clip.
    :param position: A string eg "bottom-right" where to place the text. Can be px coordinates too.
    :param font_size: The Font size
    :param font_type: The Font type referenced as tiff from a folder. Default is provided
    :return: A video with the text over it
    """
    logger.info(f"overlaying {text} to {input_video}")
    # Create the text overlay with the date
    text_clip = TextClip(
        text,
        font = font_type,
        fontsize=font_size,
        color="white",
        # bg_color="green",
        # size=(200, 40),
        print_cmd=False,
        transparent=True
    ).set_duration(input_video.duration)

    # Set the padding values
    padding_top = padding
    padding_bottom = padding
    padding_left = padding
    padding_right = padding

    # Create a transparent ColorClip with the padded size
    padded_width = text_clip.size[0] + padding_left + padding_right
    padded_height = text_clip.size[1] + padding_top + padding_bottom
    background_clip = ColorClip(size=(padded_width, padded_height), color=(0, 0, 0, 0))

    # Overlay the TextClip on the ColorClip with padding offsets
    composite_text_clip = CompositeVideoClip([
        background_clip,
        text_clip.set_position((padding_left, padding_top))
    ], size=(padded_width, padded_height)).set_duration(text_clip.duration)


    # Set the position of the text clip based on the chosen position
    if position == 'top-center':
        final_text_clip = composite_text_clip.set_position(('center', 'top'))
    elif position == 'top-left':
        final_text_clip = composite_text_clip.set_position(('left', 'top'))
    elif position == 'top-right':
        final_text_clip = composite_text_clip.set_position(('right', 'top'))
    elif position == 'bottom-left':
        final_text_clip = composite_text_clip.set_position(('left', 'bottom'))
    elif position == 'bottom-right':
        final_text_clip = composite_text_clip.set_position(('right', 'bottom'))
    elif position == 'bottom-center':
        final_text_clip = composite_text_clip.set_position(('center', 'bottom'))
    elif position == 'custom':
        final_text_clip = composite_text_clip.set_position(('center', 0.2))


    # Apply the text overlay to the video
    output_video = CompositeVideoClip([input_video, final_text_clip])
    logger.info(f"Text overlaying job succesfully completed")
    # text_clip.close()
    return output_video

def _apply_crossfade(clip1: VideoFileClip, clip2: VideoFileClip, transition_duration: int) -> VideoFileClip:
    """
    Apply a crossfade transition between two clips.

    :param clip1: The first video clip.
    :param clip2: The second video clip.
    :param transition_duration: The duration of the transition in seconds.
    :return: A concatenated video clip with the crossfade transition applied.
    """
    logger.info(f"Crossfading {clip1} with {clip2} for this duration {transition_duration}")
    # Apply the crossfade effect to the clips
    clip1 = clip1.crossfadeout(transition_duration)
    clip2 = clip2.crossfadein(transition_duration)

    # Calculate the start time of the second clip
    clip2_start_time = clip1.duration - transition_duration

    # Set the start time of the second clip
    clip2 = clip2.set_start(clip2_start_time)

    # Concatenate the clips using a CompositeVideoClip
    transition_video = CompositeVideoClip([clip1, clip2], size=clip1.size)
    logger.info(f"Crossfading job succesfully completed")
    return transition_video

def _audio_mixer(input_video, volume, audio_file):
    # Set the desired volume (0.0 to 1.0, where 1.0 is the original volume)
    logger.info(f"Mixing audio started with volume = {volume}")
    desired_volume = volume  # Adjust this value to set the desired volume level

    # Define the fade-out duration in seconds
    # fade_out_duration = 3

    # Calculate the number of loops needed to cover the video duration
    num_loops = int(input_video.duration // audio_file.duration)
    
    # Calculate the duration of the last loop
    last_loop_duration = input_video.duration % audio_file.duration

    # Create a list of audio clips, including full loops and the trimmed last loop
    audio_clips = [audio_file] * num_loops
    if last_loop_duration > 0:
        audio_clips.append(audio_file.subclip(0, last_loop_duration))
    
    # Loop the audio to match the video duration
    extended_audio = concatenate_audioclips(audio_clips)

    # Lower the audio volume of the video
    lower_volume_audio = input_video.audio.volumex(desired_volume)
    pre_final_low_volume = input_video.set_audio(lower_volume_audio)

    # Mix the original audio with the new soundtrack
    mixed_audio = CompositeAudioClip([pre_final_low_volume.audio, extended_audio])


    tmp = pre_final_low_volume.set_audio(mixed_audio)
    
    # Apply the fade-out effect to the video's audio
    faded_audio = tmp.audio.audio_fadeout(fade_out_duration)
    
    logger.info(f"Mixing audio job completed")

    # Set the mixed audio as the audio of the video
    return pre_final_low_volume.set_audio(faded_audio)


def _generate_qr_code(url, secret_uuid):
    logger.info(f"Generating QR code for {website}")
    data = website
    # Create a JSON object containing the URL and the secret UUID
    data = {
        "url": url,
        "secret": str(secret_uuid)
    }
    json_data = json.dumps(data)

    # Generate the QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=8,
        border=2,
    )
    qr.add_data(json_data)
    qr.make(fit=True)

    img_qr = qr.make_image(fill_color="black", back_color="white")
    logger.info(f"Generating QR code job succesfully completed") 

    return img_qr

def _overlay_image_on_video(video, image, position):

    # # Load the video and image (in case they are files and not objects)
    # video = VideoFileClip(video_file)
    # image = ImageClip(image_file).set_duration(video.duration)
    video_width, video_height = video.size
    image_width, image_height = image.size
    
    logger.info(f"Overlaying image on video started")
    logger.info(f"Video size: w{video_width}, h{video_height}")
    logger.info(f"Image size: w{image_width}, h{image_height}")

    # Convert the PIL Image to an RGB image if needed
    if image.mode != 'RGB':
        image = image.convert('RGB')

    # Convert the PIL Image to a MoviePy ImageClip
    image = ImageClip(np.array(image)).set_duration(video.duration)

    # Set the position of the image on the video
    image = image.set_position(position)

    # Overlay the image on the video
    composite = CompositeVideoClip([video, image])

    # # Save the result
    # output_file = "xwz.mp4"
    # composite.write_videofile(output_file, codec='libx264', audio_codec='aac')
    logger.info(f"Overlaying image job succesfully completed")

    return composite

def _resize_logo(company_logo_path):
    image = Image.open(company_logo_path)

    # Calculate the new height while maintaining the aspect ratio
    new_width
    aspect_ratio = new_width / float(image.width)
    new_height = int(image.height * aspect_ratio)

    # Resize the image
    
    resized_image = image.resize((new_width, new_height), Image.ANTIALIAS)
    logger.info(f"Logo resized")
    # Convert the PIL Image to a NumPy array
    # numpy_image = np.array(resized_image)

    # Create a MoviePy ImageClip from the NumPy array
    # image_clip = ImageClip(numpy_image)
    image.close()

    return resized_image

def prepare_heading(clip, slogan, company_logo_path):
    logger.info(f"Preparing header clip -> started")

    with_slogan = _text_overlay(slogan, clip, "bottom-center", slogan_font_size)
    logger.info(f"Applying slogan - done")

    with_logo = _overlay_image_on_video(with_slogan, _resize_logo(company_logo_path), (100,480))
    logger.info(f"Applying logo to header - done")  
    
    return with_logo

def prepare_closing(clip, name, secret, company_logo_path):

    logger.info(f"Preparing closing clip function is started")
    lines = [line_1, line_2]


    # Create a font object for the text
    text_font = ImageFont.truetype("./fonts/kollektif/Kollektif.ttf", font_size)

    passenger_name_overlay = _text_overlay(name, clip, "custom", passenger_font_size)


    # Calculate the width and height of the text block
    line_widths = [text_font.getsize(line)[0] for line in lines]
    text_width = max(line_widths)
    text_height = sum(text_font.getsize(line)[1] for line in lines) + (len(lines) - 1) * line_spacing

    # Create a transparent image with the text
    image = Image.new('RGBA', (text_width, text_height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)

    # Draw each line of text on the image
    y_offset = 0
 
    for line in lines:
        line_width, line_height = text_font.getsize(line)
        x_offset = (text_width - line_width) // 2
        draw.text((x_offset, y_offset), line, font=text_font, fill=(255, 255, 255, 255))
        y_offset += line_height + line_spacing

    # Convert the PIL Image to a NumPy array and create an ImageClip
    image_np = np.array(image)
    text_clip = ImageClip(image_np).set_duration(clip.duration)

    # Overlay the text_clip at the center of the main clip
    composite_clip = CompositeVideoClip([
        passenger_name_overlay,
        text_clip.set_position('center')
    ])

    # Apply the QR code

    qr_clip = _generate_qr_code(website, secret)
    logger.info(f"QR code succesfuly generated")
    # qr_clip.show()

    image_on_clip = _overlay_image_on_video(composite_clip, qr_clip, (1415,600))


    logger.info(f"Applying company logo - started")
    #Lastly apply the company logo
    logo_on_clip = _overlay_image_on_video(image_on_clip, _resize_logo(company_logo_path), (100,480))
    logger.info(f"Applying company logo - done")

    # Write the output video
    # overlay.write_videofile("xyz.mp4", codec="libx264")
    logger.info(f"Preparing closing clip function is completed")
    
    return logo_on_clip

def _overlay_clip_to_template(clip, template):
    logger.info(f"Start preparing the clip to overlay to an existing body template")
    
    # Extend the template to match the lenght of the clip
    extended_video = _extend_video(template, clip.duration)
        # Resize the second video to fit into the box
    clip_resized = clip.resize(height=835)  # Adjust the size according to your needs

    # Set the position of the second video (the box) within the main video
    # clip_position = (227.7, 149.1)  # (x, y) coordinates of the top-left corner of the box
    clip_position = ('center')

    # Apply the second video (the box) to the main video
    video_w_overlay = CompositeVideoClip([extended_video, clip_resized.set_position(clip_position)])
    logger.info(f"Clip succesfully overlayied to an existing body template")
    return video_w_overlay


def create_video(clip, header, body, closing, flight_date, location, audio_file, volume, uuid):
    logger.info(f"Create final video job started")

    video_w_overlay = _overlay_clip_to_template(clip, body)
    
    #join body template with closing template
    last_two = _apply_crossfade(video_w_overlay, closing, transition_duration)

    if empty_body:
        # Overlay bunch of attributes
        tmp_1 = _text_overlay(name, last_two, "top-left", 50)
        tmp_2 = _text_overlay(email, tmp_1, "bottom-center", 40)
        tmp_3 = _text_overlay(website, tmp_2, "bottom-left", 40)
        tmp_4 = _text_overlay(ph_number, tmp_3, "bottom-right", 40)

        last_transition_applied = _apply_crossfade(header, tmp_4, transition_duration)
    else:
        last_transition_applied = _apply_crossfade(header, last_two, transition_duration)

    # second_transition_applied = apply_crossfade(header, first_transition_applied, transition_duration)

    video_with_mixed_audio = _audio_mixer(last_transition_applied, volume, audio_file)

     
    # Overlay data and location
    final = _text_overlay(f'{location}, {flight_date:%d %B %Y}', video_with_mixed_audio, "top-right", 40)

    # Generate a unique filename using a UUID
    # Create a timestamp string
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    unique_filename = f"{timestamp}_{flight_date}_{location}__{uuid}.mp4"
    output_path = os.path.join(tmp_directory, unique_filename)

    # Try to explore faster codec so replacing the working libx264 with h264_nvenc h264_videotoolbox
    logger.info(f"Starting to write to file")
    final.write_videofile(output_path, codec="libx264", audio_codec="aac")
    logger.info(f"Writing to file completed")
    logger.info(f"Create video job completed")
    
    return unique_filename