#! /usr/bin/env python3

import hashlib
import os
from datetime import datetime
from urllib.parse import unquote

from ImageRead import ImageRead

from gassmeter.models import Gassmeter


def generate_image_hash(image_path):
    """Generate a SHA-256 hash for an image."""
    with open(image_path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def process_image():
    # Get the directory of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the path to the "media" directory
    media_dir = os.path.join(script_dir, "..", "media")
    # Construct the path to the "processing_images" directory within "media"
    processing_images_dir = os.path.join(media_dir, "input_images")

    # print on new lien
    print("Script Directory:", script_dir)
    print("Media Directory:", media_dir)
    print("Processing Images Directory:", processing_images_dir)

    # SORT BY DATE
    # Helper function to extract datetime from the filename
    def extract_datetime_from_filename(filename):
        # Extracting the part containing the timestamp
        timestamp_str = filename.split('_')[1].split('.jpg')[0]
        # Decoding the URL encoded characters
        timestamp_str_decoded = unquote(timestamp_str)
        # Converting to a datetime object
        return datetime.fromisoformat(timestamp_str_decoded)

    # Sort filenames by the extracted datetime
    sorted_filenames = sorted(os.listdir(processing_images_dir), key=extract_datetime_from_filename)

    print("now processing images")

    # Only take the last 50 entries
    sorted_filenames = sorted_filenames[-50:]

    # Process each image
    for filename in sorted_filenames:

        src_file_path = os.path.join(processing_images_dir, filename)

        # Check if the hash exists in the database
        image_hash = generate_image_hash(src_file_path)
        exists = Gassmeter.objects.filter(image_hash=image_hash).exists()

        if not exists:
            # First time processing this image

            imgRead = ImageRead(src_file_path, filename)
            timestamp_value = imgRead.extract_timestamp_from_filename()
            imgRead.read()
            imgRead.resize()
            imgRead.crop()
            text = imgRead.read_the_best_value()
            if text != "0":
                image_hash = generate_image_hash(src_file_path)
                imgRead.save_to_db(image_hash)
                imgRead.save_image()
            else:
                pass

        else:
            # Already in database
            print(f"Image {src_file_path} already processed and saved.")

    print('process_image dinished successfully!')


if __name__ == "__main__":
    process_image()

print("End of file")
