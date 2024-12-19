from pysondb import db
database = db.getDb("db.json")
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

get_analysis()