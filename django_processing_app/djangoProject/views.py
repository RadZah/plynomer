import os
import subprocess
import io
from urllib.parse import unquote

from django.http import HttpResponse, FileResponse, HttpResponseNotFound
from django.shortcuts import render

from decouple import config
from datetime import datetime

import numpy as np
from scipy.stats import linregress
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

    # Assuming your static/media URL setting is set correctly
    relative_image_url = os.path.join(config("RELATIVE_PROCESSING_IMAGES_PATH"), last_image)

    return relative_image_url


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


def other_view_plotly():
    """ Plot the data from the database using plotly """

    # Simple Moving Average Function
    def calculate_sma(data, window=5):
        return np.convolve(data, np.ones(window) / window, mode='valid')

    # Extract data
    data = Gassmeter.objects.values_list('value', 'timestamp').order_by('-timestamp')
    gas_values, timestamps = zip(*[(float(item[0]), item[1]) for item in data])

    # Filter out the bottom 5% and top 5% of original values
    sorted_combined = sorted(list(zip(gas_values, timestamps)), key=lambda x: x[0])
    lower_index = int(len(gas_values) * 0.15)
    upper_index = int(len(gas_values) * 0.85)

    filtered_combined = sorted_combined[lower_index:upper_index]

    # Reorder the filtered list by timestamps
    reordered_filtered_combined = sorted(filtered_combined, key=lambda x: x[1])

    # Extract values and timestamps from reordered list
    filtered_values, filtered_timestamps = zip(*reordered_filtered_combined)

    # Calculate SMAs
    window_size = 40  # Example window size
    sma_original = calculate_sma(gas_values, window_size)
    sma_filtered = calculate_sma(filtered_values, window_size)

    # Original Data Plot
    fig_original = go.Figure()
    fig_original.add_trace(go.Scatter(x=timestamps, y=gas_values, mode='markers', name='Vsechna data'))
    fig_original.add_trace(go.Scatter(x=timestamps[window_size - 1:], y=sma_original, mode='lines',
                                      name=f'Simple Moving Average {window_size}'))
    fig_original.update_layout(title='Vsechna rozpoznana data',
                               xaxis_title='Stredoevropsky cas',
                               yaxis_title='Spotreba plynu [m3]',
                                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

    # Filtered Data Plot
    fig_filtered = go.Figure()
    fig_filtered.add_trace(go.Scatter(x=filtered_timestamps, y=filtered_values, mode='markers', name='Osetrena data'))
    fig_filtered.add_trace(go.Scatter(x=filtered_timestamps[window_size - 1:], y=sma_filtered, mode='lines',
                                      name=f'Simple Moving Average {window_size}'))
    fig_filtered.update_layout(
        title='Data orezena o 10% extremnich hodnot',
        xaxis_title='Stredoevropsky cas',
        yaxis_title='Spotreba plynu [m3]',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

    # Convert the plots to HTML
    plot_html_original = fig_original.to_html(full_html=False)
    plot_html_filtered = fig_filtered.to_html(full_html=False)

    return plot_html_original, plot_html_filtered
