# Tripo3D API Model Fetcher

## Overview

The Tripo3D API Model Fetcher is a Python script designed to automate the process of generating and downloading 3D models and animations using the Tripo3D API. It allows users to generate 3D models from images, animate them if desired, and download the resulting models and animations.

## Features

- **Image to Model Conversion**: Convert images to 3D models using the Tripo3D API.
- **Animation**: Animate generated 3D models with the option to download the animations.
- **Simple Command Line Interface**: Easy-to-use command line interface for selecting images and controlling the download process.
- **Environment Configuration**: Secure API key storage using .env file.

## Requirements

- Python 3.x
- Required Python packages (installed via requirements.txt):
  - python-dotenv
  - requests
  - wget

## Installation

1. **Clone the Repository**: Clone this repository to your local machine.

    ```bash
    git clone https://github.com/Dragoy/triposr_light.git
    ```

2. **Install Dependencies**: Navigate to the project directory and install the required dependencies using pip.

    ```bash
    cd triposr_light
    pip install -r requirements.txt
    ```

3. **Configure API Key**: 
    - Copy `.env.example` to create a new `.env` file:
      ```bash
      cp .env.example .env
      ```
    - Edit `.env` and replace `your_api_key_here` with your actual Tripo3D API key:
      ```
      TRIPO_API_KEY=your_actual_api_key
      ```
    - Alternatively, you can run the script and enter your API key when prompted. The script will offer to save it to the .env file.

4. **Prepare Images**: Place the images you want to convert to 3D models in the `input` folder.

## Usage

1. **Run the Script**: Execute the `triposr_light.py` script.

    ```bash
    python triposr_light.py
    ```

2. **Follow the Prompts**: Follow the prompts to:
   - Select an image from the input folder
   - Choose model version
   - Set texture quality and alignment
   - Choose whether to animate the model
   - Wait for the download to complete

The generated models and related files will be saved in the `output` folder, organized by date and time.

## Contributing

Contributions are welcome! If you encounter any issues or have suggestions for improvements, please feel free to open an issue or submit a pull request.

## Security Note

The `.env` file containing your API key is automatically ignored by git to prevent accidentally sharing your credentials. Never commit your actual API key to version control.

---
