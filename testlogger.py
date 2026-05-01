import logging

#region test



def setup_logger(log_path="test.log") -> logging.Logger:
    logging.basicConfig(
        filename=log_path,
        encoding="utf-8",
        filemode="a",
        format="{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
    )

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    return logger

global logger
logger = setup_logger()

logger.debug("debug")
logger.error("error")
logger.info("info")
logger.warning("warning")
#endregion