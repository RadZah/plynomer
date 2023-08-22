# Raspberry Pi Zero W Photo Capture & API Upload

This application is designed for Raspberry Pi Zero W devices to automatically capture photos using a connected camera module and subsequently send them to an API server for processing.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Setup](#setup)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Features

- Automatic photo capture at defined intervals.
- Seamless upload to a designated API endpoint.

## Requirements

- Raspberry Pi Zero W.
- Raspberry Pi Camera Module (v3).
- Pre-configured API server to accept and process image uploads.
- Raspbian OS (preferably the latest version) installed on the Raspberry Pi.

## Setup

1. **Hardware Setup**:
    - Connect the Raspberry Pi Camera Module to the Raspberry Pi Zero W.
    - Ensure the Pi is connected to the internet, either via Wi-Fi or another suitable method.

2. **Software Setup**:

3. **Configuration**:
    
## Usage

1. Test the application:
    ```bash
    python run.py
    ```

2. The application should be now start capturing photos at the interval of 5 minutes (can be modified in code), and will attempt to upload them to the API server.

## Troubleshooting

- **Issue**: Failed uploads.
  - **Solution**: Check your API server's status and ensure that the Raspberry Pi has a stable internet connection.

- **Issue**: Camera not detected.
  - **Solution**: Ensure the camera module is correctly connected and that the camera interface is enabled in the Raspberry Pi configuration (`libcamera-hello`).

More troubleshooting solutions can be found in the [Wiki](https://www.raspberrypi.com/documentation/computers/camera_software.html#getting-started).

## Contributing

Contributions are welcome!

## License

This project is licensed under the MIT License.
