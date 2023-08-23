import os
import subprocess
import io
from urllib.parse import unquote

from django.http import HttpResponse, FileResponse, HttpResponseNotFound
from django.shortcuts import render

from decouple import config
from datetime import datetime

import numpy as np
from matplotlib import pyplot as plt
import plotly.graph_objects as go

from gassmeter.models import Gassmeter


def home(request):
    """ Home page with plots and image """

    context = {}

    context["just_string"] = just_string()
    context["another_string"] = another_string()

    context["last_read_image"] = last_read_image()

    context["plotly"] = other_view_plotly()

    return render(request, 'partials/home.html', context)


def just_string():
    return "just string"


def another_string():
    return "another string"


def get_gassmeter_list(request):
    """ get all values from the database """
    gassmeter_list = list(Gassmeter.objects.all())
    return gassmeter_list


def last_read_image():
    processing_images_dir = config('PROCESSING_IMAGES_PATH')

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

    # get just first value
    last_image = sorted_filenames[-1]

    path_to_last_image = os.path.join(processing_images_dir, last_image)

    # try:
    #     img_file = open(path_to_last_image, 'rb')
    #     response = FileResponse(img_file, content_type='image/jpg')
    #     response['Content-Disposition'] = f'inline; filename={last_image}'
    # except FileNotFoundError:
    #     response = HttpResponseNotFound("Image not found" + path_to_last_image)
    #
    # return response

    # Assuming your static/media URL setting is set correctly
    relative_image_url = os.path.join(config("RELATIVE_PROCESSING_IMAGES_PATH"), last_image)

    return relative_image_url
    # return render(request, 'layout.html', {'last_read_image': relative_image_url})


def YYYlast_read_image(request):
    processing_images_dir = config('PROCESSING_IMAGES_PATH')

    # Fetch the latest record from Gassmeter model
    latest_record = Gassmeter.objects.latest('timestamp')

    # If there's no record found, handle the case (return a not found response or some other handling)
    # if not latest_record:
    #     return HttpResponseNotFound("No latest record found")

    # latest_image_filename = f"image_{latest_record.timestamp.isoformat().replace(':', '%3A')}.jpg"
    latest_image_filename = f"image_{latest_record.timestamp.isoformat()}.jpg"

    # Create the full path to the latest image
    path_to_last_image = os.path.join(processing_images_dir, latest_image_filename)

    # Open the image and send it as a response
    try:
        with open(path_to_last_image, 'rb') as img_file:
            response = FileResponse(img_file, content_type='image/jpg')
            response['Content-Disposition'] = f'inline; filename={latest_image_filename}'
    except FileNotFoundError:
        error_text = " not found " + path_to_last_image
        response = HttpResponseNotFound("Image not found" + path_to_last_image)

    return response


def plot_view(request):
    """ Plot the data from the database using matplotlib """

    # Extract data
    data = Gassmeter.objects.values_list('text', 'timestamp').order_by('timestamp')
    # Convert 'text' to integers and separate the data into two lists
    texts, timestamps = zip(*[(int(item[0]), item[1]) for item in data])

    plt.figure(figsize=(12, 7))
    plt.plot(timestamps, texts)
    plt.scatter(timestamps, texts, c="red", alpha=1, s=20, marker="x")
    plt.ylabel('Spotřeba')
    plt.xlabel('Čas')
    plt.title('Spotřeba plynu')

    # Save the plot to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)

    # Serve the plot directly as an image
    response = FileResponse(buf, content_type='image/png')
    response['Content-Disposition'] = 'inline; filename="plot.png"'

    return response


def Xplot_view(request):
    """ Plot the data from the database using matplotlib """

    # Extract data
    data = Gassmeter.objects.values_list('text', 'timestamp')
    # Convert 'text' to integers and separate the data into two lists
    texts, timestamps = zip(*[(int(item[0]), item[1]) for item in data])

    # Convert timestamps into a format that can be used for mathematical operations
    timestamps_numeric = [t.timestamp() for t in timestamps]
    # Compute distances between consecutive data points
    distances = [timestamps_numeric[i + 1] - timestamps_numeric[i] for i in range(len(timestamps_numeric) - 1)]
    # Use mean and standard deviation to color points
    mean_distance = np.mean(distances)
    std_distance = np.std(distances)

    colors = []
    # for d in distances:
    #     if d < mean_distance - 0.5 * std_distance or d > mean_distance + 0.5 * std_distance:
    #         colors.append('red')  # outlier
    #     else:
    #         colors.append('blue')  # densely packed
    # colors.append(colors[-1])  # for the last point

    colors.append('blue')  # densely packed

    plt.figure(figsize=(10, 5))
    plt.scatter(timestamps, texts, c=colors)
    plt.plot(timestamps, texts, color='gray')  # connecting line
    plt.ylabel('Spotřeba')
    plt.xlabel('Čas')
    plt.title('Spotřeba plynu')

    # Save the plot to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)

    # Serve the plot directly as an image
    response = FileResponse(buf, content_type='image/png')
    response['Content-Disposition'] = 'inline; filename="plot.png"'

    return response


# def plot_view_plotly():
def other_view_plotly():
    """ Plot the data from the database using plotly """

    # Extract data - just the last 100 records
    data = Gassmeter.objects.values_list('value', 'timestamp').order_by('timestamp')[:40]
    # Convert 'text' to integers and separate the data into two lists
    gas_values, timestamps = zip(*[(float(item[0]), item[1]) for item in data])

    fig = go.Figure(data=go.Scatter(x=timestamps,
                                    y=gas_values,
                                    mode='lines+markers'))
    fig.update_layout(title='Vývoj spotřeby plynu',
                      xaxis_title='Časové razítko (Central European, Prague)',
                      yaxis_title='Rozpoznaná hodnota v m3')

    # Convert the plot to HTML
    plot_html = fig.to_html(full_html=False)

    return plot_html


def plot_view_plotly(request):
    """ Plot the data from the database using plotly """

    # Extract data
    data = Gassmeter.objects.values_list('text', 'timestamp').order_by('timestamp')
    # Convert 'text' to integers and separate the data into two lists
    texts, timestamps = zip(*[(int(item[0]), item[1]) for item in data])

    fig = go.Figure(data=go.Scatter(x=timestamps,
                                    y=texts,
                                    mode='lines+markers'))
    fig.update_layout(title='Vývoj spotřeby plynu',
                      xaxis_title='Časové razítko (timestamp | Prague)',
                      yaxis_title='Rozpoznaná hodnota v m3')

    # Convert the plot to HTML
    plot_html = fig.to_html(full_html=False)

    return render(request, 'layout.html', {'plot_html': plot_html})


def copy_script(request):
    """ Copies images from one folder to another """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    script_path = os.path.join(base_dir, 'scripts', 'copy.py')

    result = subprocess.run(['python', script_path], capture_output=True, text=True)

    if result.returncode == 0:
        return HttpResponse('Script executed successfully.<br>Output:<br>' + result.stdout)
    else:
        return HttpResponse('Error executing script.<br>Error:<br>' + result.stderr)


def process_image(request):
    """ Process image - CROP, EXTRACT TEXT, SAVE TO DB """

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    script_path = os.path.join(base_dir, 'scripts', 'process_images.py')

    result = subprocess.run(['python', script_path], capture_output=True, text=True)

    if result.returncode == 0:
        return HttpResponse('Script PROCESS_IMAGE executed successfully.<br>Output:<br>' + result.stdout)
    else:
        return HttpResponse('Error PROCESS_IMAGE executing script.<br>Error:<br>' + result.stderr)
