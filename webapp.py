import streamlit as st
from moviepy.editor import *
import datetime
import os
import tempfile
from logger_config import setup_logger
from utilities import cut_first_n_sec, cut_last_n_sec, prepare_closing, prepare_heading, create_video
import configparser
import uuid
from dotenv import load_dotenv
from cloud_dbx import dropbox_list_files, dropbox_download_file, dropbox_get_link, dropbox_upload_file


# Remove a folder and all its content, and return a list of deleted files
def remove_folder(folder_path):
    if not os.path.exists(folder_path):
        raise ValueError(f"Folder '{folder_path}' does not exist.")
    deleted_files = []
    for root, dirs, files in os.walk(folder_path, topdown=False):
        for file in files:
            file_path = os.path.join(root, file)
            os.remove(file_path)
            deleted_files.append(file_path)
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            os.rmdir(dir_path)
            deleted_files.append(dir_path)
    os.rmdir(folder_path)
    deleted_files.append(folder_path)
    return deleted_files

def validate_file_exists(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f'File not found: {filepath}')
        return False
    else:
        return True

# Add a title for the Streamlit app
st.title("Video Creator for your tandem experience")

# Load environment variables from .env file
load_dotenv()

# Set the access token as an environment variable
access_token = os.environ['DROPBOX_ACCESS_TOKEN']

logger = setup_logger()

# Read the configuration file
config = configparser.ConfigParser()
config.read('config.ini')

dbx_video_template_directory = config.get('constants', 'dbx_video_template_directory')
dbx_video_output_directory = config.get('constants', 'dbx_video_output_directory')
dbx_video_input_directory = config.get('constants', 'dbx_video_input_directory')
tmp_directory = config.get('constants', 'tmp_directory')

empty_header = config.getboolean('constants', 'EMPTY_HEADER')
empty_body = config.getboolean('constants', 'EMPTY_BODY')
empty_closing = config.getboolean('constants', 'EMPTY_CLOSING')

default_audio_path = config.get('io', 'DEFAULT_AUDIO') 
volume = config.getfloat('constants', 'DEFAULT_AUDIO_VOLUME')
slogan = config.get('text_overlay', 'slogan')

header_path = config.get('io', 'HEADER') 
header_empty_path = config.get('io', 'HEADER_EMPTY') 
body_path = config.get('io', 'BODY') 
body_empty_path = config.get('io', 'BODY_EMPTY') 
closing_path = config.get('io', 'CLOSING') 
closing_empty_path = config.get('io', 'CLOSING_EMPTY') 
company_logo_path = config.get('io', 'LOGO') 

generated_uuid = uuid.uuid4()
logger.info(f"The App has started with uuid: {generated_uuid}")

# Check if the template directory exists
try:
    if not os.path.exists(tmp_directory):
        os.makedirs(tmp_directory)
        logger.info(f"The directory {tmp_directory} does not exist but it was created!")
except Exception as e:
    logger.error(f"Error creating directory '{tmp_directory}': {str(e)}")



# Download Header empty template
dbx_header_empty_file_path = os.path.join(dbx_video_template_directory, header_empty_path)
tmp_header_empty_file_path = os.path.join(tmp_directory, header_empty_path)
st.text_input("Header empty location", value=dbx_header_empty_file_path)
# Download Header not empty template
dbx_tmp_header_file_path = os.path.join(dbx_video_template_directory, header_path)
tmp_header_file_path = os.path.join(tmp_directory, header_path)
st.text_input("Header location", value=dbx_tmp_header_file_path)

# Download Body empty template
dbx_body_empty_file_path = os.path.join(dbx_video_template_directory, body_empty_path)
tmp_body_empty_file_path = os.path.join(tmp_directory, body_empty_path)
st.text_input("Body empty location", value=dbx_body_empty_file_path)
# Download Body template
dbx_body_file_path = os.path.join(dbx_video_template_directory, body_path)
tmp_body_file_path = os.path.join(tmp_directory, body_path)
st.text_input("Body location", value=dbx_body_file_path)
# Download Closing Empty template
dbx_closing_empty_file_path = os.path.join(dbx_video_template_directory, closing_empty_path)
tmp_closing_empty_file_path = os.path.join(tmp_directory, closing_empty_path)
st.text_input("Closing location",value=dbx_closing_empty_file_path)
# Download Closing template
dbx_tmp_closing_file_path = os.path.join(dbx_video_template_directory, closing_path)
tmp_closing_file_path = os.path.join(tmp_directory, closing_path)
st.text_input("Closing empty location", value=dbx_tmp_closing_file_path)

# Download the company logo file
dbx_company_logo_file_path = os.path.join(dbx_video_template_directory, company_logo_path)
tmp_company_logo_file_path = os.path.join(tmp_directory, company_logo_path)
st.text_input("Company logo location", value=dbx_company_logo_file_path)

# Dowload the MP3 audio file
dbx_default_audio_file_path = os.path.join(dbx_video_template_directory, default_audio_path)
tmp_default_audio_path = os.path.join(tmp_directory, default_audio_path)
st.text_input("Default audio location", value=dbx_default_audio_file_path)



