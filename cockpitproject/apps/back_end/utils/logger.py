import logging


class ErrorLogger:
    """_debuggig error logger class_"""

    def debug_logger(self, logger):
        """_Create a logging instance_

        Args:
            logger (_type_): _description_
        """
        logger.setLevel(logging.INFO)  # you can set this to be DEBUG, INFO, ERROR
        try:
            # Assign a file-handler to that instance
            fh = logging.FileHandler("datasets/elogger.txt")
            fh.setLevel(logging.INFO)  # again, you can set this differently

            # Format your logs (optional)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            fh.setFormatter(formatter)  # This will set the format to the file handler

            # Add the handler to your logging instance
            logger.addHandler(fh)

        except Exception as err:
            # creating/opening a file
            with open("datasets/emessage.txt", "w") as error_file:
                # writing in the file
                error_file.write("Please, create a file elogger.txt" + str(err) + "\n")
        return None
