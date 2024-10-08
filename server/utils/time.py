from datetime import datetime


def get_formatted_now():
    """Return time now in a human readable form"""
    return datetime.now().strftime("%d:%m:%Y %H:%M:%S")
