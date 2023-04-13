from moviepy.editor import *
import datetime
from utilities import cut_first_n_sec, cut_last_n_sec, prepare_heading, prepare_closing, create_video
from logger_config import setup_logger
import configparser
import os
import uuid
import argparse


def valid_date(date_string):
    try:
        return datetime.datetime.strptime(date_string, "%d/%m/%Y").date()
    except ValueError:
        msg = f"Invalid date format: '{date_string}'. Expected format: DD/MM/YYYY."
        raise argparse.ArgumentTypeError(msg)


def parse_arguments(test_mode=False):
    if test_mode:
        class TestArgs:
            file = "clip_short.mp4"
            name = "Test Passenger"
            date = valid_date("13/04/2022")
            location = "Test location"
            volume=0.3
        return TestArgs()


    parser = argparse.ArgumentParser(description="A Cli version to make tandemo video")

    parser.add_argument("-f", "--file", help="Path to the input file. Your clip to process", required=True)
    parser.add_argument("-n", "--name", type=str, help="The name of the passenger", required=True)
    parser.add_argument("-d", "--date", type=valid_date, help="A date in the format DD/MM/YYYY", required=True)
    parser.add_argument("-l", "--location", type=str, help="The location of the flight", required=True)
    parser.add_argument("-v", "--volume", type=float, help="Set the volume of the mp3 soundtrack (default = 0.3)")

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

    video_template_directory = config.get('constants', 'video_template_directory')
    video_output_directory = config.get('constants', 'video_output_directory')

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
    if not os.path.exists(video_template_directory):
        logger.error(f"The directory {video_template_directory} does not exist!")
        raise ValueError(f"The directory {video_template_directory} does not exist!")

    logger.info(f"The directory '{video_template_directory}' exists.")

    # Create the Output directory if it doesn't exist
    os.makedirs(video_output_directory, exist_ok=True)

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


    # Load customer clip
    clip_name=args.file
    clip = VideoFileClip(clip_name)
    logger.info(f"Customer Clip is loaded named {clip_name}") 

    # Set desired volume of original clip after transofrmation if different from default
    
    if args.volume:
        volume = args.volume
        logger.info(f"Volume set to {volume}")

    # Load the MP3 audio file
    audio_file = AudioFileClip(os.path.join(video_template_directory, default_audio_path))
    logger.info(f"Default audio loaded")

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
        header = prepare_heading(header, slogan, company_logo_path)
        logger.info(f"Customizing heading clip -> done")


    # if in config.ini we set to True PREP_CLOSING then we rely on an empty template and apply our text
    if empty_closing: 
        logger.info(f"Customizing closing clip -> started")
        # If you pass a closing clip that is empty make sure the variable EMPTY_CLOSING=True in config.ini
        closing = prepare_closing(closing, passenger, generated_uuid, company_logo_path)

        logger.info(f"Customizing closing clip -> done")

    # Ready to generate the final video which is made of an header, a body template with on top a customer clip and closing
    
    filename = create_video(clip, header, body, closing, flight_date, location, audio_file, volume, generated_uuid) 


    logger.info(f"Job completed succesfully. File: {filename}")

if __name__ == '__main__':
    test_mode = os.environ.get("TEST_MODE") == "1"
    arguments = parse_arguments(test_mode)
    main(arguments)

# Example command to run
# export TEST_MODE=1
# python app.py -f clip_short.mp4 -n Simone -d 23/4/2023 -l Bergeggi

