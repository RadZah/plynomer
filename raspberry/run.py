#! /usr/bin/env python3

import subprocess
import time

from datetime import datetime
import requests
from config import URL_SERVER, RASPBERRY_PI_FILE_STORAGE

print("Script run.py initiated")


def copy_to_server(image_path):
    """ Copies the image to the server."""
    with open(image_path, "rb") as file:
        response = requests.post(URL_SERVER, files={"file": file})
    if response.status_code == 200:
        print("OK")
    else:
        print(f"Request failed with status code {response.status_code}")
        print(response.text)


def capture_image(image_path):
    """ Captures an image from the camera."""
    command = ["libcamera-still", "n", "1", "-o", image_path, "--width", "800", "--height", "450"]
    subprocess.run(command, check=True)


# Main loop
while True:
    # creates filename
    timestamp = datetime.now().isoformat()
    image_name = f"image_{timestamp}.jpg"
    image_path = RASPBERRY_PI_FILE_STORAGE + "/" + image_name

    # captures image
    capture_image(image_path)
    print("captured")

    # copies image to server
    copy_to_server(image_path)
    print("copied to server")

    # wait 5 minutes
    time.sleep(300)
