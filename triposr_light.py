import os
import requests
import base64
import time
import wget
from datetime import datetime

def choose_image(input_folder):
    """
    Выбирает изображение из указанной папки.
    """
    if not os.path.exists(input_folder):
        os.makedirs(input_folder)
        print(f"Folder '{input_folder}' created. Please put your images in JPEG format into this folder.")
        exit()

    images = [f for f in os.listdir(input_folder) if f.endswith('.jpg')]
    print("Choose image:")
    for i, img in enumerate(images, 1):
        print(f"{i}. {img}")
    
    choice = input("Enter the number of the image: ")
    try:
        choice = int(choice)
        if 1 <= choice <= len(images):
            return os.path.join(input_folder, images[choice - 1])
        else:
            print("Invalid choice. Please enter a number within the range.")
            return choose_image(input_folder)
    except ValueError:
        print("Invalid choice. Please enter a number.")
        return choose_image(input_folder)

def generate_model(image_path, api_key):
    """
    Генерирует 3D модель из изображения.
    """
    with open(image_path, 'rb') as file:
        image_data = base64.b64encode(file.read()).decode('utf-8')

    url = "https://api.tripo3d.ai/v2/openapi/task"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    data = {"type": "image_to_model", "file": {"type": "jpg", "data": image_data}}
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json().get("data", {}).get("task_id")
    else:
        print("Error:", response.text)
        return None

def check_task_status(task_id, api_key):
    """
    Проверяет статус задачи.
    """
    url = f"https://api.tripo3d.ai/v2/openapi/task/{task_id}"
    headers = {"Authorization": f"Bearer {api_key}"}

    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            status = response.json().get("data", {}).get("status")
            if status == "success":
                return True
            elif status in ["failed", "cancelled", "unknown"]:
                return False
            else:
                print("Model generation task is still in progress...")
                time.sleep(5)
        else:
            print("Error checking task status:", response.text)
            return False

def animate_and_download(model_task_id, api_key):
    animation_task_id = animate_model(model_task_id, api_key)
    if animation_task_id:
        print("Animation task ID:", animation_task_id)
        if check_task_status(animation_task_id, api_key):
            download_result(animation_task_id, api_key, is_animated=True)
            print("Animation task is completed and results are downloaded successfully!")

def animate_model(task_id, api_key):
    url = "https://api.tripo3d.ai/v2/openapi/task"
    data = {"type": "animate_model", "original_model_task_id": task_id}
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json().get("data", {}).get("task_id")
    else:
        print("Error:", response.text)
        return None

def download_result(task_id, api_key, is_animated=True):
    url = f"https://api.tripo3d.ai/v2/openapi/task/{task_id}"
    headers = {"Authorization": f"Bearer {api_key}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json().get("data", {})
        output = data.get("output")
        print(f"Output data received: {output}")  # Вывод данных для диагностики

        if output:
            folder_name = datetime.now().strftime("%y%m%d_%H_%M_%S")
            os.makedirs(folder_name, exist_ok=True)

            if is_animated:
                model_url = output.get("model")
                if model_url:
                    model_zip_filename = os.path.join(folder_name, "model.zip")
                    wget.download(model_url, model_zip_filename)
                    print(f"Animated model downloaded to {model_zip_filename}")

                video_url = output.get("rendered_video")
                if video_url:
                    video_filename = os.path.join(folder_name, "video.mp4")
                    wget.download(video_url, video_filename)
                    print(f"Video downloaded to {video_filename}")
            else:
                model_url = output.get("model")
                if model_url:
                    static_model_filename = os.path.join(folder_name, "model.glb")
                    wget.download(model_url, static_model_filename)
                    print(f"Static model downloaded to {static_model_filename}")
        else:
            print("Error: No output data found for the task.")
    else:
        print("Error:", response.text)

def main():
    api_key = "YOUR_API_KEY"  # Замените на ваш API ключ
    input_folder = "input"
    image_path = choose_image(input_folder)
    print("Selected image:", image_path)
    model_task_id = generate_model(image_path, api_key)
    
    if model_task_id:
        print("Model generation task ID:", model_task_id)
        if check_task_status(model_task_id, api_key):
            animate_choice = input("Do you want to make the model animated? (Y/n) ").lower()
        if animate_choice == 'y':
            animate_and_download(model_task_id, api_key)
        else:
            print("Downloading the static model...")
            download_result(model_task_id, api_key, is_animated=False)
            print("Model download is completed successfully!")

if __name__ == "__main__":
    main()

