import os
from flask import Flask, request, jsonify, render_template
from flask import session
from flask_cors import CORS
from huggingface_hub import InferenceClient
import base64
import re
import io
from PIL import Image


app = Flask(__name__, template_folder="../templates")
CORS(app)
app.secret_key = "some-random-secret-key"
# === CONFIG ===
API_KEY = "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"
DEFAULT_PROMPT = "Describe this image in very brief."
client = InferenceClient(provider="nebius", api_key=API_KEY)
base64_image=""

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload-image', methods=['POST'])
def caption():
    
    image = request.files['image']
	session['base64_image'] = base64_image
    #global base64_image
    base64_image = encode_image_to_base64(image)
    session['base64_image'] = base64_image
    caption = generate_caption(DEFAULT_PROMPT, base64_image)
    caption = caption.replace('**', '')

    return jsonify({"caption": caption})

@app.route('/voice-query', methods=['POST'])
def voice_query():
    data = request.get_json()
    prompt = data.get('prompt')
    base64_image = session.get('base64_image')
    caption = generate_caption(prompt, base64_image)
    caption = caption.replace('**', '')

    return jsonify({"caption": caption})

# if __name__ == '__main__':
    # #app.run(host="0.0.0.0",port=5000,debug=True)
    # app.run(ssl_context=('ssl.crt', 'ssl.key'), host='0.0.0.0', port=443,debug=True)

def handler(request):
    return app(request.environ, lambda status, headers: (status, headers))
