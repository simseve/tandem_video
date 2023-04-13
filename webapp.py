import streamlit as st
from moviepy.editor import *

import datetime
import os
import tempfile
from logger_config import setup_logger
from utilities import cut_first_n_sec, cut_last_n_sec, prepare_closing, prepare_heading, create_video
import configparser
import uuid

logger = setup_logger()

# Read the configuration file
config = configparser.ConfigParser()
config.read('config.ini')

video_template_directory = config.get('constants', 'video_template_directory')
video_output_directory = config.get('constants', 'video_output_directory')
default_audio = config.get('constants', 'DEFAULT_AUDIO')
empty_header = config.getboolean('constants', 'EMPTY_HEADER')
empty_body = config.getboolean('constants', 'EMPTY_BODY')
empty_closing = config.getboolean('constants', 'EMPTY_CLOSING')
company_logo_path = config.get('io', 'LOGO')
header_path = config.get('io', 'HEADER') 
header_empty_path = config.get('io', 'HEADER_EMPTY') 
body_path = config.get('io', 'BODY') 
body_empty_path = config.get('io', 'BODY_EMPTY') 
closing_path = config.get('io', 'CLOSING') 
closing_empty_path = config.get('io', 'CLOSING_EMPTY') 

generated_uuid = uuid.uuid4()

# Load the header video
if empty_header:
    header = VideoFileClip(os.path.join(video_template_directory, header_empty_path))
    logger.info(f"Empty Header loaded")
else:
    header = VideoFileClip(os.path.join(video_template_directory, header_path))
    logger.info(f"Header loaded")

# Load the main video
if empty_body:
    body = VideoFileClip(os.path.join(video_template_directory, body_empty_path))
    logger.info(f"Empty Body template loaded")
else:
    body = VideoFileClip(os.path.join(video_template_directory, body_path))
    logger.info(f"Body  loaded")    

# Load the second video (the one you want to insert into the main video)
if empty_closing:
    closing = VideoFileClip(os.path.join(video_template_directory, closing_empty_path))
    logger.info(f"Empty Closing loaded")
else:
    closing = VideoFileClip(os.path.join(video_template_directory, closing_path))
    logger.info(f"Closing loaded")  

# Add a title for the Streamlit app
st.title("Video Creator for your tandem experience")

# Add input boxes for flight date and location
flight_date = st.date_input("Flight Date", datetime.date.today())
location = st.text_input("Location", "Laveno")
passenger = st.text_input("Passenger", "Mattia")
slogan = st.text_input("Slogan", "YOUR TANDEM EXPERIENCE")


# Add input boxes for volume and audio file
volume = st.slider("Volume", min_value=0.0, max_value=1.0, value=0.3, step=0.1)
audio_file_path = st.file_uploader("Choose an audio file", type=["mp3"])

if audio_file_path:
    # Read the audio file as bytes
    audio_bytes = audio_file_path.read()

    # Create a temporary file to store the uploaded audio
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_file:
        temp_audio_file.write(audio_bytes)
        temp_audio_file.flush()

        # Create an AudioFileClip using the temporary file path
        audio_file = AudioFileClip(temp_audio_file.name)

    # Remove the temporary file after it's loaded into MoviePy
    os.unlink(temp_audio_file.name)
else:
    # Set the path to your default audio file
    default_audio_file_path = os.path.join(video_template_directory, default_audio)

    # Create an AudioFileClip using the default audio file path
    audio_file = AudioFileClip(default_audio_file_path)

uploaded_video = st.file_uploader("Upload a video clip", type=["mp4", "avi", "mov"])

if uploaded_video is not None:
    logger.info(f"Video clip file loaded {uploaded_video}")
    with st.spinner("Processing video..."):
        # Save the uploaded video to a temporary file
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") 
        tfile.write(uploaded_video.read())
        
        # Load the video using MoviePy
        video_clip = VideoFileClip(tfile.name)

        # Display the processed video
        st.video(tfile.name)
        st.write(f"The video lenght is: {video_clip.duration}s")
        logger.info(f"The video lenght is: {video_clip.duration}s")


if st.button("Create Video", key="video_create"):
    with st.spinner("Processing video..."):

        if empty_header:
            logger.info(f"Customizing heading clip -> started")
            header = prepare_heading(header, slogan, company_logo_path)
            logger.info(f"Customizing heading clip -> done")


        # if in config.ini we set to True PREP_CLOSING then we rely on an empty template and apply our text
        if empty_closing: 
            logger.info(f"Customizing closing clip -> started")
            # If you pass a closing clip that is empty make sure the variable EMPTY_CLOSING=True in config.ini
            closing = prepare_closing(closing, passenger, generated_uuid, company_logo_path)

            logger.info(f"Customizing closing clip -> done")



        # Ready to generate the final video which is made of an header, a body template with on top a customer clip and closing
        
        final_video = create_video(video_clip, header, body, closing, flight_date, location, audio_file, volume, generated_uuid) 

        st.success(f"Video created successfully! with UUID {generated_uuid}")

        final_clip_path=os.path.join(video_output_directory, final_video)

        # Displaying a local video file
        video_file = open(final_clip_path, 'rb') #enter the filename with filepath
        video_bytes = video_file.read() #reading the file
        st.video(video_bytes) #displaying the video


        st.download_button(
            label="Download Processed Video",
            data=video_bytes,
            file_name=f"{final_video}",
            mime="video/mp4",
        )
        
        # Clean up the temporary files
        os.unlink(tfile.name)
        # logger.info(f"All resource released")


