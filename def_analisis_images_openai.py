import base64
from openai import OpenAI
import json

   
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def image_analysis_openai(image_path):
    base64_image = encode_image(image_path)
        
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": "As an expert in ornithology and geography, especially in the field of bird species of Eastern Europe and Ukraine in particular, analyze the image and provide the following information: 1. Determine if the image contains a bird.2. Identify the species of the bird in the image. 3. Assess the probability of correct species identification based on the likelihood of encountering this species in Ukraine in the wild. Return **only** the result as a JSON object with the following structure: {\"object\":\"XXX\", \"common_name\":\"YYY\", \"latin_name\":\"ZZZ\", \"probability\":0..100}",
                },
                {
                "type": "image_url",
                "image_url": {
                    "url":  f"data:image/jpeg;base64,{base64_image}"
                },
                },
            ],
            }
        ],
    )
    response_text = response.choices[0].message.content
    
    cleaned_response = response_text.strip("```").strip().replace("json", "").strip()
    
    if cleaned_response.startswith("{"):
        try:
            json_response = json.loads(cleaned_response)
            return json_response
        except json.JSONDecodeError as e:
            print("Помилка декодування JSON:", e)
            return None
    else:
        print("Отримано не JSON:", cleaned_response)
        return None   
