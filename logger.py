import logging

# Create a custom logger
logger = logging.getLogger("app_logger")

# Set the minimum log level
logger.setLevel(logging.DEBUG)

# Create a console handler
console_handler = logging.StreamHandler()

# Set the level for the console handler
console_handler.setLevel(logging.DEBUG)

# Create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add the console handler to the logger (avoid duplicate handlers)
if not logger.hasHandlers():
    logger.addHandler(console_handler)
