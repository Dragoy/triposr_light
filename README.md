# Tripo3D API Model Fetcher

## Overview

The Tripo3D API Model Fetcher is a Python script designed to automate the process of generating and downloading 3D models and animations using the Tripo3D API. It allows users to generate 3D models from images, animate them if desired, and download the resulting models and animations.

## Features

- **Image to Model Conversion**: Convert images to 3D models using the Tripo3D API.
- **Animation**: Animate generated 3D models with the option to download the animations.
- **Simple Command Line Interface**: Easy-to-use command line interface for selecting images and controlling the download process.

## Requirements

- Python 3.x
- Requests library

## Usage

1. **Clone the Repository**: Clone this repository to your local machine.

    ```
    git clone https://github.com/Dragoy/triposr_light.git
    ```

2. **Install Dependencies**: Navigate to the project directory and install the required dependencies using pip.

    ```
    cd triposr_light
    pip install -r requirements.txt
    ```

3. **Obtain API Key**: Obtain your Tripo3D API key from the Tripo3D website and replace `"YOUR_API_KEY"` in the script with your actual API key.

4. **Prepare Images**: Place the images you want to convert to 3D models in the `input` folder.

5. **Run the Script**: Execute the `triposr_light.py` script.

    ```
    python triposr_light.py
    ```

6. **Follow the Prompts**: Follow the prompts to select an image, choose whether to animate the model, and wait for the download to complete.

## Contributing

Contributions are welcome! If you encounter any issues or have suggestions for improvements, please feel free to open an issue or submit a pull request.

---
