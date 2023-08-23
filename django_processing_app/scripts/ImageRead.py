# hack to import django models
import os
import django

import sys

sys.path.append('/srv/app')
# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')

# Initialize Django
django.setup()

# Now you can import your Django models and use the ORM
from gassmeter.models import Gassmeter

from datetime import datetime
import urllib
import pytesseract as pytesseract
# import cv2 as opencv
import cv2

from matplotlib import pyplot as plt


class ImageRead:
    orig_img = None
    img = None
    text = None
    timestamp = None
    filename = None
    path = None

    def __init__(self, path, filename):
        self.path = path
        self.filename = filename

    def read(self):
        self.orig_img = cv2.imread(self.path, cv2.IMREAD_GRAYSCALE)
        return

    def extract_timestamp_from_filename(self):
        """ Extracts timestamp from image filename
         image_2023-08-06T12:46:50.830226.jpg """
        # Extract the timestamp substring from the filename
        timestamp_str = self.filename.split("_")[1].split(".")[0]
        timestamp_str = decoded_time_string = urllib.parse.unquote(timestamp_str)

        # Convert the timestamp string to a datetime object
        self.timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S")
        # print("timestamp", self.timestamp)
        return self.timestamp

    def resize(self):
        # resize to width 800
        resized_img = cv2.resize(self.orig_img, (800, int(self.orig_img.shape[0] * 800 / self.orig_img.shape[1])))
        self.img = resized_img
        return

    def crop(self):
        y_start, y_end = 200, 260  # Start and end Y-coordinates (vertical)
        x_start, x_end = 80, 400  # Start and end X-coordinates (horizontal)
        # Crop the image using array slicing
        self.img = self.img[y_start:y_end, x_start:x_end]
        return

    def show_image(self):
        plt.imshow(self.img, cmap='gray')
        plt.show()

    def save_image(self):
        output_path = self.path.replace("input_images", "processing_images")
        cv2.imwrite(output_path, self.img)
        return

    def extract_gasmeter_value_by_pattern(self, read_values):
        """ Beecause there are multiple string separated by newline char
        it is neccessarry to compare each such stsring compare to
        for searched pattern and extract just it, if exists """

        founded = 0

        read_values_array = read_values.split("\n")
        for each_read in read_values_array:

            # START_VALUE = "0031"
            START_VALUE = "003"
            if each_read.startswith(START_VALUE) and len(each_read) >= 7:
                # founded = each_read.substr(0, 7)
                founded = each_read[0:7]

        return founded

    def extract_text(self, lang):
        """ Get text from image """

        # self.text = pytesseract.image_to_string(self.img)
        config = '-c tessedit_char_whitelist=0123456789 --psm 6'
        text = pytesseract.image_to_string(self.img, lang=lang, config=config)
        text = text.replace(" ", "")
        recognised_value = self.extract_gasmeter_value_by_pattern(text)
        # self.text = recognised_value
        # only_wanted_part = self.extract_gasmeter_value_by_pattern(recognised_value)
        # return self.text
        return recognised_value

    def read_the_best_value(self):
        first_lang_value = self.extract_text(lang='eng')

        # We'll store the updated value in best_value
        first_lang_value_str = str(first_lang_value)

        best_value = list(first_lang_value_str)

        # print("first_lang_value", first_lang_value)
        # print("first_lang_value_str", first_lang_value_str)

        # If the Czech model recognizes "1" or "4", then use English model for further decision
        if "1" in first_lang_value_str or "7" in first_lang_value_str:
        # if "4" in first_lang_value_str:
            print("1 or 7 first_lang_value_str", first_lang_value_str)
            second_lang_value = self.extract_text(lang='ces')
            second_lang_value_str = str(second_lang_value)
            if second_lang_value_str == "0":
                print("second_lang_value_str", second_lang_value_str)
                print("nebudem zpracovávat")
                best_value = list(second_lang_value_str)
            else:
                print("second value", second_lang_value)

                for i, (c, e) in enumerate(zip(first_lang_value_str, second_lang_value_str)):
                    if c == "1" or c == "7":
                        if e == "1" or e == "4":
                            best_value[i] = "1"
                            print("R first_lang_value_str", first_lang_value_str)
                            print("R best_value", best_value)
                        elif e == "7":
                            best_value[i] = "7"
                            print("S first_lang_value_str", first_lang_value_str)
                            print("S best_value", best_value)
                        else:
                            print("T english recognised ", e)

        best_value = "".join(best_value)

        # print("BBBest_value", best_value)

        self.text = best_value  # Update the class attribute with the best value
        return best_value



    def save_to_db(self, image_hash):

        # convert into decimal format
        real_decimal_value = formatted_string = f"{self.text[:-2]}.{self.text[-2:]}"

        gassmeter_instance = Gassmeter(timestamp=self.timestamp,
                                       text=self.text,
                                       image_hash=image_hash,
                                       value=real_decimal_value)
        gassmeter_instance.save()
