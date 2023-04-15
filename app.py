from moviepy.editor import *
import datetime
from utilities import cut_first_n_sec, cut_last_n_sec, prepare_heading, prepare_closing, create_video
from logger_config import setup_logger
import configparser
import os, shutil
import uuid
import argparse
from dotenv import load_dotenv
from cloud_dbx import dropbox_download_file, dropbox_get_link, dropbox_upload_file
from email_utils import send_email



# Load environment variables from .env file
load_dotenv()

# Set the access token as an environment variable
access_token = os.environ['DROPBOX_ACCESS_TOKEN']


def valid_date(date_string):
    try:
        return datetime.datetime.strptime(date_string, "%d/%m/%Y").date()
    except ValueError:
        msg = f"Invalid date format: '{date_string}'. Expected format: DD/MM/YYYY."
        raise argparse.ArgumentTypeError(msg)

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
    

def parse_arguments(test_mode=False):
    if test_mode:
        class TestArgs:
            file = "clip_short.mp4"
            name = "Test Passenger"
            date = valid_date("13/04/2022")
            location = "Test location"
            volume=0.3
            email="severini.simone@icloud.com"
        return TestArgs()


    parser = argparse.ArgumentParser(description="A Cli version to make tandemo video")

    parser.add_argument("-f", "--file", help="Name of the input file. Your clip to process", required=True)
    parser.add_argument("-n", "--name", type=str, help="The name of the passenger", required=True)
    parser.add_argument("-d", "--date", type=valid_date, help="A date in the format DD/MM/YYYY", required=True)
    parser.add_argument("-l", "--location", type=str, help="The location of the flight", required=True)
    parser.add_argument("-v", "--volume", type=float, help="Set the volume of the mp3 soundtrack (default = 0.3)")
    parser.add_argument("-e", "--email", type=str, help="The email where to send the link to download the file", required=True)

    return parser.parse_args()


