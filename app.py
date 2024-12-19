from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
import requests
import os
import base64
from openai import OpenAI
import uuid 
from def_analisis_images_openai import image_analysis_openai
from pysondb import db
from datetime import datetime

app = Flask(__name__)


app.config['UPLOAD_FOLDER'] = '/var/www/bird/images'
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

database = db.getDb("db.json")

@app.route('/upload_single_raw', methods=['POST'])
def upload_single_raw():
    # Проверяем Content-Type
    if request.content_type != 'image/jpeg':
        return jsonify({"error": "Invalid Content-Type. Only 'image/jpeg' is supported."}), 400

    # Генерация уникального имени файла
    unique_filename = f"{uuid.uuid4()}.jpg"
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

    try:
        # Создаём папку, если её нет
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Чтение потока данных и запись в файл
        with open(image_path, 'wb') as f:
            while chunk := request.stream.read(4096):  # Читаем куски по 4КБ
                f.write(chunk)

        date_now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        print(f"File saved: {image_path}")

        # Сохраняем информацию в "базу данных"
        database.add({
            "file_name": unique_filename,
            "date": date_now,
            "is_check": False,
            "result": None,
            "coordinates": "47.82291044072433, 35.0928351908966"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "message": "Upload successful",
        "file_name": unique_filename,
        "file_path": image_path
    }), 200


@app.route('/upload', methods=['POST'])
def download_images():
    if 'images' not in request.files:
        return jsonify({"error": "No image files in request"}), 400
        
    files = request.files.getlist('images')
        
    for file in files:
        if file.filename == '':
            continue

        if file:
            unique_filename = f"{uuid.uuid4()}.jpg"
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            try:
                file.save(image_path)
                date_now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                print(f"File saved: {image_path}")
                database.add({
                    "file_name": unique_filename,
                    "date": date_now,
                    "is_check": False,
                    "result": None,
                    "coordinates": "47.82291044072433, 35.0928351908966"
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
    return jsonify({"message": "Upload successful"}), 200


@app.route('/analysis', methods=['GET'])
def get_analysis():
    images = database.getAll()
    for image in images:
        if not image["is_check"]:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image["file_name"])
            if os.path.exists(image_path):
                # Отримуємо JSON-відповідь
                json_response = image_analysis_openai(image_path)
                if json_response is not None:
                    database.updateByQuery(
                        {"file_name": image["file_name"]},
                        {
                            "is_check": True,
                            "result": json_response  # Зберігаємо як JSON
                        }
                    )
                else:
                    print(f"Не вдалося проаналізувати зображення: {image_path}")
    return jsonify({"status": "Analysis complete"}), 200

@app.route('/index', methods=['GET'])
def index():
    analyzed_images = database.getByQuery({"is_check": True})
    images_data = [
        {
            "image_display_path": "http://94.72.98.150:8000/images/" + image["file_name"],
            "response_text": image["result"],
            "date": image["date"],
            "coordinates": image["coordinates"]
        }
        for image in analyzed_images
    ]
    return render_template('index.html', images_data=images_data)

@app.route('/test')
def test():
     return "Server is running!", 200

if __name__ == '__main__':
    app.run(debug=True)
