#! /usr/bin/env python3

from decouple import config

import os
import time

import requests
from tempfile import NamedTemporaryFile

from django.core.files.temp import NamedTemporaryFile


BASE_URL = config('BASE_URL')
BASE_SAVE_PATH = config('BASE_SAVE_PATH')


def fetch_images_from_laravel(image_path, image_name, order_id):

    full_url = BASE_URL + image_path + image_name
    save_path = os.path.join(BASE_SAVE_PATH, image_name)

    # Download the image
    with requests.get(full_url, stream=True) as image_response:
        image_response.raise_for_status()

        # autoamtically deletes file when closed
        # with NamedTemporaryFile(delete=True) as temp_image:
        with NamedTemporaryFile() as temp_image:

            # Read the streamed image in sections
            for chunk in image_response.iter_content(1024 * 8):
                temp_image.write(chunk)

            # Save the image
            with open(save_path, 'wb') as out_file:
                temp_image.seek(0)
                out_file.write(temp_image.read())


def fetch_list_of_images():

    url = "https://zahornad.cz/api/images"
    response = requests.get(url)
    response_data = response.json()  # Assuming the response is in JSON format

    x = 1
    for image_data in response_data:
        fetch_images_from_laravel(image_data['url'], image_data['filename'], x)
        time.sleep(1)
        x += 1


if __name__ == "__main__":
    fetch_list_of_images()
