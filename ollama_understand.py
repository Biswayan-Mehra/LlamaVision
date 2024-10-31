#!/usr/bin/python3
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import base64

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

api_key = "insert Tune AI API key Here"


def engaudio(resp):
    from pathlib import Path
    from openai import OpenAI
    client = OpenAI(api_key="enter open AI key here")

    speech_file_path = Path(__file__).parent / "output.wav"
    response = client.audio.speech.create(

    model="tts-1",
    voice="alloy",
    response_format="wav",
    input=resp
    )
    response.stream_to_file(speech_file_path)

    return base64.b64encode(open("output.wav","rb").read())

def bstoaudio(text):
    wav_file = open("output.wav", "wb")
    decode_string = base64.b64decode(text)
    wav_file.write(decode_string)
    

def translate(audio_file):
    url = "https://api.sarvam.ai/speech-to-text-translate"

    files=[
    ('file',('query.wav',open(audio_file,'rb'),'audio/wav'))
    ]
    headers = {
    'api-subscription-key': api_key
    }

    response = requests.request("POST", url, headers=headers, data={}, files=files)

    return response.json()['transcript'],response.json()['language_code']

def call_lamma_vision(text_in,imageurl_in,prompt_add): 
    url = "https://proxy.tune.app/chat/completions"
    headers = {
        "Authorization": "Enter tuneAI API_Key",
        "Content-Type": "application/json",
    }
    print(text_in + prompt_add)
    data = {
    "temperature": 0.8,
        "messages":  [
    {
        "role": "user",
        "content": [
        {
            "type": "text",
            "text": text_in + prompt_add
        },
        {
            "type": "image_url",
            "image_url": {
            "url": imageurl_in
            }
        }
        ]
    }
    ],
        "model": "meta/llama-3.2-90b-vision",
        "frequency_penalty":  0,
        "max_tokens": 900
    }
    response = requests.post(url, headers=headers, json=data)
    a = response.json()
    return a['choices'][0]['message']['content']

def translate_back(language,reply):
    if language is None or language == "en-IN":
        return engaudio(reply).decode("utf-8")
    else:
        urltr = "https://api.sarvam.ai/translate"
        payloadtr = {
            "input": reply,
            "source_language_code": "en-IN",
            "target_language_code": language,
            "mode": "formal"
        }
        headerstr = {
            "api-subscription-key": api_key,
            "Content-Type": "application/json"
        }


        translated_res = str(requests.request("POST", urltr, json=payloadtr, headers=headerstr).json()["translated_text"])
        print(translated_res)

        urlsp = "https://api.sarvam.ai/text-to-speech"

        payloadsp = {
            "inputs": [translated_res],
            "target_language_code": language
        }
        headerssp = {
            "api-subscription-key": api_key,
            "Content-Type": "application/json"
        }

        voice_bs = requests.request("POST", urlsp, json=payloadsp, headers=headerssp)

        return voice_bs.json()["audios"][0]

    # Main process flow
def process_flow(audio, img_url, eng_prompt):
    text, language_det = translate(audio)
    print(type(language_det))
    if language_det is None:
        language_det = "en-IN"
    print(text,language_det)
    response = call_lamma_vision(text, img_url, eng_prompt)
    print(response)
    bsfile = translate_back(language_det, response)
    return bsfile

# API endpoint for processing
@app.route('/process', methods=['POST'])
def process():
    if 'audio' not in request.files or 'img_url' not in request.form or 'prompt' not in request.form:
        return jsonify({"error": "Missing required parameters"}), 400
    
    audio = request.files['audio']
    img_url = request.form['img_url']
    prompt = request.form['prompt']
    
    # Save the uploaded audio file
    audio_path = "query.wav"
    audio.save(audio_path)
    
    # Call the process_flow function
    result = process_flow(audio_path, img_url, prompt)
    print(result[:10])
    
    return jsonify({"audio":str(result)})

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
