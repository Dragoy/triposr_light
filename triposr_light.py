import os
import requests
import base64
import time
import wget
from datetime import datetime
from dotenv import load_dotenv
from tqdm.auto import tqdm

def choose_image(input_folder):
    """
    Выбирает изображение из указанной папки.
    """
    if not os.path.exists(input_folder):
        os.makedirs(input_folder)
        print(f"\nFolder '{input_folder}' created. Please put your images in supported formats (PNG, JPG/JPEG, WebP) into this folder.")
        exit()

    supported_formats = ['png', 'jpg', 'jpeg', 'webp']
    images = [f for f in os.listdir(input_folder) if f.lower().endswith(tuple(supported_formats))]
    
    print("\nChoose image:")
    for i, img in enumerate(images, 1):
        print(f"{i}. {img}")
    
    try:
        choice = input("\nEnter the number of the image: ")
        try:
            choice = int(choice)
            if 1 <= choice <= len(images):
                return os.path.join(input_folder, images[choice - 1])
            else:
                print("Invalid choice. Please enter a number within the range.")
                return None
        except ValueError:
            print("Invalid input. Please enter a valid number.")
            return None
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Exiting...")
        exit(0)

def generate_model(image_path, api_key):
    """
    Генер��рует 3D модель из изображения.
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
    
    Симметрия:
    - force_symmetry: принудительная симметрия модели
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
    
    quality_choice = input("\nChoose texture quality (1-2) [2]: ").strip()
    if not quality_choice:
        quality_choice = "2"  # detailed по умолчанию
    while quality_choice not in ['1', '2']:
        print("Please enter 1 or 2")
        quality_choice = input("Choose texture quality (1-2) [2]: ").strip()
    
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
    
    # Выбор симметрии
    print("\nSymmetry options:")
    print("1. No - Default model (default)")
    print("2. Yes - Force model symmetry")
    
    symmetry_choice = input("\nForce model symmetry? (1-2) [1]: ").strip()
    if not symmetry_choice:
        symmetry_choice = "1"  # без симметрии по умолчанию
    while symmetry_choice not in ['1', '2']:
        print("Please enter 1 or 2")
        symmetry_choice = input("Force model symmetry? (1-2) [1]: ").strip()
    
    texture_quality = "detailed" if quality_choice == "2" else "standard"
    texture_alignment = "geometry" if alignment_choice == "2" else "original_image"
    is_animated = animation_choice == "2"
    force_symmetry = symmetry_choice == "2"
    
    data = {
        "type": "image_to_model",
        "file": {"type": file_extension, "data": image_data},
        "model_version": versions[version_choice],
        "texture_quality": texture_quality,
        "texture_alignment": texture_alignment,
        "force_symmetry": force_symmetry
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json().get("data", {}).get("task_id"), is_animated
    else:
        print("Error:", response.text)
        return None, False

def check_task_status(task_id, api_key):
    """
    Проверяет статус задачи с визуальным индикатором прогресса.
    """
    url = f"https://api.tripo3d.ai/v2/openapi/task/{task_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    pbar = tqdm(total=100, desc="Generating model", 
                bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]')
    
    last_progress = 0
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json().get("data", {})
            status = data.get("status")
            progress = data.get("progress", 0)
            
            if status == "success":
                pbar.update(100 - last_progress)  # Добиваем до 100%
                pbar.close()
                print("\n✓ Model generation completed successfully!")
                return True
            elif status in ["failed", "cancelled", "unknown"]:
                pbar.close()
                print(f"\n✗ Model generation {status}!")
                return False
            else:
                # Обновляем прогресс
                if progress > last_progress:
                    pbar.update(progress - last_progress)
                    last_progress = progress
                time.sleep(0.5)
        else:
            pbar.close()
            print("\nError checking task status:", response.text)
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

def create_progress_hook(filename):
    """
    Создает хук для отслеживания прогресса загрузки в едином стиле
    """
    def progress_hook(current, total, width=50):
        if total > 0:
            percent = current * 100 / total
            progress = int(width * current / total)
            progress_bar = '█' * progress + '░' * (width - progress)
            
            # Увеличим количество пробелов для гарантированной очистки
            clear_line = '\r' + ' ' * 200
            
            # Очищаем строку и возвращаем каретку в начало
            print(clear_line, end='\r')
            
            # Печатаем прогресс
            status_line = f"⬇ Downloading {filename}... [{progress_bar}] {percent:.1f}%"
            print(status_line, end='', flush=True)
            
            # Печатаем новую строку после завершения
            if current >= total:
                print()
    return progress_hook

def download_result(task_id, api_key, is_animated=True):
    """
    Скачивает результаты с прогресс-баром tqdm
    """
    url = f"https://api.tripo3d.ai/v2/openapi/task/{task_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json().get("data", {})
        output = data.get("output")

        if output:
            output_dir = "output"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            folder_name = os.path.join(output_dir, datetime.now().strftime("%y%m%d_%H_%M_%S"))
            os.makedirs(folder_name, exist_ok=True)

            def download_file(url, filename, desc):
                """Вспомогательная функция для скачивания файла с прогресс-баром"""
                response = requests.get(url, stream=True)
                total_size = int(response.headers.get('content-length', 0))
                
                with open(filename, 'wb') as f, tqdm(
                    desc=desc,
                    total=total_size,
                    unit='iB',
                    unit_scale=True,
                    unit_divisor=1024,
                ) as pbar:
                    for data in response.iter_content(chunk_size=1024):
                        size = f.write(data)
                        pbar.update(size)

            if is_animated:
                model_url = output.get("model")
                if model_url:
                    original_name = model_url.split('/')[-1].split('?')[0]
                    model_zip_filename = os.path.join(folder_name, original_name)
                    download_file(model_url, model_zip_filename, "Downloading animated model")
                    print(f"Animated model saved to: {model_zip_filename}")

                video_url = output.get("rendered_video")
                if video_url:
                    original_name = video_url.split('/')[-1].split('?')[0]
                    video_filename = os.path.join(folder_name, original_name)
                    download_file(video_url, video_filename, "Downloading video")
                    print(f"Video saved to: {video_filename}")
            else:
                model_url = output.get("model") or output.get("pbr_model")
                if model_url:
                    original_name = model_url.split('/')[-1].split('?')[0]
                    static_model_filename = os.path.join(folder_name, original_name)
                    download_file(model_url, static_model_filename, "Downloading model")
                    print(f"Model saved to: {static_model_filename}")

                image_url = output.get("rendered_image")
                if image_url:
                    original_name = image_url.split('/')[-1].split('?')[0]
                    image_filename = os.path.join(folder_name, original_name)
                    download_file(image_url, image_filename, "Downloading preview")
                    print(f"Preview image saved to: {image_filename}")
        else:
            print("Error: No output data found for the task.")
    else:
        print("Error:", response.text)

def load_api_key():
    """
    Загружает API ключ из переменных окружения или запрашивает у пользователя
    """
    load_dotenv()  # загружаем переменные из .env файла
    api_key = os.getenv('TRIPO_API_KEY')
    
    if not api_key:
        print("API key not found in .env file")
        api_key = input("Please enter your Tripo3D API key: ").strip()
        
        # Предложим сохранить ключ в .env
        save = input("Would you like to save this API key to .env file? (y/N): ").lower()
        if save == 'y':
            with open('.env', 'w') as f:
                f.write(f'TRIPO_API_KEY={api_key}')
            print("API key saved to .env file")
    
    return api_key

def main():
    try:
        api_key = load_api_key()
        input_folder = "input"
        
        while True:
            image_path = choose_image(input_folder)
            if image_path:
                break
            
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
                    
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Exiting...")
        exit(0)

if __name__ == "__main__":
    main()