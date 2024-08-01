import logging

def configure_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),  # Logs to the console
            # logging.FileHandler('app.log')  # Optionally, also log to a file
        ]
    )

