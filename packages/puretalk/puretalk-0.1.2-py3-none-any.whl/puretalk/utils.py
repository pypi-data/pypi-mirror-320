import requests
from numba.core.ir import Raise


def tts_call(voice_id,text):
    api_url = "https://api.puretalk.ai/api/v1/tts"
    payload = {
        "voice_id": voice_id,
        "text": text,
        "output_format": "wav",
        "encoding": "pcm_f32le",
        "sample_rate": 16000,
        "language": "en",
        "voice_speed": 0,
        "voice_emotion": []
    }
    headers = {
        "X-API-KEY": "tmbYsMOBbrnVdrrnj6E3TJ3e0VwwNf95MlW2R-3-xOI",
        "Content-Type": "application/json"
    }

    response = requests.post(api_url, json=payload, headers=headers)
    if response.status_code == 200:
        return response
    else:
        raise "error while calling the model"
