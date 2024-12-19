import os
import requests
import time

input_folder = "/var/www/bird/upload_images"
flask_url_upload = "http://94.72.98.150:8000/upload"
flask_url_analysis = "http://94.72.98.150:8000/analysis"
check_interval = 10

def is_file_fully_written(file_path, check_delay=0.5, retries=3):
    for attempt in range(retries):
        try:
            if os.path.getsize(file_path) > 0:
                with open(file_path, 'rb') as f:
                    f.read(1024)
                return True
        except (OSError, IOError):
            time.sleep(check_delay)
    return False

def upload_images():
    files = os.listdir(input_folder)
    images = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    for image in images:
        image_path = os.path.join(input_folder, image)
        
        if not is_file_fully_written(image_path):
            print(f"File {image} is not fully written. Skipping...")
            continue
        try:
            with open(image_path, 'rb') as img_file:
                files = {'images': img_file}
                response = requests.post(flask_url_upload, files=files)

            # Перевірка відповіді
            print(f"Response status: {response.status_code}")
            print(f"Response text: {response.text}")

            if response.status_code == 204:
                print(f"Uploaded: {image}")
                os.remove(image_path)  # Видаляємо зображення після завантаження
            else:
                print(f"Failed to upload {image}: {response.text}")

        except Exception as e:
            print(f"Error uploading {image}: {e}")


def trigger_analysis():
    try:
        response = requests.get(flask_url_analysis)
        
        if response.status_code == 200:
            print("Analysis triggered successfully.")
        else:
            print(f"Failed to trigger analysis: {response.json()}")
    except Exception as e:
        print(f"Error during analysis request: {e}")


if __name__ == "__main__":
    while True:
        upload_images()
        trigger_analysis()
        time.sleep(check_interval)