if st.button("Get all templates", key="download_templates"):
    st.divider()

    meta_header_empty = dropbox_download_file(access_token, dbx_header_empty_file_path, tmp_header_empty_file_path)
    logger.info(f"{meta_header_empty}")


    meta_header = dropbox_download_file(access_token, dbx_tmp_header_file_path, tmp_header_file_path)
    logger.info(f"{meta_header}")


    meta_body_empty = dropbox_download_file(access_token, dbx_body_empty_file_path, tmp_body_empty_file_path)
    logger.info(f"{meta_body_empty}")


    meta_body = dropbox_download_file(access_token, dbx_body_file_path, tmp_body_file_path)
    logger.info(f"{meta_body}")


    meta_closing_empty = dropbox_download_file(access_token, dbx_closing_empty_file_path, tmp_closing_empty_file_path)
    logger.info(f"{meta_closing_empty}")


    meta_closing = dropbox_download_file(access_token, dbx_tmp_closing_file_path, tmp_closing_file_path)
    logger.info(f"{meta_closing}")

    meta_logo = dropbox_download_file(access_token, dbx_company_logo_file_path, tmp_company_logo_file_path)
    logger.info(f"{meta_logo}")


    meta_audio = dropbox_download_file(access_token, dbx_default_audio_file_path, tmp_default_audio_path)
    logger.info(f"{meta_audio}")


    # Load the header video
    if empty_header:
        if validate_file_exists(tmp_header_empty_file_path):
            header = VideoFileClip(os.path.join(tmp_directory, header_empty_path))
            logger.info(f"Empty Header loaded")
    else:
        if validate_file_exists(tmp_header_file_path):
            header = VideoFileClip(os.path.join(tmp_directory, header_path))
            logger.info(f"Header loaded")

    # Load the main video
    if empty_body:
        if validate_file_exists(tmp_body_empty_file_path):
            body = VideoFileClip(os.path.join(tmp_directory, body_empty_path))
            logger.info(f"Empty Body template loaded")
    else:
        if validate_file_exists(tmp_body_file_path):
            body = VideoFileClip(os.path.join(tmp_directory, body_path))
            logger.info(f"Body  loaded")    

    # Load the second video (the one you want to insert into the main video)
    if empty_closing:
        if validate_file_exists(tmp_closing_empty_file_path):
            closing = VideoFileClip(os.path.join(tmp_directory, closing_empty_path))
            logger.info(f"Empty Closing loaded")
    else:
        if validate_file_exists(tmp_closing_file_path):
            closing = VideoFileClip(os.path.join(tmp_directory, closing_path))
            logger.info(f"Closing loaded")  


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
    default_audio_file_path = os.path.join(tmp_directory, default_audio_path)

    # Create an AudioFileClip using the default audio file path
    audio_file = AudioFileClip(default_audio_file_path)

# uploaded_video = st.file_uploader("Upload a video clip", type=["mp4", "avi", "mov"])
files = dropbox_list_files(access_token, dbx_video_input_directory)

logger.info(files)

if not files.empty:
    uploaded_video = st.selectbox("Select a file from the folder:", files.name)
    st.write(f"Selected file: {uploaded_video}")
else:
    st.write("No files found in the specified folder. Please upload your video")


if st.button("Load flight clip", key="read_video"):
    clip_name = uploaded_video
    dbx_input_file_path = os.path.join(dbx_video_input_directory, clip_name)   
    tmp_input_file_path = os.path.join(tmp_directory, clip_name)
    meta_input = dropbox_download_file(access_token, dbx_input_file_path, tmp_input_file_path)
    logger.info(f"{meta_input}")
    logger.info(f"Video clip file downloaded {tmp_input_file_path}")
    
    with st.spinner("Processing video..."):
        # # Save the uploaded video to a temporary file
        # tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") 
        # tfile.write(uploaded_video.read())
        
        # Load the video using MoviePy
        video_clip = VideoFileClip(tmp_input_file_path)

        # Display the processed video
        st.video(tmp_input_file_path)
        st.write(f"The video lenght is: {video_clip.duration}s")
        logger.info(f"The video lenght is: {video_clip.duration}s")


if st.button("Create Video", key="video_create"):
    with st.spinner("Processing video..."):

        if empty_header:
            logger.info(f"Customizing heading clip -> started")
            if validate_file_exists(tmp_company_logo_file_path):
                header = prepare_heading(header, slogan, tmp_company_logo_file_path)
                logger.info(f"Customizing heading clip -> done")


        # if in config.ini we set to True PREP_CLOSING then we rely on an empty template and apply our text
        if empty_closing: 
            logger.info(f"Customizing closing clip -> started")
            # If you pass a closing clip that is empty make sure the variable EMPTY_CLOSING=True in config.ini
            if validate_file_exists(tmp_company_logo_file_path):
                closing = prepare_closing(closing, passenger, generated_uuid, tmp_company_logo_file_path)

                logger.info(f"Customizing closing clip -> done")



        # Ready to generate the final video which is made of an header, a body template with on top a customer clip and closing
        
        filename = create_video(video_clip, header, body, closing, flight_date, location, audio_file, volume, generated_uuid) 
        
        tmp_output_file_path = os.path.join(tmp_directory, filename)
        logger.info(f"{tmp_output_file_path} succesfully created")

        dbx_tmp_output_file_path = os.path.join(dbx_video_output_directory, filename)
   
        meta_upload = dropbox_upload_file(access_token, tmp_directory, filename, dbx_tmp_output_file_path)
        logger.info(f"{meta_upload}")
        
        # share the link
        link = dropbox_get_link(access_token, dbx_tmp_output_file_path)
        logger.info(f"File {link} ready to be downloaded")

        st.success(f"Video created successfully! with UUID {generated_uuid}")

        # # Clean the temporary folder
        # deleted_files = remove_folder(tmp_directory)
        # print(f"All files in '{tmp_directory}' were deleted: {deleted_files}")
        # logger.debug(f"All files deleted succesfully")

        open_link_button = st.button("Open Link")

        if open_link_button:
            st.markdown(f'[Click here to download your final video]({link})', unsafe_allow_html=True)


        # st.download_button(
        #     label="Download Processed Video",
        #     data=video_bytes,
        #     file_name=f"{link}",
        #     mime="video/mp4",
        # )
        
        # Clean up the temporary files
        # os.unlink(tfile.name)
        # logger.info(f"All resource released")


