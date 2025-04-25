import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from huggingface_hub import InferenceClient
import base64
import pyttsx3
import re
import io
from PIL import Image
#from googletrans import Translator
#import asyncio
#from indic_transliteration import sanscript
#from indic_transliteration.sanscript import transliterate

app = Flask(__name__)
CORS(app)

# === CONFIG ===
API_KEY = "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"
DEFAULT_PROMPT = "Describe this image in very brief."
client = InferenceClient(provider="nebius", api_key=API_KEY)
base64_image=""
#translator = Translator()

# === TTS setup ===

def speak(text):
    print("\n Caption:\n" + text)
    engine = pyttsx3.init()
    engine.setProperty('rate', 160)
    engine.setProperty('volume', 1.0)
    voices = engine.getProperty('voices')

    for voice in voices:
        if 'english' in voice.name.lower() and 'india' in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break

    engine.say(text)
    engine.runAndWait()

def generate_caption(prompt, base64_image):
    print(f"\n Sending prompt: {prompt}")

    completion = client.chat.completions.create(
        model="google/gemma-3-27b-it",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }},
                ]
            }
        ],
        max_tokens=256,
    )
    return completion.choices[0].message["content"]

def encode_image_to_base64(file):
    image_bytes = file.read()
    return base64.b64encode(image_bytes).decode("utf-8")

# async def translate_text(caption):
#     translator = Translator()
#     result = await translator.translate(caption, dest="or")
#     translated_text=result.text
#     print(translated_text)
#     return translated_text

# def transliterate_text(text, lang='oriya'):
#     return transliterate(text, sanscript.ORIYA, sanscript.ITRANS)

def clean_text(caption: str) -> str:
    # Remove ** formatting
    caption = caption.replace('**', '')

    match = re.search(r'Overall Impression:\s*(.*?)(\n\s*\n|\Z)', caption, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload-image', methods=['POST'])
def caption():
    
    image = request.files['image']
    global base64_image
    base64_image = encode_image_to_base64(image)
    caption = generate_caption(DEFAULT_PROMPT, base64_image)
    #print(caption)
    caption = caption.replace('**', '')
    #caption3=asyncio.run(translate_text(caption2))
    #transliterated_caption = transliterate_text(caption3)
    #speak(caption2)
    return jsonify({"caption": caption})

@app.route('/voice-query', methods=['POST'])
def voice_query():
    #base64_image = data['image']
    data = request.get_json()
    prompt = data.get('prompt')
    caption = generate_caption(prompt, base64_image)
    caption = caption.replace('**', '')
    #caption3=asyncio.run(translate_text(caption))
    return jsonify({"caption": caption})

if __name__ == '__main__':
    #app.run(host="0.0.0.0",port=5000,debug=True)
    app.run(ssl_context=('ssl.crt', 'ssl.key'), host='0.0.0.0', port=443,debug=True)
