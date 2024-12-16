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
        print(f"Folder '{input_folder}' created. Please put your images in supported formats (PNG, JPG/JPEG, WebP) into this folder.")
        exit()

    supported_formats = ['png', 'jpg', 'jpeg', 'webp']
    images = [f for f in os.listdir(input_folder) if f.lower().endswith(tuple(supported_formats))]
    
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
    except ValueError:
        print("Invalid input. Please enter a valid number.")

def generate_model(image_path, api_key):
    """
    Генерирует 3D модель из изображения.
    Поддерживает разные версии моделей:
    - default
    - v2.0-20240919
    - v1.4-20240625
    - v1.3-20240522
    
    Качество текстур:
    - standard: стандартное качество (по умолчанию)
    - detailed: высокое качество с детализацией
    
    Выравнивание текстур:
    - original_image: приоритет визуальной точности к исходному изображению
    - geometry: приоритет точности 3D геометрии
    """
    with open(image_path, 'rb') as file:
        image_data = base64.b64encode(file.read()).decode('utf-8')

    file_extension = image_path.split('.')[-1].lower()

    if file_extension not in ['png', 'jpg', 'jpeg', 'webp']:
        raise ValueError("Unsupported file format. Only PNG, JPG/JPEG, and WebP are supported.")

    url = "https://api.tripo3d.ai/v2/openapi/task"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    
    # Доступные версии моделей
    versions = {
        "1": "default",
        "2": "v2.0-20240919",
        "3": "v1.4-20240625",
        "4": "v1.3-20240522"
    }
    
    print("\nAvailable model versions:")
    for key, value in versions.items():
        print(f"{key}. {value}")
    
    version_choice = input("\nChoose model version (1-4) [2]: ").strip()
    if not version_choice:
        version_choice = "2"  # v2.0-20240919 по умолчанию
    while version_choice not in versions:
        print("Please enter a number between 1 and 4")
        version_choice = input("Choose model version (1-4) [2]: ").strip()
    
    # Выбор качества текстуры
    print("\nTexture quality options:")
    print("1. standard - Standard quality (default)")
    print("2. detailed - High quality with fine details")
    
    quality_choice = input("\nChoose texture quality (1-2) [1]: ").strip()
    if not quality_choice:
        quality_choice = "1"  # standard по умолчанию
    while quality_choice not in ['1', '2']:
        print("Please enter 1 or 2")
        quality_choice = input("Choose texture quality (1-2) [1]: ").strip()
    
    # Выбор выравнивания текстуры
    print("\nTexture alignment options:")
    print("1. original_image - Prioritize visual fidelity to source image (default)")
    print("2. geometry - Prioritize 3D structural accuracy")
    
    alignment_choice = input("\nChoose texture alignment (1-2) [1]: ").strip()
    if not alignment_choice:
        alignment_choice = "1"  # original_image по умолчанию
    while alignment_choice not in ['1', '2']:
        print("Please enter 1 or 2")
        alignment_choice = input("Choose texture alignment (1-2) [1]: ").strip()
    
    # Выбор анимации
    print("\nAnimation options:")
    print("1. No - Static model (default)")
    print("2. Yes - Animated model")
    
    animation_choice = input("\nChoose animation option (1-2) [1]: ").strip()
    if not animation_choice:
        animation_choice = "1"  # без анимации по умолчанию
    while animation_choice not in ['1', '2']:
        print("Please enter 1 or 2")
        animation_choice = input("Choose animation option (1-2) [1]: ").strip()
    
    texture_quality = "detailed" if quality_choice == "2" else "standard"
    texture_alignment = "geometry" if alignment_choice == "2" else "original_image"
    is_animated = animation_choice == "2"
    
    data = {
        "type": "image_to_model",
        "file": {"type": file_extension, "data": image_data},
        "model_version": versions[version_choice],
        "texture_quality": texture_quality,
        "texture_alignment": texture_alignment
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json().get("data", {}).get("task_id"), is_animated
    else:
        print("Error:", response.text)
        return None, False

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
            # Создаем папку output если её нет
            output_dir = "output"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Создаем подпапку с датой и временем внутри output
            folder_name = os.path.join(output_dir, datetime.now().strftime("%y%m%d_%H_%M_%S"))
            os.makedirs(folder_name, exist_ok=True)

            if is_animated:
                model_url = output.get("model")
                if model_url:
                    model_zip_filename = os.path.join(folder_name, "model.zip")
                    wget.download(model_url, model_zip_filename)
                    print(f"\nAnimated model downloaded to {model_zip_filename}")

                video_url = output.get("rendered_video")
                if video_url:
                    video_filename = os.path.join(folder_name, "video.mp4")
                    wget.download(video_url, video_filename)
                    print(f"\nVideo downloaded to {video_filename}")
            else:
                # Пробуем получить обычную модель
                model_url = output.get("model")
                if not model_url:
                    # Если нет обычной модели, пробуем получить PBR модель
                    model_url = output.get("pbr_model")
                
                if model_url:
                    static_model_filename = os.path.join(folder_name, "model.glb")
                    print(f"\nDownloading model from: {model_url}")
                    wget.download(model_url, static_model_filename)
                    print(f"\nStatic model downloaded to {static_model_filename}")
                else:
                    print("\nError: No model URL found in the output")

                # Скачиваем превью изображение, если оно есть
                image_url = output.get("rendered_image")
                if image_url:
                    image_filename = os.path.join(folder_name, "preview.webp")
                    wget.download(image_url, image_filename)
                    print(f"\nPreview image downloaded to {image_filename}")
        else:
            print("Error: No output data found for the task.")
    else:
        print("Error:", response.text)

def main():
    api_key = "tsk_1YNclg9JGliLfWkTA1oHKf4bEhpjElkZMvi0569d0EE"  # Замените на ваш API ключ
    input_folder = "input"
    image_path = choose_image(input_folder)
    print("Selected image:", image_path)
    
    model_task_id, is_animated = generate_model(image_path, api_key)
    
    if model_task_id:
        print("Model generation task ID:", model_task_id)
        if check_task_status(model_task_id, api_key):
            if is_animated:
                animate_and_download(model_task_id, api_key)
            else:
                print("Downloading the static model...")
                download_result(model_task_id, api_key, is_animated=False)
                print("Model download is completed successfully!")

if __name__ == "__main__":
    main()