def main(args):

    logger = setup_logger()

    # Set the absolute required values
    passenger = args.name
    logger.info(f"Passenger name set as {args.name}")  

    # Set a specific date (year, month, day) and location
    flight_date = args.date
    location = args.location
    logger.info(f"flight date and location set to {flight_date} and {location}")

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


    # Download all the needed files

    # Load customer clip from Dropbox
    clip_name = args.file
    dbx_input_file_path = os.path.join(dbx_video_input_directory, clip_name)   
    tmp_input_file_path = os.path.join(tmp_directory, clip_name)
    meta_input = dropbox_download_file(access_token, dbx_input_file_path, tmp_input_file_path)
    logger.info(f"{meta_input}")

    if validate_file_exists(tmp_input_file_path):
        clip = VideoFileClip(tmp_input_file_path)
        logger.info(f"Customer Clip is loaded named {tmp_input_file_path}") 


    # Download Header empty template
    dbx_header_empty_file_path = os.path.join(dbx_video_template_directory, header_empty_path)
    tmp_header_empty_file_path = os.path.join(tmp_directory, header_empty_path)
    meta_header_empty = dropbox_download_file(access_token, dbx_header_empty_file_path, tmp_header_empty_file_path)
    logger.info(f"{meta_header_empty}")

    # Download Header not empty template
    dbx_tmp_header_file_path = os.path.join(dbx_video_template_directory, header_path)
    tmp_header_file_path = os.path.join(tmp_directory, header_path)
    meta_header = dropbox_download_file(access_token, dbx_tmp_header_file_path, tmp_header_file_path)
    logger.info(f"{meta_header}")

    # Download Body empty template
    dbx_body_empty_file_path = os.path.join(dbx_video_template_directory, body_empty_path)
    tmp_body_empty_file_path = os.path.join(tmp_directory, body_empty_path)
    meta_body_empty = dropbox_download_file(access_token, dbx_body_empty_file_path, tmp_body_empty_file_path)
    logger.info(f"{meta_body_empty}")

    # Download Body template
    dbx_body_file_path = os.path.join(dbx_video_template_directory, body_path)
    tmp_body_file_path = os.path.join(tmp_directory, body_path)
    meta_body = dropbox_download_file(access_token, dbx_body_file_path, tmp_body_file_path)
    logger.info(f"{meta_body}")

    # Download Closing Empty template
    dbx_closing_empty_file_path = os.path.join(dbx_video_template_directory, closing_empty_path)
    tmp_closing_empty_file_path = os.path.join(tmp_directory, closing_empty_path)
    meta_closing_empty = dropbox_download_file(access_token, dbx_closing_empty_file_path, tmp_closing_empty_file_path)
    logger.info(f"{meta_closing_empty}")

    # Download Closing template
    dbx_tmp_closing_file_path = os.path.join(dbx_video_template_directory, closing_path)
    tmp_closing_file_path = os.path.join(tmp_directory, closing_path)
    meta_closing = dropbox_download_file(access_token, dbx_tmp_closing_file_path, tmp_closing_file_path)
    logger.info(f"{meta_closing}")

    # Download the company logo file
    dbx_company_logo_file_path = os.path.join(dbx_video_template_directory, company_logo_path)
    tmp_company_logo_file_path = os.path.join(tmp_directory, company_logo_path)
    meta_logo = dropbox_download_file(access_token, dbx_company_logo_file_path, tmp_company_logo_file_path)
    logger.info(f"{meta_logo}")

    # Dowload the MP3 audio file
    dbx_default_audio_file_path = os.path.join(dbx_video_template_directory, default_audio_path)
    tmp_default_audio_path = os.path.join(tmp_directory, default_audio_path)
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


    # Set desired volume of original clip after transofrmation if different from default
    
    if args.volume:
        volume = args.volume
        logger.info(f"Volume set to {volume}")

    if validate_file_exists(tmp_default_audio_path):
        audio_file = AudioFileClip(tmp_default_audio_path)
        logger.info(f"Default audio loaded {meta_audio}")

    # Define how much to trim at the start and at the end of the selected clip
    start_trim_sec = 0
    stop_trim_sec = 0
    logger.info(f"start_trim_sec = {start_trim_sec} and stop_trim_sec = {stop_trim_sec} ")

    if start_trim_sec !=0:
        clip = cut_first_n_sec(clip, start_trim_sec)
        logger.info(f"Trimming the start of {start_trim_sec}")

    if stop_trim_sec != 0:
        clip = cut_last_n_sec(clip, stop_trim_sec)
        logger.info(f"Trimming the end of {stop_trim_sec}")

    logger.info(f"Check if the closing must be customized")
    logger.info(f"Empty closing is {empty_closing}")

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
    
    filename = create_video(clip, header, body, closing, flight_date, location, audio_file, volume, generated_uuid) 

    tmp_output_file_path = os.path.join(tmp_directory, filename)
    logger.info(f"{tmp_output_file_path} succesfully created")

    if validate_file_exists(tmp_output_file_path):
        # upload to Dropox
        dbx_tmp_output_file_path = os.path.join(dbx_video_output_directory, filename)
   
        meta_upload = dropbox_upload_file(access_token, tmp_directory, filename, dbx_tmp_output_file_path)
        logger.info(f"{meta_upload}")
        
        # share the link
        link = dropbox_get_link(access_token, dbx_tmp_output_file_path)
        logger.info(f"File {link} ready to be downloaded")

        # Clean the temporary folder
        deleted_files = remove_folder(tmp_directory)
        print(f"All files in '{tmp_directory}' were deleted: {deleted_files}")
        logger.debug(f"All files deleted succesfully")

        # send to provided email
        if args.email:
            logger.info("Preparing to send email")
            sender_email = 'severini.simone@gmail.com'
            receiver_email = args.email
            subject = f'Volo tandem del {flight_date} a {location}'
            body = f'Carissimo/a {passenger},\n\ngrazie per aver condividiso con me questo bellissimo volo. Questo il link dove scaricare la tua esperienza di volo libero in parapendio. Ciao Simone {link}'

            send_email(sender_email, receiver_email, subject, body)
            logger.info(f"Email sent to {args.email}")


if __name__ == '__main__':
    test_mode = os.environ.get("TEST_MODE") == "1"
    arguments = parse_arguments(test_mode)
    main(arguments)

# Example command to run
# export TEST_MODE=1
# python app.py -f clip_short.mp4 -n Simone -d 23/4/2023 -l Bergeggi

