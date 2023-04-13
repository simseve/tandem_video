import logging

def setup_logger():
    # Set up the logger
    logging.basicConfig(
        level=logging.DEBUG,  # Set the minimum logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format="%(asctime)s - %(levelname)s - %(message)s",  # Set the log message format
        handlers=[
            logging.FileHandler("app.log"),  # Log messages to a file named "app.log"
            logging.StreamHandler()  # Log messages to the console (stdout)
        ],
    )
    return logging.getLogger()